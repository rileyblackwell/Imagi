import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    isLoading: false,
    errors: [],
    notifications: [],
    currentRoute: null,
    breadcrumbs: [],
    lastUpdated: null
  }),

  getters: {
    hasErrors: (state) => state.errors.length > 0,
    hasNotifications: (state) => state.notifications.length > 0,
    currentBreadcrumbs: (state) => state.breadcrumbs
  },

  actions: {
    setLoading(status) {
      this.isLoading = status
    },

    addError(error) {
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

    addNotification(notification) {
      this.notifications.push({
        id: Date.now(),
        message: notification.message,
        type: notification.type || 'info',
        timestamp: new Date(),
        duration: notification.duration || 5000 // Default 5 seconds
      })
    },

    removeNotification(id) {
      this.notifications = this.notifications.filter(n => n.id !== id)
    },

    updateRoute(route) {
      this.currentRoute = route
      this.lastUpdated = new Date()
    },

    setBreadcrumbs(breadcrumbs) {
      this.breadcrumbs = breadcrumbs
    }
  }
}) 