<!-- Home navbar dropdown button component with custom gradients -->
<template>
  <div class="relative">
    <button
      :class="[
        gradientClass,
        buttonStyleClass,
        'group relative overflow-hidden',
        'backdrop-blur-sm',
        'before:absolute before:inset-0 before:bg-white/0 hover:before:bg-white/10',
        'before:transition-all before:duration-300',
        { 'shadow-xl scale-[1.02]': isOpen }
      ]"
      @click="toggleDropdown"
    >
      <slot name="trigger">
        <span class="flex items-center gap-2 relative z-10">
          <slot></slot>
          <i 
            class="fas fa-chevron-down text-xs transition-all duration-300 ease-out" 
            :class="{ 'transform rotate-180': isOpen }"
          ></i>
        </span>
      </slot>
    </button>

    <!-- Dropdown Menu with enhanced styling -->
    <transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0 scale-95 -translate-y-2"
      enter-to-class="opacity-100 scale-100 translate-y-0"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100 scale-100 translate-y-0"
      leave-to-class="opacity-0 scale-95 -translate-y-2"
    >
      <div
        v-show="isOpen"
        class="absolute right-0 mt-3 w-64 origin-top-right z-50"
      >
        <div class="rounded-2xl bg-gradient-to-br from-dark-900/98 via-dark-800/98 to-dark-900/98 border border-primary-400/20 shadow-2xl shadow-primary-500/10 backdrop-blur-xl overflow-hidden ring-1 ring-white/5">
          <!-- Glow effect at top -->
          <div class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-primary-400/50 to-transparent"></div>
          
          <div class="py-2">
            <slot name="menu"></slot>
          </div>
          
          <!-- Glow effect at bottom -->
          <div class="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-primary-400/30 to-transparent"></div>
        </div>
      </div>
    </transition>

    <!-- Enhanced Overlay -->
    <transition
      enter-active-class="transition-opacity ease-out duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity ease-in duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isOpen"
        class="fixed inset-0 z-40 bg-dark-900/20 backdrop-blur-[3px]"
        @click="closeDropdown"
      ></div>
    </transition>
  </div>
</template>

<script>
import { defineComponent, computed, ref } from 'vue'

export default defineComponent({
  name: 'HomeNavbarDropdownButton',
  props: {
    gradientType: {
      type: String,
      default: 'primary',
      validator: value => ['primary', 'secondary', 'amber', 'indigo', 'ghost', 'minimal'].includes(value)
    },
    modelValue: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const isOpen = computed({
      get: () => props.modelValue,
      set: (value) => emit('update:modelValue', value)
    })

    const gradientClass = computed(() => {
      // Minimal style - clean Apple/Cursor-inspired design
      if (props.gradientType === 'minimal') {
        return 'bg-gray-900 dark:bg-white text-white dark:text-gray-900 hover:shadow-xl';
      }

      const gradients = {
        primary: 'bg-gradient-to-br from-primary-600 via-primary-500 to-indigo-600 hover:from-primary-500 hover:via-primary-400 hover:to-indigo-500 text-white shadow-primary-500/30 hover:shadow-primary-500/50',
        secondary: 'bg-gradient-to-br from-violet-600 via-fuchsia-500 to-pink-600 hover:from-violet-500 hover:via-fuchsia-400 hover:to-pink-500 text-white shadow-violet-500/30 hover:shadow-violet-500/50',
        amber: 'bg-gradient-to-br from-amber-600 via-orange-500 to-yellow-600 hover:from-amber-500 hover:via-orange-400 hover:to-yellow-500 text-white shadow-amber-500/30 hover:shadow-amber-500/50',
        indigo: 'bg-gradient-to-br from-blue-600 via-indigo-500 to-violet-600 hover:from-blue-500 hover:via-indigo-400 hover:to-violet-500 text-white shadow-indigo-500/30 hover:shadow-indigo-500/50',
        ghost: 'bg-dark-800/40 hover:bg-dark-700/60 backdrop-blur-md border border-primary-400/30 hover:border-primary-400/60 text-white shadow-primary-500/10 hover:shadow-primary-500/20'
      }
      return gradients[props.gradientType]
    })

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
    })

    const toggleDropdown = () => {
      isOpen.value = !isOpen.value
    }

    const closeDropdown = () => {
      isOpen.value = false
    }

    return {
      isOpen,
      gradientClass,
      buttonStyleClass,
      toggleDropdown,
      closeDropdown
    }
  }
})
</script> 