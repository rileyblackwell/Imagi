<template>
  <div class="min-h-screen bg-dark-900">
    <!-- Navbar -->
    <nav class="fixed top-0 left-0 right-0 z-50 bg-dark-900/80 backdrop-blur-lg border-b border-dark-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <router-link to="/" class="flex items-center space-x-2">
            <img src="@/shared/assets/images/logo.webp" alt="Imagi Logo" class="h-8 w-auto" />
            <span class="text-xl font-bold text-white">Imagi</span>
          </router-link>

          <!-- Navigation Links -->
          <div class="hidden md:flex items-center space-x-8">
            <slot name="navbar-links">
              <!-- Default navigation links -->
              <template v-if="isAuthenticated">
                <div class="relative group">
                  <button class="home-nav-btn flex items-center space-x-1">
                    <i class="fas fa-th"></i>
                    <span>Products</span>
                  </button>
                  <div class="absolute left-0 mt-2 w-48 rounded-lg bg-dark-800 border border-dark-700 shadow-lg opacity-0 group-hover:opacity-100 transform group-hover:translate-y-0 translate-y-2 transition-all duration-200">
                    <router-link to="/builder" class="block px-4 py-2 text-sm text-gray-300 hover:bg-dark-700">
                      <i class="fas fa-magic mr-2"></i>
                      Imagi Oasis
                    </router-link>
                  </div>
                </div>
                <router-link to="/payments/credits" class="home-nav-btn">
                  <i class="fas fa-coins mr-1"></i>
                  <span>Buy Credits</span>
                </router-link>
              </template>
            </slot>
          </div>

          <!-- Auth Buttons -->
          <div class="flex items-center space-x-4">
            <slot name="auth-buttons">
              <!-- Default auth buttons -->
              <template v-if="isAuthenticated">
                <button @click="logout" class="home-nav-btn">
                  <i class="fas fa-sign-out-alt mr-1"></i>
                  <span>Logout</span>
                </button>
              </template>
              <template v-else>
                <router-link to="/auth/login" class="home-nav-btn">
                  <i class="fas fa-sign-in-alt mr-1"></i>
                  <span>Login</span>
                </router-link>
              </template>
            </slot>
          </div>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="relative pt-32 overflow-hidden">
      <slot name="hero">
        <!-- Default hero content -->
      </slot>
    </section>

    <!-- Main Content -->
    <main>
      <slot></slot>
    </main>

    <!-- Footer -->
    <footer class="bg-dark-800 border-t border-dark-700">
      <div class="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <slot name="footer">
          <!-- Default footer content -->
          <div class="text-center text-gray-400">
            <p>&copy; {{ new Date().getFullYear() }} Imagi. All rights reserved.</p>
          </div>
        </slot>
      </div>
    </footer>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'BaseLayout',
  setup() {
    const authStore = useAuthStore()

    return {
      isAuthenticated: computed(() => authStore.isAuthenticated),
      logout: () => authStore.logout()
    }
  }
}
</script>

<style>
.home-nav-btn {
  @apply inline-flex items-center px-4 py-2 text-sm font-medium text-gray-300 rounded-lg 
         bg-dark-800 hover:bg-dark-700 hover:text-white transition-colors;
}

.home-nav-btn i {
  @apply text-primary-400;
}
</style> 