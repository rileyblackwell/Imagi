import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useBalanceStore as useGlobalBalanceStore } from '@/shared/stores/balance'

/**
 * Builder module store for handling builder-specific balance concerns
 * This store delegates global balance state management to the root balance store
 * while providing builder-specific functionality
 */
export const useBalanceStore = defineStore('builder-balance', () => {
  // Local state for builder-specific functionality
  const loading = ref(false)
  const error = ref<string | null>(null)
  const isEstimating = ref(false)
  const lastEstimation = ref<{
    requestType: string;
    credits: number;
    timestamp: Date;
  } | null>(null)
  
  // Get global balance store
  const globalBalanceStore = useGlobalBalanceStore()
  
  // Computed properties
  const balance = computed(() => globalBalanceStore.balance)
  const lastUpdated = computed(() => globalBalanceStore.lastUpdated)
  const formattedBalance = computed(() => globalBalanceStore.formattedBalance)
  const isBalanceLoading = computed(() => globalBalanceStore.loading)
  
  // Computed to determine if user has enough credits
  const hasEnoughCredits = computed(() => {
    if (lastEstimation.value && lastEstimation.value.credits > 0) {
      return balance.value >= lastEstimation.value.credits
    }
    return true
  })
  
  /**
   * Fetch current balance
   */
  const fetchBalance = async (showLoading: boolean = true): Promise<void> => {
    if (showLoading) {
      loading.value = true
    }
    
    try {
      await globalBalanceStore.fetchBalance(false) // Don't show loading in global store
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch balance'
    } finally {
      if (showLoading) {
        loading.value = false
      }
    }
  }
  
  /**
   * Estimate credits for a specific builder operation
   * @param requestType Type of request (e.g., 'generate-app', 'add-feature')
   * @param parameters Parameters that might affect cost estimation
   */
  const estimateCredits = async (
    requestType: string,
    parameters: Record<string, any> = {}
  ): Promise<number> => {
    isEstimating.value = true
    error.value = null
    
    try {
      // Default credit costs based on request type
      // In real implementation, this would call an API endpoint
      let credits = 0
      
      switch (requestType) {
        case 'generate-app':
          credits = 100 // Basic app generation
          if (parameters.complexity === 'high') credits = 200
          break
        case 'add-feature':
          credits = 50 // Basic feature addition
          if (parameters.size === 'large') credits = 100
          break
        case 'debug':
          credits = 25 // Basic debugging
          break
        default:
          credits = 10 // Default cost
      }
      
      // Store last estimation
      lastEstimation.value = {
        requestType,
        credits,
        timestamp: new Date()
      }
      
      return credits
    } catch (err: any) {
      error.value = err.message || 'Failed to estimate credits'
      return 0
    } finally {
      isEstimating.value = false
    }
  }
  
  /**
   * Check if user has enough credits for a specific operation
   * @param credits Number of credits needed
   */
  const checkCredits = (credits: number): boolean => {
    return balance.value >= credits
  }
  
  /**
   * Clear any errors
   */
  const clearError = (): void => {
    error.value = null
  }
  
  return {
    // State
    loading,
    error,
    isEstimating,
    lastEstimation,
    
    // Computed from global store
    balance,
    lastUpdated,
    formattedBalance,
    isBalanceLoading,
    hasEnoughCredits,
    
    // Actions
    fetchBalance,
    estimateCredits,
    checkCredits,
    clearError
  }
}) 