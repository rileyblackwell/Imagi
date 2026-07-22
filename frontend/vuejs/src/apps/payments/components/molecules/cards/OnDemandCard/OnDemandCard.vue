<template>
  <div class="ondemand-card rounded-2xl bg-white/85 dark:bg-white/[0.045] border border-orange-200/70 dark:border-orange-300/[0.14] backdrop-blur-sm p-8 transition-all duration-300">
    <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-8">
      <!-- Left: Description -->
      <div class="flex-1">
        <h3 class="text-xl font-semibold tracking-tight text-blue-950 dark:text-white mb-2 transition-colors duration-300">
          On-Demand Credits
        </h3>
        <p class="text-blue-950/65 dark:text-blue-100/65 text-sm leading-relaxed text-pretty transition-colors duration-300">
          Need extra API usage beyond your plan? Purchase additional credits anytime. Credits are added to your account instantly and never expire.
        </p>
      </div>

      <!-- Right: Purchase Controls -->
      <div class="flex-shrink-0 w-full md:w-auto md:min-w-[320px]">
        <!-- Preset Amounts -->
        <div class="grid grid-cols-4 gap-2 mb-4">
          <button
            v-for="preset in presets"
            :key="preset"
            @click="selectPreset(preset)"
            class="py-2.5 px-3 rounded-full text-sm font-medium transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
            :class="[
              selectedAmount === preset && !isCustom
                ? 'bg-blue-950 text-[#fdf9f2] dark:bg-[#f3ede2] dark:text-blue-950 shadow-[0_1px_2px_rgba(23,37,84,0.2),0_3px_8px_-2px_rgba(23,37,84,0.25)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.4),0_3px_8px_-2px_rgba(0,0,0,0.45)]'
                : 'border border-blue-950/[0.14] text-blue-950/80 hover:text-blue-950 hover:border-blue-950/30 hover:bg-blue-950/[0.03] dark:border-white/[0.16] dark:text-blue-100/80 dark:hover:text-white dark:hover:border-white/30 dark:hover:bg-white/[0.06]'
            ]"
          >
            ${{ preset }}
          </button>
        </div>

        <!-- Custom Amount Input -->
        <div class="relative mb-4">
          <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <span class="text-blue-950/60 dark:text-blue-100/55 text-sm font-medium">$</span>
          </div>
          <input
            v-model.number="customInput"
            type="number"
            min="5"
            max="1000"
            step="1"
            placeholder="Custom amount (5-1000)"
            @focus="isCustom = true"
            @input="handleCustomInput"
            class="w-full pl-8 pr-4 py-3 rounded-xl bg-white dark:bg-white/[0.05] border border-blue-950/[0.12] dark:border-white/[0.14] text-blue-950 dark:text-white placeholder-blue-950/40 dark:placeholder-blue-100/30 text-sm transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:border-blue-500/50 dark:focus-visible:border-blue-300/50"
          />
        </div>

        <!-- Buy Button -->
        <button
          @click="handlePurchase"
          :disabled="!isValidAmount || loading"
          class="w-full inline-flex items-center justify-center py-3 px-6 rounded-full bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white font-medium text-sm transition-colors duration-200 shadow-[0_1px_2px_rgba(23,37,84,0.2),0_3px_8px_-2px_rgba(23,37,84,0.25)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.4),0_3px_8px_-2px_rgba(0,0,0,0.45)] disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
        >
          <span v-if="loading" class="flex items-center justify-center gap-2">
            <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
            </svg>
            Processing...
          </span>
          <span v-else>
            Buy ${{ selectedAmount || 0 }} in Credits
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

defineProps<{
  loading?: boolean
}>()

const emit = defineEmits<{
  purchase: [amount: number]
}>()

const presets = [10, 25, 50, 100]
const selectedAmount = ref<number>(25)
const customInput = ref<number | null>(null)
const isCustom = ref(false)

const isValidAmount = computed(() => {
  return selectedAmount.value >= 5 && selectedAmount.value <= 1000
})

const selectPreset = (amount: number) => {
  selectedAmount.value = amount
  customInput.value = null
  isCustom.value = false
}

const handleCustomInput = () => {
  if (customInput.value && customInput.value >= 5) {
    selectedAmount.value = customInput.value
  }
}

const handlePurchase = () => {
  if (isValidAmount.value) {
    emit('purchase', selectedAmount.value)
  }
}
</script>

<style scoped>
/* Crisp, sharply-defined card: hairline edge + tight layered shadow */
.ondemand-card {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}

.dark .ondemand-card {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 12px 28px -10px rgba(0, 0, 0, 0.55);
}
</style>
