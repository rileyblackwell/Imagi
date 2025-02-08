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
      'inline-flex items-center justify-center text-sm font-medium rounded-lg !text-white hover:!text-white'
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
        primary: 'bg-gradient-to-r from-primary-500 via-indigo-500 to-violet-500 hover:from-primary-400 hover:via-indigo-400 hover:to-violet-400 hover:shadow-primary-500/20 text-white',
        secondary: 'bg-gradient-to-r from-violet-500 via-fuchsia-500 to-pink-500 hover:from-violet-400 hover:via-fuchsia-400 hover:to-pink-400 hover:shadow-violet-500/20 text-white',
        amber: 'bg-gradient-to-r from-amber-500 via-orange-500 to-yellow-500 hover:from-amber-400 hover:via-orange-400 hover:to-yellow-400 hover:shadow-amber-500/20 text-white',
        indigo: 'bg-gradient-to-r from-blue-500 via-indigo-500 to-violet-500 hover:from-blue-400 hover:via-indigo-400 hover:to-violet-400 hover:shadow-blue-500/20 text-white',
        ghost: 'bg-gradient-to-r from-primary-500/90 via-indigo-500/90 to-violet-500/90 hover:from-primary-400/90 hover:via-indigo-400/90 hover:to-violet-400/90 backdrop-blur-md border border-white/10 hover:border-white/20 shadow-sm hover:shadow-primary-500/10 text-white'
      }
      return gradients[props.gradientType]
    })

    return {
      gradientClass
    }
  }
})
</script> 