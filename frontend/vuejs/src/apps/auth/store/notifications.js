import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

function formatRelativeTime(date) {
  const now = new Date()
  const target = new Date(date)
  const diff = Math.floor((now - target) / 1000) // difference in seconds

  if (diff < 60) return 'just now'
  if (diff < 3600) return `${Math.floor(diff / 60)} minutes ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`
  if (diff < 2592000) return `${Math.floor(diff / 86400)} days ago`
  if (diff < 31536000) return `${Math.floor(diff / 2592000)} months ago`
  return `${Math.floor(diff / 31536000)} years ago`
}

export const useNotificationsStore = defineStore('notifications', () => {
  // State
  const notifications = ref([])
  const unreadCount = ref(0)
  const loading = ref(false)
  const error = ref(null)

  // Computed
  const notificationsList = computed(() => {
    return notifications.value.map(notification => ({
      ...notification,
      relativeTime: formatRelativeTime(notification.created_at)
    }))
  })

  const unreadNotifications = computed(() => {
    return notifications.value.filter(notification => !notification.read)
  })

  const hasUnread = computed(() => unreadCount.value > 0)
  const isLoading = computed(() => loading.value)
  const notificationError = computed(() => error.value)

  // Actions
  async function fetchNotifications({ page = 1, limit = 20 } = {}) {
    loading.value = true
    error.value = null

    try {
      const response = await axios.get('/api/notifications/', {
        params: { page, limit }
      })
      notifications.value = response.data.notifications
      unreadCount.value = response.data.unread_count
    } catch (err) {
      console.error('Failed to fetch notifications:', err)
      error.value = err.response?.data?.message || 'Failed to fetch notifications. Please try again.'
    } finally {
      loading.value = false
    }
  }

  async function markAsRead(notificationId) {
    try {
      await axios.post(`/api/notifications/${notificationId}/read/`)
      const notification = notifications.value.find(n => n.id === notificationId)
      if (notification && !notification.read) {
        notification.read = true
        unreadCount.value--
      }
    } catch (err) {
      console.error('Failed to mark notification as read:', err)
      error.value = err.response?.data?.message || 'Failed to mark notification as read. Please try again.'
    }
  }

  async function markAllAsRead() {
    try {
      await axios.post('/api/notifications/mark-all-read/')
      notifications.value.forEach(notification => {
        notification.read = true
      })
      unreadCount.value = 0
    } catch (err) {
      console.error('Failed to mark all notifications as read:', err)
      error.value = err.response?.data?.message || 'Failed to mark all notifications as read. Please try again.'
    }
  }

  async function deleteNotification(notificationId) {
    try {
      await axios.delete(`/api/notifications/${notificationId}/`)
      const index = notifications.value.findIndex(n => n.id === notificationId)
      if (index !== -1) {
        const notification = notifications.value[index]
        if (!notification.read) {
          unreadCount.value--
        }
        notifications.value.splice(index, 1)
      }
    } catch (err) {
      console.error('Failed to delete notification:', err)
      error.value = err.response?.data?.message || 'Failed to delete notification. Please try again.'
    }
  }

  async function clearAll() {
    try {
      await axios.delete('/api/notifications/')
      notifications.value = []
      unreadCount.value = 0
    } catch (err) {
      console.error('Failed to clear notifications:', err)
      error.value = err.response?.data?.message || 'Failed to clear notifications. Please try again.'
    }
  }

  async function updatePreferences(preferences) {
    try {
      await axios.patch('/api/notifications/preferences/', preferences)
    } catch (err) {
      console.error('Failed to update notification preferences:', err)
      error.value = err.response?.data?.message || 'Failed to update notification preferences. Please try again.'
      throw err
    }
  }

  // Helper function to show a notification
  function showNotification({ type = 'info', message, duration = 5000 }) {
    notifications.value.unshift({
      id: Date.now().toString(),
      type,
      message,
      created_at: new Date().toISOString(),
      read: false
    })
    unreadCount.value++

    if (duration > 0) {
      setTimeout(() => {
        const index = notifications.value.findIndex(n => n.id === id)
        if (index !== -1) {
          notifications.value.splice(index, 1)
          if (!notifications.value[index].read) {
            unreadCount.value--
          }
        }
      }, duration)
    }
  }

  return {
    // State
    notifications: notificationsList,
    unreadNotifications,
    hasUnread,
    unreadCount,
    isLoading,
    error: notificationError,

    // Methods
    fetchNotifications,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    clearAll,
    updatePreferences,
    showNotification
  }
}) 