<template>
  <div 
    class="group block p-4 rounded-lg hover:bg-dark-700/60 transition-all duration-200 cursor-pointer border border-transparent hover:border-indigo-500/20"
    @click="$emit('click')"
  >
    <div class="flex items-center justify-between">
      <!-- Project info section -->
      <div class="flex-1 pr-4">
        <!-- Project name with hover effect -->
        <h3 class="text-lg font-bold text-white group-hover:text-indigo-400/90 transition-colors truncate">{{ project.name }}</h3>
        
        <!-- Last modified date -->
        <div class="flex items-center gap-2 text-xs text-gray-400 mt-1 group-hover:text-indigo-300 transition-colors">
          <i class="fas fa-clock"></i>
          <span>Last modified: {{ formatDate(project.updated_at) }}</span>
        </div>
        
        <!-- Project description with line clamp -->
        <p v-if="project.description" class="text-gray-400 text-xs mt-2 line-clamp-1 group-hover:text-gray-300 transition-colors">
          {{ project.description }}
        </p>
        <p v-else class="text-gray-500 text-xs mt-2 italic">No description provided</p>
      </div>
      
      <!-- Action button -->
      <div class="flex items-center justify-center">
        <div class="w-8 h-8 rounded-lg flex items-center justify-center text-indigo-400 group-hover:text-white bg-indigo-500/10 group-hover:bg-indigo-500/20 transition-colors">
          <i class="fas fa-arrow-right text-sm"></i>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// defineProps and defineEmits are compiler macros and don't need to be imported
import type { Project } from '../../../types/components'

defineProps<{
  project: Project
}>()

defineEmits<{
  (e: 'click'): void
}>()

/**
 * Format a date string into a readable format
 * @param date Optional date string to format
 * @returns Formatted date string
 */
function formatDate(date?: string) {
  if (!date) return 'No date available';
  
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(date));
}
</script>
