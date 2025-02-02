<!-- Reusable icon button component -->
<template>
  <component
    :is="to ? 'router-link' : 'button'"
    :to="to"
    class="inline-flex items-center justify-center transition-all duration-300"
    :class="[sizeClass, variantClass, { 'opacity-50 cursor-not-allowed': disabled }]"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <i v-if="icon" :class="['mr-2', icon]"></i>
    <slot></slot>
    <i v-if="iconRight" :class="['ml-2', iconRight]"></i>
  </component>
</template>

<script>
export default {
  name: 'IconButton',
  props: {
    to: {
      type: [String, Object],
      default: null
    },
    variant: {
      type: String,
      default: 'primary',
      validator: value => ['primary', 'secondary', 'outline', 'ghost'].includes(value)
    },
    size: {
      type: String,
      default: 'base',
      validator: value => ['sm', 'base', 'lg'].includes(value)
    },
    icon: {
      type: String,
      default: ''
    },
    iconRight: {
      type: String,
      default: ''
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    sizeClass() {
      return {
        sm: 'px-3 py-1.5 text-sm',
        base: 'px-4 py-2 text-base',
        lg: 'px-6 py-3 text-lg'
      }[this.size]
    },
    variantClass() {
      const variants = {
        primary: 'bg-primary-600 hover:bg-primary-700 text-white rounded-lg',
        secondary: 'bg-dark-700 hover:bg-dark-600 text-white rounded-lg',
        outline: 'border border-primary-600 text-primary-600 hover:bg-primary-600 hover:text-white rounded-lg',
        ghost: 'text-white hover:text-primary-400'
      }
      return variants[this.variant]
    }
  }
}
</script> 