<template>
  <div class="inline-block px-4 py-1 bg-dark-800/50 backdrop-blur-sm rounded-full border border-primary-500/30 mb-6">
    <span class="text-sm font-medium text-gray-300">
      <i class="fas fa-sparkles text-primary-500 mr-2"></i>
      {{ text }}
    </span>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'HeroBadge',
  props: {
    text: {
      type: String,
      required: true
    }
  }
})
</script> 