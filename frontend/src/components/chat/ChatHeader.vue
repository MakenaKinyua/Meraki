<script setup>
import { PlusIcon } from '@lucide/vue'
import { Button } from '@/components/ui/button'

defineProps({ title: { type: String, required: true } })
const emit = defineEmits(['new-chat'])
</script>

<template>
  <header class="flex h-14 shrink-0 items-center justify-between border-b px-5 sm:px-8">
    <h1 class="truncate text-sm font-medium">{{ title }}</h1>
    <Button class="md:hidden" variant="outline" size="icon" aria-label="New conversation" @click="emit('new-chat')">
      <PlusIcon class="size-4" />
    </Button>
  </header>
</template>
