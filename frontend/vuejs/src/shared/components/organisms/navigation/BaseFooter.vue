<template>
  <footer class="relative bg-[#050508] border-t border-white/[0.06] overflow-hidden">
    <!-- Background effects -->
    <div class="absolute inset-0 pointer-events-none">
      <!-- Subtle gradient mesh -->
      <div class="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,rgba(120,119,198,0.08),transparent_50%)]"></div>
      <div class="absolute inset-0 bg-[radial-gradient(ellipse_60%_40%_at_80%_80%,rgba(78,68,206,0.05),transparent_40%)]"></div>
      
      <!-- Subtle grain texture -->
      <div class="absolute inset-0 opacity-[0.015]" style="background-image: url('data:image/svg+xml,%3Csvg viewBox=%220 0 256 256%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noise%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.8%22 numOctaves=%224%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noise)%22/%3E%3C/svg%3E');"></div>
      
      <!-- Floating orb -->
      <div class="absolute bottom-0 left-[20%] w-[400px] h-[400px] rounded-full bg-gradient-to-tr from-violet-600/6 to-fuchsia-600/3 blur-[100px]"></div>
    </div>

    <div class="relative max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
      <!-- Main footer content -->
      <div class="py-12 sm:py-16 grid grid-cols-1 md:grid-cols-12 gap-8 md:gap-12">
        <!-- Brand section -->
        <div class="md:col-span-5 space-y-6">
          <div class="space-y-4">
            <ImagiLogo size="md" />
            <p class="text-white/50 leading-relaxed text-sm max-w-sm">
              Transform your ideas into powerful web applications using natural language with Imagi's AI technology.
            </p>
          </div>
          
          <!-- Social links placeholder - can be expanded later -->
          <div class="flex items-center gap-3">
            <a 
              href="#" 
              class="group flex items-center justify-center w-9 h-9 rounded-lg bg-white/[0.03] border border-white/[0.06] hover:bg-white/[0.06] hover:border-white/[0.12] transition-all duration-300"
              aria-label="Twitter"
            >
              <i class="fab fa-twitter text-white/40 group-hover:text-white/70 transition-colors duration-300 text-sm"></i>
            </a>
            <a 
              href="#" 
              class="group flex items-center justify-center w-9 h-9 rounded-lg bg-white/[0.03] border border-white/[0.06] hover:bg-white/[0.06] hover:border-white/[0.12] transition-all duration-300"
              aria-label="GitHub"
            >
              <i class="fab fa-github text-white/40 group-hover:text-white/70 transition-colors duration-300 text-sm"></i>
            </a>
            <a 
              href="#" 
              class="group flex items-center justify-center w-9 h-9 rounded-lg bg-white/[0.03] border border-white/[0.06] hover:bg-white/[0.06] hover:border-white/[0.12] transition-all duration-300"
              aria-label="Discord"
            >
              <i class="fab fa-discord text-white/40 group-hover:text-white/70 transition-colors duration-300 text-sm"></i>
            </a>
          </div>
        </div>

        <!-- Links sections -->
        <div class="md:col-span-7 grid grid-cols-2 sm:grid-cols-3 gap-8">
          <!-- Learn section -->
          <div class="space-y-4">
            <h4 class="text-xs font-semibold text-white/90 uppercase tracking-wider">
              Learn
            </h4>
            <ul class="space-y-3">
              <li>
                <router-link 
                  to="/docs" 
                  class="group inline-flex items-center gap-2 text-sm text-white/50 hover:text-white/90 transition-colors duration-300"
                >
                  <span class="w-0 group-hover:w-1 h-1 rounded-full bg-violet-400 transition-all duration-300"></span>
                  <span>Documentation</span>
                </router-link>
              </li>
              <li>
                <router-link 
                  to="/about" 
                  class="group inline-flex items-center gap-2 text-sm text-white/50 hover:text-white/90 transition-colors duration-300"
                >
                  <span class="w-0 group-hover:w-1 h-1 rounded-full bg-violet-400 transition-all duration-300"></span>
                  <span>About Us</span>
                </router-link>
              </li>
              <li>
                <router-link 
                  to="/contact" 
                  class="group inline-flex items-center gap-2 text-sm text-white/50 hover:text-white/90 transition-colors duration-300"
                >
                  <span class="w-0 group-hover:w-1 h-1 rounded-full bg-violet-400 transition-all duration-300"></span>
                  <span>Contact</span>
                </router-link>
              </li>
            </ul>
          </div>

          <!-- Legal section -->
          <div class="space-y-4">
            <h4 class="text-xs font-semibold text-white/90 uppercase tracking-wider">
              Legal
            </h4>
            <ul class="space-y-3">
              <li>
                <router-link 
                  to="/privacy" 
                  class="group inline-flex items-center gap-2 text-sm text-white/50 hover:text-white/90 transition-colors duration-300"
                >
                  <span class="w-0 group-hover:w-1 h-1 rounded-full bg-violet-400 transition-all duration-300"></span>
                  <span>Privacy Policy</span>
                </router-link>
              </li>
              <li>
                <router-link 
                  to="/terms" 
                  class="group inline-flex items-center gap-2 text-sm text-white/50 hover:text-white/90 transition-colors duration-300"
                >
                  <span class="w-0 group-hover:w-1 h-1 rounded-full bg-violet-400 transition-all duration-300"></span>
                  <span>Terms of Service</span>
                </router-link>
              </li>
            </ul>
          </div>

          <!-- Product section -->
          <div class="space-y-4">
            <h4 class="text-xs font-semibold text-white/90 uppercase tracking-wider">
              Product
            </h4>
            <ul class="space-y-3">
              <li>
                <router-link 
                  to="/products/oasis/builder/dashboard" 
                  class="group inline-flex items-center gap-2 text-sm text-white/50 hover:text-white/90 transition-colors duration-300"
                >
                  <span class="w-0 group-hover:w-1 h-1 rounded-full bg-violet-400 transition-all duration-300"></span>
                  <span>Oasis Builder</span>
                </router-link>
              </li>
              <li>
                <router-link 
                  to="/payments/checkout" 
                  class="group inline-flex items-center gap-2 text-sm text-white/50 hover:text-white/90 transition-colors duration-300"
                >
                  <span class="w-0 group-hover:w-1 h-1 rounded-full bg-violet-400 transition-all duration-300"></span>
                  <span>Pricing</span>
                </router-link>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Bottom bar -->
      <div class="relative py-6 border-t border-white/[0.06]">
        <!-- Top accent line -->
        <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-500/30 to-transparent"></div>
        
        <div class="flex items-center justify-center">
          <p class="text-white/40 text-xs font-light">
            &copy; {{ currentYear }} Imagi. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ImagiLogo } from '@/shared/components/molecules'

const currentYear = computed(() => new Date().getFullYear())
</script>

<style scoped>
/* Animations matching homepage */
@keyframes float-slow {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -20px) scale(1.02);
  }
  66% {
    transform: translate(-20px, 10px) scale(0.98);
  }
}

.animate-float-slow {
  animation: float-slow 25s ease-in-out infinite;
}
</style>
