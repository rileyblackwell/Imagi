"""
Payments app prebuilt template.
Generates frontend (Vue) and backend (Django) files for the payments/checkout app.
Self-contained checkout page mirroring the Imagi design with Stripe integration.
"""
from __future__ import annotations

from typing import Dict, List

from .shared import _frontend_scaffold, _backend_scaffold


def payments_app_files() -> List[Dict[str, str]]:
    """
    Generate comprehensive payments app files with full Checkout functionality.
    Self-contained payments app mirroring the Imagi design with Stripe integration.
    """
    app_name = 'payments'
    cap = 'Payments'
    welcome = 'Manage subscriptions and transactions.'
    files: List[Dict[str, str]] = []
    files += _frontend_scaffold(app_name, cap, welcome)
    files += _backend_scaffold(app_name, cap)

    # Override the basic views with payment-specific endpoints
    files.append({
        'name': f'backend/django/apps/{app_name}/views.py',
        'type': 'python',
        'content': (
            "from rest_framework.decorators import api_view\n"
            "from rest_framework.response import Response\n"
            "from rest_framework import status\n\n"
            "@api_view(['GET'])\n"
            "def plans(_request):\n"
            "    return Response({'plans': []}, status=status.HTTP_200_OK)\n\n"
            "@api_view(['POST'])\n"
            "def checkout(_request):\n"
            "    return Response({'status': 'not implemented'}, status=status.HTTP_200_OK)\n"
        ),
    })
    files.append({
        'name': f'backend/django/apps/{app_name}/urls.py',
        'type': 'python',
        'content': (
            "from django.urls import path\n"
            "from . import views\n\n"
            "urlpatterns = [\n"
            "    path('plans/', views.plans, name='plans'),\n"
            "    path('checkout/', views.checkout, name='checkout'),\n"
            "]\n"
        ),
    })
    
    # ========== Enhanced Frontend Files ==========
    
    # Main index.ts - override default
    files.append({
        'name': 'frontend/vuejs/src/apps/payments/index.ts',
        'type': 'typescript',
        'content': '''export { usePaymentStore } from './stores/payments'
export type { PaymentState, Transaction } from './types/payments'
'''
    })
    
    # ===== Types =====
    files.append({
        'name': 'frontend/vuejs/src/apps/payments/types/payments.ts',
        'type': 'typescript',
        'content': '''export interface PaymentState {
  balance: number | null;
  isLoading: boolean;
  error: string | null;
  processingPayment: boolean;
}

export interface Transaction {
  id: string;
  amount: number;
  description: string;
  created_at: string;
  status: 'completed' | 'pending' | 'failed';
}

export interface PaymentData {
  amount: number;
  paymentMethodId: string;
}

export interface PaymentResponse {
  success: boolean;
  newBalance?: number;
  error?: string;
}
'''
    })
    
    # ===== Self-contained Payment API Service =====
    files.append({
        'name': 'frontend/vuejs/src/apps/payments/services/api.ts',
        'type': 'typescript',
        'content': '''import axios from 'axios'
import type { PaymentData, PaymentResponse } from '../types/payments'

// Create self-contained axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  return config
})

const API_PATH = '/v1/payments'

export const PaymentAPI = {
  async getBalance(): Promise<{ balance: number }> {
    const response = await api.get(`${API_PATH}/balance/`)
    return response.data
  },

  async processPayment(data: PaymentData): Promise<PaymentResponse> {
    const response = await api.post(`${API_PATH}/process/`, data)
    return response.data
  },

  async getTransactions(): Promise<{ transactions: any[] }> {
    const response = await api.get(`${API_PATH}/transactions/`)
    return response.data
  },

  async healthCheck(): Promise<{ status: string }> {
    const response = await api.get(`${API_PATH}/health/`)
    return response.data
  }
}
'''
    })
    
    # ===== Self-contained Payment Store =====
    files.append({
        'name': 'frontend/vuejs/src/apps/payments/stores/payments.ts',
        'type': 'typescript',
        'content': '''import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { PaymentAPI } from '../services/api'
import type { PaymentData, Transaction } from '../types/payments'

export const usePaymentStore = defineStore('payments', () => {
  const balance = ref<number | null>(null)
  const isLoading = ref(false)
  const isLoadingBalance = ref(false)
  const error = ref<string | null>(null)
  const processingPayment = ref(false)
  const transactions = ref<Transaction[]>([])

  const fetchBalance = async () => {
    isLoadingBalance.value = true
    error.value = null
    try {
      const response = await PaymentAPI.getBalance()
      balance.value = response.balance
      return response.balance
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch balance'
      return null
    } finally {
      isLoadingBalance.value = false
    }
  }

  const processPayment = async (paymentData: PaymentData) => {
    processingPayment.value = true
    error.value = null
    try {
      const result = await PaymentAPI.processPayment(paymentData)
      if (result.success && result.newBalance !== undefined) {
        balance.value = result.newBalance
      }
      return result
    } catch (err: any) {
      error.value = err.message || 'Payment failed'
      throw err
    } finally {
      processingPayment.value = false
    }
  }

  const initializePayments = async () => {
    isLoading.value = true
    try {
      await fetchBalance()
      return true
    } catch (err) {
      return false
    } finally {
      isLoading.value = false
    }
  }

  const fetchUserCredits = async () => {
    return await fetchBalance()
  }

  return {
    balance,
    isLoading,
    isLoadingBalance,
    error,
    processingPayment,
    transactions,
    fetchBalance,
    processPayment,
    initializePayments,
    fetchUserCredits
  }
})
'''
    })
    
    files.append({
        'name': 'frontend/vuejs/src/apps/payments/stores/index.ts',
        'type': 'typescript',
        'content': '''export { usePaymentStore } from './payments'
'''
    })
    
    # ===== Router =====
    files.append({
        'name': 'frontend/vuejs/src/apps/payments/router/index.ts',
        'type': 'typescript',
        'content': '''import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/payments',
    children: [
      {
        path: 'checkout',
        name: 'checkout',
        component: () => import('../views/CheckoutView.vue'),
        meta: {
          requiresAuth: true,
          title: 'Checkout'
        }
      }
    ]
  }
]

export { routes }
export default routes
'''
    })
    
    # ===== Checkout View - matching Imagi design =====
    files.append({
        'name': 'frontend/vuejs/src/apps/payments/views/CheckoutView.vue',
        'type': 'vue',
        'content': '''<template>
  <div class="checkout-view min-h-screen bg-white dark:bg-[#0a0a0a] relative overflow-hidden transition-colors duration-500">
    <!-- Minimal background with subtle texture -->
    <div class="fixed inset-0 pointer-events-none -z-10">
      <div class="absolute inset-0 bg-gradient-to-b from-gray-50/50 via-white to-white dark:from-[#0a0a0a] dark:via-[#0a0a0a] dark:to-[#0a0a0a] transition-colors duration-500"></div>
      <div class="absolute inset-0 opacity-[0.015] dark:opacity-[0.02]" 
           style="background-image: linear-gradient(rgba(128,128,128,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(128,128,128,0.1) 1px, transparent 1px); background-size: 64px 64px;"></div>
    </div>

    <!-- Content Container -->
    <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16">
      <!-- Clean Header Section -->
      <div class="mb-16 text-center">
        <h1 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight leading-[1.1] transition-colors duration-300">
          Purchase Credits
        </h1>
        <p class="text-xl sm:text-2xl text-gray-500 dark:text-white/60 max-w-3xl mx-auto transition-colors duration-300">
          Add credits to your account to use AI models and build your applications.
        </p>
      </div>
      
      <!-- Single unified checkout container -->
      <div class="max-w-2xl mx-auto">
        <!-- Status Messages -->
        <div v-if="success" class="animate-fade-in-up mb-6">
          <div class="rounded-2xl bg-emerald-50 dark:bg-emerald-900/10 border border-emerald-200 dark:border-emerald-800/30 p-6 transition-colors duration-300">
            <div class="flex items-start gap-4">
              <div class="w-10 h-10 rounded-full bg-emerald-100 dark:bg-emerald-900/20 flex items-center justify-center flex-shrink-0">
                <i class="fas fa-check text-emerald-600 dark:text-emerald-400"></i>
              </div>
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-emerald-900 dark:text-emerald-100 mb-2">Payment Successful!</h3>
                <p class="text-emerald-700 dark:text-emerald-300/80">Your payment has been processed and credits have been added to your account.</p>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="paymentError" class="animate-fade-in-up mb-6">
          <div class="rounded-2xl bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800/30 p-6 transition-colors duration-300">
            <div class="flex items-start gap-4">
              <div class="w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/20 flex items-center justify-center flex-shrink-0">
                <i class="fas fa-exclamation-triangle text-red-600 dark:text-red-400"></i>
              </div>
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-red-900 dark:text-red-100 mb-2">Payment Error</h3>
                <p class="text-red-700 dark:text-red-300/80">{{ paymentError }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Unified checkout card -->
        <div class="animate-fade-in-up animation-delay-300">
          <div class="rounded-2xl bg-white/50 dark:bg-white/[0.03] border border-gray-200 dark:border-white/[0.08] backdrop-blur-sm transition-all duration-300 hover:border-gray-300 dark:hover:border-white/[0.12] hover:shadow-lg overflow-hidden">
            <!-- Current Balance Section -->
            <div class="p-8 border-b border-gray-200 dark:border-white/[0.08] text-center">
              <div class="mb-2">
                <span class="text-sm font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide">Current Balance</span>
              </div>
              <div class="flex items-baseline gap-2 justify-center">
                <div v-if="store.isLoadingBalance" class="animate-pulse">
                  <div class="h-9 w-20 bg-gray-200 dark:bg-white/10 rounded-lg"></div>
                </div>
                <div v-else class="text-3xl sm:text-4xl font-semibold text-gray-900 dark:text-white">
                  ${{ (store.balance ?? 0).toLocaleString() }}
                </div>
                <div class="text-sm text-gray-500 dark:text-gray-400">USD</div>
              </div>
            </div>

            <!-- Payment Details Section -->
            <div class="p-8">
              <PaymentForm
                :is-loading="processingPayment"
                :button-text="`Pay $${formattedAmount}`"
                @submit="processPayment"
                @update:amount="updateAmount"
                @payment-error="handlePaymentError"
              />
            </div>
          </div>
        </div>

        <!-- Secure Payment Badge -->
        <div class="animate-fade-in-up animation-delay-600 mt-6">
          <div class="flex items-center justify-center gap-3 py-3 px-6 bg-white/50 dark:bg-white/[0.03] backdrop-blur-sm rounded-full border border-gray-200/50 dark:border-white/[0.06] w-fit mx-auto transition-colors duration-300">
            <div class="w-8 h-8 rounded-full bg-gray-100 dark:bg-white/[0.05] flex items-center justify-center">
              <i class="fas fa-lock text-gray-600 dark:text-gray-400"></i>
            </div>
            <span class="text-gray-600 dark:text-gray-400 text-sm">All payments are secure and encrypted</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { usePaymentStore } from '../stores/payments'
import PaymentForm from '../components/organisms/forms/PaymentForm.vue'

const store = usePaymentStore()

// State
const success = ref(false)
const customAmount = ref<number>(5)
const paymentError = ref('')
const processingPayment = ref(false)

// Initialize
onMounted(async () => {
  try {
    await store.initializePayments()
  } catch (error) {
    console.error('Failed to initialize checkout view:', error)
  }
})

// Computed
const formattedAmount = computed(() => {
  return customAmount.value ? customAmount.value.toFixed(2) : '0.00'
})

// Methods
const updateAmount = (amount: string | number) => {
  customAmount.value = typeof amount === 'string' ? parseFloat(amount) : amount
}

const handlePaymentError = (errorMessage: string) => {
  paymentError.value = errorMessage
}

const processPayment = async (paymentData: any) => {
  if (!customAmount.value || customAmount.value < 5) return

  try {
    paymentError.value = ''
    processingPayment.value = true
    
    await store.processPayment({
      amount: paymentData.amount,
      paymentMethodId: paymentData.paymentMethodId
    })
    
    success.value = true
    await store.fetchBalance()
    
    setTimeout(() => {
      success.value = false
    }, 5000)
  } catch (err: any) {
    paymentError.value = err.response?.data?.error || err.message || 'Payment processing failed'
  } finally {
    processingPayment.value = false
  }
}
</script>

<style scoped>
.animation-delay-300 { animation-delay: 300ms; }
.animation-delay-600 { animation-delay: 600ms; }

@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in-up {
  animation: fade-in-up 0.6s ease-out forwards;
}
</style>
'''
    })
    
    files.append({
        'name': 'frontend/vuejs/src/apps/payments/views/index.ts',
        'type': 'typescript',
        'content': '''export { default as CheckoutView } from './CheckoutView.vue'
'''
    })
    
    # ===== Components =====
    files.append({
        'name': 'frontend/vuejs/src/apps/payments/components/index.ts',
        'type': 'typescript',
        'content': '''export * from './atoms'
export * from './molecules'
export * from './organisms'
'''
    })
    
    files.append({
        'name': 'frontend/vuejs/src/apps/payments/components/atoms/index.ts',
        'type': 'typescript',
        'content': '''// atoms
'''
    })
    
    files.append({
        'name': 'frontend/vuejs/src/apps/payments/components/molecules/index.ts',
        'type': 'typescript',
        'content': '''// molecules
'''
    })
    
    files.append({
        'name': 'frontend/vuejs/src/apps/payments/components/organisms/index.ts',
        'type': 'typescript',
        'content': '''export { default as PaymentForm } from './forms/PaymentForm.vue'
'''
    })
    
    # Payment Form Component
    files.append({
        'name': 'frontend/vuejs/src/apps/payments/components/organisms/forms/PaymentForm.vue',
        'type': 'vue',
        'content': '''<template>
  <div>
    <!-- Two-column layout -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
      <!-- Credit Amount Section -->
      <div>
        <div class="mb-6 text-center md:text-left">
          <span class="text-sm font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide">Credit Amount</span>
        </div>
        
        <div>
          <div class="mb-4">
            <div class="relative mt-1 rounded-xl shadow-sm">
              <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                <span class="text-gray-500 dark:text-gray-400 sm:text-sm">$</span>
              </div>
              <input
                v-model.number="amount"
                type="number"
                :min="minAmount"
                :max="maxAmount"
                class="no-focus-effect block w-full rounded-xl border-gray-300 dark:border-white/20 bg-white dark:bg-white/5 py-3 pl-8 pr-28 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-white/40"
              />
              <div class="absolute inset-y-0 right-12 flex flex-col justify-center py-1 gap-0.5">
                <button type="button" @click="incrementAmount" class="flex items-center justify-center px-1 text-gray-500 dark:text-gray-400" tabindex="-1">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
                    <path fill-rule="evenodd" d="M10 17a.75.75 0 01-.75-.75V5.612L5.29 9.77a.75.75 0 01-1.08-1.04l5.25-5.5a.75.75 0 011.08 0l5.25 5.5a.75.75 0 11-1.08 1.04l-3.96-4.158V16.25A.75.75 0 0110 17z" clip-rule="evenodd" />
                  </svg>
                </button>
                <button type="button" @click="decrementAmount" class="flex items-center justify-center px-1 text-gray-500 dark:text-gray-400" tabindex="-1">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
                    <path fill-rule="evenodd" d="M10 3a.75.75 0 01.75.75v10.638l3.96-4.158a.75.75 0 111.08 1.04l-5.25 5.5a.75.75 0 01-1.08 0l-5.25-5.5a.75.75 0 111.08-1.04l3.96 4.158V3.75A.75.75 0 0110 3z" clip-rule="evenodd" />
                  </svg>
                </button>
              </div>
              <div class="absolute inset-y-0 right-0 flex items-center pr-3">
                <span class="text-gray-500 dark:text-gray-400 sm:text-sm">USD</span>
              </div>
            </div>
            <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">Amount range: $5 - $100</p>
          </div>
        </div>
      </div>
      
      <!-- Payment Method Section -->
      <div class="md:col-span-2">
        <div class="mb-6 text-center md:text-left">
          <span class="text-sm font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide">Payment Method</span>
        </div>
        
        <form @submit.prevent="submitPayment">
          <!-- Stripe Elements -->
          <div class="mb-8">
            <div class="mb-4">
              <div 
                id="card-element" 
                ref="cardElement"
                class="block w-full rounded-xl border border-gray-300 dark:border-white/20 bg-white dark:bg-white/5 py-3 px-4 text-gray-900 dark:text-white transition-all duration-300 focus-within:border-gray-900 dark:focus-within:border-white/40 focus-within:ring-1 focus-within:ring-gray-900 dark:focus-within:ring-white/40 min-h-[45px]"
              ></div>
              <div id="card-errors" class="mt-2 text-sm text-red-600 dark:text-red-400"></div>
            </div>
          </div>
          
          <!-- Order Summary -->
          <div class="mb-8 rounded-xl border border-gray-200 dark:border-white/10 bg-gray-50 dark:bg-white/5 overflow-hidden">
            <div class="p-4 border-b border-gray-200 dark:border-white/10 bg-white dark:bg-white/5">
              <h4 class="font-semibold text-gray-900 dark:text-white">Order Summary</h4>
              <p class="text-sm text-gray-500 dark:text-gray-400">Review your order details</p>
            </div>
            <div class="p-4">
              <div class="flex justify-between py-2 border-b border-gray-200 dark:border-white/10">
                <span class="text-gray-600 dark:text-gray-400">Credits</span>
                <span class="font-medium text-gray-900 dark:text-white">${{ formattedAmount }}</span>
              </div>
              <div class="flex justify-between py-2">
                <span class="text-gray-600 dark:text-gray-400">Total</span>
                <span class="font-semibold text-gray-900 dark:text-white">${{ formattedAmount }}</span>
              </div>
            </div>
          </div>
          
          <!-- Submit Button -->
          <button 
            type="submit"
            :disabled="!isValidAmount || isLoading || !cardComplete"
            class="group relative w-full inline-flex items-center justify-center gap-3 px-8 py-4 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-full font-medium text-lg transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:hover:shadow-none overflow-hidden"
          >
            <span class="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-700 ease-out"></span>
            
            <span v-if="isLoading" class="relative flex items-center justify-center gap-2">
              <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Processing payment...</span>
            </span>
            <span v-else class="relative flex items-center gap-2">
              {{ buttonText }}
              <svg class="w-5 h-5 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'

const props = defineProps({
  minAmount: { type: Number, default: 5 },
  maxAmount: { type: Number, default: 100 },
  isLoading: { type: Boolean, default: false },
  buttonText: { type: String, default: 'Complete Payment' }
})

const emit = defineEmits(['submit', 'update:amount', 'payment-error'])

// State
const cardElement = ref<HTMLElement | null>(null)
const stripeElements = ref<any>(null)
const stripeInstance = ref<any>(null)
const cardComplete = ref(false)
const amount = ref<number>(props.minAmount)

// Computed
const isValidAmount = computed(() => {
  return amount.value && amount.value >= props.minAmount && amount.value <= props.maxAmount
})

const formattedAmount = computed(() => {
  const numAmount = typeof amount.value === 'string' ? parseFloat(amount.value) : amount.value
  return numAmount ? numAmount.toFixed(2) : '0.00'
})

// Initialize Stripe
onMounted(async () => {
  setTimeout(async () => {
    if (!window.Stripe) {
      // Load Stripe.js if not available
      const script = document.createElement('script')
      script.src = 'https://js.stripe.com/v3/'
      script.async = true
      script.onload = () => initializeStripe()
      document.head.appendChild(script)
      return
    }
    initializeStripe()
  }, 500)
})

const initializeStripe = () => {
  try {
    const cardElementDiv = document.getElementById('card-element')
    if (!cardElementDiv) {
      setTimeout(() => initializeStripe(), 500)
      return
    }
    
    const stripePublishableKey = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY
    if (!stripePublishableKey) {
      emit('payment-error', 'Stripe key not configured')
      return
    }
    
    const stripe = window.Stripe(stripePublishableKey)
    stripeInstance.value = stripe
    
    const elements = stripe.elements()
    stripeElements.value = elements
    
    const isDarkMode = document.documentElement.classList.contains('dark')
    
    const card = elements.create('card', {
      style: {
        base: {
          color: isDarkMode ? '#FFFFFF' : '#111827',
          fontFamily: 'ui-sans-serif, system-ui, sans-serif',
          fontSize: '16px',
          '::placeholder': {
            color: isDarkMode ? 'rgba(255, 255, 255, 0.4)' : 'rgba(107, 114, 128, 0.8)'
          }
        },
        invalid: { color: '#EF4444' }
      }
    })
    
    card.mount('#card-element')
    
    card.on('change', (event: any) => {
      const displayError = document.getElementById('card-errors')
      if (displayError) {
        displayError.textContent = event.error ? event.error.message : ''
      }
      cardComplete.value = event.complete
    })
  } catch (err: any) {
    emit('payment-error', err.message || 'Failed to initialize payment form')
  }
}

// Watch amount changes
watch(amount, (newValue) => {
  emit('update:amount', newValue)
})

// Submit payment
const submitPayment = async () => {
  if (!isValidAmount.value || props.isLoading || !cardComplete.value) return
  
  try {
    if (!stripeInstance.value) {
      throw new Error('Stripe has not been initialized')
    }
    
    const result = await stripeInstance.value.createPaymentMethod({
      type: 'card',
      card: stripeElements.value.getElement('card'),
    })
    
    if (result.error) {
      const errorElement = document.getElementById('card-errors')
      if (errorElement) {
        errorElement.textContent = result.error.message || 'An error occurred'
      }
      emit('payment-error', result.error.message || 'Payment failed')
      return
    }
    
    emit('submit', {
      amount: amount.value,
      paymentMethodId: result.paymentMethod.id
    })
  } catch (err: any) {
    emit('payment-error', err.message || 'Payment submission failed')
  }
}

// Amount controls
const incrementAmount = () => {
  if (amount.value < props.maxAmount) amount.value += 1
}

const decrementAmount = () => {
  if (amount.value > props.minAmount) amount.value -= 1
}

// Clear form
const clearForm = () => {
  amount.value = props.minAmount
  if (stripeElements.value) {
    const cardEl = stripeElements.value.getElement('card')
    if (cardEl) {
      cardEl.clear()
      cardComplete.value = false
    }
  }
  const errorElement = document.getElementById('card-errors')
  if (errorElement) errorElement.textContent = ''
}

defineExpose({ clearForm })
</script>

<style scoped>
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] { -moz-appearance: textfield; }

.no-focus-effect { outline: none !important; box-shadow: none !important; border-color: inherit !important; }
.no-focus-effect:focus { outline: none !important; box-shadow: none !important; border-color: rgb(209 213 219) !important; }

:root.dark .no-focus-effect:focus { border-color: rgba(255, 255, 255, 0.2) !important; }

#card-element { display: block; width: 100%; }
#card-element iframe { display: block; width: 100%; }
</style>
'''
    })
    
    return files
