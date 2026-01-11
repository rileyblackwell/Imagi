<template>
  <nav class="fixed w-full z-50 bg-[#0a0a0f]/80 backdrop-blur-xl border-b border-white/10">
    <!-- Subtle top gradient accent -->
    <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-500/30 to-transparent"></div>
    
    <!-- Background effects -->
    <div class="absolute inset-0 pointer-events-none overflow-hidden">
      <!-- Subtle gradient glow -->
      <div class="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,rgba(120,119,198,0.08),transparent_50%)]"></div>
      
      <!-- Subtle grain texture -->
      <div class="absolute inset-0 opacity-[0.01]" style="background-image: url('data:image/svg+xml,%3Csvg viewBox=%220 0 256 256%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noise%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.8%22 numOctaves=%224%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noise)%22/%3E%3C/svg%3E');"></div>
    </div>

    <div class="relative max-w-full mx-auto px-6 sm:px-8 lg:px-12">
      <div class="relative flex items-center h-20">
        <!-- Left section -->
        <div class="flex items-center z-10">
          <ImagiLogo size="md">
            <slot name="logo">Imagi</slot>
          </ImagiLogo>
          <slot name="left"></slot>
        </div>

        <!-- Center section: absolutely centered, independent of left/right widths -->
        <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div class="pointer-events-auto">
            <slot name="center"></slot>
          </div>
        </div>

        <!-- Right section -->
        <div class="ml-auto flex items-center h-full justify-end z-10">
          <slot name="right"></slot>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ImagiLogo } from '@/shared/components/molecules'
</script>

<style scoped>
/* Ensure the navbar adapts to layout changes */
nav {
  width: 100%;
  overflow: visible;
}

/* Right side slots should always be visible */
.justify-end {
  position: relative;
  z-index: 10;
}

/* Smooth backdrop blur */
@supports (backdrop-filter: blur(20px)) {
  nav {
    backdrop-filter: blur(20px);
  }
}
</style>
