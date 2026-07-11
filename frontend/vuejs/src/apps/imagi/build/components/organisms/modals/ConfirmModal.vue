<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <!-- Backdrop -->
        <div 
          class="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
          @click="handleCancel"
        />

        <!-- Modal Panel -->
        <div 
          class="relative w-full max-w-md rounded-2xl border shadow-2xl overflow-hidden transform transition-all"
          :class="modalClasses"
        >
          <!-- Header -->
          <div class="px-6 py-5 border-b" :class="headerClasses">
            <div class="flex items-start gap-4">
              <!-- Icon -->
              <div 
                class="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
                :class="iconContainerClasses"
              >
                <i :class="iconClasses" class="text-xl"></i>
              </div>
              
              <!-- Title and Message -->
              <div class="flex-1 min-w-0 pt-1">
                <h3 class="text-lg font-semibold mb-1" :class="titleClasses">
                  {{ options.title || defaultTitle }}
                </h3>
                <p class="text-sm leading-relaxed" :class="messageClasses">
                  {{ options.message }}
                </p>
              </div>

              <!-- Close button -->
              <button
                type="button"
                class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800/50 transition-all flex-shrink-0"
                @click="handleCancel"
                aria-label="Close"
              >
                <i class="fas fa-times text-sm"></i>
              </button>
            </div>
          </div>

          <!-- Footer / Actions -->
          <div class="px-6 py-4 bg-gray-50 dark:bg-gray-900/40 flex items-center justify-end gap-3">
            <button
              type="button"
              class="px-5 py-2.5 text-sm font-medium rounded-lg border transition-all duration-200"
              :class="cancelButtonClasses"
              @click="handleCancel"
              :disabled="isProcessing"
            >
              {{ options.cancelText || 'Cancel' }}
            </button>
            
            <button
              type="button"
              class="px-5 py-2.5 text-sm font-medium rounded-lg border transition-all duration-200 min-w-[100px]"
              :class="confirmButtonClasses"
              @click="handleConfirm"
              :disabled="isProcessing"
            >
              <span v-if="isProcessing" class="inline-flex items-center gap-2">
                <i class="fas fa-spinner fa-spin text-xs"></i>
                <span>Processing...</span>
              </span>
              <span v-else class="inline-flex items-center gap-2">
                <i v-if="options.type === 'danger'" class="fas fa-trash text-xs"></i>
                <i v-else-if="options.type === 'warning'" class="fas fa-exclamation-triangle text-xs"></i>
                <i v-else-if="options.type === 'success'" class="fas fa-check text-xs"></i>
                <i v-else class="fas fa-info-circle text-xs"></i>
                <span>{{ options.confirmText || 'Confirm' }}</span>
              </span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { ConfirmOptions } from '../../../types/composables'

interface Props {
  isOpen: boolean
  options: ConfirmOptions
}

const props = withDefaults(defineProps<Props>(), {
  isOpen: false,
  options: () => ({
    message: 'Are you sure?',
    type: 'info'
  })
})

const emit = defineEmits<{
  (e: 'confirm'): void
  (e: 'cancel'): void
}>()

const isProcessing = ref(false)

// Default title based on type
const defaultTitle = computed(() => {
  switch (props.options.type) {
    case 'danger':
      return 'Confirm Deletion'
    case 'warning':
      return 'Warning'
    case 'success':
      return 'Success'
    default:
      return 'Confirm Action'
  }
})

// Modal styling based on type
const modalClasses = computed(() => {
  const baseClasses = 'bg-white dark:bg-gray-50'
  
  switch (props.options.type) {
    case 'danger':
      return `${baseClasses} border-red-200 dark:border-red-300`
    case 'warning':
      return `${baseClasses} border-amber-200 dark:border-amber-300`
    case 'success':
      return `${baseClasses} border-green-200 dark:border-green-300`
    default:
      return `${baseClasses} border-gray-200 dark:border-gray-300`
  }
})

const headerClasses = computed(() => {
  switch (props.options.type) {
    case 'danger':
      return 'border-red-100 dark:border-red-200/50 bg-red-50/50 dark:bg-red-50/30'
    case 'warning':
      return 'border-amber-100 dark:border-amber-200/50 bg-amber-50/50 dark:bg-amber-50/30'
    case 'success':
      return 'border-green-100 dark:border-green-200/50 bg-green-50/50 dark:bg-green-50/30'
    default:
      return 'border-gray-100 dark:border-gray-200/50 bg-gray-50/50 dark:bg-gray-50/30'
  }
})

const iconContainerClasses = computed(() => {
  switch (props.options.type) {
    case 'danger':
      return 'bg-red-100 dark:bg-red-100 border border-red-200 dark:border-red-300'
    case 'warning':
      return 'bg-amber-100 dark:bg-amber-100 border border-amber-200 dark:border-amber-300'
    case 'success':
      return 'bg-green-100 dark:bg-green-100 border border-green-200 dark:border-green-300'
    default:
      return 'bg-gray-100 dark:bg-gray-100 border border-gray-200 dark:border-gray-300'
  }
})

const iconClasses = computed(() => {
  switch (props.options.type) {
    case 'danger':
      return 'fas fa-exclamation-triangle text-red-600 dark:text-red-600'
    case 'warning':
      return 'fas fa-exclamation-circle text-amber-600 dark:text-amber-600'
    case 'success':
      return 'fas fa-check-circle text-green-600 dark:text-green-600'
    default:
      return 'fas fa-info-circle text-gray-600 dark:text-gray-600'
  }
})

const titleClasses = computed(() => {
  return 'text-gray-900 dark:text-gray-900'
})

const messageClasses = computed(() => {
  return 'text-gray-700 dark:text-gray-700'
})

const cancelButtonClasses = computed(() => {
  return 'bg-white dark:bg-white border-gray-200 dark:border-gray-300 text-gray-700 dark:text-gray-700 hover:bg-gray-50 dark:hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed'
})

const confirmButtonClasses = computed(() => {
  switch (props.options.type) {
    case 'danger':
      return 'bg-red-600 dark:bg-red-600 border-red-700 dark:border-red-700 text-white hover:bg-red-700 dark:hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed'
    case 'warning':
      return 'bg-amber-600 dark:bg-amber-600 border-amber-700 dark:border-amber-700 text-white hover:bg-amber-700 dark:hover:bg-amber-700 disabled:opacity-50 disabled:cursor-not-allowed'
    case 'success':
      return 'bg-green-600 dark:bg-green-600 border-green-700 dark:border-green-700 text-white hover:bg-green-700 dark:hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed'
    default:
      return 'bg-gray-900 dark:bg-gray-900 border-gray-900 dark:border-gray-900 text-white hover:bg-gray-800 dark:hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed'
  }
})

function handleConfirm() {
  if (isProcessing.value) return
  isProcessing.value = true
  emit('confirm')
  // Reset processing state after a short delay
  setTimeout(() => {
    isProcessing.value = false
  }, 500)
}

function handleCancel() {
  if (isProcessing.value) return
  emit('cancel')
}
</script>

<style scoped>
/* Modal transition animations */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-active > div,
.modal-leave-active > div {
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from > div,
.modal-leave-to > div {
  transform: scale(0.95);
  opacity: 0;
}

.modal-enter-to,
.modal-leave-from {
  opacity: 1;
}

.modal-enter-to > div,
.modal-leave-from > div {
  transform: scale(1);
  opacity: 1;
}
</style>
