<script setup>
import { cn } from "cn";
import { Primitive } from "reka-ui";
import { bubbleVariants } from ".";

const props = defineProps({
  variant: { type: null, required: false, default: "default" },
  align: { type: String, required: false, default: "start" },
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
    data-slot="bubble"
    :data-variant="variant"
    :data-align="align"
    :as="as"
    :as-child="asChild"
    :class="cn(bubbleVariants({ variant }), props.class)"
  >
    <slot />
  </Primitive>
</template>
