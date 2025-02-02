<!-- Base navigation component -->
<template>
  <nav class="bg-dark-900/80 backdrop-blur-sm fixed w-full z-50 border-b border-dark-700">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <!-- Left side -->
        <div class="flex items-center">
          <!-- Logo -->
          <router-link 
            to="/" 
            class="text-white font-bold text-xl"
          >
            <slot name="logo">Imagi</slot>
          </router-link>

          <!-- Left slot -->
          <slot name="left"></slot>
        </div>

        <!-- Right slot -->
        <slot name="right"></slot>
      </div>
    </div>
  </nav>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'BaseNavbar'
})
</script>

<style scoped>
/* No additional styles needed for BaseNavbar */
</style> 