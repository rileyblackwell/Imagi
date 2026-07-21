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
        ${{ price }}
      </span>
      <span class="text-blue-950/60 dark:text-blue-100/55 text-sm transition-colors duration-300">/month</span>
    </div>

    <!-- Key Highlights -->
    <div class="mb-6 space-y-2">
      <div class="flex items-center gap-2 text-sm text-blue-950/70 dark:text-blue-100/70 transition-colors duration-300">
        <svg class="w-4 h-4 flex-shrink-0" :class="isPopular ? 'text-orange-600 dark:text-orange-300' : 'text-blue-600 dark:text-blue-300'" fill="currentColor" viewBox="0 0 20 20">
          <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838l-3.14 1.346L10 11.25l6.606-2.83a1 1 0 000-1.84l-7-3zM3.31 9.397L5 10.12v4.102a8.969 8.969 0 00-1.05-.174 1 1 0 01-.89-.89 11.115 11.115 0 01.25-3.762zM9.3 16.573A9.026 9.026 0 007 14.935v-3.957l1.818.78a3 3 0 002.364 0l5.508-2.361a11.026 11.026 0 01.25 3.762 1 1 0 01-.89.89 8.968 8.968 0 00-5.35 2.524 1 1 0 01-1.4 0zM6 18a1 1 0 001-1v-2.065a8.935 8.935 0 00-2-.712V17a1 1 0 001 1z"/>
        </svg>
        <span>{{ deployments }}</span>
      </div>
      <div class="flex items-center gap-2 text-sm text-blue-950/70 dark:text-blue-100/70 transition-colors duration-300">
        <svg class="w-4 h-4 flex-shrink-0" :class="isPopular ? 'text-orange-600 dark:text-orange-300' : 'text-blue-600 dark:text-blue-300'" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"/>
        </svg>
        <span>{{ apiUsage }}</span>
      </div>
    </div>

    <!-- Feature List -->
    <ul class="space-y-3 mb-8 pt-5 border-t border-blue-950/[0.06] dark:border-white/[0.07]">
      <li
        v-for="(feature, index) in features"
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
      @click="$emit('subscribe')"
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
      <span v-else>Get Started</span>
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  name: string
  price: number
  features: string[]
  deployments: string
  apiUsage: string
  isPopular?: boolean
  loading?: boolean
}>()

defineEmits<{
  subscribe: []
}>()
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
