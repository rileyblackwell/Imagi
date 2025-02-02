<template>
  <div class="fixed bottom-4 right-4 z-50 space-y-2">
    <TransitionGroup name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="[
          'px-4 py-3 rounded-lg shadow-lg transform transition-all duration-300',
          {
            'bg-red-900 text-white': toast.type === 'error',
            'bg-green-900 text-white': toast.type === 'success',
            'bg-dark-800 text-white': toast.type === 'info'
          }
        ]"
        v-show="toast.show"
      >
        <div class="flex items-center space-x-2">
          <!-- Icons -->
          <span v-if="toast.type === 'error'" class="text-red-400">
            <i class="fas fa-exclamation-circle"></i>
          </span>
          <span v-else-if="toast.type === 'success'" class="text-green-400">
            <i class="fas fa-check-circle"></i>
          </span>
          <span v-else class="text-primary-400">
            <i class="fas fa-info-circle"></i>
          </span>

          <!-- Message -->
          <p>{{ toast.message }}</p>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<script>
import { useToast } from '../../composables/useToast'

export default {
  name: 'PaymentToast',
  setup() {
    const { toasts } = useToast()
    return { toasts }
  }
}
</script>

<style scoped>
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