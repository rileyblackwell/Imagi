export type NotificationType = 'success' | 'error' | 'warning' | 'info'

export interface NotificationOptions {
  type: NotificationType
  message: string
  duration?: number
}