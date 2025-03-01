<template>
  <div class="h-full flex flex-col">
    <!-- Editor Header -->
    <div class="shrink-0 p-4 border-b border-dark-800 flex items-center justify-between">
      <div class="flex items-center space-x-4">
        <!-- File Info -->
        <div v-if="file" class="flex items-center space-x-2">
          <i :class="[
            'fas',
            getFileIcon(file.type),
            'text-gray-400'
          ]" />
          <span class="text-sm font-medium text-gray-200">
            {{ file.path.split('/').pop() }}
          </span>
        </div>
        <div v-else class="text-sm text-gray-400">
          No file selected
        </div>
      </div>

      <!-- Editor Controls -->
      <div class="flex items-center space-x-2">
        <button
          v-for="mode in editorModes"
          :key="mode"
          class="px-3 py-1.5 text-sm rounded-md transition-colors"
          :class="[
            editorMode === mode
              ? 'bg-primary-500/20 text-primary-400'
              : 'hover:bg-dark-800 text-gray-400 hover:text-gray-300'
          ]"
          @click="$emit('update:editorMode', mode)"
        >
          {{ formatEditorMode(mode) }}
        </button>
      </div>
    </div>

    <!-- Editor Content -->
    <div class="flex-1 overflow-hidden">
      <div 
        class="h-full"
        :class="{
          'grid grid-cols-2 divide-x divide-dark-800': editorMode === 'split',
          'block': editorMode !== 'split'
        }"
      >
        <!-- Code Editor -->
        <div 
          v-show="editorMode !== 'preview'"
          class="h-full overflow-auto"
        >
          <textarea
            v-model="localContent"
            class="w-full h-full bg-dark-900 text-gray-200 p-4 font-mono text-sm resize-none focus:outline-none"
            :placeholder="file ? 'Start coding...' : 'Select a file to start editing'"
            :spellcheck="false"
            @input="handleChange"
            @keydown.tab.prevent="handleTab"
          />
        </div>

        <!-- Preview Panel -->
        <div 
          v-show="editorMode !== 'editor'"
          class="h-full overflow-auto"
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

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
  if (newValue !== localContent.value) {
    localContent.value = newValue
  }
})

// Utility functions
const getFileIcon = (type?: string) => {
  const iconMap: Record<string, string> = {
    'js': 'fa-js',
    'ts': 'fa-js',
    'vue': 'fa-vuejs',
    'html': 'fa-html5',
    'css': 'fa-css3',
    'scss': 'fa-css3',
    'json': 'fa-code',
    'md': 'fa-markdown'
  }
  
  if (!type) return 'fa-file'
  return iconMap[type.toLowerCase()] || 'fa-file'
}

const formatEditorMode = (mode: EditorMode) => {
  const modeMap: Record<EditorMode, string> = {
    'editor': 'Code',
    'split': 'Split',
    'preview': 'Preview'
  }
  return modeMap[mode]
}

// Event handlers
const handleChange = (event: Event) => {
  const content = (event.target as HTMLTextAreaElement).value
  localContent.value = content
  emit('update:modelValue', content)
  emit('change', content)
}

const handleTab = (event: KeyboardEvent) => {
  const target = event.target as HTMLTextAreaElement
  const start = target.selectionStart
  const end = target.selectionEnd

  // Insert two spaces for tab
  const spaces = '  '
  localContent.value = localContent.value.substring(0, start) + spaces + localContent.value.substring(end)
  
  // Move cursor after the inserted spaces
  setTimeout(() => {
    target.selectionStart = target.selectionEnd = start + spaces.length
  }, 0)
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
</style> 