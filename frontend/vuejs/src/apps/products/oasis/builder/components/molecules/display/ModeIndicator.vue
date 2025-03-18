<!--
  ModeIndicator.vue - Display current mode, file, and model information
  
  This component shows:
  1. Current mode (chat or build)
  2. Selected file (when in build mode)
  3. Selected AI model
-->
<template>
  <div class="mode-indicator flex items-center gap-2 text-xs text-gray-400">
    <!-- Mode Indicator -->
    <div class="flex items-center gap-1.5">
      <div 
        class="w-2 h-2 rounded-full"
        :class="[
          mode === 'chat' ? 'bg-emerald-500' : 'bg-blue-500'
        ]"
      ></div>
      <span class="font-medium">
        {{ mode === 'chat' ? 'Chat Mode' : 'Build Mode' }}
      </span>
    </div>
    
    <!-- File Indicator (Only in build mode) -->
    <template v-if="mode === 'build' && selectedFile">
      <span class="text-gray-500">|</span>
      <div class="flex items-center gap-1">
        <i class="fas fa-file-code text-gray-500"></i>
        <span class="truncate max-w-[150px]">{{ selectedFile.path }}</span>
      </div>
    </template>
    
    <!-- Model Indicator -->
    <template v-if="selectedModelId">
      <span class="text-gray-500">|</span>
      <div class="flex items-center gap-1">
        <i class="fas fa-microchip text-gray-500"></i>
        <span>{{ modelName }}</span>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { BuilderMode } from '../../../types'
import type { AIModel } from '../../../types/builder'

// Define a compatible type that matches the file interface
interface SelectedFile {
  path: string;
  type: string;
  content: string;
  lastModified?: string;
  id?: string;
  name?: string;
}

// Props
const props = defineProps<{
  mode: BuilderMode
  selectedFile: SelectedFile | null
  selectedModelId: string | null
  availableModels: AIModel[]
}>()

// Computed properties
const modelName = computed(() => {
  if (!props.selectedModelId || !props.availableModels?.length) return 'AI Model'
  
  const model = props.availableModels.find(m => m.id === props.selectedModelId)
  return model?.name || 'AI Model'
})
</script>

<style scoped>
.mode-indicator {
  white-space: nowrap;
}
</style> 