<template>
  <div class="text-center mb-12">
    <h2 class="text-3xl sm:text-4xl font-bold text-white mb-4">{{ title }}</h2>
    <p class="text-lg text-gray-300 max-w-2xl mx-auto">{{ subtitle }}</p>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'SectionHeader',
  props: {
    title: {
      type: String,
      required: true
    },
    subtitle: {
      type: String,
      default: ''
    }
  }
})
</script> 