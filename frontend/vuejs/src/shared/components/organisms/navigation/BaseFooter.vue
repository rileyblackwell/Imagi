<template>
  <footer class="crisp-footer relative font-body bg-white dark:bg-[#0a0a0a] border-t border-blue-950/[0.08] dark:border-white/[0.14] transition-colors duration-300">
    <div class="relative max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
      
      <!-- Main footer content -->
      <div class="py-10">
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-8 lg:gap-16">
          
          <!-- Product section -->
          <div>
            <h4 class="text-xs font-semibold uppercase tracking-[0.16em] text-blue-950/70 dark:text-blue-100/55 mb-4 transition-colors duration-300">
              Product
            </h4>
            <ul class="space-y-3">
              <li>
                <router-link 
                  to="/imagi/projects" 
                  class="text-sm rounded-sm text-blue-950/65 dark:text-blue-100/65 hover:text-blue-950 dark:hover:text-white transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
                >
                  Imagi
                </router-link>
              </li>
              <li>
                <router-link 
                  to="/payments/pricing" 
                  class="text-sm rounded-sm text-blue-950/65 dark:text-blue-100/65 hover:text-blue-950 dark:hover:text-white transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
                >
                  Pricing
                </router-link>
              </li>
            </ul>
          </div>

          <!-- Resources section -->
          <div>
            <h4 class="text-xs font-semibold uppercase tracking-[0.16em] text-blue-950/70 dark:text-blue-100/55 mb-4 transition-colors duration-300">
              Resources
            </h4>
            <ul class="space-y-3">
              <li>
                <router-link 
                  to="/docs" 
                  class="text-sm rounded-sm text-blue-950/65 dark:text-blue-100/65 hover:text-blue-950 dark:hover:text-white transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
                >
                  Documentation
                </router-link>
              </li>
            </ul>
          </div>

          <!-- Company section -->
          <div>
            <h4 class="text-xs font-semibold uppercase tracking-[0.16em] text-blue-950/70 dark:text-blue-100/55 mb-4 transition-colors duration-300">
              Company
            </h4>
            <ul class="space-y-3">
              <li>
                <router-link 
                  to="/about" 
                  class="text-sm rounded-sm text-blue-950/65 dark:text-blue-100/65 hover:text-blue-950 dark:hover:text-white transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
                >
                  About Us
                </router-link>
              </li>
            </ul>
          </div>

          <!-- Legal section -->
          <div>
            <h4 class="text-xs font-semibold uppercase tracking-[0.16em] text-blue-950/70 dark:text-blue-100/55 mb-4 transition-colors duration-300">
              Legal
            </h4>
            <ul class="space-y-3">
              <li>
                <router-link 
                  to="/privacy" 
                  class="text-sm rounded-sm text-blue-950/65 dark:text-blue-100/65 hover:text-blue-950 dark:hover:text-white transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
                >
                  Privacy Policy
                </router-link>
              </li>
              <li>
                <router-link 
                  to="/terms" 
                  class="text-sm rounded-sm text-blue-950/65 dark:text-blue-100/65 hover:text-blue-950 dark:hover:text-white transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
                >
                  Terms of Service
                </router-link>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Bottom bar -->
      <div class="py-5 border-t border-blue-950/[0.08] dark:border-white/[0.14] transition-colors duration-300">
        <div class="flex items-center justify-between">
          <p class="text-blue-950/60 dark:text-blue-100/55 text-sm transition-colors duration-300">
            &copy; {{ currentYear }} Imagi. All rights reserved.
          </p>
          
          <ThemeToggle />
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ThemeToggle } from '@/shared/components/atoms'

const currentYear = computed(() => new Date().getFullYear())
</script>

<style scoped>
/* Crisp, sharp text rendering for the footer */
.crisp-footer {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}
</style>
