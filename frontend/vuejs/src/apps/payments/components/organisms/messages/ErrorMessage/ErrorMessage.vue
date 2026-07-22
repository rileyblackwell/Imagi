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
          class="stroke-red-500 dark:stroke-red-400"
        />
      </svg>
    </div>

    <h1 class="font-display text-3xl font-semibold tracking-[-0.02em] text-blue-950 dark:text-white mb-4 transition-colors duration-300">{{ title }}</h1>
    <p class="text-blue-950/65 dark:text-blue-100/65 mb-8 transition-colors duration-300">{{ subtitle }}</p>

    <div v-if="message" class="bg-red-50/80 dark:bg-red-500/10 border border-red-200/70 dark:border-red-400/25 rounded-xl p-4 mb-8 max-w-md mx-auto transition-colors duration-300">
      <p class="text-red-700 dark:text-red-300">{{ message }}</p>
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
    <p v-if="helpText" class="mt-8 text-sm text-blue-950/60 dark:text-blue-100/55 transition-colors duration-300">
      {{ helpText }}
      <a
        v-if="contactLink"
        :href="contactLink"
        class="text-blue-700 hover:text-blue-800 dark:text-blue-300 dark:hover:text-blue-200 underline decoration-blue-700/30 dark:decoration-blue-300/30 underline-offset-2 rounded transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
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

@media (prefers-reduced-motion: reduce) {
  .error-icon {
    animation: none;
  }
}
</style> 