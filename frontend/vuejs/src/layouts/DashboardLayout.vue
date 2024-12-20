<template>
  <div class="dashboard-layout">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
      <div class="sidebar-header">
        <router-link to="/" class="logo">
          <img
            v-if="!isSidebarCollapsed"
            src="@/assets/images/logo-full.svg"
            alt="Imagi Logo"
            class="logo-full"
          />
          <img
            v-else
            src="@/assets/images/logo-icon.svg"
            alt="Imagi"
            class="logo-icon"
          />
        </router-link>
        <button class="sidebar-toggle" @click="toggleSidebar">
          <i class="fas" :class="isSidebarCollapsed ? 'fa-chevron-right' : 'fa-chevron-left'"></i>
        </button>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in navigationItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isCurrentRoute(item.path) }"
          :title="isSidebarCollapsed ? item.label : ''"
        >
          <i class="nav-icon" :class="item.icon"></i>
          <span v-if="!isSidebarCollapsed" class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="credits" v-if="!isSidebarCollapsed">
          <div class="credits-label">AI Credits</div>
          <div class="credits-amount">{{ formatNumber(remainingCredits) }}</div>
        </div>
        <button
          class="btn btn-outline btn-sm buy-credits"
          @click="navigateToPricing"
          :title="isSidebarCollapsed ? 'Buy Credits' : ''"
        >
          <i class="fas fa-plus"></i>
          <span v-if="!isSidebarCollapsed">Buy Credits</span>
        </button>
      </div>
    </aside>

    <!-- Main content -->
    <div class="dashboard-content">
      <!-- Header -->
      <header class="dashboard-header">
        <div class="header-left">
          <h1 class="page-title">{{ currentPageTitle }}</h1>
        </div>
        <div class="header-right">
          <!-- Notifications -->
          <div class="notifications-dropdown" v-click-outside="closeNotifications">
            <button
              class="btn btn-icon"
              @click="toggleNotifications"
              :class="{ 'has-notifications': hasUnreadNotifications }"
            >
              <i class="fas fa-bell"></i>
              <span v-if="unreadCount" class="notification-badge">{{ unreadCount }}</span>
            </button>
            <div v-if="showNotifications" class="notifications-panel">
              <div class="notifications-header">
                <h3>Notifications</h3>
                <button
                  v-if="notifications.length"
                  class="btn btn-text"
                  @click="markAllAsRead"
                >
                  Mark all as read
                </button>
              </div>
              <div class="notifications-list">
                <template v-if="notifications.length">
                  <div
                    v-for="notification in notifications"
                    :key="notification.id"
                    class="notification-item"
                    :class="{ unread: !notification.read }"
                  >
                    <div class="notification-icon">
                      <i :class="getNotificationIcon(notification.type)"></i>
                    </div>
                    <div class="notification-content">
                      <div class="notification-message">{{ notification.message }}</div>
                      <div class="notification-time">{{ notification.relativeTime }}</div>
                    </div>
                  </div>
                </template>
                <div v-else class="notifications-empty">
                  <i class="fas fa-check-circle"></i>
                  <p>You're all caught up!</p>
                </div>
              </div>
            </div>
          </div>

          <!-- User menu -->
          <div class="user-menu" v-click-outside="closeUserMenu">
            <button class="btn btn-icon" @click="toggleUserMenu">
              <img
                :src="user.avatar || '/images/default-avatar.png'"
                :alt="user.name"
                class="user-avatar"
              />
            </button>
            <div v-if="showUserMenu" class="user-menu-panel">
              <div class="user-info">
                <img
                  :src="user.avatar || '/images/default-avatar.png'"
                  :alt="user.name"
                  class="user-avatar"
                />
                <div class="user-details">
                  <div class="user-name">{{ user.name }}</div>
                  <div class="user-email">{{ user.email }}</div>
                </div>
              </div>
              <div class="menu-items">
                <router-link to="/settings/profile" class="menu-item">
                  <i class="fas fa-user"></i>
                  Profile Settings
                </router-link>
                <router-link to="/settings/billing" class="menu-item">
                  <i class="fas fa-credit-card"></i>
                  Billing & Plans
                </router-link>
                <button class="menu-item text-error" @click="handleLogout">
                  <i class="fas fa-sign-out-alt"></i>
                  Sign Out
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Main content area -->
      <main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuth } from '@/composables/useAuth';
import { useNotifications } from '@/composables/useNotifications';
import { useAI } from '@/composables/useAI';
import { formatNumber } from '@/utils/helpers';

// Router
const router = useRouter();
const route = useRoute();

// Composables
const { user, logout } = useAuth();
const { notifications, unreadCount, hasUnread: hasUnreadNotifications, markAllAsRead } = useNotifications();
const { credits: remainingCredits } = useAI();

// State
const isSidebarCollapsed = ref(false);
const showNotifications = ref(false);
const showUserMenu = ref(false);

// Navigation items
const navigationItems = [
  { path: '/dashboard', label: 'Dashboard', icon: 'fas fa-home' },
  { path: '/projects', label: 'Projects', icon: 'fas fa-folder' },
  { path: '/builder', label: 'Builder', icon: 'fas fa-magic' },
  { path: '/settings', label: 'Settings', icon: 'fas fa-cog' }
];

// Computed
const currentPageTitle = computed(() => {
  const currentRoute = navigationItems.find(item => isCurrentRoute(item.path));
  return currentRoute ? currentRoute.label : '';
});

// Methods
function toggleSidebar() {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
  localStorage.setItem('sidebarCollapsed', isSidebarCollapsed.value);
}

function isCurrentRoute(path) {
  return route.path.startsWith(path);
}

function toggleNotifications() {
  showNotifications.value = !showNotifications.value;
  if (showUserMenu.value) showUserMenu.value = false;
}

function toggleUserMenu() {
  showUserMenu.value = !showUserMenu.value;
  if (showNotifications.value) showNotifications.value = false;
}

function closeNotifications() {
  showNotifications.value = false;
}

function closeUserMenu() {
  showUserMenu.value = false;
}

function getNotificationIcon(type) {
  switch (type) {
    case 'success':
      return 'fas fa-check-circle text-success';
    case 'error':
      return 'fas fa-exclamation-circle text-error';
    case 'warning':
      return 'fas fa-exclamation-triangle text-warning';
    default:
      return 'fas fa-info-circle text-primary';
  }
}

function navigateToPricing() {
  router.push('/settings/billing');
}

async function handleLogout() {
  try {
    await logout();
    router.push('/auth/login');
  } catch (err) {
    console.error('Logout failed:', err);
  }
}

// Lifecycle
onMounted(() => {
  const savedCollapsed = localStorage.getItem('sidebarCollapsed');
  if (savedCollapsed !== null) {
    isSidebarCollapsed.value = savedCollapsed === 'true';
  }
});
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
}

/* Sidebar */
.sidebar {
  width: 260px;
  background-color: var(--bg-primary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-base);
}

.sidebar-collapsed {
  width: 80px;
}

.sidebar-header {
  padding: var(--spacing-4);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-color);
}

.logo {
  display: flex;
  align-items: center;
}

.logo-full {
  height: 32px;
  width: auto;
}

.logo-icon {
  height: 32px;
  width: 32px;
}

.sidebar-toggle {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition-base);
}

.sidebar-toggle:hover {
  color: var(--text-primary);
}

.sidebar-nav {
  flex: 1;
  padding: var(--spacing-4) 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: var(--spacing-3) var(--spacing-4);
  color: var(--text-secondary);
  text-decoration: none;
  transition: var(--transition-base);
}

.nav-item:hover {
  color: var(--text-primary);
  background-color: var(--bg-secondary);
}

.nav-item.active {
  color: var(--primary-color);
  background-color: rgba(99, 102, 241, 0.1);
}

.nav-icon {
  width: 20px;
  text-align: center;
  margin-right: var(--spacing-3);
}

.sidebar-collapsed .nav-icon {
  margin-right: 0;
}

.sidebar-footer {
  padding: var(--spacing-4);
  border-top: 1px solid var(--border-color);
}

.credits {
  margin-bottom: var(--spacing-3);
}

.credits-label {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.credits-amount {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
}

.buy-credits {
  width: 100%;
}

/* Dashboard content */
.dashboard-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-secondary);
}

.dashboard-header {
  padding: var(--spacing-4) var(--spacing-6);
  background-color: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.page-title {
  font-size: var(--font-size-2xl);
  font-weight: 600;
  color: var(--text-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
}

/* Notifications */
.notifications-dropdown {
  position: relative;
}

.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background-color: var(--error-color);
  color: white;
  font-size: var(--font-size-xs);
  padding: 2px 6px;
  border-radius: var(--border-radius-full);
}

.notifications-panel {
  position: absolute;
  top: 100%;
  right: 0;
  width: 360px;
  background-color: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-xl);
  margin-top: var(--spacing-2);
  z-index: var(--z-dropdown);
}

.notifications-header {
  padding: var(--spacing-4);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.notifications-list {
  max-height: 400px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  padding: var(--spacing-4);
  border-bottom: 1px solid var(--border-color);
  transition: var(--transition-base);
}

.notification-item:hover {
  background-color: var(--bg-secondary);
}

.notification-item.unread {
  background-color: rgba(99, 102, 241, 0.05);
}

.notification-icon {
  margin-right: var(--spacing-3);
  font-size: var(--font-size-xl);
}

.notification-time {
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
  margin-top: var(--spacing-1);
}

.notifications-empty {
  padding: var(--spacing-8);
  text-align: center;
  color: var(--text-secondary);
}

.notifications-empty i {
  font-size: var(--font-size-3xl);
  color: var(--success-color);
  margin-bottom: var(--spacing-4);
}

/* User menu */
.user-menu {
  position: relative;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: var(--border-radius-full);
  object-fit: cover;
}

.user-menu-panel {
  position: absolute;
  top: 100%;
  right: 0;
  width: 280px;
  background-color: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-xl);
  margin-top: var(--spacing-2);
  z-index: var(--z-dropdown);
}

.user-info {
  padding: var(--spacing-4);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
}

.user-info .user-avatar {
  width: 48px;
  height: 48px;
  margin-right: var(--spacing-3);
}

.user-name {
  font-weight: 600;
  color: var(--text-primary);
}

.user-email {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.menu-items {
  padding: var(--spacing-2);
}

.menu-item {
  display: flex;
  align-items: center;
  padding: var(--spacing-3) var(--spacing-4);
  color: var(--text-secondary);
  text-decoration: none;
  transition: var(--transition-base);
  border-radius: var(--border-radius-md);
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
}

.menu-item:hover {
  color: var(--text-primary);
  background-color: var(--bg-secondary);
}

.menu-item i {
  width: 20px;
  margin-right: var(--spacing-3);
}

.menu-item.text-error {
  color: var(--error-color);
}

.menu-item.text-error:hover {
  background-color: rgba(239, 68, 68, 0.1);
}

/* Main content */
.main-content {
  flex: 1;
  padding: var(--spacing-6);
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

/* Responsive */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    top: 0;
    bottom: 0;
    z-index: var(--z-drawer);
    transform: translateX(-100%);
  }

  .sidebar.sidebar-collapsed {
    transform: translateX(0);
  }

  .dashboard-content {
    margin-left: 0;
  }

  .notifications-panel,
  .user-menu-panel {
    position: fixed;
    top: 60px;
    right: var(--spacing-4);
    left: var(--spacing-4);
    width: auto;
  }
}
</style> 