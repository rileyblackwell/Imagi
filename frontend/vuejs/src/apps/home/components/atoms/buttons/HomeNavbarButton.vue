<!-- Home navbar button component with custom gradients -->
<template>
  <IconButton
    :to="to"
    :variant="variant"
    :size="size"
    :icon="icon"
    :class="[
      gradientClass,
      'group relative overflow-hidden',
      buttonStyleClass,
      '!text-white hover:!text-white dark:!text-gray-900 dark:hover:!text-gray-900',
      'backdrop-blur-sm',
      'before:absolute before:inset-0 before:bg-white/0 hover:before:bg-white/10',
      'before:transition-all before:duration-300',
      '!rounded-full'
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
      validator: (value) => ['primary', 'amber', 'emerald', 'rose', 'fuchsia', 'indigo', 'minimal'].includes(value)
    }
  },
  emits: ['click'],
  setup(props) {
    // Computed class for gradient with enhanced modern styling
    const gradientClass = computed(() => {
      // Minimal style - clean Apple/Cursor-inspired design
      if (props.gradientType === 'minimal') {
        return 'bg-gray-900 dark:bg-white hover:shadow-xl';
      }

      const gradients = {
        primary: 'bg-gradient-to-br from-primary-600 via-primary-500 to-indigo-600 hover:from-primary-500 hover:via-primary-400 hover:to-indigo-500 shadow-primary-500/30 hover:shadow-primary-500/50',
        amber: 'bg-gradient-to-br from-amber-600 via-amber-500 to-orange-600 hover:from-amber-500 hover:via-amber-400 hover:to-orange-500 shadow-amber-500/30 hover:shadow-amber-500/50',
        emerald: 'bg-gradient-to-br from-emerald-600 via-emerald-500 to-teal-600 hover:from-emerald-500 hover:via-emerald-400 hover:to-teal-500 shadow-emerald-500/30 hover:shadow-emerald-500/50',
        rose: 'bg-gradient-to-br from-rose-600 via-rose-500 to-pink-600 hover:from-rose-500 hover:via-rose-400 hover:to-pink-500 shadow-rose-500/30 hover:shadow-rose-500/50',
        fuchsia: 'bg-gradient-to-br from-fuchsia-600 via-fuchsia-500 to-purple-600 hover:from-fuchsia-500 hover:via-fuchsia-400 hover:to-purple-500 shadow-fuchsia-500/30 hover:shadow-fuchsia-500/50',
        indigo: 'bg-gradient-to-br from-indigo-600 via-indigo-500 to-blue-600 hover:from-indigo-500 hover:via-indigo-400 hover:to-blue-500 shadow-indigo-500/30 hover:shadow-indigo-500/50'
      };

      const ghostGradients = {
        primary: 'bg-dark-800/40 hover:bg-dark-700/60 backdrop-blur-md border border-primary-400/30 hover:border-primary-400/60 shadow-primary-500/10 hover:shadow-primary-500/20',
        amber: 'bg-dark-800/40 hover:bg-dark-700/60 backdrop-blur-md border border-amber-400/30 hover:border-amber-400/60 shadow-amber-500/10 hover:shadow-amber-500/20',
        emerald: 'bg-dark-800/40 hover:bg-dark-700/60 backdrop-blur-md border border-emerald-400/30 hover:border-emerald-400/60 shadow-emerald-500/10 hover:shadow-emerald-500/20',
        rose: 'bg-dark-800/40 hover:bg-dark-700/60 backdrop-blur-md border border-rose-400/30 hover:border-rose-400/60 shadow-rose-500/10 hover:shadow-rose-500/20',
        fuchsia: 'bg-dark-800/40 hover:bg-dark-700/60 backdrop-blur-md border border-fuchsia-400/30 hover:border-fuchsia-400/60 shadow-fuchsia-500/10 hover:shadow-fuchsia-500/20',
        indigo: 'bg-dark-800/40 hover:bg-dark-700/60 backdrop-blur-md border border-indigo-400/30 hover:border-indigo-400/60 shadow-indigo-500/10 hover:shadow-indigo-500/20'
      };

      if (props.variant === 'primary') {
        return gradients[props.gradientType];
      } else if (props.variant === 'ghost') {
        return ghostGradients[props.gradientType];
      }
      
      return '';
    });

    // Computed class for button styling - different for minimal vs gradient buttons
    const buttonStyleClass = computed(() => {
      if (props.gradientType === 'minimal') {
        return [
          'transform hover:scale-[1.02] active:scale-[0.98]',
          'transition-all duration-300',
          'min-w-[100px] px-6 py-2.5',
          'inline-flex items-center justify-center gap-2',
          'text-sm font-medium rounded-full'
        ].join(' ');
      }
      
      // Default gradient button styling
      return [
        'transform hover:scale-[1.03] active:scale-[0.98]',
        'transition-all duration-300 ease-out',
        'shadow-lg hover:shadow-xl',
        'min-w-[120px] h-11 px-5',
        'inline-flex items-center justify-center gap-2',
        'text-sm font-semibold tracking-wide rounded-xl'
      ].join(' ');
    });

    return {
      gradientClass,
      buttonStyleClass
    };
  }
})
</script> 