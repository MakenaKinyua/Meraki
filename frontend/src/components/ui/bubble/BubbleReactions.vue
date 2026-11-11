<script setup>
import { cn } from "cn";
import { Primitive } from "reka-ui";
import { bubbleReactionsVariants } from ".";

const props = defineProps({
  side: { type: null, required: false, default: "bottom" },
  align: { type: null, required: false, default: "end" },
  class: {
    type: [Boolean, null, String, Object, Array],
    required: false,
    skipCheck: true,
  },
  asChild: { type: Boolean, required: false },
  as: { type: null, required: false, default: "div" },
});
</script>

<template>
  <Primitive
    data-slot="bubble-reactions"
    :data-side="side"
    :data-align="align"
    :as="as"
    :as-child="asChild"
    :class="cn(bubbleReactionsVariants({ side, align }), props.class)"
  >
    <slot />
  </Primitive>
</template>
