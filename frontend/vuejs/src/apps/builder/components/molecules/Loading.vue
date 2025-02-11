<template>
  <div class="flex flex-col items-center justify-center py-12">
    <div class="w-14 h-14 bg-primary-500/10 rounded-full flex items-center justify-center mb-4">
      <i class="fas fa-spinner fa-spin text-2xl text-primary-400"></i>
    </div>
    <p class="text-gray-400">{{ message }}</p>
  </div>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    default: 'Loading...'
  }
});
</script>
