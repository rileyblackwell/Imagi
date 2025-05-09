<template>
  <div class="credit-balance-container" :class="{ 'inline': inline }">
    <div v-if="isLoading" class="flex items-center">
      <svg class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span>Loading...</span>
    </div>
    
    <div v-else-if="balance !== null" class="balance-display">
      <div class="flex items-center">
        <span v-if="size === 'large'" class="font-semibold mr-1">Available Balance:</span>
        <span 
          class="balance-value" 
          :class="{ 
            'text-sm': size === 'small',
            'text-base': size === 'medium',
            'text-lg': size === 'large',
            'font-semibold': size !== 'small'
          }"
        >
          ${{ balance.toLocaleString() }}
        </span>
        <button 
          v-if="showRefresh" 
          @click="refreshBalance" 
          class="refresh-btn ml-2 text-gray-400 hover:text-gray-600"
          :class="{ 'refresh-small': size === 'small' }"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
      
      <!-- "Add Credits" button removed as requested -->
    </div>
    
    <div v-else class="text-red-500 text-sm">
      <span>Failed to load balance</span>
      <button @click="refreshBalance" class="ml-2 text-indigo-600">Retry</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { usePaymentStore } from '@/apps/payments/stores'
import { useRouter } from 'vue-router'

const store = usePaymentStore()
const router = useRouter()

const props = withDefaults(defineProps<{
  size?: 'small' | 'medium' | 'large';
  showRefresh?: boolean;
  showAddCredits?: boolean;
  inline?: boolean;
}>(), {
  size: 'medium',
  showRefresh: false,
  showAddCredits: false,
  inline: false
})

const balance = computed(() => store.balance)
const isLoading = computed(() => store.isLoadingBalance)

// Load balance on mount
onMounted(() => {
  if (balance.value === null) {
    refreshBalance()
  }
})

// Function to refresh balance
const refreshBalance = async () => {
  try {
    await store.fetchBalance()
  } catch (err) {
    console.error('Error refreshing balance:', err)
  }
}

// Handle add credits event
const handleAddCredits = () => {
  router.push('/payments/checkout')
}

// Define emits
defineEmits<{
  (e: 'addCredits'): void
}>()
</script>

<style scoped>
.credit-balance-container {
  display: block;
}

.credit-balance-container.inline {
  display: inline-block;
}

.refresh-small {
  padding: 0;
}

.balance-value {
  color: #4f46e5; /* indigo-600 */
}
</style> 