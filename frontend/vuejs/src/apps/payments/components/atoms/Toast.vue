<template>
  <div class="fixed top-4 right-4 z-50 flex flex-col space-y-2 max-w-md">
    <transition-group name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="[
          'toast-notification',
          `toast-${toast.type}`,
          'flex items-center p-4 rounded-lg shadow-lg border transform transition-all duration-300'
        ]"
      >
        <div class="flex-shrink-0 mr-3">
          <i :class="getIconClass(toast.type)"></i>
        </div>
        <div class="flex-grow">
          <p class="text-sm font-medium">{{ toast.message }}</p>
        </div>
        <button
          @click="hideToast(toast.id)"
          class="flex-shrink-0 ml-3 text-gray-400 hover:text-gray-500 focus:outline-none"
        >
          <i class="fas fa-times"></i>
        </button>
      </div>
    </transition-group>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useToast } from '../../composables/useToast'

export default defineComponent({
  name: 'PaymentToast',
  setup() {
    const { toasts, hideToast } = useToast()

    const getIconClass = (type: string) => {
      const icons = {
        success: 'fas fa-check-circle text-green-500',
        error: 'fas fa-exclamation-circle text-red-500',
        warning: 'fas fa-exclamation-triangle text-yellow-500',
        info: 'fas fa-info-circle text-blue-500'
      }
      return icons[type as keyof typeof icons] || icons.info
    }

    return {
      toasts,
      hideToast,
      getIconClass
    }
  }
})
</script>

<style scoped>
.toast-notification {
  max-width: 24rem;
  min-width: 16rem;
}

.toast-success {
  background-color: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.3);
  color: #ecfdf5;
}

.toast-error {
  background-color: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: #fef2f2;
}

.toast-warning {
  background-color: rgba(245, 158, 11, 0.1);
  border-color: rgba(245, 158, 11, 0.3);
  color: #fffbeb;
}

.toast-info {
  background-color: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.3);
  color: #eff6ff;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style> 