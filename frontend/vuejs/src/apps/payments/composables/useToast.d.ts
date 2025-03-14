export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface Toast {
  id: number;
  message: string;
  type: ToastType;
  timeout: number;
}

export interface UseToastReturn {
  toasts: readonly Toast[];
  addToast(message: string, type: ToastType, timeout?: number): void;
  removeToast(id: number): void;
  clearToasts(): void;
  success(message: string, timeout?: number): void;
  error(message: string, timeout?: number): void;
  info(message: string, timeout?: number): void;
  warning(message: string, timeout?: number): void;
}

export function useToast(): UseToastReturn; 