<script setup>
import { ArrowUpIcon, LoaderCircleIcon } from '@lucide/vue'
import {
  InputGroup,
  InputGroupAddon,
  InputGroupButton,
  InputGroupTextarea,
} from '@/components/ui/input-group'

const draft = defineModel({ type: String, required: true })
defineProps({
  loading: { type: Boolean, default: false },
  online: { type: Boolean, default: true },
  error: { type: String, default: '' },
})
const emit = defineEmits(['send'])
</script>

<template>
  <div class="mx-auto w-full max-w-[820px] px-4 pb-4 sm:px-8">
    <p v-if="error" class="mb-2 rounded-lg border border-destructive/20 bg-destructive/5 px-3 py-2 text-sm text-destructive" role="alert">{{ error }}</p>
    <form @submit.prevent="emit('send')">
      <InputGroup>
        <InputGroupTextarea
          v-model="draft"
          aria-label="Ingredient question"
          placeholder="Ask about an ingredient"
          :disabled="loading"
          maxlength="200"
          class="max-h-40 min-h-12"
          @keydown.enter.exact.prevent="emit('send')"
        />
        <InputGroupAddon align="block-end">
          <InputGroupButton
            type="submit"
            size="icon-sm"
            variant="default"
            class="send-button ml-auto"
            :disabled="loading || !online || !draft.trim()"
            aria-label="Send message"
          >
            <LoaderCircleIcon v-if="loading" class="size-4 animate-spin" />
            <ArrowUpIcon v-else class="size-4" />
          </InputGroupButton>
        </InputGroupAddon>
      </InputGroup>
    </form>
    <p class="mt-2 text-center text-xs text-muted-foreground">
      {{ online ? 'General skincare information, not medical advice.' : 'Connect to the internet to send your message.' }}
    </p>
  </div>
</template>
