<template>
  <div class="workflow-step">
    <div class="step-number">{{ number }}</div>
    <h3 class="step-title">{{ title }}</h3>
    <p class="step-description">{{ description }}</p>
  </div>
</template>

<script setup>
defineProps({
  number: {
    type: Number,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  }
})
</script>

<style>
.workflow-step {
  @apply text-center relative;
}

.step-number {
  @apply w-12 h-12 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 
         flex items-center justify-center text-xl font-bold text-white mx-auto mb-6;
}

.step-title {
  @apply text-xl font-bold mb-4 text-white;
}

.step-description {
  @apply text-gray-300 leading-relaxed;
}
</style>
