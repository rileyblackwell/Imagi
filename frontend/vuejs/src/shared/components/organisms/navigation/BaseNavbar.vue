<template>
  <nav class="bg-dark-900/80 backdrop-blur-sm fixed w-full z-50 border-b border-dark-700">
    <div class="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
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

<script>
import { defineComponent } from 'vue'
import { ImagiLogo } from '@/shared/components/molecules'

export default defineComponent({
  name: 'BaseNavbar',
  components: {
    ImagiLogo
  }
})
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
</style>
