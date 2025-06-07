import { ref, readonly, type Ref, type DeepReadonly } from 'vue'

export type ToastType = 'success' | 'error' | 'info' | 'warning'

export interface Toast {
  id: number;
  message: string;
  type: ToastType;
  timeout: number;
}

export interface UseToastReturn {
  toasts: DeepReadonly<Ref<Toast[]>>;
  showToast(message: string, type?: ToastType, timeout?: number): number;
  hideToast(id: number): void;
  clearToasts(): void;
  success(message: string, timeout?: number): number;
  error(message: string, timeout?: number): number;
  info(message: string, timeout?: number): number;
  warning(message: string, timeout?: number): number;
}

// Create a global reactive list of toasts
const toasts = ref<Toast[]>([])
let toastIdCounter = 0

/**
 * Composable for toast notifications
 * 
 * @returns Object with methods to show different types of toasts and clear them
 */
export function useToast(): UseToastReturn {
  /**
   * Show a toast notification
   * 
   * @param message Message to display
   * @param type Type of toast (success, error, info, warning)
   * @param timeout Time in milliseconds before auto-hiding (0 for no auto-hide)
   * @returns The ID of the created toast
   */
  const showToast = (message: string, type: ToastType = 'info', timeout = 5000): number => {
    const id = toastIdCounter++
    const toast: Toast = { id, message, type, timeout }
    toasts.value.push(toast)
    
    // Auto-hide toast after timeout (if timeout > 0)
    if (timeout > 0) {
      setTimeout(() => {
        hideToast(id)
      }, timeout)
    }
    
    return id
  }
  
  /**
   * Hide a specific toast by ID
   * 
   * @param id ID of the toast to hide
   */
  const hideToast = (id: number): void => {
    const index = toasts.value.findIndex(toast => toast.id === id)
    if (index !== -1) {
      toasts.value.splice(index, 1)
    }
  }
  
  /**
   * Clear all toasts
   */
  const clearToasts = (): void => {
    toasts.value = []
  }
  
  /**
   * Show a success toast
   * 
   * @param message Message to display
   * @param timeout Time in milliseconds before auto-hiding
   * @returns The ID of the created toast
   */
  const success = (message: string, timeout = 5000): number => {
    return showToast(message, 'success', timeout)
  }
  
  /**
   * Show an error toast
   * 
   * @param message Message to display
   * @param timeout Time in milliseconds before auto-hiding
   * @returns The ID of the created toast
   */
  const error = (message: string, timeout = 5000): number => {
    return showToast(message, 'error', timeout)
  }
  
  /**
   * Show an info toast
   * 
   * @param message Message to display
   * @param timeout Time in milliseconds before auto-hiding
   * @returns The ID of the created toast
   */
  const info = (message: string, timeout = 5000): number => {
    return showToast(message, 'info', timeout)
  }
  
  /**
   * Show a warning toast
   * 
   * @param message Message to display
   * @param timeout Time in milliseconds before auto-hiding
   * @returns The ID of the created toast
   */
  const warning = (message: string, timeout = 5000): number => {
    return showToast(message, 'warning', timeout)
  }
  
  return {
    // Provide read-only access to toasts
    toasts: readonly(toasts),
    
    // Methods
    showToast,
    hideToast,
    clearToasts,
    success,
    error,
    info,
    warning
  }
} 