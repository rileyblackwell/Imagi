<template>
  <div class="main-layout">
    <AppHeader />
    
    <main class="main-content">
      <div class="container">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>

    <AppFooter />

    <!-- Notifications -->
    <div class="notifications-container">
      <transition-group name="notification">
        <div
          v-for="notification in notifications"
          :key="notification.id"
          class="notification"
          :class="notification.type"
        >
          <div class="notification-content">
            <i :class="getNotificationIcon(notification.type)" class="notification-icon"></i>
            <div class="notification-message">{{ notification.message }}</div>
          </div>
          <button
            class="notification-close"
            @click="dismissNotification(notification.id)"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
      </transition-group>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useNotifications } from '@/composables/useNotifications';
import AppHeader from '@/components/common/AppHeader.vue';
import AppFooter from '@/components/common/AppFooter.vue';

const { notifications, dismissNotification } = useNotifications();

function getNotificationIcon(type) {
  switch (type) {
    case 'success':
      return 'fas fa-check-circle';
    case 'error':
      return 'fas fa-exclamation-circle';
    case 'warning':
      return 'fas fa-exclamation-triangle';
    case 'info':
    default:
      return 'fas fa-info-circle';
  }
}
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding: var(--spacing-8) 0;
  background-color: var(--bg-secondary);
}

/* Notifications */
.notifications-container {
  position: fixed;
  top: var(--spacing-4);
  right: var(--spacing-4);
  z-index: var(--z-toast);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
  max-width: 400px;
}

.notification {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-4);
  border-radius: var(--border-radius-md);
  background-color: var(--bg-primary);
  box-shadow: var(--shadow-lg);
  margin-bottom: var(--spacing-2);
}

.notification-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.notification-icon {
  font-size: var(--font-size-xl);
}

.notification-message {
  font-size: var(--font-size-sm);
  color: var(--text-primary);
}

.notification-close {
  background: none;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: var(--spacing-2);
  transition: var(--transition-base);
}

.notification-close:hover {
  color: var(--text-primary);
}

/* Notification types */
.notification.success {
  border-left: 4px solid var(--success-color);
}

.notification.success .notification-icon {
  color: var(--success-color);
}

.notification.error {
  border-left: 4px solid var(--error-color);
}

.notification.error .notification-icon {
  color: var(--error-color);
}

.notification.warning {
  border-left: 4px solid var(--warning-color);
}

.notification.warning .notification-icon {
  color: var(--warning-color);
}

.notification.info {
  border-left: 4px solid var(--primary-color);
}

.notification.info .notification-icon {
  color: var(--primary-color);
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style> 