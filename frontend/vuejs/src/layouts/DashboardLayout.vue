<template>
  <MainLayout>
    <div class="dashboard-layout">
      <!-- Sidebar -->
      <aside class="dashboard-sidebar" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
        <div class="sidebar-header">
          <button class="collapse-btn" @click="toggleSidebar">
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
          >
            <i :class="item.icon"></i>
            <span v-if="!isSidebarCollapsed" class="nav-label">{{ item.label }}</span>
          </router-link>
        </nav>
      </aside>

      <!-- Main Content -->
      <main class="dashboard-content">
        <router-view />
      </main>
    </div>
  </MainLayout>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import MainLayout from './MainLayout.vue'

const route = useRoute()
const isSidebarCollapsed = ref(false)

const navigationItems = [
  { path: '/dashboard', label: 'Dashboard', icon: 'fas fa-home' },
  { path: '/dashboard/projects', label: 'Projects', icon: 'fas fa-project-diagram' },
  { path: '/dashboard/settings', label: 'Settings', icon: 'fas fa-cog' },
  { path: '/dashboard/billing', label: 'Billing', icon: 'fas fa-credit-card' }
]

function isCurrentRoute(path) {
  return route.path === path
}

function toggleSidebar() {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: calc(100vh - var(--header-height) - var(--footer-height));
}

.dashboard-sidebar {
  width: 240px;
  background: var(--color-background);
  border-right: 1px solid var(--color-border);
  transition: width 0.3s ease;
}

.sidebar-collapsed {
  width: 64px;
}

.sidebar-header {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 var(--spacing-sm);
  border-bottom: 1px solid var(--color-border);
}

.collapse-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: var(--border-radius-sm);
  transition: all 0.2s;
}

.collapse-btn:hover {
  background: var(--color-background-alt);
  color: var(--color-text);
}

.sidebar-nav {
  padding: var(--spacing-md) 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: all 0.2s;
  gap: var(--spacing-sm);
}

.nav-item:hover {
  background: var(--color-background-alt);
  color: var(--color-text);
}

.nav-item.active {
  background: var(--color-primary-light);
  color: var(--color-primary);
}

.nav-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dashboard-content {
  flex: 1;
  padding: var(--spacing-lg);
  background: var(--color-background-alt);
  overflow-y: auto;
}

@media (max-width: 768px) {
  .dashboard-sidebar {
    position: fixed;
    left: 0;
    top: var(--header-height);
    bottom: 0;
    z-index: var(--z-drawer);
    transform: translateX(-100%);
  }

  .sidebar-collapsed {
    transform: translateX(0);
  }

  .dashboard-content {
    margin-left: 0;
  }
}
</style> 