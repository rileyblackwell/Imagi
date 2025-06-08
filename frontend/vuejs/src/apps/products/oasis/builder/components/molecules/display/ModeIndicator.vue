<!--
  ModeIndicator.vue - Display current mode, file, and model information
  
  This component shows:
  1. Current mode (chat or build)
  2. Selected file (when in build mode)
  3. Selected AI model
-->
<template>
  <div class="space-y-3">
    <!-- Enhanced Indicators with modern glassmorphism design -->
    <div class="relative group">
      <!-- Subtle glow effect -->
      <div class="absolute -inset-0.5 bg-gradient-to-r from-indigo-500/10 to-violet-500/10 rounded-2xl opacity-0 group-hover:opacity-50 blur transition-all duration-300 pointer-events-none"></div>
      
      <!-- Main indicator container -->
      <div class="relative flex items-center gap-4 py-3 px-4 bg-gradient-to-br from-dark-850/90 via-dark-900/80 to-dark-850/90 backdrop-blur-xl rounded-2xl border border-white/10 shadow-xl transition-all duration-300 hover:border-white/20">
        <!-- Sleek gradient top line -->
        <div class="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-indigo-400/30 via-violet-400/30 to-indigo-400/30 opacity-50 rounded-t-2xl"></div>
        
        <!-- Mode indicator with enhanced styling -->
        <div class="flex items-center">
          <div
            :class="[
              'flex items-center justify-center w-10 h-10 rounded-xl mr-3 border transition-all duration-200',
              mode === 'chat' 
                ? 'bg-gradient-to-br from-violet-500/20 to-indigo-500/20 text-violet-400 border-violet-400/30 shadow-lg shadow-violet-500/10' 
                : 'bg-gradient-to-br from-emerald-500/20 to-teal-500/20 text-emerald-400 border-emerald-400/30 shadow-lg shadow-emerald-500/10'
            ]"
          >
            <i :class="[mode === 'chat' ? 'fas fa-comment-alt' : 'fas fa-code', 'text-sm']"></i>
          </div>
          <div>
            <div class="text-[10px] text-gray-400 uppercase tracking-wider font-medium mb-0.5">Mode</div>
            <div class="text-sm font-semibold" :class="[
              mode === 'chat' ? 'text-violet-300' : 'text-emerald-300'
            ]">
              {{ mode === 'chat' ? 'Chat' : 'Build' }}
              <span v-if="mode === 'build' && selectedFile" class="text-xs ml-1.5 opacity-70 font-normal">
                ({{ fileTypeLabel }})
              </span>
            </div>
          </div>
        </div>

        <!-- File information when available -->
        <div v-if="selectedFile" class="flex items-center">
          <div
            class="flex items-center justify-center w-10 h-10 rounded-xl mr-3 bg-gradient-to-br from-blue-500/20 to-cyan-500/20 text-blue-400 border border-blue-400/30 shadow-lg shadow-blue-500/10 transition-all duration-200"
          >
            <i class="fas fa-file-code text-sm"></i>
          </div>
          <div>
            <div class="text-[10px] text-gray-400 uppercase tracking-wider font-medium mb-0.5">File</div>
            <div class="text-sm font-semibold text-blue-300 truncate max-w-[120px]">
              {{ getFilename(selectedFile.path) }}
            </div>
          </div>
        </div>

        <!-- Enhanced separator with gradient styling -->
        <div class="h-10 w-px bg-gradient-to-b from-transparent via-white/20 to-transparent mx-1"></div>

        <!-- Model information with enhanced styling -->
        <div v-if="selectedModelId" class="flex items-center">
          <div
            class="flex items-center justify-center w-10 h-10 rounded-xl mr-3 bg-gradient-to-br from-indigo-500/20 to-violet-500/20 text-indigo-400 border border-indigo-400/30 shadow-lg shadow-indigo-500/10 transition-all duration-200"
          >
            <i class="fas fa-robot text-sm"></i>
          </div>
          <div>
            <div class="text-[10px] text-gray-400 uppercase tracking-wider font-medium mb-0.5">Model</div>
            <div class="text-sm font-semibold text-indigo-300 flex items-center">
              {{ formattedModelName }}
              <span class="inline-flex items-center ml-2 px-2 py-0.5 rounded-lg text-[10px] font-medium bg-gradient-to-r from-indigo-500/15 to-violet-500/15 text-indigo-200 border border-indigo-500/20 shadow-sm">
                <i class="fas fa-bolt mr-1 text-[8px]"></i>AI
              </span>
            </div>
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