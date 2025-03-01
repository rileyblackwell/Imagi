import { defineStore } from 'pinia';

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration: number;
}

let notificationCounter = 0;
const generateId = () => {
  return `notification_${Date.now()}_${notificationCounter++}`;
};

export const useNotificationStore = defineStore('notifications', {
  state: () => ({
    notifications: [] as Notification[]
  }),

  actions: {
    add(notification: Partial<Notification> & { message: string }) {
      const id = generateId();
      this.notifications.push({
        id,
        type: notification.type || 'info',
        message: notification.message,
        duration: notification.duration || 5000
      });

      // Auto-remove notification after duration
      setTimeout(() => {
        this.remove(id);
      }, notification.duration || 5000);

      return id;
    },

    remove(id: string) {
      const index = this.notifications.findIndex(n => n.id === id);
      if (index > -1) {
        this.notifications.splice(index, 1);
      }
    },

    clear() {
      this.notifications = [];
    }
  }
}); 