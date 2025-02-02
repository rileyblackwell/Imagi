import { ref } from 'vue'

export function useToast() {
  const toasts = ref([])

  function showToast(message, type = 'info', duration = 3000) {
    const id = Date.now()
    const toast = {
      id,
      message,
      type,
      show: true
    }

    toasts.value.push(toast)

    setTimeout(() => {
      const index = toasts.value.findIndex(t => t.id === id)
      if (index !== -1) {
        toasts.value[index].show = false
        setTimeout(() => {
          toasts.value = toasts.value.filter(t => t.id !== id)
        }, 300)
      }
    }, duration)
  }

  function error(message) {
    showToast(message, 'error')
  }

  function success(message) {
    showToast(message, 'success')
  }

  function info(message) {
    showToast(message, 'info')
  }

  return {
    toasts,
    error,
    success,
    info
  }
} 