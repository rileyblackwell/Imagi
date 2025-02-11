import { useNotificationStore } from '../stores/notificationStore'

interface NotificationOptions {
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
}

export function useNotification() {
  const notificationStore = useNotificationStore()

  const showNotification = (options: NotificationOptions) => {
    const duration = options.duration || 5000
    return notificationStore.add({
      type: options.type,
      message: options.message,
      duration
    })
  }

  return {
    showNotification
  }
}
