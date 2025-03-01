<template>
  <Transition
    enter-active-class="transition-opacity duration-300"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition-opacity duration-300"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div 
      class="fixed inset-0 flex items-center justify-center z-50"
      :class="transparent ? 'bg-dark-900/50' : 'bg-dark-900'"
    >
      <div class="flex flex-col items-center space-y-4">
        <div class="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
        <p class="text-white text-lg">{{ message }}</p>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
defineProps<{
  message?: string
  transparent?: boolean
}>()
</script>