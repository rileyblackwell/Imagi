<template>
  <div
    class="tier-card relative rounded-2xl p-8 bg-white/85 dark:bg-white/[0.045] backdrop-blur-sm border transition-all duration-300"
    :class="[
      isPopular
        ? 'border-orange-300/80 dark:border-orange-300/[0.25]'
        : 'border-blue-200/70 dark:border-blue-300/[0.14]'
    ]"
  >
    <!-- Popular Badge -->
    <div v-if="isPopular" class="absolute -top-3.5 left-1/2 -translate-x-1/2">
      <span class="inline-flex items-center px-3.5 py-1.5 rounded-full border border-orange-200/70 dark:border-orange-400/25 bg-[#fdf9f2] dark:bg-[#0c0c0e] text-xs font-semibold text-orange-700 dark:text-orange-300 uppercase tracking-[0.18em] transition-colors duration-300">
        Most Popular
      </span>
    </div>

    <!-- Tier Name -->
    <h3 class="text-lg font-semibold tracking-tight text-blue-950 dark:text-white mb-2 transition-colors duration-300">
      {{ name }}
    </h3>

    <!-- Price -->
    <div class="flex items-baseline gap-1 mb-6">
      <span class="font-display text-4xl font-semibold text-blue-950 dark:text-white tracking-tight tabular-nums transition-colors duration-300">
        {{ active.price === 0 ? 'Free' : `$${active.price}` }}
      </span>
      <span v-if="active.price !== 0" class="text-blue-950/60 dark:text-blue-100/55 text-sm transition-colors duration-300">/month</span>
    </div>

    <!-- Usage option selector (Max-style tiers pick between 5× and 20×) -->
    <div
      v-if="options && options.length > 1"
      class="flex w-full p-1 mb-6 rounded-full bg-blue-950/[0.04] dark:bg-white/[0.05] border border-blue-950/[0.07] dark:border-white/[0.08]"
      role="tablist"
      aria-label="Usage amount"
    >
      <button
        v-for="(opt, i) in options"
        :key="opt.lookupKey"
        type="button"
        role="tab"
        :aria-selected="selected === i"
        @click="selected = i"
        class="flex-1 py-1.5 px-3 rounded-full text-xs font-semibold transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50"
        :class="selected === i
          ? 'bg-white text-blue-950 shadow-sm dark:bg-[#f3ede2] dark:text-blue-950'
          : 'text-blue-950/55 hover:text-blue-950/80 dark:text-blue-100/55 dark:hover:text-blue-100/80'"
      >
        {{ opt.label }}
      </button>
    </div>

    <!-- Key Highlights: usage refreshes on a rolling 5-hour session and a weekly limit -->
    <div class="mb-6 space-y-2">
      <div class="flex items-center gap-2 text-sm text-blue-950/70 dark:text-blue-100/70 transition-colors duration-300">
        <svg class="w-4 h-4 flex-shrink-0" :class="isPopular ? 'text-orange-600 dark:text-orange-300' : 'text-blue-600 dark:text-blue-300'" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/>
        </svg>
        <span>{{ active.sessionLimit }}</span>
      </div>
      <div class="flex items-center gap-2 text-sm text-blue-950/70 dark:text-blue-100/70 transition-colors duration-300">
        <svg class="w-4 h-4 flex-shrink-0" :class="isPopular ? 'text-orange-600 dark:text-orange-300' : 'text-blue-600 dark:text-blue-300'" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"/>
        </svg>
        <span>{{ active.weeklyLimit }}</span>
      </div>
    </div>

    <!-- Feature List -->
    <ul class="space-y-3 mb-8 pt-5 border-t border-blue-950/[0.06] dark:border-white/[0.07]">
      <li
        v-for="(feature, index) in active.features"
        :key="index"
        class="flex items-start gap-3 text-sm text-blue-950/70 dark:text-blue-100/70 transition-colors duration-300"
      >
        <span
          class="flex-shrink-0 w-[18px] h-[18px] rounded-full ring-1 flex items-center justify-center mt-0.5 transition-all duration-300"
          :class="isPopular ? 'bg-orange-100 dark:bg-orange-400/[0.14] ring-orange-200/80 dark:ring-orange-300/[0.18]' : 'bg-gradient-to-br from-[#dbeeff] to-[#9ecdf3] dark:from-blue-400/[0.18] dark:to-blue-500/[0.22] ring-blue-200/80 dark:ring-blue-300/[0.18]'"
        >
          <svg class="w-2.5 h-2.5" :class="isPopular ? 'text-orange-600 dark:text-orange-300' : 'text-blue-600 dark:text-blue-300'" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
          </svg>
        </span>
        <span>{{ feature }}</span>
      </li>
    </ul>

    <!-- CTA Button -->
    <button
      @click="$emit('subscribe', active.lookupKey)"
      :disabled="loading"
      class="w-full inline-flex items-center justify-center py-3 px-6 rounded-full font-medium text-sm transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
      :class="[
        isPopular
          ? 'bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white shadow-[0_1px_2px_rgba(23,37,84,0.2),0_3px_8px_-2px_rgba(23,37,84,0.25)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.4),0_3px_8px_-2px_rgba(0,0,0,0.45)]'
          : 'border border-blue-950/[0.14] text-blue-950/80 hover:text-blue-950 hover:border-blue-950/30 hover:bg-blue-950/[0.03] dark:border-white/[0.16] dark:text-blue-100/80 dark:hover:text-white dark:hover:border-white/30 dark:hover:bg-white/[0.06]'
      ]"
    >
      <span v-if="loading" class="flex items-center justify-center gap-2">
        <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
        </svg>
        Processing...
      </span>
      <span v-else>{{ cta ?? 'Get Started' }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface TierOption {
  label: string
  price: number
  lookupKey: string
  sessionLimit: string
  weeklyLimit: string
  features: string[]
}

const props = defineProps<{
  name: string
  cta?: string
  isPopular?: boolean
  loading?: boolean
  // Single-option tiers pass these directly…
  price?: number
  lookupKey?: string | null
  sessionLimit?: string
  weeklyLimit?: string
  features?: string[]
  // …multi-option tiers (e.g. Max) pass these instead.
  options?: TierOption[]
}>()

defineEmits<{
  subscribe: [lookupKey: string | null]
}>()

const selected = ref(0)

// What's currently shown: the selected option for multi-option tiers,
// otherwise the tier's own props.
const active = computed(() => {
  const opt = props.options?.[selected.value]
  if (opt) return opt
  return {
    price: props.price ?? 0,
    lookupKey: props.lookupKey ?? null,
    sessionLimit: props.sessionLimit ?? '',
    weeklyLimit: props.weeklyLimit ?? '',
    features: props.features ?? [],
  }
})
</script>

<style scoped>
/* Crisp, sharply-defined card: hairline edge + tight layered shadow, gentle lift on hover */
.tier-card {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}

.tier-card:hover {
  transform: translateY(-4px);
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.04),
    0 2px 4px rgba(15, 23, 42, 0.06),
    0 10px 20px -4px rgba(15, 23, 42, 0.1),
    0 24px 44px -12px rgba(15, 23, 42, 0.14);
}

.dark .tier-card {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 12px 28px -10px rgba(0, 0, 0, 0.55);
}

.dark .tier-card:hover {
  transform: translateY(-4px);
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.06),
    0 2px 4px rgba(0, 0, 0, 0.5),
    0 12px 24px -4px rgba(0, 0, 0, 0.5),
    0 28px 48px -12px rgba(0, 0, 0, 0.6);
}

@media (prefers-reduced-motion: reduce) {
  .tier-card,
  .tier-card:hover {
    transform: none;
  }
}
</style>
