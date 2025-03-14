<!-- Reusable gradient text component -->
<template>
  <span
    class="bg-gradient-to-r bg-clip-text text-transparent"
    :class="[gradientClass, fontClass, variant === 'imagi' ? 'animate-gradient drop-shadow-[0_0_12px_rgba(236,72,153,0.3)] tracking-tight' : '']"
  >
    <slot></slot>
  </span>
</template>

<script>
export default {
  name: 'GradientText',
  props: {
    variant: {
      type: String,
      default: 'primary',
      validator: value => ['primary', 'secondary', 'accent', 'imagi'].includes(value)
    },
    size: {
      type: String,
      default: 'base',
      validator: value => ['sm', 'base', 'lg', 'xl', '2xl', '3xl'].includes(value)
    }
  },
  computed: {
    gradientClass() {
      const gradients = {
        primary: 'from-primary-400 to-primary-600',
        secondary: 'from-cyan-400 to-blue-500',
        accent: 'from-emerald-400 to-teal-600',
        imagi: 'from-pink-300 via-emerald-300 to-yellow-200'
      }
      return gradients[this.variant]
    },
    fontClass() {
      const sizes = {
        sm: 'text-sm',
        base: 'text-base',
        lg: 'text-lg',
        xl: 'text-xl',
        '2xl': 'text-2xl',
        '3xl': 'text-3xl'
      }
      return sizes[this.size]
    }
  }
}
</script>

<style scoped>
@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.animate-gradient {
  background-size: 200% auto;
  animation: gradient-shift 4s ease infinite;
}
</style> 