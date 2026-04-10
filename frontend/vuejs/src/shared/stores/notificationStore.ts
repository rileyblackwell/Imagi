import { defineStore } from 'pinia';

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info' | 'delete';
  message: string;
  duration: number;
  timeoutId?: number; // Track timeout ID for cleanup
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
      
      // Create new notification object
      const newNotification: Notification = {
        id,
        type: notification.type || 'info',
        message: notification.message,
        duration: notification.duration || 5000
      };
      
      // Set auto-remove timeout
      const timeoutId = window.setTimeout(() => {
        this.remove(id);
      }, newNotification.duration);
      
      // Store timeout ID for cleanup
      newNotification.timeoutId = timeoutId;
      
      // Add to notifications array
      this.notifications.push(newNotification);

      return id;
    },

    remove(id: string) {
      const index = this.notifications.findIndex(n => n.id === id);
      if (index > -1) {
        // Clear timeout if it exists to prevent memory leaks
        const notification = this.notifications[index];
        if (notification.timeoutId) {
          window.clearTimeout(notification.timeoutId);
        }
        
        // Remove notification from array
        this.notifications.splice(index, 1);
      }
    },
    
    // Renamed from remove to removeNotification for clarity
    removeNotification(id: string) {
      this.remove(id);
    },

    clear() {
      // Clear all timeouts to prevent memory leaks
      this.notifications.forEach(n => {
        if (n.timeoutId) {
          window.clearTimeout(n.timeoutId);
        }
      });
      
      this.notifications = [];
    }
  }
}); 