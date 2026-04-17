<template>
  <div class="rounded-2xl bg-white/50 dark:bg-white/[0.03] border border-gray-200 dark:border-white/[0.08] backdrop-blur-sm p-8 transition-all duration-300 hover:border-gray-300 dark:hover:border-white/[0.12] hover:shadow-lg hover:shadow-gray-200/30 dark:hover:shadow-none">
    <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-8">
      <!-- Left: Description -->
      <div class="flex-1">
        <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2 transition-colors duration-300">
          On-Demand Credits
        </h3>
        <p class="text-gray-500 dark:text-white/60 text-sm leading-relaxed transition-colors duration-300">
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
            class="py-2.5 px-3 rounded-xl text-sm font-medium transition-all duration-200 active:scale-[0.97]"
            :class="[
              selectedAmount === preset && !isCustom
                ? 'bg-gray-900 dark:bg-white text-white dark:text-gray-900'
                : 'bg-gray-100 dark:bg-white/[0.06] text-gray-700 dark:text-white/70 hover:bg-gray-200 dark:hover:bg-white/[0.1] border border-gray-200 dark:border-white/[0.08]'
            ]"
          >
            ${{ preset }}
          </button>
        </div>

        <!-- Custom Amount Input -->
        <div class="relative mb-4">
          <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <span class="text-gray-500 dark:text-white/50 text-sm font-medium">$</span>
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
            class="w-full pl-8 pr-4 py-3 rounded-xl bg-gray-50 dark:bg-white/[0.04] border border-gray-200 dark:border-white/[0.08] text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-white/30 text-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 dark:focus:border-blue-400"
          />
        </div>

        <!-- Buy Button -->
        <button
          @click="handlePurchase"
          :disabled="!isValidAmount || loading"
          class="w-full py-3 px-6 rounded-xl bg-gray-900 dark:bg-white text-white dark:text-gray-900 font-medium text-sm transition-all duration-200 active:scale-[0.98] hover:bg-gray-800 dark:hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
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
