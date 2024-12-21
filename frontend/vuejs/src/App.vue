<template>
  <div id="app" class="min-h-screen bg-gradient-to-br from-dark-950 via-dark-900 to-dark-950">
    <div class="fixed inset-0 bg-gradient-radial from-primary-500/10 via-transparent to-transparent pointer-events-none"></div>
    
    <!-- Main Content -->
    <main class="relative">
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
                <router-link to="/" class="flex items-center gap-3">
                  <img src="@/shared/assets/images/logo.webp" alt="Imagi Logo" class="h-8 w-auto" />
                  <span class="text-xl font-bold bg-gradient-to-r from-primary-300 to-primary-500 text-transparent bg-clip-text">
                    Imagi
                  </span>
                </router-link>
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
import { useRoute } from 'vue-router'

export default {
  name: 'App',
  setup() {
    const route = useRoute()
    
    const hideFooter = computed(() => {
      return route.meta.hideFooter || false
    })
    
    return {
      hideFooter
    }
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@200..800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@100..800&display=swap');
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');

/* Page Transitions */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* Scrollbar Styling */
::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-track {
  background: theme('colors.dark.900');
}

::-webkit-scrollbar-thumb {
  background: theme('colors.dark.700');
  border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
  background: theme('colors.dark.600');
}

/* Selection Styling */
::selection {
  background: theme('colors.primary.500/30');
  color: theme('colors.primary.100');
}

/* Focus Outline */
*:focus-visible {
  outline: 2px solid theme('colors.primary.500');
  outline-offset: 2px;
}

/* Base Styles */
html {
  scroll-behavior: smooth;
}

body {
  @apply antialiased text-dark-50 bg-dark-950;
  font-feature-settings: "cv02", "cv03", "cv04", "cv11";
}

#app {
  @apply flex flex-col min-h-screen;
}
</style>
