<!-- Home navbar dropdown button component with custom gradients -->
<template>
  <div class="relative">
    <button
      :class="[
        gradientClass,
        'transform hover:scale-[1.02] transition-all duration-200 shadow-sm hover:shadow-md min-w-[100px] h-10 px-4',
        'inline-flex items-center justify-center text-sm font-medium rounded-lg',
        { 'shadow-md': isOpen }
      ]"
      @click="toggleDropdown"
    >
      <slot name="trigger">
        <span class="flex items-center">
          <slot></slot>
          <i class="fas fa-chevron-down ml-2 text-xs transition-transform duration-200" :class="{ 'transform rotate-180': isOpen }"></i>
        </span>
      </slot>
    </button>

    <!-- Dropdown Menu -->
    <div
      v-show="isOpen"
      class="absolute right-0 mt-2 w-56 rounded-lg bg-gradient-to-b from-dark-900/95 via-dark-800/95 to-dark-900/95 border border-white/5 shadow-lg backdrop-blur-md z-50 overflow-hidden"
    >
      <div class="py-1">
        <slot name="menu"></slot>
      </div>
    </div>

    <!-- Overlay -->
    <div
      v-if="isOpen"
      class="fixed inset-0 z-40 bg-black/5 backdrop-blur-[2px]"
      @click="closeDropdown"
    ></div>
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
      validator: value => ['primary', 'secondary', 'amber', 'indigo', 'ghost'].includes(value)
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
      const gradients = {
        primary: 'bg-gradient-to-r from-primary-600/95 via-indigo-500/95 to-primary-500/95 hover:from-primary-500/95 hover:via-indigo-400/95 hover:to-primary-400/95 hover:shadow-primary-600/10',
        secondary: 'bg-gradient-to-r from-violet-600/95 via-indigo-500/95 to-blue-500/95 hover:from-violet-500/95 hover:via-indigo-400/95 hover:to-blue-400/95 hover:shadow-violet-600/10',
        amber: 'bg-gradient-to-r from-amber-500/95 via-orange-400/95 to-yellow-400/95 hover:from-amber-400/95 hover:via-orange-300/95 hover:to-yellow-300/95 hover:shadow-amber-500/10',
        indigo: 'bg-gradient-to-r from-indigo-600/95 via-blue-500/95 to-indigo-500/95 hover:from-indigo-500/95 hover:via-blue-400/95 hover:to-indigo-400/95 hover:shadow-indigo-600/10',
        ghost: 'bg-gradient-to-r from-dark-800/80 via-dark-700/80 to-dark-800/80 hover:from-dark-700/80 hover:via-dark-600/80 hover:to-dark-700/80 backdrop-blur-md border border-white/5 hover:border-white/10 shadow-sm hover:shadow-md text-white/90 hover:text-white'
      }
      return gradients[props.gradientType]
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
      toggleDropdown,
      closeDropdown
    }
  }
})
</script> 