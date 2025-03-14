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
      default: null
    },
    gradientType: {
      type: String,
      default: 'primary',
      validator: (value) => ['primary', 'amber', 'emerald', 'rose', 'fuchsia', 'indigo'].includes(value)
    }
  },
  emits: ['click'],
  setup(props) {
    // Computed class for gradient
    const gradientClass = computed(() => {
      const gradients = {
        primary: 'bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-500 hover:to-indigo-500',
        amber: 'bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500',
        emerald: 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500',
        rose: 'bg-gradient-to-r from-rose-600 to-pink-600 hover:from-rose-500 hover:to-pink-500',
        fuchsia: 'bg-gradient-to-r from-fuchsia-600 to-purple-600 hover:from-fuchsia-500 hover:to-purple-500',
        indigo: 'bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500'
      };

      const ghostGradients = {
        primary: 'bg-dark-800/60 hover:bg-dark-800/90 border border-primary-500/30 hover:border-primary-500/50',
        amber: 'bg-dark-800/60 hover:bg-dark-800/90 border border-amber-500/30 hover:border-amber-500/50',
        emerald: 'bg-dark-800/60 hover:bg-dark-800/90 border border-emerald-500/30 hover:border-emerald-500/50',
        rose: 'bg-dark-800/60 hover:bg-dark-800/90 border border-rose-500/30 hover:border-rose-500/50',
        fuchsia: 'bg-dark-800/60 hover:bg-dark-800/90 border border-fuchsia-500/30 hover:border-fuchsia-500/50',
        indigo: 'bg-dark-800/60 hover:bg-dark-800/90 border border-indigo-500/30 hover:border-indigo-500/50'
      };

      if (props.variant === 'primary') {
        return gradients[props.gradientType];
      } else if (props.variant === 'ghost') {
        return ghostGradients[props.gradientType];
      }
      
      return '';
    });

    return {
      gradientClass
    };
  }
})
</script> 