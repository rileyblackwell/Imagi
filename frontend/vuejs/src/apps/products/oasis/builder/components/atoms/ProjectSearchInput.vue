<template>
  <div class="relative group flex-1 max-w-md">
    <div class="relative flex items-center">
      <div class="absolute left-4 flex items-center justify-center w-4 h-4 z-20">
        <i class="fas fa-search text-white text-sm search-light-glow"></i>
      </div>
      <input
        :value="modelValue"
        @input="handleInput"
        type="text"
        :placeholder="placeholder || 'Search projects'"
        class="relative z-10 w-full pl-11 pr-4 py-3 bg-white/5 border border-white/10 focus:border-violet-400/50 hover:border-white/15 rounded-xl text-white placeholder-gray-400 transition-all duration-300 backdrop-blur-sm hover:bg-white/8 focus:bg-white/8 focus:shadow-lg focus:shadow-violet-500/20"
        style="outline: none !important; box-shadow: none !important;"
      >
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  modelValue: {
    type: String,
    required: true
  },
  placeholder: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['update:modelValue']);

function handleInput(event: Event): void {
  const target = event.target as HTMLInputElement;
  emit('update:modelValue', target.value);
}
</script>

<style scoped>
/* Completely remove any browser default styling */
input {
  outline: none !important;
  box-shadow: none !important;
  -webkit-appearance: none !important;
  -moz-appearance: none !important;
  appearance: none !important;
}

input:focus {
  outline: none !important;
  box-shadow: none !important;
}

/* Search light glow effect - dimmed */
.search-light-glow {
  text-shadow: 
    0 0 3px rgba(255, 255, 255, 0.4),
    0 0 6px rgba(255, 255, 255, 0.3),
    0 0 9px rgba(255, 255, 255, 0.2),
    0 0 12px rgba(255, 255, 255, 0.1);
  filter: brightness(1.05);
}
</style>
