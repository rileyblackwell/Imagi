import type { NotificationType, NotificationOptions } from '../types/notifications'

export const notify = (options: NotificationOptions) => {
  // For now, just use console, we can enhance this later with a proper notification system
  const { type, message } = options
  console.log(`[${type.toUpperCase()}] ${message}`)
}