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
                class="text-blue-950/40 hover:text-blue-950/70 dark:text-blue-100/50 dark:hover:text-white p-1 rounded-lg hover:bg-blue-50 dark:hover:bg-white/[0.06] transition-colors duration-200 flex-shrink-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#101014]"
                @click="handleCancel"
                aria-label="Close"
              >
                <i class="fas fa-times text-sm"></i>
              </button>
            </div>
          </div>

          <!-- Footer / Actions -->
          <div class="px-6 py-4 bg-blue-50/60 dark:bg-white/[0.03] flex items-center justify-end gap-3">
            <button
              type="button"
              class="px-5 py-2.5 text-sm font-medium rounded-full border transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#101014]"
              :class="cancelButtonClasses"
              @click="handleCancel"
              :disabled="isProcessing"
            >
              {{ options.cancelText || 'Cancel' }}
            </button>

            <button
              type="button"
              class="px-5 py-2.5 text-sm font-medium rounded-full border transition-colors duration-200 min-w-[100px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#101014]"
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
  const baseClasses = 'bg-white dark:bg-[#101014]'

  switch (props.options.type) {
    case 'danger':
      return `${baseClasses} border-red-200 dark:border-red-500/30`
    case 'warning':
      return `${baseClasses} border-amber-200 dark:border-amber-500/30`
    case 'success':
      return `${baseClasses} border-green-200 dark:border-green-500/30`
    default:
      return `${baseClasses} border-blue-200 dark:border-blue-300/[0.16]`
  }
})

const headerClasses = computed(() => {
  switch (props.options.type) {
    case 'danger':
      return 'border-red-100 dark:border-red-500/20 bg-red-50/50 dark:bg-red-500/[0.06]'
    case 'warning':
      return 'border-amber-100 dark:border-amber-500/20 bg-amber-50/50 dark:bg-amber-500/[0.06]'
    case 'success':
      return 'border-green-100 dark:border-green-500/20 bg-green-50/50 dark:bg-green-500/[0.06]'
    default:
      return 'border-blue-100 dark:border-blue-400/20 bg-blue-50/50 dark:bg-blue-400/[0.06]'
  }
})

const iconContainerClasses = computed(() => {
  switch (props.options.type) {
    case 'danger':
      return 'bg-red-100 dark:bg-red-500/[0.12] border border-red-200 dark:border-red-500/30'
    case 'warning':
      return 'bg-amber-100 dark:bg-amber-500/[0.12] border border-amber-200 dark:border-amber-500/30'
    case 'success':
      return 'bg-green-100 dark:bg-green-500/[0.12] border border-green-200 dark:border-green-500/30'
    default:
      return 'bg-blue-100 dark:bg-blue-400/[0.12] border border-blue-200 dark:border-blue-400/30'
  }
})

const iconClasses = computed(() => {
  switch (props.options.type) {
    case 'danger':
      return 'fas fa-exclamation-triangle text-red-600 dark:text-red-400'
    case 'warning':
      return 'fas fa-exclamation-circle text-amber-600 dark:text-amber-400'
    case 'success':
      return 'fas fa-check-circle text-green-600 dark:text-green-400'
    default:
      return 'fas fa-info-circle text-blue-600 dark:text-blue-300'
  }
})

const titleClasses = computed(() => {
  return 'text-blue-950 dark:text-white'
})

const messageClasses = computed(() => {
  return 'text-blue-950/70 dark:text-blue-100/70'
})

const cancelButtonClasses = computed(() => {
  return 'bg-white dark:bg-white/[0.03] border-blue-950/[0.14] dark:border-white/[0.16] text-blue-950/80 dark:text-blue-100/80 hover:text-blue-950 dark:hover:text-white hover:border-blue-950/30 dark:hover:border-white/30 hover:bg-blue-950/[0.03] dark:hover:bg-white/[0.06] disabled:opacity-50 disabled:cursor-not-allowed'
})

const confirmButtonClasses = computed(() => {
  switch (props.options.type) {
    case 'danger':
      return 'bg-red-600 dark:bg-red-600 border-transparent text-white hover:bg-red-700 dark:hover:bg-red-500 shadow-[0_1px_2px_rgba(127,29,29,0.2),0_3px_8px_-2px_rgba(127,29,29,0.25)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.4),0_3px_8px_-2px_rgba(0,0,0,0.45)] disabled:opacity-50 disabled:cursor-not-allowed'
    case 'warning':
      return 'bg-amber-600 dark:bg-amber-600 border-transparent text-white hover:bg-amber-700 dark:hover:bg-amber-500 shadow-[0_1px_2px_rgba(120,53,15,0.2),0_3px_8px_-2px_rgba(120,53,15,0.25)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.4),0_3px_8px_-2px_rgba(0,0,0,0.45)] disabled:opacity-50 disabled:cursor-not-allowed'
    case 'success':
      return 'bg-green-600 dark:bg-green-600 border-transparent text-white hover:bg-green-700 dark:hover:bg-green-500 shadow-[0_1px_2px_rgba(20,83,45,0.2),0_3px_8px_-2px_rgba(20,83,45,0.25)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.4),0_3px_8px_-2px_rgba(0,0,0,0.45)] disabled:opacity-50 disabled:cursor-not-allowed'
    default:
      return 'bg-blue-950 dark:bg-[#f3ede2] border-transparent text-[#fdf9f2] dark:text-blue-950 hover:bg-blue-900 dark:hover:bg-white shadow-[0_1px_2px_rgba(23,37,84,0.2),0_3px_8px_-2px_rgba(23,37,84,0.25)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.4),0_3px_8px_-2px_rgba(0,0,0,0.45)] disabled:opacity-50 disabled:cursor-not-allowed'
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

@media (prefers-reduced-motion: reduce) {
  .modal-enter-active,
  .modal-leave-active,
  .modal-enter-active > div,
  .modal-leave-active > div {
    transition: none;
  }

  .modal-enter-from > div,
  .modal-leave-to > div {
    transform: none;
  }
}
</style>
