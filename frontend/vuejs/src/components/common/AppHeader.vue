<template>
  <header class="app-header">
    <div class="container">
      <div class="header-content">
        <!-- Logo -->
        <router-link to="/" class="logo">
          <img src="@/assets/images/logo-full.svg" alt="Imagi Logo" class="logo-full" />
        </router-link>

        <!-- Navigation -->
        <nav class="nav-menu" :class="{ 'nav-menu-open': isMenuOpen }">
          <router-link
            v-for="item in navigationItems"
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ active: isCurrentRoute(item.path) }"
            @click="closeMenu"
          >
            {{ item.label }}
          </router-link>
        </nav>

        <!-- Actions -->
        <div class="header-actions">
          <template v-if="isAuthenticated">
            <!-- Credits -->
            <div class="credits-display">
              <i class="fas fa-bolt"></i>
              <span class="credits-amount">{{ formatNumber(remainingCredits) }}</span>
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
                  <router-link to="/dashboard" class="menu-item" @click="closeUserMenu">
                    <i class="fas fa-home"></i>
                    Dashboard
                  </router-link>
                  <router-link to="/settings/profile" class="menu-item" @click="closeUserMenu">
                    <i class="fas fa-user"></i>
                    Profile Settings
                  </router-link>
                  <router-link to="/settings/billing" class="menu-item" @click="closeUserMenu">
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
          </template>
          <template v-else>
            <router-link to="/auth/login" class="btn btn-outline">Sign In</router-link>
            <router-link to="/auth/register" class="btn btn-primary">Get Started</router-link>
          </template>

          <!-- Mobile menu toggle -->
          <button class="menu-toggle" @click="toggleMenu">
            <i class="fas" :class="isMenuOpen ? 'fa-times' : 'fa-bars'"></i>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuth } from '@/composables/useAuth';
import { useAI } from '@/composables/useAI';
import { formatNumber } from '@/utils/helpers';

// Router
const router = useRouter();
const route = useRoute();

// Composables
const { user, isAuthenticated, logout } = useAuth();
const { credits: remainingCredits } = useAI();

// State
const isMenuOpen = ref(false);
const showUserMenu = ref(false);

// Navigation items
const navigationItems = [
  { path: '/features', label: 'Features' },
  { path: '/pricing', label: 'Pricing' },
  { path: '/docs', label: 'Documentation' },
  { path: '/blog', label: 'Blog' }
];

// Methods
function isCurrentRoute(path) {
  return route.path === path;
}

function toggleMenu() {
  isMenuOpen.value = !isMenuOpen.value;
  if (isMenuOpen.value) {
    document.body.style.overflow = 'hidden';
  } else {
    document.body.style.overflow = '';
  }
}

function closeMenu() {
  isMenuOpen.value = false;
  document.body.style.overflow = '';
}

function toggleUserMenu() {
  showUserMenu.value = !showUserMenu.value;
}

function closeUserMenu() {
  showUserMenu.value = false;
}

async function handleLogout() {
  try {
    await logout();
    closeUserMenu();
    router.push('/');
  } catch (err) {
    console.error('Logout failed:', err);
  }
}
</script>

<style scoped>
.app-header {
  height: 72px;
  background-color: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
}

.header-content {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
}

.logo-full {
  height: 32px;
  width: auto;
}

/* Navigation */
.nav-menu {
  display: flex;
  align-items: center;
  gap: var(--spacing-6);
}

.nav-item {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: var(--font-size-sm);
  transition: var(--transition-base);
}

.nav-item:hover {
  color: var(--text-primary);
}

.nav-item.active {
  color: var(--primary-color);
}

/* Header actions */
.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
}

.credits-display {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-3);
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius-full);
  color: var(--text-primary);
  font-size: var(--font-size-sm);
}

.credits-display i {
  color: var(--primary-color);
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
  top: calc(100% + var(--spacing-2));
  right: 0;
  width: 280px;
  background-color: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-xl);
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
  font-size: var(--font-size-sm);
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

/* Mobile menu toggle */
.menu-toggle {
  display: none;
  width: 40px;
  height: 40px;
  align-items: center;
  justify-content: center;
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition-base);
}

.menu-toggle:hover {
  color: var(--text-primary);
}

/* Responsive */
@media (max-width: 768px) {
  .nav-menu {
    display: none;
  }

  .nav-menu-open {
    display: flex;
    flex-direction: column;
    position: fixed;
    top: 72px;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: var(--bg-primary);
    padding: var(--spacing-4);
    gap: var(--spacing-4);
  }

  .menu-toggle {
    display: flex;
  }

  .header-actions {
    gap: var(--spacing-2);
  }

  .credits-display {
    display: none;
  }

  .btn-outline,
  .btn-primary {
    display: none;
  }

  .nav-menu-open .nav-item {
    font-size: var(--font-size-lg);
    padding: var(--spacing-4);
    border-bottom: 1px solid var(--border-color);
  }

  .user-menu-panel {
    position: fixed;
    top: 72px;
    left: var(--spacing-4);
    right: var(--spacing-4);
    width: auto;
  }
}
</style> 