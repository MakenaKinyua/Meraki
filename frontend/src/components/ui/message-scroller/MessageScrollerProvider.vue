<script setup>
import { provideMessageScroller } from "./useMessageScroller";

const props = defineProps({
  autoScroll: { type: Boolean, required: false },
  defaultScrollPosition: { type: String, required: false },
  scrollEdgeThreshold: { type: Number, required: false },
  scrollPreviousItemPeek: { type: Number, required: false },
  scrollMargin: { type: Number, required: false },
});

provideMessageScroller(props);
</script>

<template>
  <slot />
</template>
