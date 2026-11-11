<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { ArrowDownIcon } from '@lucide/vue'
import { TextPart } from '@tanstack/ai-vue/ui'
import { LatticeLoader } from '@/components/ui/lattice-loader'
import {
  MessageScroller,
  MessageScrollerButton,
  MessageScrollerContent,
  MessageScrollerItem,
  MessageScrollerViewport,
  useMessageScroller,
} from '@/components/ui/message-scroller'

const props = defineProps({
  messages: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
})
const { scrollToEnd } = useMessageScroller()

const displayMessages = computed(() => props.messages.map((message) => ({
  ...message,
  content: message.parts
    .filter((part) => part.type === 'text')
    .map((part) => part.content)
    .join(''),
})))
const completedMessageId = ref('')
watch(() => props.messages.map((message) => message.id).join('\u0000'), async (ids, previousIds) => {
  const previous = new Set(previousIds ? previousIds.split('\u0000') : [])
  const newQuestion = props.messages.some((message) => !previous.has(message.id) && message.role === 'user')
  if (!newQuestion) return
  await nextTick()
  scrollToEnd({ behavior: 'smooth' })
})
watch(() => displayMessages.value.at(-1)?.role, (role) => {
  if (role === 'user') completedMessageId.value = ''
})
watch(() => props.loading, (loading, wasLoading) => {
  if (wasLoading && !loading) {
    completedMessageId.value = displayMessages.value.at(-1)?.role === 'assistant'
      ? displayMessages.value.at(-1).id
      : ''
  }
})
</script>

<template>
  <MessageScroller>
    <MessageScrollerViewport>
      <MessageScrollerContent
        :aria-busy="loading"
        class="mx-auto w-full max-w-[760px] gap-8 px-5 py-8 sm:px-8"
      >
        <MessageScrollerItem
          v-for="message in displayMessages"
          :key="message.id"
          :message-id="message.id"
          class="chat-message-enter"
        >
          <div v-if="message.role === 'user'" class="flex justify-end">
            <div class="user-message max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-6">{{ message.content }}</div>
          </div>
          <div v-else class="space-y-2">
            <TextPart :content="message.content" role="assistant" class="assistant-markdown text-sm leading-7" />
            <LatticeLoader
              v-if="(loading && message.id === displayMessages.at(-1)?.id) || completedMessageId === message.id"
              :status="error ? 'error' : loading ? 'working' : 'done'"
              label="Writing"
              done-label="Done in"
              error-label="Failed after"
              color="currentColor"
              done-color="#a5cf9a"
              error-color="#ef7777"
              :cell-size="5"
              :gap="2"
              :font-size="11"
              :step="82"
              class-name="text-muted-foreground"
            />
          </div>
        </MessageScrollerItem>
        <div v-if="loading && displayMessages.at(-1)?.role === 'user'" class="chat-message-enter pl-1">
          <LatticeLoader label="Thinking" color="currentColor" :font-size="12" :cell-size="5" :step="82" class-name="text-muted-foreground" />
        </div>
      </MessageScrollerContent>
    </MessageScrollerViewport>
    <MessageScrollerButton class="w-auto gap-2 rounded-full px-3 shadow-lg">
      <ArrowDownIcon class="size-4" /><span class="text-xs">{{ loading ? 'New response · Go to latest' : 'Go to latest' }}</span><span class="sr-only">Scroll to latest message</span>
    </MessageScrollerButton>
  </MessageScroller>
</template>
