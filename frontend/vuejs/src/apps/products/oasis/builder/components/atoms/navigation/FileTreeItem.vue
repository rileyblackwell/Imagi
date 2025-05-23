<template>
  <button
    class="group w-full flex items-center px-2 py-1.5 rounded-md text-left transition-all duration-200 text-xs relative"
    :class="[
      isSelected 
        ? 'bg-gradient-to-r from-primary-500/20 to-violet-500/10 text-white border border-primary-500/30' 
        : 'text-gray-300 hover:text-white hover:bg-dark-800/80 hover:border-primary-500/20 border border-transparent'
    ]"
    @click="$emit('select', file)"
  >
    <!-- Subtle glow effect when selected -->
    <div v-if="isSelected" class="absolute -inset-0.5 bg-primary-500/10 rounded-md blur opacity-50"></div>
    
    <!-- File Icon -->
    <i 
      class="fas mr-1.5 w-4 text-center relative"
      :class="fileIcon"
    />
    
    <!-- File Name with Directory Badge -->
    <div class="flex items-center flex-1 min-w-0 relative">
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
    
    <!-- File Status Indicators and Actions -->
    <div class="ml-auto flex items-center space-x-1 relative">
      <span 
        v-if="hasUnsavedChanges"
        class="w-1.5 h-1.5 rounded-full bg-yellow-500"
        title="Unsaved changes"
      />
      
      <!-- Delete button with improved hover effect -->
      <button
        class="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded transition-all duration-200"
        title="Delete file"
        @click.stop="$emit('delete', file)"
        aria-label="Delete file"
      >
        <i class="fas fa-trash-alt text-xs"></i>
      </button>
    </div>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ProjectFile } from '../../../types/components'

const props = defineProps<{
  file: ProjectFile
  isSelected?: boolean
  hasUnsavedChanges?: boolean
}>()

const emit = defineEmits<{
  (e: 'select', file: ProjectFile): void
  (e: 'delete', file: ProjectFile): void
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
  } else if (extension === 'js' || extension === 'ts') {
    return 'fa-file-code text-yellow-400'
  } else if (extension === 'json') {
    return 'fa-file-code text-green-400'
  } else if (extension === 'md') {
    return 'fa-file-alt text-gray-400'
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

/* Make the parent a group to enable hover effects on children */
button {
  position: relative;
  transition: all 0.2s ease-in-out;
  overflow: hidden;
}

/* Ensure delete button is visible on hover */
button:hover .opacity-0 {
  opacity: 1 !important;
}

/* Add slight pulse animation to selected item */
@keyframes subtle-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0); }
  50% { box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1); }
}

.border-primary-500\/30 {
  animation: subtle-pulse 3s infinite ease-in-out;
}
</style>