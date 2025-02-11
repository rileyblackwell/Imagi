export type NotificationType = 'success' | 'error' | 'warning' | 'info'

export interface Notification {
  type: NotificationType
  message: string
  duration?: number
  id?: string
}
