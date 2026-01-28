<template>
  <nav class="fixed w-full z-50 bg-white/80 dark:bg-[#0a0a0a]/80 backdrop-blur-xl border-b border-gray-200/80 dark:border-white/5 transition-colors duration-300">
    <div class="relative max-w-7xl mx-auto pl-6 pr-6 sm:pl-8 sm:pr-8 lg:pl-12 lg:pr-12">
      <div class="relative flex items-center h-14">
        <!-- Left section -->
        <div class="flex items-center z-10 -ml-36">
          <ImagiLogo size="md">
            <slot name="logo">Imagi</slot>
          </ImagiLogo>
          <slot name="left"></slot>
        </div>

        <!-- Center section -->
        <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div class="pointer-events-auto">
            <slot name="center"></slot>
          </div>
        </div>

        <!-- Right section -->
        <div class="ml-auto flex items-center h-full justify-end z-10 -mr-36">
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
nav {
  width: 100%;
  overflow: visible;
}

.justify-end {
  position: relative;
  z-index: 10;
}

@supports (backdrop-filter: blur(20px)) {
  nav {
    backdrop-filter: blur(20px);
  }
}
</style>
