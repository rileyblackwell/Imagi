import type { NotificationType, NotificationOptions } from '../types/notifications'

export const notify = (options: NotificationOptions) => {
  // Store notifications in a queue for the UI to display
  // This will be replaced with a proper notification system in the future
  const { type, message } = options
  
  // Add to notification queue (to be implemented)
  // For now, we'll just suppress the console logs
}