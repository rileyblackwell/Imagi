<template>
  <div
    class="relative rounded-2xl p-8 transition-all duration-300 hover:shadow-xl"
    :class="[
      isPopular
        ? 'bg-white dark:bg-white/[0.05] border-2 border-blue-500 dark:border-blue-400 hover:shadow-blue-100/50 dark:hover:shadow-none'
        : 'bg-white/50 dark:bg-white/[0.03] border border-gray-200 dark:border-white/[0.08] hover:shadow-gray-200/30 dark:hover:shadow-none hover:border-gray-300 dark:hover:border-white/[0.12]'
    ]"
  >
    <!-- Popular Badge -->
    <div v-if="isPopular" class="absolute -top-3.5 left-1/2 -translate-x-1/2">
      <span class="inline-flex items-center px-4 py-1 rounded-full text-xs font-semibold bg-blue-500 text-white tracking-wide uppercase">
        Most Popular
      </span>
    </div>

    <!-- Tier Name -->
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2 transition-colors duration-300">
      {{ name }}
    </h3>

    <!-- Price -->
    <div class="flex items-baseline gap-1 mb-6">
      <span class="text-4xl font-semibold text-gray-900 dark:text-white tracking-tight transition-colors duration-300">
        ${{ price }}
      </span>
      <span class="text-gray-500 dark:text-white/50 text-sm transition-colors duration-300">/month</span>
    </div>

    <!-- Key Highlights -->
    <div class="mb-6 space-y-2">
      <div class="flex items-center gap-2 text-sm text-gray-700 dark:text-white/70 transition-colors duration-300">
        <svg class="w-4 h-4 text-blue-500 dark:text-blue-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838l-3.14 1.346L10 11.25l6.606-2.83a1 1 0 000-1.84l-7-3zM3.31 9.397L5 10.12v4.102a8.969 8.969 0 00-1.05-.174 1 1 0 01-.89-.89 11.115 11.115 0 01.25-3.762zM9.3 16.573A9.026 9.026 0 007 14.935v-3.957l1.818.78a3 3 0 002.364 0l5.508-2.361a11.026 11.026 0 01.25 3.762 1 1 0 01-.89.89 8.968 8.968 0 00-5.35 2.524 1 1 0 01-1.4 0zM6 18a1 1 0 001-1v-2.065a8.935 8.935 0 00-2-.712V17a1 1 0 001 1z"/>
        </svg>
        <span>{{ deployments }}</span>
      </div>
      <div class="flex items-center gap-2 text-sm text-gray-700 dark:text-white/70 transition-colors duration-300">
        <svg class="w-4 h-4 text-blue-500 dark:text-blue-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"/>
        </svg>
        <span>{{ apiUsage }}</span>
      </div>
    </div>

    <!-- Feature List -->
    <ul class="space-y-3 mb-8">
      <li
        v-for="(feature, index) in features"
        :key="index"
        class="flex items-start gap-3 text-sm text-gray-600 dark:text-white/60 transition-colors duration-300"
      >
        <svg class="w-4 h-4 text-emerald-500 dark:text-emerald-400 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
        </svg>
        <span>{{ feature }}</span>
      </li>
    </ul>

    <!-- CTA Button -->
    <button
      @click="$emit('subscribe')"
      :disabled="loading"
      class="w-full py-3 px-6 rounded-xl font-medium text-sm transition-all duration-200 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
      :class="[
        isPopular
          ? 'bg-blue-500 hover:bg-blue-600 text-white'
          : 'bg-gray-900 dark:bg-white text-white dark:text-gray-900 hover:bg-gray-800 dark:hover:bg-gray-100'
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
