<template>
  <div class="main-layout">
    <nav class="navbar">
      <div class="navbar-brand">
        <router-link to="/" class="logo-link">
          <img src="@/assets/images/logo.webp" alt="Imagi Logo" class="logo-image" />
          <span class="logo-text">Imagi</span>
        </router-link>
      </div>

      <div class="navbar-menu">
        <template v-if="isAuthenticated">
          <div class="nav-items">
            <div class="dropdown">
              <button class="nav-btn btn-products dropdown-toggle" id="navbarDropdown">
                <i class="fas fa-th"></i> Products
              </button>
              <div class="dropdown-menu">
                <router-link class="dropdown-item" to="/dashboard">
                  <i class="fas fa-magic"></i> Imagi Oasis
                </router-link>
              </div>
            </div>
            <router-link to="/payments/checkout" class="nav-btn btn-credits">
              <i class="fas fa-coins"></i>
              <span>Buy Credits</span>
            </router-link>
            <button @click="logout" class="nav-btn btn-secondary">
              <i class="fas fa-sign-out-alt"></i>
              <span>Logout</span>
            </button>
          </div>
        </template>
        <template v-else>
          <router-link to="/auth/login" class="nav-btn btn-primary">
            <i class="fas fa-sign-in-alt"></i>
            <span>Login</span>
          </router-link>
        </template>
      </div>
    </nav>

    <router-view></router-view>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'MainLayout',
  
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const isAuthenticated = computed(() => store.state.auth.isAuthenticated)
    
    const logout = async () => {
      await store.dispatch('auth/logout')
      router.push('/')
    }
    
    return {
      isAuthenticated,
      logout
    }
  }
}
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  @apply fixed top-0 left-0 right-0 z-50 px-6 py-4 flex items-center justify-between
         bg-gray-900/80 backdrop-blur-md border-b border-gray-800;
}

.navbar-brand {
  @apply flex items-center;
}

.logo-link {
  @apply flex items-center gap-3 text-white hover:opacity-90 transition-opacity;
}

.logo-image {
  @apply h-8 w-auto;
}

.logo-text {
  @apply text-xl font-bold bg-gradient-to-r from-primary-300 to-primary-500 
         text-transparent bg-clip-text;
}

.navbar-menu {
  @apply flex items-center gap-4;
}

.nav-items {
  @apply flex items-center gap-4;
}

.nav-btn {
  @apply inline-flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all duration-200
         hover:transform hover:scale-105;
}

.btn-products {
  @apply bg-gray-800/50 text-white border border-gray-700 hover:bg-gray-700/50;
}

.btn-credits {
  @apply bg-gradient-to-r from-green-500 to-green-600 text-white
         hover:from-green-400 hover:to-green-500;
}

.btn-primary {
  @apply bg-gradient-to-r from-primary-500 to-primary-600 text-white
         hover:from-primary-400 hover:to-primary-500
         shadow-lg hover:shadow-primary-500/25;
}

.btn-secondary {
  @apply bg-gray-800/50 text-white border border-gray-700
         hover:bg-gray-700/50;
}

.dropdown {
  @apply relative;
}

.dropdown-menu {
  @apply absolute right-0 mt-2 w-48 py-2 bg-gray-800 rounded-lg shadow-xl border border-gray-700
         invisible opacity-0 translate-y-2 transition-all duration-200;
}

.dropdown:hover .dropdown-menu {
  @apply visible opacity-100 translate-y-0;
}

.dropdown-item {
  @apply flex items-center gap-2 px-4 py-2 text-gray-300 hover:text-white hover:bg-gray-700/50
         transition-colors;
}

/* Responsive styles */
@media (max-width: 768px) {
  .navbar {
    @apply px-4;
  }

  .nav-items {
    @apply hidden;
  }

  .navbar-menu {
    @apply gap-2;
  }

  .nav-btn {
    @apply px-3 py-2 text-sm;
  }

  .logo-text {
    @apply text-lg;
  }
}
</style>
