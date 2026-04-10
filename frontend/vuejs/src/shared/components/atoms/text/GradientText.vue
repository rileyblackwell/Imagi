<template>
  <span
    class="bg-gradient-to-r bg-clip-text text-transparent"
    :class="[gradientClass, fontClass]"
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
      validator: value => ['primary', 'secondary', 'accent'].includes(value)
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
        accent: 'from-emerald-400 to-teal-600'
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
