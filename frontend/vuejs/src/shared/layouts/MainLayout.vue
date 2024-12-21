<template>
  <div class="min-h-screen flex flex-col">
    <!-- Navigation -->
    <nav class="fixed top-0 left-0 right-0 z-50 bg-dark-950/80 backdrop-blur-lg border-b border-dark-800">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <router-link to="/" class="flex items-center gap-3">
            <img src="@/shared/assets/images/logo.webp" alt="Imagi Logo" class="h-8 w-8 object-contain" />
            <span class="text-xl font-bold bg-gradient-to-r from-primary-300 to-primary-500 text-transparent bg-clip-text">
              Imagi
            </span>
          </router-link>

          <!-- Navigation Links -->
          <div class="hidden md:flex items-center gap-6">
            <router-link 
              v-for="link in navigationLinks"
              :key="link.to"
              :to="link.to"
              class="text-gray-300 hover:text-primary-400 transition-colors"
            >
              {{ link.text }}
            </router-link>
          </div>

          <!-- Auth Buttons -->
          <div class="flex items-center gap-4">
            <template v-if="isAuthenticated">
              <router-link 
                to="/dashboard" 
                class="text-gray-300 hover:text-primary-400 transition-colors"
              >
                Dashboard
              </router-link>
              <button 
                @click="handleLogout" 
                class="text-gray-300 hover:text-primary-400 transition-colors"
              >
                Logout
              </button>
            </template>
            <template v-else>
              <router-link 
                to="/auth/login"
                class="text-gray-300 hover:text-primary-400 transition-colors"
              >
                Sign In
              </router-link>
              <router-link 
                to="/auth/register"
                class="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors"
              >
                Get Started
              </router-link>
            </template>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="min-h-screen pt-16">
      <router-view v-slot="{ Component }">
        <transition 
          name="page" 
          mode="out-in"
          appear
        >
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- Footer -->
    <footer v-if="!hideFooter" class="relative mt-auto">
      <div class="absolute inset-0 bg-gradient-to-t from-dark-950 to-transparent pointer-events-none"></div>
      
      <div class="container mx-auto px-4 py-8 relative">
        <div class="max-w-7xl mx-auto">
          <!-- Footer Content -->
          <div class="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <!-- Brand -->
            <div class="space-y-4">
              <div class="flex items-center gap-3">
                <img src="@/shared/assets/images/logo.webp" alt="Imagi Logo" class="h-8 w-auto" />
                <span class="text-xl font-bold bg-gradient-to-r from-primary-300 to-primary-500 text-transparent bg-clip-text">
                  Imagi
                </span>
              </div>
              <p class="text-dark-400 text-sm">
                Build amazing web applications with natural language
              </p>
            </div>

            <!-- Product -->
            <div>
              <h3 class="text-sm font-semibold text-dark-200 uppercase tracking-wider mb-4">Product</h3>
              <ul class="space-y-3">
                <li>
                  <router-link to="/features" class="text-dark-400 hover:text-primary-400 transition-colors text-sm">
                    Features
                  </router-link>
                </li>
                <li>
                  <router-link to="/pricing" class="text-dark-400 hover:text-primary-400 transition-colors text-sm">
                    Pricing
                  </router-link>
                </li>
                <li>
                  <router-link to="/docs" class="text-dark-400 hover:text-primary-400 transition-colors text-sm">
                    Documentation
                  </router-link>
                </li>
              </ul>
            </div>

            <!-- Company -->
            <div>
              <h3 class="text-sm font-semibold text-dark-200 uppercase tracking-wider mb-4">Company</h3>
              <ul class="space-y-3">
                <li>
                  <router-link to="/about" class="text-dark-400 hover:text-primary-400 transition-colors text-sm">
                    About
                  </router-link>
                </li>
                <li>
                  <router-link to="/blog" class="text-dark-400 hover:text-primary-400 transition-colors text-sm">
                    Blog
                  </router-link>
                </li>
                <li>
                  <router-link to="/careers" class="text-dark-400 hover:text-primary-400 transition-colors text-sm">
                    Careers
                  </router-link>
                </li>
              </ul>
            </div>

            <!-- Legal -->
            <div>
              <h3 class="text-sm font-semibold text-dark-200 uppercase tracking-wider mb-4">Legal</h3>
              <ul class="space-y-3">
                <li>
                  <router-link to="/privacy" class="text-dark-400 hover:text-primary-400 transition-colors text-sm">
                    Privacy
                  </router-link>
                </li>
                <li>
                  <router-link to="/terms" class="text-dark-400 hover:text-primary-400 transition-colors text-sm">
                    Terms
                  </router-link>
                </li>
                <li>
                  <router-link to="/cookies" class="text-dark-400 hover:text-primary-400 transition-colors text-sm">
                    Cookie Policy
                  </router-link>
                </li>
              </ul>
            </div>
          </div>

          <!-- Bottom Bar -->
          <div class="border-t border-dark-800 pt-8">
            <div class="flex flex-col md:flex-row justify-between items-center gap-4">
              <p class="text-dark-400 text-sm">
                &copy; {{ new Date().getFullYear() }} Imagi. All rights reserved.
              </p>
              <div class="flex items-center space-x-6">
                <a href="https://twitter.com/imagiai" target="_blank" rel="noopener noreferrer" class="text-dark-400 hover:text-primary-400 transition-colors">
                  <span class="sr-only">Twitter</span>
                  <i class="fab fa-twitter text-lg"></i>
                </a>
                <a href="https://github.com/imagiai" target="_blank" rel="noopener noreferrer" class="text-dark-400 hover:text-primary-400 transition-colors">
                  <span class="sr-only">GitHub</span>
                  <i class="fab fa-github text-lg"></i>
                </a>
                <a href="https://discord.gg/imagiai" target="_blank" rel="noopener noreferrer" class="text-dark-400 hover:text-primary-400 transition-colors">
                  <span class="sr-only">Discord</span>
                  <i class="fab fa-discord text-lg"></i>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AuthService from '@/apps/auth/services/auth.service'

export default {
  name: 'MainLayout',
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    const navigationLinks = [
      { to: '/features', text: 'Features' },
      { to: '/pricing', text: 'Pricing' },
      { to: '/docs', text: 'Documentation' },
      { to: '/about', text: 'About' },
    ]

    const isAuthenticated = computed(() => {
      return !!localStorage.getItem('token')
    })

    const hideFooter = computed(() => {
      return route.meta.hideFooter || false
    })

    const handleLogout = async () => {
      try {
        AuthService.logout()
        await router.push('/auth/login')
      } catch (error) {
        console.error('Logout error:', error)
      }
    }

    return {
      navigationLinks,
      isAuthenticated,
      hideFooter,
      handleLogout
    }
  }
}
</script>
