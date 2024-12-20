<template>
  <div class="dashboard-layout">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
      <div class="sidebar-header">
        <router-link to="/" class="brand">
          <span v-if="!isSidebarCollapsed" class="brand-highlight">Imagi</span>
          <span v-else class="brand-icon">I</span>
        </router-link>
        <button class="sidebar-toggle" @click="toggleSidebar">
          <i :class="isSidebarCollapsed ? 'fas fa-chevron-right' : 'fas fa-chevron-left'"></i>
        </button>
      </div>

      <nav class="sidebar-nav">
        <router-link 
          to="/dashboard" 
          class="nav-item"
          :class="{ active: $route.path === '/dashboard' }"
        >
          <i class="fas fa-home"></i>
          <span v-if="!isSidebarCollapsed">Dashboard</span>
        </router-link>

        <router-link 
          to="/dashboard/projects" 
          class="nav-item"
          :class="{ active: $route.path.startsWith('/dashboard/projects') }"
        >
          <i class="fas fa-project-diagram"></i>
          <span v-if="!isSidebarCollapsed">Projects</span>
        </router-link>

        <router-link 
          to="/dashboard/profile" 
          class="nav-item"
          :class="{ active: $route.path === '/dashboard/profile' }"
        >
          <i class="fas fa-user"></i>
          <span v-if="!isSidebarCollapsed">Profile</span>
        </router-link>
      </nav>
    </aside>

    <!-- Main Content -->
    <div class="dashboard-content">
      <!-- Top Navigation -->
      <header class="top-nav">
        <div class="search-bar">
          <i class="fas fa-search"></i>
          <input 
            type="text" 
            placeholder="Search..." 
            v-model="searchQuery"
            @input="handleSearch"
          >
        </div>

        <div class="top-nav-right">
          <button class="notification-btn" @click="toggleNotifications">
            <i class="fas fa-bell"></i>
            <span v-if="unreadNotifications" class="notification-badge">
              {{ unreadNotifications }}
            </span>
          </button>

          <div class="user-menu" ref="userMenu">
            <button class="user-menu-btn" @click="toggleUserMenu">
              <img 
                :src="user?.avatar || '/default-avatar.png'" 
                :alt="user?.name"
                class="user-avatar"
              >
              <span v-if="user?.name" class="user-name">{{ user.name }}</span>
              <i class="fas fa-chevron-down"></i>
            </button>

            <div v-if="isUserMenuOpen" class="user-menu-dropdown">
              <router-link to="/dashboard/profile" class="menu-item">
                <i class="fas fa-user"></i>
                Profile
              </router-link>
              <router-link to="/dashboard/settings" class="menu-item">
                <i class="fas fa-cog"></i>
                Settings
              </router-link>
              <div class="menu-divider"></div>
              <button @click="handleLogout" class="menu-item text-danger">
                <i class="fas fa-sign-out-alt"></i>
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <main class="page-content">
        <router-view></router-view>
      </main>
    </div>

    <!-- Notifications Panel -->
    <div 
      v-if="showNotifications" 
      class="notifications-panel"
      ref="notificationsPanel"
    >
      <div class="notifications-header">
        <h3>Notifications</h3>
        <button @click="markAllAsRead" class="mark-all-btn">
          Mark all as read
        </button>
      </div>

      <div class="notifications-list">
        <div 
          v-for="notification in notifications" 
          :key="notification.id"
          class="notification-item"
          :class="{ unread: !notification.read }"
        >
          <div class="notification-icon">
            <i :class="notification.icon"></i>
          </div>
          <div class="notification-content">
            <p class="notification-text">{{ notification.message }}</p>
            <span class="notification-time">{{ formatTime(notification.time) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import { formatDistanceToNow } from 'date-fns'

export default {
  name: 'DashboardLayout',
  data() {
    return {
      isSidebarCollapsed: false,
      searchQuery: '',
      isUserMenuOpen: false,
      showNotifications: false,
      notifications: [
        {
          id: 1,
          message: 'Your project "Landing Page" has been created',
          time: new Date(),
          icon: 'fas fa-plus-circle text-success',
          read: false
        },
        {
          id: 2,
          message: 'New comment on "E-commerce Site"',
          time: new Date(Date.now() - 3600000),
          icon: 'fas fa-comment text-primary',
          read: false
        }
      ]
    }
  },
  computed: {
    ...mapGetters({
      user: 'auth/user'
    }),
    unreadNotifications() {
      return this.notifications.filter(n => !n.read).length
    }
  },
  methods: {
    ...mapActions({
      logout: 'auth/logout'
    }),
    toggleSidebar() {
      this.isSidebarCollapsed = !this.isSidebarCollapsed
    },
    toggleUserMenu() {
      this.isUserMenuOpen = !this.isUserMenuOpen
      if (this.isUserMenuOpen) {
        this.showNotifications = false
      }
    },
    toggleNotifications() {
      this.showNotifications = !this.showNotifications
      if (this.showNotifications) {
        this.isUserMenuOpen = false
      }
    },
    handleSearch() {
      // Implement search functionality
      console.log('Searching for:', this.searchQuery)
    },
    async handleLogout() {
      try {
        await this.logout()
        this.$router.push('/auth/login')
      } catch (error) {
        console.error('Logout failed:', error)
      }
    },
    markAllAsRead() {
      this.notifications = this.notifications.map(n => ({ ...n, read: true }))
    },
    formatTime(date) {
      try {
        return formatDistanceToNow(new Date(date), { addSuffix: true })
      } catch (error) {
        console.error('Date formatting error:', error)
        return ''
      }
    }
  },
  mounted() {
    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
      if (this.$refs.userMenu && !this.$refs.userMenu.contains(e.target)) {
        this.isUserMenuOpen = false
      }
      if (this.$refs.notificationsPanel && !this.$refs.notificationsPanel.contains(e.target)) {
        this.showNotifications = false
      }
    })
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside)
  }
}
</script>

<style scoped>
.dashboard-layout {
  min-height: 100vh;
  display: flex;
}

/* Sidebar */
.sidebar {
  width: 260px;
  background: white;
  border-right: 1px solid #e2e8f0;
  transition: width 0.3s ease;
  display: flex;
  flex-direction: column;
}

.sidebar-collapsed {
  width: 80px;
}

.sidebar-header {
  padding: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e2e8f0;
}

.brand {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2d3748;
  text-decoration: none;
}

.brand-highlight {
  color: #6366f1;
}

.brand-icon {
  color: #6366f1;
  font-weight: 900;
}

.sidebar-toggle {
  background: none;
  border: none;
  color: #718096;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.375rem;
  transition: background-color 0.2s;
}

.sidebar-toggle:hover {
  background-color: #f7fafc;
}

.sidebar-nav {
  padding: 1rem 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  color: #4a5568;
  text-decoration: none;
  transition: background-color 0.2s;
}

.nav-item i {
  font-size: 1.25rem;
  margin-right: 1rem;
  width: 1.5rem;
  text-align: center;
}

.nav-item:hover {
  background-color: #f7fafc;
}

.nav-item.active {
  background-color: #ebf4ff;
  color: #6366f1;
}

/* Main Content */
.dashboard-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #f8fafc;
}

/* Top Navigation */
.top-nav {
  background: white;
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e2e8f0;
}

.search-bar {
  display: flex;
  align-items: center;
  background: #f7fafc;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  width: 300px;
}

.search-bar i {
  color: #a0aec0;
  margin-right: 0.5rem;
}

.search-bar input {
  border: none;
  background: none;
  outline: none;
  width: 100%;
  color: #4a5568;
}

.top-nav-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.notification-btn {
  background: none;
  border: none;
  color: #718096;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.375rem;
  position: relative;
}

.notification-badge {
  position: absolute;
  top: 0;
  right: 0;
  background: #e53e3e;
  color: white;
  font-size: 0.75rem;
  padding: 0.125rem 0.375rem;
  border-radius: 1rem;
}

.user-menu {
  position: relative;
}

.user-menu-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  padding: 0.5rem;
  cursor: pointer;
  border-radius: 0.375rem;
}

.user-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  object-fit: cover;
}

.user-name {
  color: #2d3748;
  font-weight: 500;
}

.user-menu-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  min-width: 200px;
  margin-top: 0.5rem;
  z-index: 50;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: #4a5568;
  text-decoration: none;
  transition: background-color 0.2s;
}

.menu-item:hover {
  background-color: #f7fafc;
}

.menu-item i {
  width: 1rem;
}

.menu-divider {
  height: 1px;
  background-color: #e2e8f0;
  margin: 0.5rem 0;
}

.text-danger {
  color: #e53e3e;
}

/* Notifications Panel */
.notifications-panel {
  position: fixed;
  top: 4rem;
  right: 1.5rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  width: 400px;
  max-height: 80vh;
  overflow-y: auto;
  z-index: 50;
}

.notifications-header {
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e2e8f0;
}

.notifications-header h3 {
  margin: 0;
  font-size: 1.125rem;
  color: #2d3748;
}

.mark-all-btn {
  background: none;
  border: none;
  color: #6366f1;
  font-size: 0.875rem;
  cursor: pointer;
}

.notifications-list {
  padding: 0.5rem;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  border-radius: 0.375rem;
  transition: background-color 0.2s;
}

.notification-item:hover {
  background-color: #f7fafc;
}

.notification-item.unread {
  background-color: #ebf8ff;
}

.notification-icon {
  padding: 0.5rem;
  border-radius: 50%;
  background: #f7fafc;
}

.notification-content {
  flex: 1;
}

.notification-text {
  margin: 0;
  color: #4a5568;
}

.notification-time {
  font-size: 0.875rem;
  color: #a0aec0;
}

/* Page Content */
.page-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    height: 100vh;
    z-index: 40;
    transform: translateX(-100%);
  }

  .sidebar-collapsed {
    transform: translateX(0);
  }

  .search-bar {
    display: none;
  }
}
</style> 