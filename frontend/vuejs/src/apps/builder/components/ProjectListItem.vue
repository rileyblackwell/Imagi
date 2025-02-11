<template>
  <div 
    class="block p-4 rounded-lg hover:bg-dark-700 transition-colors duration-200 cursor-pointer"
    @click="$emit('click')"
  >
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-lg font-semibold text-white">{{ project.name }}</h3>
        <p class="text-sm text-gray-400">{{ project.description || 'No description' }}</p>
      </div>
      <div class="text-sm text-gray-500">
        {{ formatDateWithStyle(project.created_at, 'relative') }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'
import { formatDateWithStyle } from '@/shared/utils/date'

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
