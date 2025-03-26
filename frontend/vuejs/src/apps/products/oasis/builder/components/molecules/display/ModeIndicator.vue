<!--
  ModeIndicator.vue - Display current mode, file, and model information
  
  This component shows:
  1. Current mode (chat or build)
  2. Selected file (when in build mode)
  3. Selected AI model
-->
<template>
  <div class="flex items-center space-x-2 py-1 px-2 bg-dark-850/80 rounded-lg">
    <!-- Mode indicator -->
    <div class="flex items-center">
      <div
        :class="[
          'flex items-center justify-center w-7 h-7 rounded-full mr-2',
          mode === 'chat' ? 'bg-violet-500/20 text-violet-400' : 'bg-emerald-500/20 text-emerald-400'
        ]"
      >
        <i :class="[mode === 'chat' ? 'fas fa-comment-alt' : 'fas fa-code']"></i>
      </div>
      <div>
        <div class="text-xs text-gray-400">Mode:</div>
        <div class="text-sm font-medium" :class="[
          mode === 'chat' ? 'text-violet-400' : 'text-emerald-400'
        ]">
          {{ mode === 'chat' ? 'Chat' : 'Build' }}
          <span v-if="mode === 'build' && selectedFile" class="text-xs ml-1">
            ({{ fileTypeLabel }})
          </span>
        </div>
      </div>
    </div>

    <!-- Model information -->
    <div v-if="selectedModelId" class="flex items-center border-l border-dark-700 pl-3 ml-1">
      <div
        class="flex items-center justify-center w-7 h-7 rounded-full mr-2 bg-primary-500/20 text-primary-400"
      >
        <i class="fas fa-robot"></i>
      </div>
      <div>
        <div class="text-xs text-gray-400">Model:</div>
        <div class="text-sm font-medium text-primary-400">
          {{ selectedModelName }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AIModel } from '../../../types/builder'

interface SelectedFile {
  path: string;
  type: string;
  content?: string;
  lastModified?: string;
  id?: string;
  name?: string;
}

const props = defineProps<{
  mode: string;
  selectedModelId: string | null;
  selectedFile: SelectedFile | null;
  availableModels: AIModel[];
}>();

// Get the selected model name based on the ID
const selectedModelName = computed(() => {
  if (!props.selectedModelId) return 'None';
  
  const model = props.availableModels.find(m => m.id === props.selectedModelId);
  return model ? model.name : props.selectedModelId;
});

// Determine file type label
const fileTypeLabel = computed(() => {
  if (!props.selectedFile) return '';
  
  const fileName = props.selectedFile.path;
  const extension = fileName.split('.').pop()?.toLowerCase() || '';
  
  const fileTypeMap: Record<string, string> = {
    'html': 'HTML Template',
    'htm': 'HTML Template',
    'django-html': 'Django Template',
    'jinja': 'Template',
    'css': 'CSS Stylesheet',
    'scss': 'SCSS Stylesheet',
    'js': 'JavaScript',
    'ts': 'TypeScript',
    'json': 'JSON',
    'md': 'Markdown',
    'py': 'Python'
  };
  
  return fileTypeMap[extension] || extension.toUpperCase();
});
</script>

<style scoped>
.mode-indicator {
  white-space: nowrap;
}
</style> 