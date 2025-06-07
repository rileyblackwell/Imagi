<template>
  <div class="relative group flex-1 max-w-md">
    <div class="absolute inset-0 bg-gradient-to-r from-indigo-500/10 to-violet-500/10 rounded-lg blur-[2px] opacity-0 group-focus-within:opacity-100 transition-all duration-300 pointer-events-none"></div>
    <div class="relative flex items-center">
      <i class="fas fa-search text-gray-500 absolute left-4"></i>
      <input
        :value="modelValue"
        @input="handleInput"
        type="text"
        :placeholder="placeholder || 'Search projects by name...'"
        class="relative z-10 w-full pl-10 pr-4 py-3 bg-dark-900/90 border border-dark-600 focus:border-transparent rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all duration-200"
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
