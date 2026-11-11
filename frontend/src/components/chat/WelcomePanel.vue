<script setup>
import { Button } from '@/components/ui/button'

defineProps({ suggestions: { type: Array, required: true } })
const emit = defineEmits(['suggestion'])
</script>

<template>
  <div class="m-auto w-full max-w-[640px] px-5 py-12 sm:px-8">
    <h2 class="text-3xl font-medium tracking-tight sm:text-4xl">Ask about a skincare ingredient</h2>
    <p class="mt-3 text-muted-foreground">What it does, who it suits, and what to watch for.</p>
    <div class="mt-8 flex flex-col items-start gap-2">
      <Button v-for="suggestion in suggestions" :key="suggestion" variant="outline" @click="emit('suggestion', suggestion)">
        {{ suggestion }}
      </Button>
    </div>
  </div>
</template>
