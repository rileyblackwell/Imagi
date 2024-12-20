<template>
  <div id="app">
    <nav class="header-navbar">
      <div class="nav-container">
        <div class="nav-brand">
          <router-link class="brand-link" to="/">
            <span class="brand-text">Imagi</span>
          </router-link>
        </div>

        <div class="nav-menu">
          <template v-if="isAuthenticated">
            <router-link to="/dashboard" class="nav-link">Dashboard</router-link>
            <router-link to="/dashboard/projects" class="nav-link">Projects</router-link>
            <button @click="handleLogout" class="btn btn-outline">
              <i class="fas fa-sign-out-alt"></i>
              <span>Logout</span>
            </button>
          </template>
          <template v-else>
            <router-link to="/auth/login" class="btn btn-primary">
              <i class="fas fa-sign-in-alt"></i>
              <span>Login</span>
            </router-link>
          </template>
        </div>
      </div>
    </nav>

    <main class="main-content">
      <router-view></router-view>
    </main>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'App',
  
  setup() {
    const store = useStore()
    const router = useRouter()
    
    onMounted(() => {
      // Load Font Awesome
      const fontAwesome = document.createElement('link')
      fontAwesome.rel = 'stylesheet'
      fontAwesome.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'
      document.head.appendChild(fontAwesome)
    })
    
    const isAuthenticated = computed(() => store.getters['auth/isAuthenticated'])
    const currentUser = computed(() => store.getters['auth/currentUser'])
    
    const handleLogout = async () => {
      try {
        await store.dispatch('auth/logout')
        router.push('/auth/login')
      } catch (err) {
        console.error('Logout failed:', err)
      }
    }
    
    return {
      isAuthenticated,
      currentUser,
      handleLogout
    }
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --primary-color: #6366f1;
  --primary-hover: #4f46e5;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --border-color: #e2e8f0;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', sans-serif;
  line-height: 1.5;
  color: var(--text-primary);
  background-color: var(--bg-secondary);
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header-navbar {
  background-color: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-brand {
  display: flex;
  align-items: center;
}

.brand-link {
  text-decoration: none;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.brand-text {
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.nav-link:hover {
  color: var(--primary-color);
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
  border: none;
}

.btn i {
  font-size: 1rem;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background-color: var(--primary-hover);
}

.btn-outline {
  background-color: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.btn-outline:hover {
  background-color: var(--bg-secondary);
}

.main-content {
  flex: 1;
}
</style>
