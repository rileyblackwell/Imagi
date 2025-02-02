<!-- BaseFooter component -->
<template>
  <footer class="bg-gradient-to-b from-dark-900 to-dark-950 border-t border-dark-700/30">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Main Footer Content -->
      <div class="py-8 grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-12">
        <!-- Company Info -->
        <div class="col-span-1 space-y-4">
          <div class="space-y-3">
            <router-link 
              to="/" 
              class="inline-block"
            >
              <span class="text-2xl font-extrabold bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent hover:from-primary-300 hover:to-primary-500 transition-all duration-300">
                Imagi
              </span>
            </router-link>
            <p class="text-gray-400/90 leading-relaxed base font-light">
              Transform your ideas into powerful web applications using natural language with Imagi's AI technology.
            </p>
          </div>
        </div>

        <!-- Quick Links -->
        <div class="col-span-1 flex justify-end">
          <div class="space-y-4">
            <h4 class="text-xs font-semibold text-primary-400/90 uppercase tracking-wider">Quick Links</h4>
            <ul class="space-y-2.5">
              <li class="w-full">
                <router-link 
                  to="/about" 
                  class="group flex items-center text-gray-400/90 hover:text-gray-200 transition-colors duration-150 w-full"
                >
                  <span class="flex items-center min-w-[20px]">
                    <i class="fas fa-chevron-right text-[8px] opacity-0 -translate-x-2 group-hover:opacity-50 group-hover:translate-x-0 transition-all duration-150 ease-out"></i>
                  </span>
                  <span class="text-sm">About Us</span>
                </router-link>
              </li>
              <li class="w-full">
                <router-link 
                  to="/contact" 
                  class="group flex items-center text-gray-400/90 hover:text-gray-200 transition-colors duration-150 w-full"
                >
                  <span class="flex items-center min-w-[20px]">
                    <i class="fas fa-chevron-right text-[8px] opacity-0 -translate-x-2 group-hover:opacity-50 group-hover:translate-x-0 transition-all duration-150 ease-out"></i>
                  </span>
                  <span class="text-sm">Contact</span>
                </router-link>
              </li>
              <li class="w-full">
                <router-link 
                  to="/privacy" 
                  class="group flex items-center text-gray-400/90 hover:text-gray-200 transition-colors duration-150 w-full"
                >
                  <span class="flex items-center min-w-[20px]">
                    <i class="fas fa-chevron-right text-[8px] opacity-0 -translate-x-2 group-hover:opacity-50 group-hover:translate-x-0 transition-all duration-150 ease-out"></i>
                  </span>
                  <span class="text-sm">Privacy Policy</span>
                </router-link>
              </li>
              <li class="w-full">
                <router-link 
                  to="/terms" 
                  class="group flex items-center text-gray-400/90 hover:text-gray-200 transition-colors duration-150 w-full"
                >
                  <span class="flex items-center min-w-[20px]">
                    <i class="fas fa-chevron-right text-[8px] opacity-0 -translate-x-2 group-hover:opacity-50 group-hover:translate-x-0 transition-all duration-150 ease-out"></i>
                  </span>
                  <span class="text-sm">Terms of Service</span>
                </router-link>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Bottom Bar -->
      <div class="py-4 border-t border-dark-700/30">
        <p class="text-gray-400/80 text-xs text-center font-light">
          &copy; {{ currentYear }} Imagi. All rights reserved.
        </p>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'BaseFooter',
  computed: {
    currentYear() {
      return new Date().getFullYear()
    }
  }
}
</script>

<style scoped>
/* No additional styles needed - using Tailwind's utility classes */
</style> 