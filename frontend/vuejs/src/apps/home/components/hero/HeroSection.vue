<!-- Hero section component used across different pages -->
<template>
  <section class="relative min-h-[600px] flex items-center justify-center">
    <!-- Background gradient -->
    <div class="absolute inset-0 bg-gradient-radial from-primary-500/10 via-transparent to-transparent"></div>
    
    <!-- Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
      <div class="text-center max-w-3xl mx-auto">
        <h1 class="text-5xl md:text-6xl font-extrabold tracking-tight">
          <slot name="title">
            <span class="block text-white">{{ title }}</span>
            <span v-if="gradientTitle" class="block bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">
              {{ gradientTitle }}
            </span>
          </slot>
        </h1>
        
        <p class="mt-6 text-xl text-gray-300">
          <slot name="description">{{ description }}</slot>
        </p>
        
        <div class="mt-10">
          <slot name="cta"></slot>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'HeroSection',
  props: {
    title: {
      type: String,
      required: true
    },
    gradientTitle: {
      type: String,
      default: ''
    },
    description: {
      type: String,
      required: true
    }
  }
}
</script> 