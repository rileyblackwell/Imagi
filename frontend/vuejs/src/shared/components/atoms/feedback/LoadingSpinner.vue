<!--
  LoadingSpinner.vue — the one spinner.

  Ten views drew this by hand as a bordered div with a contrasting top edge,
  and they had drifted into three colours: blue in Market and Operate, emerald
  in Sell, and a mix of blue-600 and blue-700 for the same ring in adjacent
  files. A spinner is chrome, not identity — it says "the app is working", not
  "you are in Sell" — so it is ink everywhere now, at one weight.
-->
<template>
  <div class="flex justify-center" :class="padded ? 'py-16' : ''">
    <div
      class="border-2 rounded-full animate-spin motion-reduce:animate-none border-blue-950/15 dark:border-white/15 border-t-blue-950/60 dark:border-t-white/70"
      :class="sizeClass"
      role="status"
      :aria-label="label"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    /** `sm` sits inside a button or a row; `md` is the default panel spinner. */
    size?: 'sm' | 'md' | 'lg'
    /** Wrap in the standard `py-16` block used when a whole panel is loading. */
    padded?: boolean
    /** Announced to screen readers in place of the silent spinning div. */
    label?: string
  }>(),
  { size: 'md', padded: true, label: 'Loading' }
)

const sizeClass = computed(
  () => ({ sm: 'w-4 h-4', md: 'w-6 h-6', lg: 'w-8 h-8' })[props.size]
)
</script>
