<template>
  <button
    class="w-full flex items-center px-2 py-1.5 rounded-lg text-left transition-colors"
    :class="[
      isSelected 
        ? 'bg-primary-500/20 text-white' 
        : 'text-gray-400 hover:text-white hover:bg-dark-800'
    ]"
    @click="$emit('select', file)"
  >
    <!-- File Icon -->
    <i 
      class="fas mr-2"
      :class="[
        file.path.endsWith('/') 
          ? 'fa-folder text-yellow-500' 
          : `fa-file text-${fileIconColor}`
      ]"
    />
    
    <!-- File Name -->
    <span class="truncate">{{ fileName }}</span>
    
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
import type { ProjectFile } from '../../types/builder'

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
  return parts[parts.length - 1] || parts[parts.length - 2]
})

const fileIconColor = computed(() => {
  const extensionMap: Record<string, string> = {
    '.ts': 'blue-500',
    '.js': 'yellow-500',
    '.vue': 'green-500',
    '.css': 'pink-500',
    '.html': 'orange-500',
    '.json': 'purple-500'
  }
  
  const extension = props.file.path.split('.').pop()
  return extensionMap[`.${extension}`] || 'gray-500'
})
</script>