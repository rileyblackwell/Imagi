<template>
  <div class="relative">
    <input
      type="text"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      class="w-full px-4 py-2 pl-10 bg-dark-900/50 border border-dark-600 focus:border-primary-500/50 rounded-xl text-white placeholder-gray-500 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
      :placeholder="placeholder"
    >
    <i class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"></i>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    required: true
  },
  placeholder: {
    type: String,
    default: 'Search...'
  }
});

defineEmits(['update:modelValue']);
</script>
