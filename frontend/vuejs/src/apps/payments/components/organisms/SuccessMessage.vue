<template>
  <div class="text-center py-8">
    <!-- Success Animation -->
    <div class="success-animation mb-6">
      <svg class="checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52">
        <circle class="checkmark-circle" cx="26" cy="26" r="25" fill="none"/>
        <path class="checkmark-check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
      </svg>
    </div>

    <h1 class="text-3xl font-bold text-white mb-4">{{ title }}</h1>
    <p class="text-gray-400 mb-8">{{ subtitle }}</p>

    <!-- Payment Details -->
    <div class="bg-dark-900 rounded-lg p-6 mb-8 max-w-md mx-auto">
      <div class="space-y-4">
        <div v-for="(detail, index) in details" :key="index" class="flex justify-between items-center">
          <span class="text-gray-400">{{ detail.label }}:</span>
          <span 
            class="text-xl font-semibold" 
            :class="detail.highlight ? 'text-primary-500' : 'text-white'"
          >
            {{ detail.value }}
          </span>
        </div>
        
        <div v-if="total" class="border-t border-dark-700 pt-4">
          <div class="flex justify-between items-center">
            <span class="text-gray-400">{{ totalLabel }}:</span>
            <span class="text-2xl font-bold text-white">{{ total }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-4">
      <slot name="actions">
        <PaymentButton @click="$emit('primary-action')">
          <i :class="['fas', primaryIcon, 'mr-2']"></i>
          {{ primaryText }}
        </PaymentButton>
        <PaymentButton variant="secondary" @click="$emit('secondary-action')">
          <i :class="['fas', secondaryIcon, 'mr-2']"></i>
          {{ secondaryText }}
        </PaymentButton>
      </slot>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import type { PropType } from 'vue'
import PaymentButton from '../atoms/Button.vue'

interface PaymentDetail {
  label: string;
  value: string;
  highlight?: boolean;
}

export default defineComponent({
  name: 'SuccessMessage',
  components: {
    PaymentButton
  },
  props: {
    title: {
      type: String,
      default: 'Payment Successful!'
    },
    subtitle: {
      type: String,
      default: 'Your payment has been processed and credits have been added to your account.'
    },
    details: {
      type: Array as PropType<PaymentDetail[]>,
      default: () => []
    },
    total: {
      type: String,
      default: ''
    },
    totalLabel: {
      type: String,
      default: 'New Balance'
    },
    primaryText: {
      type: String,
      default: 'Go to Builder'
    },
    primaryIcon: {
      type: String,
      default: 'fa-magic'
    },
    secondaryText: {
      type: String,
      default: 'Back to Dashboard'
    },
    secondaryIcon: {
      type: String,
      default: 'fa-home'
    }
  },
  emits: ['primary-action', 'secondary-action']
})
</script>

<style scoped>
.success-animation {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto;
}

.checkmark {
  width: 80px;
  height: 80px;
}

.checkmark-circle {
  stroke-dasharray: 166;
  stroke-dashoffset: 166;
  stroke-width: 2;
  stroke-miterlimit: 10;
  stroke: #00ffc6;
  fill: none;
  animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards;
}

.checkmark-check {
  transform-origin: 50% 50%;
  stroke-dasharray: 48;
  stroke-dashoffset: 48;
  stroke-width: 3;
  stroke: #00ffc6;
  animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards;
}

@keyframes stroke {
  100% {
    stroke-dashoffset: 0;
  }
}
</style> 