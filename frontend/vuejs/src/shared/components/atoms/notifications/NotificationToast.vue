<template>
  <TransitionGroup
    tag="div"
    enter-active-class="transition duration-300 ease-out"
    enter-from-class="transform translate-y-2 opacity-0"
    enter-to-class="transform translate-y-0 opacity-100"
    leave-active-class="transition duration-200 ease-in"
    leave-from-class="transform translate-y-0 opacity-100"
    leave-to-class="transform translate-y-2 opacity-0"
    class="fixed bottom-0 right-0 z-50 p-4 space-y-4"
  >
    <div
      v-for="notification in notifications"
      :key="notification.id"
      class="max-w-md p-4 rounded-lg shadow-lg flex items-center gap-3"
      :class="getNotificationClasses(notification.type)"
    >
      <i class="text-lg" :class="getNotificationIcon(notification.type)"></i>
      <p class="flex-1">{{ notification.message }}</p>
      <button
        @click="closeNotification(notification.id)"
        class="p-1 opacity-60 hover:opacity-100 transition-opacity focus:outline-none"
        aria-label="Close notification"
      >
        <i class="fas fa-times"></i>
      </button>
    </div>
  </TransitionGroup>
</template>

<script setup>
import { computed } from 'vue';
import { useNotificationStore } from '@/shared/stores/notificationStore';

const store = useNotificationStore();
const notifications = computed(() => store.notifications);

const getNotificationClasses = (type) => {
  switch (type) {
    case 'success':
      return 'bg-green-500/10 text-green-400 border border-green-500/20';
    case 'error':
      return 'bg-red-500/10 text-red-400 border border-red-500/20';
    case 'warning':
      return 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20';
    default:
      return 'bg-blue-500/10 text-blue-400 border border-blue-500/20';
  }
};

const getNotificationIcon = (type) => {
  switch (type) {
    case 'success':
      return 'fas fa-check-circle';
    case 'error':
      return 'fas fa-exclamation-circle';
    case 'warning':
      return 'fas fa-exclamation-triangle';
    default:
      return 'fas fa-info-circle';
  }
};

const closeNotification = (id) => {
  store.removeNotification(id);
};
</script>
