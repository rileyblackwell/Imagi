import { defineStore } from 'pinia'

interface AppState {
  isLoading: boolean
  errors: Array<{
    id: number
    message: string
    type: string
    timestamp: Date
  }>
  notifications: Array<{
    id: number
    message: string
    type: string
    timestamp: Date
    duration: number
  }>
  currentRoute: string | null
  breadcrumbs: Array<{
    text: string
    to?: string
  }>
  lastUpdated: Date | null
}

export const useAppStore = defineStore('app', {
  state: (): AppState => ({
    isLoading: false,
    errors: [],
    notifications: [],
    currentRoute: null,
    breadcrumbs: [],
    lastUpdated: null
  }),

  getters: {
    hasErrors: (state): boolean => state.errors.length > 0,
    hasNotifications: (state): boolean => state.notifications.length > 0,
    currentBreadcrumbs: (state) => state.breadcrumbs
  },

  actions: {
    setLoading(status: boolean) {
      this.isLoading = status
    },

    addError(error: { message: string; type?: string }) {
      this.errors.push({
        id: Date.now(),
        message: error.message || 'An error occurred',
        type: error.type || 'error',
        timestamp: new Date()
      })
    },

    clearErrors() {
      this.errors = []
    },

    addNotification(notification: { message: string; type?: string; duration?: number }) {
      this.notifications.push({
        id: Date.now(),
        message: notification.message,
        type: notification.type || 'info',
        timestamp: new Date(),
        duration: notification.duration || 5000
      })
    },

    removeNotification(id: number) {
      this.notifications = this.notifications.filter(n => n.id !== id)
    },

    updateRoute(route: string) {
      this.currentRoute = route
      this.lastUpdated = new Date()
    },

    setBreadcrumbs(breadcrumbs: Array<{ text: string; to?: string }>) {
      this.breadcrumbs = breadcrumbs
    }
  }
}) 