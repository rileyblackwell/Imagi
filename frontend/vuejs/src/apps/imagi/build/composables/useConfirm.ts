import { ref } from 'vue'
import type { ConfirmOptions } from '../types/composables'

// Global state for the confirm modal
const isModalOpen = ref(false)
const modalOptions = ref<ConfirmOptions>({
  message: '',
  type: 'info'
})
let resolvePromise: ((value: boolean) => void) | null = null

export function useConfirm() {
  /**
   * Shows a confirmation dialog and returns a promise that resolves 
   * to true if confirmed, false if cancelled
   */
  const confirm = (options: ConfirmOptions): Promise<boolean> => {
    return new Promise((resolve) => {
      modalOptions.value = options
      isModalOpen.value = true
      resolvePromise = resolve
    })
  }

  const handleConfirm = () => {
    isModalOpen.value = false
    if (resolvePromise) {
      resolvePromise(true)
      resolvePromise = null
    }
  }

  const handleCancel = () => {
    isModalOpen.value = false
    if (resolvePromise) {
      resolvePromise(false)
      resolvePromise = null
    }
  }

  return {
    confirm,
    isModalOpen,
    modalOptions,
    handleConfirm,
    handleCancel
  }
}

 