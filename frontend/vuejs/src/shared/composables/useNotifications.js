import { ref, computed } from 'vue';
import axios from 'axios';
import { formatRelativeTime } from '@/utils/helpers';

const notifications = ref([]);
const unreadCount = ref(0);
const loading = ref(false);
const error = ref(null);

export function useNotifications() {
  /**
   * Fetch user's notifications
   * @param {Object} options - Fetch options
   * @param {number} options.page - Page number
   * @param {number} options.limit - Number of notifications per page
   */
  async function fetchNotifications({ page = 1, limit = 20 } = {}) {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.get('/api/notifications/', {
        params: { page, limit }
      });
      notifications.value = response.data.notifications;
      unreadCount.value = response.data.unread_count;
    } catch (err) {
      console.error('Failed to fetch notifications:', err);
      error.value = err.response?.data?.message || 'Failed to fetch notifications. Please try again.';
    } finally {
      loading.value = false;
    }
  }

  /**
   * Mark a notification as read
   * @param {string} notificationId - ID of the notification to mark as read
   */
  async function markAsRead(notificationId) {
    try {
      await axios.post(`/api/notifications/${notificationId}/read/`);
      const notification = notifications.value.find(n => n.id === notificationId);
      if (notification && !notification.read) {
        notification.read = true;
        unreadCount.value--;
      }
    } catch (err) {
      console.error('Failed to mark notification as read:', err);
      error.value = err.response?.data?.message || 'Failed to mark notification as read. Please try again.';
    }
  }

  /**
   * Mark all notifications as read
   */
  async function markAllAsRead() {
    try {
      await axios.post('/api/notifications/mark-all-read/');
      notifications.value.forEach(notification => {
        notification.read = true;
      });
      unreadCount.value = 0;
    } catch (err) {
      console.error('Failed to mark all notifications as read:', err);
      error.value = err.response?.data?.message || 'Failed to mark all notifications as read. Please try again.';
    }
  }

  /**
   * Delete a notification
   * @param {string} notificationId - ID of the notification to delete
   */
  async function deleteNotification(notificationId) {
    try {
      await axios.delete(`/api/notifications/${notificationId}/`);
      const index = notifications.value.findIndex(n => n.id === notificationId);
      if (index !== -1) {
        const notification = notifications.value[index];
        if (!notification.read) {
          unreadCount.value--;
        }
        notifications.value.splice(index, 1);
      }
    } catch (err) {
      console.error('Failed to delete notification:', err);
      error.value = err.response?.data?.message || 'Failed to delete notification. Please try again.';
    }
  }

  /**
   * Clear all notifications
   */
  async function clearAll() {
    try {
      await axios.delete('/api/notifications/');
      notifications.value = [];
      unreadCount.value = 0;
    } catch (err) {
      console.error('Failed to clear notifications:', err);
      error.value = err.response?.data?.message || 'Failed to clear notifications. Please try again.';
    }
  }

  /**
   * Update notification preferences
   * @param {Object} preferences - Notification preferences
   * @param {boolean} preferences.email_notifications - Whether to receive email notifications
   * @param {boolean} preferences.push_notifications - Whether to receive push notifications
   */
  async function updatePreferences(preferences) {
    try {
      await axios.patch('/api/notifications/preferences/', preferences);
    } catch (err) {
      console.error('Failed to update notification preferences:', err);
      error.value = err.response?.data?.message || 'Failed to update notification preferences. Please try again.';
      throw err;
    }
  }

  // Computed properties
  const notificationsList = computed(() => {
    return notifications.value.map(notification => ({
      ...notification,
      relativeTime: formatRelativeTime(notification.created_at)
    }));
  });

  const unreadNotifications = computed(() => {
    return notifications.value.filter(notification => !notification.read);
  });

  const hasUnread = computed(() => unreadCount.value > 0);
  const isLoading = computed(() => loading.value);
  const notificationError = computed(() => error.value);

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
    updatePreferences
  };
} 