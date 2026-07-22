<!--
  SectionLabel — minimal editorial eyebrow for section headers.
  The non-numbered sibling of StepBadge: a small tone diamond, a hairline, and a
  tracked uppercase label. Shares the "marker → hairline → label" spine so every
  section header across the site reads as one system. Tones: blue | orange.
-->
<template>
  <div class="inline-flex items-center gap-2.5 transition-colors duration-300">
    <span class="w-1.5 h-1.5 rotate-45 rounded-[1px]" :class="markerClass" aria-hidden="true"></span>
    <span class="hairline h-px w-5" :class="hairlineClass" aria-hidden="true"></span>
    <span class="text-[0.7rem] font-semibold uppercase tracking-[0.24em]" :class="labelClass">
      {{ label }}
    </span>
  </div>
</template>

<script>
import { defineComponent, computed } from 'vue'

export default defineComponent({
  name: 'SectionLabel',
  props: {
    label: { type: String, required: true }, // e.g. 'Why Imagi'
    tone: { type: String, default: 'blue' } // blue | orange
  },
  setup(props) {
    const isOrange = computed(() => props.tone === 'orange')

    const markerClass = computed(() =>
      isOrange.value
        ? 'bg-orange-500/80 dark:bg-orange-400/80'
        : 'bg-blue-500/80 dark:bg-blue-400/80'
    )

    const hairlineClass = computed(() =>
      isOrange.value
        ? 'bg-orange-300/70 dark:bg-orange-300/30'
        : 'bg-blue-300/70 dark:bg-blue-300/30'
    )

    const labelClass = computed(() =>
      isOrange.value
        ? 'text-orange-700/90 dark:text-orange-200/80'
        : 'text-blue-700/90 dark:text-blue-200/80'
    )

    return { markerClass, hairlineClass, labelClass }
  }
})
</script>
