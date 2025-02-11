<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="[
      'relative group',
      fullWidth ? 'w-full' : 'w-auto',
      disabled ? 'opacity-50 cursor-not-allowed' : ''
    ]"
  >
    <!-- Gradient background -->
    <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500 to-violet-500 rounded-xl blur opacity-75 group-hover:opacity-100 transition duration-300"></div>
    
    <!-- Button content -->
    <div class="relative flex items-center justify-center px-6 py-3 bg-dark-900 rounded-xl transition-all duration-300">
      <i v-if="icon" :class="['fas fa-' + icon, 'mr-2 text-primary-400 group-hover:text-primary-300']"></i>
      <span class="font-medium text-white">
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
  }
});

defineEmits(['click']);
</script>
