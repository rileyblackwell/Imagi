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
      class="absolute right-0 mt-2 w-56 rounded-lg bg-gradient-to-br from-dark-900/95 via-dark-800/95 to-dark-900/95 border border-primary-500/20 shadow-lg shadow-primary-500/5 backdrop-blur-md z-50 overflow-hidden ring-1 ring-primary-500/10"
    >
      <div class="py-1">
        <slot name="menu"></slot>
      </div>
    </div>

    <!-- Overlay -->
    <div
      v-if="isOpen"
      class="fixed inset-0 z-40 bg-dark-900/5 backdrop-blur-[2px]"
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
        primary: 'bg-gradient-to-r from-primary-500 via-indigo-500 to-violet-500 hover:from-primary-400 hover:via-indigo-400 hover:to-violet-400 hover:shadow-primary-500/20',
        secondary: 'bg-gradient-to-r from-violet-500 via-fuchsia-500 to-pink-500 hover:from-violet-400 hover:via-fuchsia-400 hover:to-pink-400 hover:shadow-violet-500/20',
        amber: 'bg-gradient-to-r from-amber-500 via-orange-500 to-yellow-500 hover:from-amber-400 hover:via-orange-400 hover:to-yellow-400 hover:shadow-amber-500/20',
        indigo: 'bg-gradient-to-r from-blue-500 via-indigo-500 to-violet-500 hover:from-blue-400 hover:via-indigo-400 hover:to-violet-400 hover:shadow-blue-500/20',
        ghost: 'bg-gradient-to-r from-primary-500/90 via-indigo-500/90 to-violet-500/90 hover:from-primary-400/90 hover:via-indigo-400/90 hover:to-violet-400/90 backdrop-blur-md border border-white/10 hover:border-white/20 shadow-sm hover:shadow-primary-500/10 text-white hover:text-white'
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