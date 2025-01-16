<!-- Reusable feature card component -->
<template>
  <div class="relative group">
    <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
      <!-- Icon -->
      <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
        <i :class="['text-2xl text-primary-400', icon]"></i>
      </div>
      
      <!-- Content -->
      <h3 class="text-xl font-semibold text-white mb-4">{{ title }}</h3>
      <p class="text-gray-300">
        <slot>{{ description }}</slot>
      </p>
      
      <!-- Optional link -->
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FeatureCard',
  props: {
    icon: {
      type: String,
      required: true
    },
    title: {
      type: String,
      required: true
    },
    description: {
      type: String,
      default: ''
    }
  }
}
</script>

<style scoped>
.shadow-glow {
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(0, 255, 204, 0.1);
}
</style> 