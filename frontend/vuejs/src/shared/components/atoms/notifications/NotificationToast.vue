<template>
  <TransitionGroup
    tag="div"
    enter-active-class="transition-all duration-500 ease-out"
    enter-from-class="transform translate-x-full opacity-0 scale-95"
    enter-to-class="transform translate-x-0 opacity-100 scale-100"
    leave-active-class="transition-all duration-300 ease-in"
    leave-from-class="transform translate-x-0 opacity-100 scale-100"
    leave-to-class="transform translate-x-full opacity-0 scale-95"
    class="fixed top-6 right-6 z-[100] flex flex-col space-y-3 pointer-events-none"
  >
    <div
      v-for="notification in notifications"
      :key="notification.id"
      class="relative group overflow-hidden pointer-events-auto"
      @click="closeNotification(notification.id)"
    >
      <!-- Animated glow effect -->
      <div 
        class="absolute -inset-0.5 rounded-2xl opacity-0 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"
        :class="getGlowClasses(notification.type)"
      ></div>
      
      <!-- Main notification container -->
      <div
        class="relative min-w-[320px] max-w-md backdrop-blur-xl rounded-2xl border shadow-2xl transition-all duration-300 hover:shadow-3xl hover:-translate-y-1 cursor-pointer"
        :class="getNotificationClasses(notification.type)"
      >
        <!-- Subtle gradient header strip -->
        <div 
          class="h-0.5 w-full rounded-t-2xl"
          :class="getHeaderClasses(notification.type)"
        ></div>
        
        <!-- Content area -->
        <div class="p-4 flex items-center gap-3">
          <!-- Icon with animated background -->
          <div 
            class="w-8 h-8 rounded-xl flex items-center justify-center border transition-all duration-300"
            :class="getIconContainerClasses(notification.type)"
          >
            <i 
              class="text-sm transition-all duration-300" 
              :class="[getNotificationIcon(notification.type), getIconClasses(notification.type)]"
            ></i>
          </div>
          
          <!-- Message content -->
          <div class="flex-1 min-w-0">
            <p 
              class="text-sm font-medium leading-relaxed transition-all duration-300"
              :class="getTextClasses(notification.type)"
            >
              {{ notification.message }}
            </p>
          </div>
          
          <!-- Close button -->
          <button
            @click.stop="closeNotification(notification.id)"
            class="w-7 h-7 rounded-lg flex items-center justify-center opacity-50 hover:opacity-100 transition-all duration-200 hover:bg-white/5"
            aria-label="Close notification"
          >
            <i class="fas fa-times text-xs"></i>
          </button>
        </div>
        
        <!-- Animated progress bar -->
        <div class="absolute bottom-0 left-0 right-0 h-0.5 bg-white/5 rounded-b-2xl overflow-hidden">
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

const getNotificationClasses = (type) => {
  const baseClasses = 'bg-gradient-to-br from-dark-900/95 via-dark-900/90 to-dark-800/95 border-white/10';
  
  switch (type) {
    case 'success':
      return `${baseClasses} shadow-green-500/10`;
    case 'error':
      return `${baseClasses} shadow-red-500/10`;
    case 'warning':
      return `${baseClasses} shadow-yellow-500/10`;
    default:
      return `${baseClasses} shadow-indigo-500/10`;
  }
};

const getGlowClasses = (type) => {
  switch (type) {
    case 'success':
      return 'bg-gradient-to-r from-green-500/50 to-emerald-500/50';
    case 'error':
      return 'bg-gradient-to-r from-red-500/50 to-rose-500/50';
    case 'warning':
      return 'bg-gradient-to-r from-yellow-500/50 to-amber-500/50';
    default:
      return 'bg-gradient-to-r from-indigo-500/50 to-violet-500/50';
  }
};

const getHeaderClasses = (type) => {
  switch (type) {
    case 'success':
      return 'bg-gradient-to-r from-green-400 via-emerald-400 to-green-400 opacity-80';
    case 'error':
      return 'bg-gradient-to-r from-red-400 via-rose-400 to-red-400 opacity-80';
    case 'warning':
      return 'bg-gradient-to-r from-yellow-400 via-amber-400 to-yellow-400 opacity-80';
    default:
      return 'bg-gradient-to-r from-indigo-400 via-violet-400 to-indigo-400 opacity-80';
  }
};

const getIconContainerClasses = (type) => {
  switch (type) {
    case 'success':
      return 'bg-gradient-to-br from-green-500/20 to-emerald-500/20 border-green-400/30';
    case 'error':
      return 'bg-gradient-to-br from-red-500/20 to-rose-500/20 border-red-400/30';
    case 'warning':
      return 'bg-gradient-to-br from-yellow-500/20 to-amber-500/20 border-yellow-400/30';
    default:
      return 'bg-gradient-to-br from-indigo-500/20 to-violet-500/20 border-indigo-400/30';
  }
};

const getIconClasses = (type) => {
  switch (type) {
    case 'success':
      return 'text-green-300';
    case 'error':
      return 'text-red-300';
    case 'warning':
      return 'text-yellow-300';
    default:
      return 'text-indigo-300';
  }
};

const getTextClasses = (type) => {
  switch (type) {
    case 'success':
      return 'text-white';
    case 'error':
      return 'text-white';
    case 'warning':
      return 'text-white';
    default:
      return 'text-white';
  }
};

const getProgressClasses = (type) => {
  switch (type) {
    case 'success':
      return 'bg-gradient-to-r from-green-400 to-emerald-400';
    case 'error':
      return 'bg-gradient-to-r from-red-400 to-rose-400';
    case 'warning':
      return 'bg-gradient-to-r from-yellow-400 to-amber-400';
    default:
      return 'bg-gradient-to-r from-indigo-400 to-violet-400';
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

/* Enhanced shadow utilities */
.shadow-3xl {
  box-shadow: 0 35px 60px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255, 255, 255, 0.05);
}

/* Smooth transitions for all interactive elements */
* {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}

/* Backdrop blur fallback */
.backdrop-blur-xl {
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
}

/* Ensure proper stacking and interactivity */
.pointer-events-none {
  pointer-events: none;
}

.pointer-events-auto {
  pointer-events: auto;
}
</style>
