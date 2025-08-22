<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="[
      'relative group',
      fullWidth ? 'w-full' : 'w-auto',
      disabled ? 'opacity-50 cursor-not-allowed' : ''
    ]"
    @click="$emit('click')"
  >
    <!-- Gradient background (scaled for size) -->
    <div :class="[
          'absolute bg-gradient-to-r from-primary-500 to-violet-500 transition duration-300',
          size === 'sm' ? '-inset-px rounded-lg blur-sm opacity-70' : '-inset-0.5 rounded-xl blur opacity-75',
          'group-hover:opacity-100'
        ]"></div>
    
    <!-- Button content -->
    <div :class="[
          'relative flex items-center justify-center bg-dark-900 transition-all duration-300',
          size === 'sm' ? 'px-3 py-1.5 rounded-lg' : 'px-6 py-3 rounded-xl'
        ]">
      <i v-if="icon" :class="[
          'fas fa-' + icon,
          'text-primary-400 group-hover:text-primary-300',
          size === 'sm' ? 'mr-1.5 text-xs' : 'mr-2 text-sm'
        ]"></i>
      <span :class="['font-medium text-white', size === 'sm' ? 'text-xs' : 'text-sm']">
        <slot>{{ loading ? loadingText : text }}</slot>
      </span>
    </div>
  </button>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    default: 'button'
  },
  text: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: ''
  },
  loading: {
    type: Boolean,
    default: false
  },
  loadingText: {
    type: String,
    default: 'Loading...'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  fullWidth: {
    type: Boolean,
    default: false
  },
  size: {
    type: String,
    default: 'md' // 'sm' | 'md'
  }
});

defineEmits(['click']);
</script>
