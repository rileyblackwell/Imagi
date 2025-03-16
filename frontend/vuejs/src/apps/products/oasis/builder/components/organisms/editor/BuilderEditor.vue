<template>
  <div class="h-full flex flex-col bg-dark-950 relative">
    <!-- Background effects -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-primary-900/20 to-transparent opacity-30"></div>
      <div class="absolute -top-20 -right-20 w-72 h-72 bg-gradient-to-br from-primary-400 to-violet-600 rounded-full filter blur-3xl opacity-10 animate-pulse-slow"></div>
    </div>

    <!-- Editor Header -->
    <div class="shrink-0 px-4 py-3 border-b border-dark-800/70 bg-dark-900/50 backdrop-blur-md flex items-center justify-between shadow-md relative z-10 overflow-hidden">
      <!-- Gradient header line -->
      <div class="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-primary-500/50 to-transparent"></div>
      
      <div class="flex items-center space-x-4">
        <!-- File Info -->
        <div v-if="file" class="flex items-center space-x-2">
          <div class="w-6 h-6 flex items-center justify-center rounded-md bg-dark-800/70 shadow-sm border border-dark-700/50">
            <i :class="[
              'fas',
              getFileIcon(file.type),
              'text-primary-400'
            ]" />
          </div>
          <span class="text-sm font-medium text-gray-200">
            {{ file.path.split('/').pop() }}
            <span class="text-xs text-gray-500 ml-1">{{ getFileExtension(file.path) }}</span>
          </span>
        </div>
        <div v-else class="text-sm text-gray-400">
          No file selected
        </div>
      </div>

      <!-- Editor Controls -->
      <div class="flex items-center space-x-1">
        <button
          v-for="mode in editorModes"
          :key="mode"
          class="px-3 py-1.5 text-sm rounded-md transition-all duration-200 backdrop-blur-sm"
          :class="[
            editorMode === mode
              ? 'bg-primary-500/30 text-primary-300 shadow-sm border border-primary-500/20'
              : 'hover:bg-dark-800/70 text-gray-400 hover:text-gray-300 border border-transparent'
          ]"
          @click="$emit('update:editorMode', mode)"
        >
          <i :class="['fas mr-1.5', getModeIcon(mode)]"></i>
          {{ formatEditorMode(mode) }}
        </button>
        
        <!-- Save Button -->
        <button
          class="ml-2 px-3 py-1.5 text-sm rounded-md bg-primary-500/20 hover:bg-primary-500/30 text-primary-300 transition-all duration-200 flex items-center border border-primary-500/20 shadow-sm"
          @click="$emit('save')"
          title="Save changes (Ctrl+S)"
        >
          <i class="fas fa-save mr-1.5"></i>
          Save
        </button>
      </div>
    </div>

    <!-- Editor Content -->
    <div class="flex-1 overflow-hidden">
      <div 
        class="h-full"
        :class="{
          'grid grid-cols-2 divide-x divide-dark-800/50': editorMode === 'split',
          'block': editorMode !== 'split'
        }"
      >
        <!-- Code Editor -->
        <div 
          v-show="editorMode !== 'preview'"
          class="h-full overflow-auto bg-dark-950/80 backdrop-blur-sm"
        >
          <textarea
            v-model="localContent"
            class="w-full h-full bg-transparent text-gray-200 p-4 font-mono text-sm resize-none focus:outline-none leading-relaxed"
            :placeholder="file ? 'Start coding...' : 'Select a file to start editing'"
            :spellcheck="false"
            @input="handleChange"
            @keydown.tab.prevent="handleTab"
          />
        </div>

        <!-- Preview Panel -->
        <div 
          v-show="editorMode !== 'editor'"
          class="h-full overflow-auto bg-dark-900/30 backdrop-blur-sm"
        >
          <div class="p-4">
            <PreviewPanel
              :content="localContent"
              :file-type="file?.type"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import PreviewPanel from '../preview/PreviewPanel.vue'
import type { ProjectFile } from '@/apps/products/oasis/builder/types/builder'
import type { EditorMode } from '@/apps/products/oasis/builder/types/builder'

const props = defineProps<{
  modelValue: string
  file: ProjectFile | null
  editorMode: EditorMode
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'update:editorMode', mode: EditorMode): void
  (e: 'change', content: string): void
  (e: 'save'): void
}>()

// Local state
const localContent = ref(props.modelValue)
const editorModes: EditorMode[] = ['editor', 'split', 'preview']

// Watch for external changes to modelValue
watch(() => props.modelValue, (newValue) => {
  localContent.value = newValue
})

// Handle content changes
const handleChange = () => {
  emit('update:modelValue', localContent.value)
  emit('change', localContent.value)
}

// Handle tab key in textarea
const handleTab = (e: KeyboardEvent) => {
  const target = e.target as HTMLTextAreaElement
  const start = target.selectionStart
  const end = target.selectionEnd
  
  // Insert tab at cursor position
  localContent.value = 
    localContent.value.substring(0, start) + 
    '  ' + 
    localContent.value.substring(end)
  
  // Move cursor after the inserted tab
  setTimeout(() => {
    target.selectionStart = target.selectionEnd = start + 2
  }, 0)
}

// Format editor mode for display
const formatEditorMode = (mode: EditorMode): string => {
  switch (mode) {
    case 'editor': return 'Code'
    case 'split': return 'Split'
    case 'preview': return 'Preview'
    default: return mode
  }
}

// Get icon for editor mode
const getModeIcon = (mode: EditorMode): string => {
  switch (mode) {
    case 'editor': return 'fa-code'
    case 'split': return 'fa-columns'
    case 'preview': return 'fa-eye'
    default: return 'fa-code'
  }
}

// Get file icon based on file type
const getFileIcon = (fileType?: string): string => {
  if (!fileType) return 'fa-file'
  
  switch (fileType.toLowerCase()) {
    case 'html': return 'fa-html5'
    case 'css': return 'fa-css3-alt'
    case 'js': return 'fa-js'
    case 'ts': return 'fa-code'
    case 'vue': return 'fa-vuejs'
    case 'json': return 'fa-file-code'
    case 'md': return 'fa-file-alt'
    default: return 'fa-file-code'
  }
}

// Get file extension from path
const getFileExtension = (path?: string): string => {
  if (!path) return ''
  const parts = path.split('.')
  return parts.length > 1 ? `.${parts[parts.length - 1]}` : ''
}
</script>

<style scoped>
textarea {
  tab-size: 2;
  -moz-tab-size: 2;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  line-height: 1.5;
  font-size: 0.875rem;
}

/* Custom scrollbar */
textarea::-webkit-scrollbar,
div::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

textarea::-webkit-scrollbar-track,
div::-webkit-scrollbar-track {
  background: rgba(30, 30, 46, 0.6);
}

textarea::-webkit-scrollbar-thumb,
div::-webkit-scrollbar-thumb {
  background: rgba(90, 90, 120, 0.4);
  border-radius: 4px;
}

textarea::-webkit-scrollbar-thumb:hover,
div::-webkit-scrollbar-thumb:hover {
  background: rgba(124, 58, 237, 0.4);
}

@keyframes pulse-slow {
  0%, 100% {
    opacity: 0.1;
  }
  50% {
    opacity: 0.2;
  }
}

.animate-pulse-slow {
  animation: pulse-slow 8s infinite;
}
</style> 