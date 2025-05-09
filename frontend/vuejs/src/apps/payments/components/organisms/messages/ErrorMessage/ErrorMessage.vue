<template>
  <div class="text-center py-8">
    <!-- Error Icon -->
    <div class="error-icon mb-6">
      <svg class="w-20 h-20 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path 
          stroke-linecap="round" 
          stroke-linejoin="round" 
          stroke-width="1.5" 
          d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" 
          class="stroke-red-500" 
        />
      </svg>
    </div>

    <h1 class="text-3xl font-bold text-white mb-4">{{ title }}</h1>
    <p class="text-gray-400 mb-8">{{ subtitle }}</p>

    <div v-if="message" class="bg-red-900/20 border border-red-900/30 rounded-lg p-4 mb-8 max-w-md mx-auto">
      <p class="text-red-400">{{ message }}</p>
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

    <!-- Help Text -->
    <p v-if="helpText" class="mt-8 text-sm text-gray-400">
      {{ helpText }}
      <a 
        v-if="contactLink" 
        :href="contactLink" 
        class="text-primary-400 hover:text-primary-300"
      >
        {{ contactText }}
      </a>
    </p>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import PaymentButton from '../atoms/Button.vue'

export default defineComponent({
  name: 'ErrorMessage',
  components: {
    PaymentButton
  },
  props: {
    title: {
      type: String,
      default: 'Payment Failed'
    },
    subtitle: {
      type: String,
      default: 'There was an issue processing your payment.'
    },
    message: {
      type: String,
      default: ''
    },
    helpText: {
      type: String,
      default: 'If you continue to experience issues, please'
    },
    contactText: {
      type: String,
      default: 'contact our support team.'
    },
    contactLink: {
      type: String,
      default: 'mailto:support@imagi.ai'
    },
    primaryText: {
      type: String,
      default: 'Try Again'
    },
    primaryIcon: {
      type: String,
      default: 'fa-redo'
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
.error-icon {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(0.95);
    opacity: 0.8;
  }
  70% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(0.95);
    opacity: 0.8;
  }
}
</style> 