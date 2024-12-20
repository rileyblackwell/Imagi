<template>
  <nav class="header-navbar navbar">
    <div class="global-container">
      <div class="navbar-header">
        <router-link class="header-brand" to="/">
          <div class="header-logo-placeholder"></div>
          <span class="header-brand-highlight">Imagi</span>
        </router-link>
      </div>

      <!-- Navigation -->
      <nav class="home-nav-buttons">
        <ul class="home-nav-list">
          <template v-if="isAuthenticated">
            <li class="home-nav-item dropdown">
              <button class="home-nav-btn btn-products dropdown-toggle" @click="toggleProductsMenu">
                <i class="fas fa-th"></i> Products
              </button>
              <div v-if="showProductsMenu" class="home-dropdown-menu">
                <router-link to="/builder" class="home-dropdown-btn">
                  <i class="fas fa-magic"></i> Imagi Oasis
                </router-link>
              </div>
            </li>
            <li class="home-nav-item">
              <router-link to="/payments" class="btn btn-success">
                <i class="fas fa-coins"></i>
                <span>Buy Credits</span>
              </router-link>
            </li>
            <li class="home-nav-item">
              <button @click="handleLogout" class="btn btn-secondary">
                <i class="fas fa-sign-out-alt"></i>
                <span>Logout</span>
              </button>
            </li>
          </template>
          <template v-else>
            <li class="home-nav-item">
              <router-link to="/auth/login" class="btn btn-primary">
                <i class="fas fa-sign-in-alt"></i>
                <span>Login</span>
              </router-link>
            </li>
          </template>
        </ul>
      </nav>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { isAuthenticated, logout } = useAuth()

const showProductsMenu = ref(false)

function toggleProductsMenu() {
  showProductsMenu.value = !showProductsMenu.value
}

async function handleLogout() {
  try {
    await logout()
    router.push('/auth/login')
  } catch (err) {
    console.error('Logout failed:', err)
  }
}
</script>

<style scoped>
.header-navbar {
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
}

.global-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.navbar-header {
  display: flex;
  align-items: center;
}

.header-brand {
  display: flex;
  align-items: center;
  text-decoration: none;
  gap: 0.5rem;
}

.header-logo-placeholder {
  width: 32px;
  height: 32px;
  background: var(--primary-gradient);
  border-radius: 8px;
}

.header-brand-highlight {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Navigation */
.home-nav-buttons {
  margin-left: auto;
}

.home-nav-list {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 16px;
  align-items: center;
}

.home-nav-item {
  position: relative;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s;
  text-decoration: none;
  border: none;
  cursor: pointer;
}

.btn-products {
  background: rgba(255, 255, 255, 0.03);
  color: var(--text-primary);
  border: none;
}

.btn-success {
  background: var(--primary-gradient);
  color: white;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

.btn-primary {
  background: var(--primary-gradient);
  color: white;
}

.btn:hover {
  transform: translateY(-1px);
}

/* Dropdown */
.home-dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  min-width: 200px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 0.5rem;
  margin-top: 0.5rem;
  box-shadow: var(--shadow-lg);
}

.home-dropdown-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  color: var(--text-primary);
  text-decoration: none;
  border-radius: 6px;
  transition: all 0.2s;
}

.home-dropdown-btn:hover {
  background: rgba(255, 255, 255, 0.05);
}

@media (max-width: 768px) {
  .home-nav-list {
    gap: 8px;
  }

  .btn {
    padding: 0.5rem;
  }

  .btn span {
    display: none;
  }
}
</style> 