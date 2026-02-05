<template>
  <TransitionGroup
    tag="div"
    enter-active-class="transition-all duration-500 ease-out"
    enter-from-class="transform translate-x-full opacity-0 scale-95"
    enter-to-class="transform translate-x-0 opacity-100 scale-100"
    leave-active-class="transition-all duration-300 ease-in"
    leave-from-class="transform translate-x-0 opacity-100 scale-100"
    leave-to-class="transform translate-x-full opacity-0 scale-95"
    class="fixed bottom-6 right-6 z-[100] flex flex-col-reverse space-y-3 space-y-reverse pointer-events-none"
  >
    <div
      v-for="notification in notifications"
      :key="notification.id"
      class="relative group overflow-hidden pointer-events-auto"
      @click="closeNotification(notification.id)"
    >
      <!-- Main notification container - Light theme matching Projects page -->
      <div
        class="relative min-w-[320px] max-w-md rounded-2xl border shadow-md transition-all duration-300 hover:shadow-lg hover:-translate-y-0.5 cursor-pointer"
        :class="getNotificationClasses(notification.type)"
      >
        <!-- Content area -->
        <div class="p-4 flex items-center gap-3">
          <!-- Icon container -->
          <div 
            class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
            :class="getIconContainerClasses(notification.type)"
          >
            <i 
              class="text-base" 
              :class="[getNotificationIcon(notification.type), getIconClasses(notification.type)]"
            ></i>
          </div>
          
          <!-- Message content -->
          <div class="flex-1 min-w-0">
            <p 
              class="text-sm font-medium leading-relaxed"
              :class="getTextClasses(notification.type)"
            >
              {{ notification.message }}
            </p>
          </div>
          
          <!-- Close button -->
          <button
            @click.stop="closeNotification(notification.id)"
            class="w-7 h-7 rounded-lg flex items-center justify-center transition-all duration-200 flex-shrink-0"
            :class="getCloseButtonClasses(notification.type)"
            aria-label="Close notification"
          >
            <i class="fas fa-times text-xs"></i>
          </button>
        </div>
        
        <!-- Animated progress bar -->
        <div class="absolute bottom-0 left-0 right-0 h-1 rounded-b-2xl overflow-hidden bg-gray-100">
          <div 
            class="h-full rounded-b-2xl animate-progress-bar"
            :class="getProgressClasses(notification.type)"
            :style="{ animationDuration: `${notification.duration}ms` }"
          ></div>
        </div>
      </div>
    </div>
  </TransitionGroup>
</template>

<script setup>
import { computed } from 'vue';
import { useNotificationStore } from '@/shared/stores/notificationStore';

const store = useNotificationStore();
const notifications = computed(() => store.notifications);

// Light theme styling to match Projects page design
const getNotificationClasses = (type) => {
  const baseClasses = 'bg-white';
  
  switch (type) {
    case 'success':
      return `${baseClasses} border-green-200`;
    case 'error':
      return `${baseClasses} border-red-200`;
    case 'delete':
      return `${baseClasses} border-red-200`;
    case 'warning':
      return `${baseClasses} border-amber-200`;
    default:
      return `${baseClasses} border-gray-200`;
  }
};

const getIconContainerClasses = (type) => {
  switch (type) {
    case 'success':
      return 'bg-green-50 border border-green-200';
    case 'error':
      return 'bg-red-50 border border-red-200';
    case 'delete':
      return 'bg-red-50 border border-red-200';
    case 'warning':
      return 'bg-amber-50 border border-amber-200';
    default:
      return 'bg-gray-50 border border-gray-200';
  }
};

const getIconClasses = (type) => {
  switch (type) {
    case 'success':
      return 'text-green-600';
    case 'error':
      return 'text-red-600';
    case 'delete':
      return 'text-red-600';
    case 'warning':
      return 'text-amber-600';
    default:
      return 'text-gray-600';
  }
};

const getTextClasses = (type) => {
  return 'text-gray-900';
};

const getCloseButtonClasses = (type) => {
  switch (type) {
    case 'success':
      return 'text-green-400 hover:text-green-600 hover:bg-green-50';
    case 'error':
      return 'text-red-400 hover:text-red-600 hover:bg-red-50';
    case 'delete':
      return 'text-red-400 hover:text-red-600 hover:bg-red-50';
    case 'warning':
      return 'text-amber-400 hover:text-amber-600 hover:bg-amber-50';
    default:
      return 'text-gray-400 hover:text-gray-600 hover:bg-gray-50';
  }
};

const getProgressClasses = (type) => {
  switch (type) {
    case 'success':
      return 'bg-green-500';
    case 'error':
      return 'bg-red-500';
    case 'delete':
      return 'bg-red-500';
    case 'warning':
      return 'bg-amber-500';
    default:
      return 'bg-gray-500';
  }
};

const getNotificationIcon = (type) => {
  switch (type) {
    case 'success':
      return 'fas fa-check-circle';
    case 'error':
      return 'fas fa-exclamation-circle';
    case 'delete':
      return 'fas fa-trash-alt';  // Trash icon for delete success
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

<style scoped>
/* Custom progress bar animation */
@keyframes progress-bar {
  from {
    width: 100%;
  }
  to {
    width: 0%;
  }
}

.animate-progress-bar {
  animation: progress-bar linear forwards;
}

/* Ensure proper stacking and interactivity */
.pointer-events-none {
  pointer-events: none;
}

.pointer-events-auto {
  pointer-events: auto;
}
</style>
