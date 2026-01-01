<template>
  <!-- CTA Section - Premium Design matching homepage -->
  <div class="py-8 mt-8">
    <div class="group relative">
      <!-- Background glow -->
      <div class="absolute -inset-1 bg-gradient-to-r from-violet-600/20 via-fuchsia-600/20 to-violet-600/20 rounded-3xl blur-xl opacity-50 group-hover:opacity-70 transition-opacity duration-500"></div>
      
      <!-- Card content -->
      <div class="relative p-8 md:p-10 rounded-2xl border border-white/[0.08] bg-[#0a0a0f]/80 backdrop-blur-xl overflow-hidden">
        <!-- Accent line -->
        <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-500/50 to-transparent"></div>
        
        <!-- Content layout -->
        <div class="flex flex-col md:flex-row items-start gap-6">
          <!-- Icon -->
          <div class="flex-shrink-0">
            <div class="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 border border-violet-500/20">
              <i :class="icon" class="text-violet-400 text-xl"></i>
            </div>
          </div>
          
          <!-- Text content -->
          <div class="flex-1">
            <h2 class="text-2xl md:text-3xl font-semibold text-white/90 mb-4 leading-tight">
              <span class="bg-gradient-to-r from-violet-400 to-fuchsia-400 bg-clip-text text-transparent">{{ title }}</span>
            </h2>
            
            <p class="text-base md:text-lg text-white/50 mb-8 leading-relaxed max-w-xl">
              {{ description }}
            </p>
            
            <!-- Primary Button - matching homepage CTA style -->
            <router-link 
              :to="buttonLink"
              class="group/btn inline-flex items-center justify-center gap-2 px-7 py-3.5 bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-xl text-white font-medium shadow-lg shadow-violet-500/25 hover:shadow-xl hover:shadow-violet-500/30 transition-all duration-300 hover:-translate-y-0.5"
            >
              <i :class="buttonIcon"></i>
              <span>{{ buttonText }}</span>
              <i class="fas fa-arrow-right text-sm transform group-hover/btn:translate-x-1 transition-transform duration-300"></i>
            </router-link>
            
            <!-- Subtle tagline -->
            <p class="text-xs text-white/30 mt-4 flex items-center gap-2">
              <i class="fas fa-bolt text-amber-400/60 text-[10px]"></i>
              <span>Start building in minutes, not months</span>
            </p>
          </div>
        </div>
        
        <!-- Decorative elements -->
        <div class="absolute -bottom-20 -right-20 w-40 h-40 bg-violet-500/5 rounded-full blur-3xl"></div>
        <div class="absolute -top-20 -left-20 w-32 h-32 bg-fuchsia-500/5 rounded-full blur-3xl"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  title: string;
  icon: string;
  description: string;
  buttonText: string;
  buttonLink: string;
  buttonIcon: string;
}>(), {
  title: 'Ready to Get Started?',
  icon: 'fas fa-lightbulb',
  description: 'Follow our step-by-step guide to create your first project and see Imagi Oasis in action.',
  buttonText: 'Quick Start Guide',
  buttonLink: '/docs/quickstart',
  buttonIcon: 'fas fa-arrow-right'
});
</script>
