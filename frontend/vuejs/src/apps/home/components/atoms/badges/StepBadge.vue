<!--
  StepBadge — minimal editorial step marker for the home sections.
  A tone-tinted numeral chip (echoing the feature-card icon tiles) paired with a
  hairline and a tracked uppercase label. Replaces the old filled pill for a
  cleaner, more premium look. Tones: blue (Build) | orange (Run).
-->
<template>
  <div class="inline-flex items-center gap-3 transition-colors duration-300">
    <!-- Numeral chip -->
    <span
      class="relative grid place-items-center w-7 h-7 rounded-[0.55rem] ring-1 transition-all duration-300"
      :class="chipClass"
    >
      <span class="font-display text-[0.8rem] font-semibold leading-none tabular-nums" :class="numeralClass">
        {{ number }}
      </span>
    </span>

    <!-- Hairline + label -->
    <span class="inline-flex items-center gap-2.5">
      <span class="hairline h-px w-5" :class="hairlineClass" aria-hidden="true"></span>
      <span class="text-[0.7rem] font-semibold uppercase tracking-[0.24em]" :class="labelClass">
        {{ label }}
      </span>
    </span>
  </div>
</template>

<script>
import { defineComponent, computed } from 'vue'

export default defineComponent({
  name: 'StepBadge',
  props: {
    number: { type: String, required: true }, // e.g. '01'
    label: { type: String, required: true }, // e.g. 'Build'
    tone: { type: String, default: 'blue' } // blue | orange
  },
  setup(props) {
    const isOrange = computed(() => props.tone === 'orange')

    const chipClass = computed(() =>
      isOrange.value
        ? 'bg-orange-100 dark:bg-orange-400/[0.14] ring-orange-900/[0.08] dark:ring-orange-300/[0.18]'
        : 'bg-gradient-to-br from-[#dbeeff] to-[#9ecdf3] dark:from-blue-400/[0.18] dark:to-blue-500/[0.22] ring-blue-900/[0.08] dark:ring-blue-300/[0.18]'
    )

    const numeralClass = computed(() =>
      isOrange.value
        ? 'text-orange-700 dark:text-orange-200'
        : 'text-blue-700 dark:text-blue-200'
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

    return { chipClass, numeralClass, hairlineClass, labelClass }
  }
})
</script>
