<template>
  <footer class="relative bg-white dark:bg-[#0a0a0a] border-t border-gray-200 dark:border-white/10 transition-colors duration-300">
    <div class="relative max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
      
      <!-- Main footer content -->
      <div class="py-16">
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-8 lg:gap-16">
          
          <!-- Product section -->
          <div>
            <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-4 transition-colors duration-300">
              Product
            </h4>
            <ul class="space-y-3">
              <li>
                <router-link 
                  to="/products/oasis/builder/dashboard" 
                  class="text-sm text-gray-600 dark:text-white/60 hover:text-gray-900 dark:hover:text-white transition-colors duration-200"
                >
                  Imagi
                </router-link>
              </li>
              <li>
                <router-link 
                  to="/payments/pricing" 
                  class="text-sm text-gray-600 dark:text-white/60 hover:text-gray-900 dark:hover:text-white transition-colors duration-200"
                >
                  Pricing
                </router-link>
              </li>
            </ul>
          </div>

          <!-- Resources section -->
          <div>
            <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-4 transition-colors duration-300">
              Resources
            </h4>
            <ul class="space-y-3">
              <li>
                <router-link 
                  to="/docs" 
                  class="text-sm text-gray-600 dark:text-white/60 hover:text-gray-900 dark:hover:text-white transition-colors duration-200"
                >
                  Documentation
                </router-link>
              </li>
            </ul>
          </div>

          <!-- Company section -->
          <div>
            <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-4 transition-colors duration-300">
              Company
            </h4>
            <ul class="space-y-3">
              <li>
                <router-link 
                  to="/about" 
                  class="text-sm text-gray-600 dark:text-white/60 hover:text-gray-900 dark:hover:text-white transition-colors duration-200"
                >
                  About Us
                </router-link>
              </li>
            </ul>
          </div>

          <!-- Legal section -->
          <div>
            <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-4 transition-colors duration-300">
              Legal
            </h4>
            <ul class="space-y-3">
              <li>
                <router-link 
                  to="/privacy" 
                  class="text-sm text-gray-600 dark:text-white/60 hover:text-gray-900 dark:hover:text-white transition-colors duration-200"
                >
                  Privacy Policy
                </router-link>
              </li>
              <li>
                <router-link 
                  to="/terms" 
                  class="text-sm text-gray-600 dark:text-white/60 hover:text-gray-900 dark:hover:text-white transition-colors duration-200"
                >
                  Terms of Service
                </router-link>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Bottom bar -->
      <div class="py-6 border-t border-gray-200 dark:border-white/10 transition-colors duration-300">
        <div class="flex items-center justify-between">
          <p class="text-gray-500 dark:text-white/50 text-sm transition-colors duration-300">
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
