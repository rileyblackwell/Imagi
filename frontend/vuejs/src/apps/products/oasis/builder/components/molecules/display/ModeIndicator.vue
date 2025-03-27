<!--
  ModeIndicator.vue - Display current mode, file, and model information
  
  This component shows:
  1. Current mode (chat or build)
  2. Selected file (when in build mode)
  3. Selected AI model
-->
<template>
  <div class="space-y-3">
    <!-- Indicators - Removed the "Conversation History" and file path header -->
    <div class="flex items-center gap-3 py-2 px-4 bg-dark-850/90 backdrop-blur-sm rounded-lg border border-dark-700/60 shadow-md">
      <!-- Mode indicator with enhanced styling -->
      <div class="flex items-center">
        <div
          :class="[
            'flex items-center justify-center w-9 h-9 rounded-full mr-2.5',
            mode === 'chat' 
              ? 'bg-violet-500/20 text-violet-400 border border-violet-400/30' 
              : 'bg-emerald-500/20 text-emerald-400 border border-emerald-400/30'
          ]"
        >
          <i :class="[mode === 'chat' ? 'fas fa-comment-alt' : 'fas fa-code']"></i>
        </div>
        <div>
          <div class="text-[10px] text-gray-500 uppercase tracking-wide font-medium">Mode</div>
          <div class="text-sm font-medium" :class="[
            mode === 'chat' ? 'text-violet-400' : 'text-emerald-400'
          ]">
            {{ mode === 'chat' ? 'Chat' : 'Build' }}
            <span v-if="mode === 'build' && selectedFile" class="text-xs ml-1 opacity-80">
              ({{ fileTypeLabel }})
            </span>
          </div>
        </div>
      </div>

      <!-- File information when available -->
      <div v-if="selectedFile" class="flex items-center">
        <div
          class="flex items-center justify-center w-9 h-9 rounded-full mr-2.5 bg-blue-500/20 text-blue-400 border border-blue-400/30"
        >
          <i class="fas fa-file-code"></i>
        </div>
        <div>
          <div class="text-[10px] text-gray-500 uppercase tracking-wide font-medium">File</div>
          <div class="text-sm font-medium text-blue-400 truncate max-w-[120px]">
            {{ getFilename(selectedFile.path) }}
          </div>
        </div>
      </div>

      <!-- Separator with gradient styling -->
      <div class="h-8 w-px bg-gradient-to-b from-dark-700/10 via-dark-700/40 to-dark-700/10 mx-0.5"></div>

      <!-- Model information with enhanced styling -->
      <div v-if="selectedModelId" class="flex items-center">
        <div
          class="flex items-center justify-center w-9 h-9 rounded-full mr-2.5 bg-primary-500/20 text-primary-400 border border-primary-400/30"
        >
          <i class="fas fa-robot"></i>
        </div>
        <div>
          <div class="text-[10px] text-gray-500 uppercase tracking-wide font-medium">Model</div>
          <div class="text-sm font-medium text-primary-400">
            {{ formattedModelName }}
            <span class="inline-flex items-center ml-1.5 px-1.5 py-0.5 rounded-full text-[10px] font-medium bg-primary-500/10 text-primary-300 border border-primary-500/20">
              <i class="fas fa-bolt mr-1 text-[8px]"></i>AI
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AIModel } from '../../../types/services'
import type { SelectedFile } from '../../../types/components'

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

// Format model name for display (shorten if needed)
const formattedModelName = computed(() => {
  const name = selectedModelName.value;
  
  // Common replacements for better display
  if (name.includes('claude-3-')) {
    return name.replace('claude-3-', 'Claude 3 ').replace('-20250219', '');
  }
  
  if (name.includes('gpt-4')) {
    return name.replace('gpt-4', 'GPT-4').replace('-preview', '');
  }
  
  if (name.includes('gpt-3.5')) {
    return 'GPT-3.5';
  }
  
  // If name is longer than 15 chars, trim it
  if (name.length > 15) {
    return name.substring(0, 12) + '...';
  }
  
  return name;
});

// Get just the filename from a path
function getFilename(path: string): string {
  if (!path) return '';
  // Extract the filename from the path
  const parts = path.split('/');
  return parts[parts.length - 1];
}

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
    'vue': 'Vue Component',
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