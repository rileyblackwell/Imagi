<template>
  <div 
    class="block p-4 rounded-lg hover:bg-dark-700 transition-colors duration-200 cursor-pointer"
    @click="$emit('click')"
  >
    // ...existing template code...
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'

interface Project {
  id: string | number;
  name: string;
  description?: string;
  created_at: string;
}

defineProps<{
  project: Project
}>()

defineEmits<{
  (e: 'click'): void
}>()
</script>
