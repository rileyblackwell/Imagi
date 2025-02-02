<!-- Home navbar button component with custom gradients -->
<template>
  <IconButton
    :to="to"
    :variant="variant"
    :size="size"
    :icon="icon"
    :class="[
      gradientClass,
      'transform hover:scale-[1.02] transition-all duration-200 shadow-sm hover:shadow-md min-w-[100px] h-10 px-4',
      'inline-flex items-center justify-center text-sm font-medium rounded-lg'
    ]"
    v-bind="$attrs"
    @click="$emit('click', $event)"
  >
    <slot></slot>
  </IconButton>
</template>

<script>
import { defineComponent, computed } from 'vue'
import IconButton from './IconButton.vue'

export default defineComponent({
  name: 'HomeNavbarButton',
  components: {
    IconButton
  },
  inheritAttrs: false,
  props: {
    to: {
      type: [String, Object],
      default: null
    },
    variant: {
      type: String,
      default: 'primary'
    },
    size: {
      type: String,
      default: 'base'
    },
    icon: {
      type: String,
      default: ''
    },
    gradientType: {
      type: String,
      default: 'primary',
      validator: value => ['primary', 'secondary', 'amber', 'indigo', 'ghost'].includes(value)
    }
  },
  emits: ['click'],
  setup(props) {
    const gradientClass = computed(() => {
      const gradients = {
        primary: 'bg-gradient-to-r from-primary-600/95 via-indigo-500/95 to-primary-500/95 hover:from-primary-500/95 hover:via-indigo-400/95 hover:to-primary-400/95 hover:shadow-primary-600/10',
        secondary: 'bg-gradient-to-r from-violet-600/95 via-indigo-500/95 to-blue-500/95 hover:from-violet-500/95 hover:via-indigo-400/95 hover:to-blue-400/95 hover:shadow-violet-600/10',
        amber: 'bg-gradient-to-r from-amber-500/95 via-orange-400/95 to-yellow-400/95 hover:from-amber-400/95 hover:via-orange-300/95 hover:to-yellow-300/95 hover:shadow-amber-500/10',
        indigo: 'bg-gradient-to-r from-indigo-600/95 via-blue-500/95 to-indigo-500/95 hover:from-indigo-500/95 hover:via-blue-400/95 hover:to-indigo-400/95 hover:shadow-indigo-600/10',
        ghost: 'bg-gradient-to-r from-dark-800/80 via-dark-700/80 to-dark-800/80 hover:from-dark-700/80 hover:via-dark-600/80 hover:to-dark-700/80 backdrop-blur-md border border-white/5 hover:border-white/10 shadow-sm hover:shadow-md text-white/90 hover:text-white'
      }
      return gradients[props.gradientType]
    })

    return {
      gradientClass
    }
  }
})
</script> 