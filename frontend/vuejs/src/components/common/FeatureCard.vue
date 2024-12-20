<template>
  <div class="feature-card">
    <div class="feature-icon">
      <i :class="`fas fa-${icon}`" />
    </div>
    <h3 class="feature-title">{{ title }}</h3>
    <p class="feature-description">{{ description }}</p>
  </div>
</template>

<script setup>
defineProps({
  icon: {
    type: String,
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
.feature-card {
  @apply p-8 rounded-2xl bg-gray-800/50 hover:bg-gradient-to-r hover:from-cyan-500/5 hover:to-blue-500/5 
         transition-all transform hover:scale-105 border border-gray-700/50;
}

.feature-icon {
  @apply w-16 h-16 flex items-center justify-center text-2xl text-cyan-400 mb-6 
         bg-gray-800 rounded-xl group-hover:scale-110 group-hover:rotate-6 transition-transform;
}

.feature-title {
  @apply text-xl font-bold mb-4 text-white;
}

.feature-description {
  @apply text-gray-300 leading-relaxed;
}
</style>
