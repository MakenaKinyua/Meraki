<script setup>
import { WifiOffIcon } from "@lucide/vue";
import { Button } from "@/components/ui/button";

defineProps({
  online: { type: Boolean, default: true },
  interrupted: Boolean,
});
defineEmits(["reconnect"]);
</script>

<template>
  <div
    v-if="!online || interrupted"
    class="flex items-center justify-between gap-3 border-b bg-muted px-5 py-2 text-sm sm:px-8"
    role="status"
  >
    <p class="flex items-center gap-2">
      <WifiOffIcon class="size-4 shrink-0" />
      {{
        online
          ? "Connection lost. Sync to check for new messages."
          : "You’re offline. Messages can’t send until you reconnect."
      }}
    </p>
    <Button
      v-if="online"
      variant="outline"
      size="sm"
      @click="$emit('reconnect')"
      >Sync</Button
    >
  </div>
</template>
