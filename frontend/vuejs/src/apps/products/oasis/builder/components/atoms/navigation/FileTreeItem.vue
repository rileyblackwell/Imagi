<template>
  <button
    class="w-full flex items-center px-2 py-1 rounded-md text-left transition-colors text-xs"
    :class="[
      isSelected 
        ? 'bg-primary-500/20 text-white border border-primary-500/30' 
        : 'text-gray-300 hover:text-white hover:bg-dark-800/80 border border-transparent'
    ]"
    @click="$emit('select', file)"
  >
    <!-- File Icon -->
    <i 
      class="fas mr-1.5 w-4 text-center"
      :class="fileIcon"
    />
    
    <!-- File Name with Directory Badge -->
    <div class="flex items-center flex-1 min-w-0">
      <!-- Directory badge -->
      <span 
        v-if="fileDirectory" 
        class="mr-1.5 text-xxs px-1 py-0.5 rounded bg-dark-700/80 text-primary-300 font-medium"
      >
        {{ fileDirectory }}
      </span>
      
      <!-- File name -->
      <span class="truncate">{{ fileName }}</span>
    </div>
    
    <!-- File Status Indicators -->
    <div class="ml-auto flex items-center space-x-1">
      <span 
        v-if="hasUnsavedChanges"
        class="w-1.5 h-1.5 rounded-full bg-yellow-500"
        title="Unsaved changes"
      />
    </div>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ProjectFile } from '../../../types/builder'

const props = defineProps<{
  file: ProjectFile
  isSelected?: boolean
  hasUnsavedChanges?: boolean
}>()

const emit = defineEmits<{
  (e: 'select', file: ProjectFile): void
}>()

const fileName = computed(() => {
  const parts = props.file.path.split('/')
  // Return just the filename, not the full path
  return parts[parts.length - 1] || props.file.path
})

// Get the directory part for badge display
const fileDirectory = computed(() => {
  const parts = props.file.path.split('/')
  if (parts.length > 1) {
    // Return the first directory
    if (parts[0] === 'templates') return 'template'
    if (parts[0] === 'static' && parts[1] === 'css') return 'css'
    return parts[0]
  }
  return null
})

const fileIcon = computed(() => {
  // Get file extension
  const extension = props.file.path.split('.').pop()?.toLowerCase() || ''
  
  // Icon based on file type
  if (extension === 'html') {
    return 'fa-file-code text-orange-400'
  } else if (extension === 'css') {
    return 'fa-file-code text-blue-400'
  } else if (props.file.path.endsWith('/')) {
    return 'fa-folder text-yellow-500'
  }
  
  return 'fa-file text-gray-500'
})
</script>

<style scoped>
.text-xxs {
  font-size: 0.65rem;
  line-height: 1rem;
}
</style>