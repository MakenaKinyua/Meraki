<script setup>
import { PlusIcon } from '@lucide/vue'
import { Button } from '@/components/ui/button'

defineProps({
  conversations: { type: Array, required: true },
  activeId: { type: String, default: '' },
})
const emit = defineEmits(['new-chat', 'select'])
</script>

<template>
  <aside class="hidden w-72 shrink-0 flex-col border-r p-4 md:flex">
    <Button class="mb-4 justify-start gap-2" variant="outline" @click="emit('new-chat')">
      <PlusIcon class="size-4" /> New conversation
    </Button>
    <nav class="min-h-0 flex-1 space-y-1 overflow-y-auto" aria-label="Conversations">
      <button
        v-for="conversation in conversations"
        :key="conversation.id"
        class="conversation-link w-full truncate rounded-lg px-3 py-2 text-left text-sm"
        :class="conversation.id === activeId && 'conversation-link-active'"
        :title="conversation.title || 'New conversation'"
        @click="emit('select', conversation.id)"
      >{{ conversation.title || 'New conversation' }}</button>
      <p v-if="!conversations.length" class="px-3 py-2 text-sm text-muted-foreground">No conversations yet.</p>
    </nav>
  </aside>
</template>
