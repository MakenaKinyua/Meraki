<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { fetchServerSentEvents, useChat } from '@tanstack/ai-vue'
import { onlineManager } from '@tanstack/vue-query'
import ChatComposer from '@/components/chat/ChatComposer.vue'
import ChatHeader from '@/components/chat/ChatHeader.vue'
import ChatMessages from '@/components/chat/ChatMessages.vue'
import NetworkBanner from '@/components/chat/NetworkBanner.vue'
import ChatSidebar from '@/components/chat/ChatSidebar.vue'
import WelcomePanel from '@/components/chat/WelcomePanel.vue'
import { LatticeLoader } from '@/components/ui/lattice-loader'
import { MessageScrollerProvider } from '@/components/ui/message-scroller'
import { queryClient } from '@/lib/query-client'
import { useChatStore } from '@/stores/chat'

const suggestions = [
  'What does niacinamide do?',
  'Is retinol right for sensitive skin?',
  'Tell me about glycerin',
]
const apiUrl = import.meta.env.VITE_API_URL || ''
const chatStore = useChatStore()
const draft = ref('')

const streamChat = useChat({
  threadId: crypto.randomUUID(),
  connection: fetchServerSentEvents(
    () => `${apiUrl}/api/conversations/${chatStore.conversationId}/messages`,
  ),
  onError: (error) => chatStore.handleConnectionError(error),
})

watch(
  () => streamChat.messages.value,
  (messages) => (chatStore.messages = messages),
  { deep: true },
)

watch(
  () => streamChat.isLoading.value,
  (loading) => {
    chatStore.isLoading = loading
    if (!loading) void chatStore.loadConversations()
  },
)

function startNewChat() {
  if (chatStore.isLoading) streamChat.stop()
  chatStore.startNewChat()
  streamChat.clear()
}

async function syncChat() {
  if (!chatStore.isOnline) return
  chatStore.error = ''
  const id = chatStore.conversationId
  await queryClient.invalidateQueries({ queryKey: ['conversations'] })
  if (id) await queryClient.invalidateQueries({ queryKey: ['conversations', id] })
  await chatStore.loadConversations()
  const messages = id ? await chatStore.loadConversation(id) : []
  if (!chatStore.error && messages !== null) {
    streamChat.setMessages(messages)
    chatStore.clearStreamInterrupted()
  }
}

async function openConversation(id) {
  if (chatStore.isLoading) streamChat.stop()
  chatStore.error = ''
  const previousId = chatStore.conversationId
  const previousTitle = chatStore.conversationTitle
  chatStore.setConversation(id)
  const messages = await chatStore.loadConversation(id)
  if (messages === null) {
    chatStore.setConversation(previousId, previousTitle)
    return
  }
  chatStore.clearStreamInterrupted()
  streamChat.setMessages(messages)
}

async function sendMessage(text = draft.value) {
  const content = text.trim()
  if (!content || chatStore.isLoading) return
  if (!chatStore.isOnline) return
  chatStore.clearStreamInterrupted()
  draft.value = ''

  try {
    if (!chatStore.conversationId) {
      const id = await chatStore.createConversation()
      streamChat.clear()
      chatStore.setConversation(id)
    }
    if (chatStore.conversationTitle === 'New conversation') {
      chatStore.conversationTitle = content
    }
    await streamChat.sendMessage(content)
  } catch (error) {
    chatStore.handleConnectionError(error)
  } finally {
    if (chatStore.conversationId) {
      void queryClient.invalidateQueries({ queryKey: ['conversations', chatStore.conversationId] })
    }
    void queryClient.invalidateQueries({ queryKey: ['conversations'] })
    void chatStore.loadConversations()
  }
}

const unsubscribeOnline = onlineManager.subscribe((online) => {
  const wasOnline = chatStore.isOnline
  chatStore.setOnline(online)
  if (!online && streamChat.isLoading.value) streamChat.stop()
  if (online && !wasOnline) void syncChat()
})

onMounted(async () => {
  chatStore.setOnline(onlineManager.isOnline())
  try {
    if (chatStore.isOnline) {
      await Promise.all([chatStore.loadConversations(), chatStore.loadConversation()])
      streamChat.setMessages(chatStore.messages)
    }
  } finally {
    chatStore.isInitializing = false
  }
})

onBeforeUnmount(() => {
  unsubscribeOnline()
})
</script>

<template>
  <div v-if="chatStore.isInitializing" class="app-loading min-h-svh">
    <LatticeLoader label="Preparing your chat" color="currentColor" :font-size="13" :cell-size="6" :step="90" />
  </div>

  <div v-else class="flex min-h-svh bg-background text-foreground">
    <ChatSidebar
      :conversations="chatStore.conversations"
      :active-id="chatStore.conversationId"
      @new-chat="startNewChat"
      @select="openConversation"
    />

    <main class="mx-auto flex h-svh w-full min-w-0 max-w-[1440px] flex-col">
      <ChatHeader :title="chatStore.conversationTitle" @new-chat="startNewChat" />
      <NetworkBanner :online="chatStore.isOnline" :interrupted="chatStore.streamInterrupted" @reconnect="syncChat" />

      <MessageScrollerProvider auto-scroll default-scroll-position="last-anchor">
        <section class="flex min-h-0 flex-1 flex-col" aria-label="Conversation">
          <WelcomePanel
            v-if="!chatStore.messages.length"
            :suggestions="suggestions"
            @suggestion="sendMessage"
          />
          <ChatMessages
            v-else
            :messages="chatStore.messages"
            :loading="chatStore.isLoading"
            :error="chatStore.error"
          />
        </section>
      </MessageScrollerProvider>

      <ChatComposer
        v-model="draft"
        :loading="chatStore.isLoading"
        :online="chatStore.isOnline"
        :error="chatStore.error"
        @send="sendMessage()"
      />
    </main>
  </div>
</template>
