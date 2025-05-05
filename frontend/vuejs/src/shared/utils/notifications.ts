import type { NotificationType, NotificationOptions } from '../types/notifications'
import { useNotificationStore } from '../stores/notificationStore'

export const notify = (options: NotificationOptions) => {
  // Get the notification store
  try {
    const notificationStore = useNotificationStore()
    
    // Destructure notification options
    const { type, message, duration } = options
    
    // Add notification to store
    return notificationStore.add({
      type: type || 'info',
      message: message,
      duration: duration
    })
  } catch (error) {
    // Fallback to console if store is not available
    console.warn('Notification system not available:', options.message)
    
    // Log to console with appropriate styling
    switch (options.type) {
      case 'error':
        console.error(options.message)
        break
      case 'warning':
        console.warn(options.message)
        break
      case 'success':
        console.info('%c✓ ' + options.message, 'color: green')
        break
      default:
        console.info(options.message)
    }
    
    return null
  }
}