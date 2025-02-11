// Export all type definitions
export * from './editor'
export * from './project'

// Re-export user types
export interface User {
  id: number
  email: string
  username: string
  created_at: string
  updated_at: string
}

// Re-export notification types
export type NotificationType = 'success' | 'error' | 'warning' | 'info'

export interface Notification {
  type: NotificationType
  message: string
  duration?: number
  id?: string
}
