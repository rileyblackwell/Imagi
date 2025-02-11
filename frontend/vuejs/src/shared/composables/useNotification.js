import { useNotificationStore } from '../stores/notificationStore';

export function useNotification() {
  const notificationStore = useNotificationStore();

  const showNotification = ({ type, message, duration }) => {
    return notificationStore.add({
      type,
      message,
      duration
    });
  };

  return {
    showNotification
  };
}
