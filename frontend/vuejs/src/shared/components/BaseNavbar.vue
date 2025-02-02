<!-- BaseNavbar component -->
<template>
  <nav class="bg-dark-900 border-b border-dark-700">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-20">
        <!-- Left side -->
        <div class="flex items-center">
          <!-- Logo -->
          <router-link 
            to="/" 
            class="text-3xl font-bold text-white hover:text-primary-400 transition-colors mr-10"
          >
            Imagi
          </router-link>
          <!-- Left slot -->
          <slot name="left"></slot>
        </div>

        <!-- Right slot -->
        <slot name="right">
          <HomeNavbar v-if="isHomeNav" />
        </slot>
      </div>
    </div>
  </nav>
</template>

<script>
import HomeNavbar from '@/apps/home/components/HomeNavbar.vue'

export default {
  name: 'BaseNavbar',
  components: {
    HomeNavbar
  },
  props: {
    isHomeNav: {
      type: Boolean,
      default: false
    }
  }
}
</script>

<style scoped>
/* No additional styles needed for BaseNavbar */
</style> 