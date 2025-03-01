<template>
  <div class="h-full flex flex-col bg-dark-900 border-r border-dark-700">
    <!-- Content that adapts to collapsed state -->
    <div class="flex-1 overflow-y-auto overflow-x-hidden relative">
      <template v-if="!isCollapsed">
        <!-- Project Info -->
        <div class="p-4 border-b border-dark-700">
          <div class="flex items-center space-x-2">
            <div class="w-8 h-8 rounded-full bg-primary-500/20 flex items-center justify-center text-primary-400">
              <i class="fas fa-project-diagram"></i>
            </div>
            <div class="truncate">
              <h3 class="font-medium text-gray-200 truncate">
                {{ currentProject?.name || 'Untitled Project' }}
              </h3>
              <p class="text-xs text-gray-500">
                {{ currentProject?.description || 'No description' }}
              </p>
            </div>
          </div>
        </div>
        
        <!-- AI Model Selection -->
        <div class="p-4 border-b border-dark-700">
          <h4 class="text-xs font-medium text-gray-500 uppercase mb-2">AI Model</h4>
          <ModelSelector
            :models="models"
            :model-id="modelId"
            :mode="mode"
            @update:model-id="handleModelChange"
          />
        </div>
        
        <!-- Mode Toggle -->
        <div class="p-4 border-b border-dark-700">
          <h4 class="text-xs font-medium text-gray-500 uppercase mb-2">Mode</h4>
          <ModeSelector
            :mode="mode"
            :modes="modes"
            @update:mode="handleModeChange"
          />
        </div>

        <!-- File Explorer -->
        <div class="p-4">
          <h4 class="text-xs font-medium text-gray-500 uppercase mb-2">Project Files</h4>
          <FileExplorer
            :files="files"
            :selected-file="selectedFile"
            :show-new-form="showNewFileFormValue"
            :file-types="fileTypes"
            @select-file="$emit('selectFile', $event)"
            @create-file="$emit('createFile', $event)"
          />
        </div>
      </template>

      <!-- Collapsed State Icons -->
      <template v-else>
        <div class="py-4 flex flex-col items-center space-y-6">
          <!-- Project Icon -->
          <div class="w-8 h-8 rounded-full bg-primary-500/20 flex items-center justify-center text-primary-400">
            <i class="fas fa-project-diagram"></i>
          </div>
          
          <!-- Model Icon -->
          <IconButton
            icon-class="fa-robot"
            size="sm"
            :variant="modelId ? 'primary' : 'default'"
            :title="'AI Model: ' + (selectedModel?.name || 'Select Model')"
          />
          
          <!-- Mode Icons -->
          <div class="space-y-2">
            <IconButton
              v-for="modeOption in modes"
              :key="modeOption"
              :icon-class="getModeIcon(modeOption)"
              :variant="mode === modeOption ? 'primary' : 'default'"
              :title="formatMode(modeOption)"
              size="sm"
              @click="handleModeChange(modeOption)"
            />
          </div>

          <!-- File Icon -->
          <IconButton
            icon-class="fa-folder"
            :variant="selectedFile ? 'primary' : 'default'"
            title="Project Files"
            size="sm"
          />

          <!-- Action Icons -->
          <div class="space-y-2">
            <IconButton
              icon-class="fa-eye"
              :variant="currentEditorMode === 'preview' ? 'primary' : 'default'"
              title="Preview App"
              size="sm"
              @click="$emit('preview')"
            />
            <IconButton
              icon-class="fa-undo"
              :variant="'default'"
              title="Undo Last Change"
              size="sm"
              :disabled="isLoading"
              @click="$emit('undo')"
            />
          </div>
        </div>
      </template>
    </div>

    <!-- Action Buttons (only shown when expanded) -->
    <div v-if="!isCollapsed" class="shrink-0 border-t border-dark-700 p-4 space-y-3">
      <ActionButton
        title="Preview Application"
        icon="eye"
        text="Preview App"
        :variant="currentEditorMode === 'preview' ? 'primary' : 'default'"
        :full-width="true"
        @click="$emit('preview')"
      />
      <ActionButton
        title="Undo Last Change"
        icon="undo"
        text="Undo Last Change"
        variant="default"
        :full-width="true"
        :disabled="isLoading"
        @click="$emit('undo')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import ModelSelector from '@/apps/products/oasis/builder/components/molecules/sidebar/ModelSelector.vue'
import ModeSelector from '@/apps/products/oasis/builder/components/molecules/sidebar/ModeSelector.vue'
import FileExplorer from '@/apps/products/oasis/builder/components/molecules/sidebar/FileExplorer.vue'
import { ActionButton, IconButton } from '@/apps/products/oasis/builder/components'
import type { 
  AIModel, 
  BuilderMode,
  ProjectFile,
  EditorMode,
  ProjectType
} from '@/apps/products/oasis/builder/types/builder'

// Local state
const showNewFileFormValue = ref(false)
const modes: BuilderMode[] = ['chat', 'build']

const props = defineProps<{
  currentProject: ProjectType | null
  models: AIModel[]
  modelId: string | null
  files: ProjectFile[]
  selectedFile: ProjectFile | null
  fileTypes: Record<string, string>
  isLoading: boolean
  mode: BuilderMode
  currentEditorMode?: EditorMode
  isCollapsed?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelId', value: string): void
  (e: 'update:mode', value: BuilderMode): void
  (e: 'selectFile', file: ProjectFile): void
  (e: 'createFile', data: { name: string; type: string }): void
  (e: 'undo'): void
  (e: 'preview'): void
}>()

const getModeIcon = (mode: BuilderMode): string => {
  const icons: Record<BuilderMode, string> = {
    chat: 'fa-comments',
    build: 'fa-code'
  }
  return icons[mode] || 'fa-code'
}

const formatMode = (mode: BuilderMode): string => {
  return mode.charAt(0).toUpperCase() + mode.slice(1)
}

// Compute selected model for collapsed state tooltip
const selectedModel = computed(() => 
  props.models.find(m => m.id === props.modelId)
)

// Add validation before emitting model changes
const handleModelChange = (modelId: string) => {
  const model = props.models.find(m => m.id === modelId)
  if (model) {
    emit('update:modelId', modelId)
  }
}

// Add validation before emitting mode changes
const handleModeChange = (mode: BuilderMode) => {
  if (['chat', 'build'].includes(mode)) {
    emit('update:mode', mode)
  }
}

// Computed property for mode options with icons
const modeOptions = computed(() => ([
  { id: 'chat', icon: 'fa-comments', label: 'Chat Mode' },
  { id: 'build', icon: 'fa-code', label: 'Build Mode' }
]))
</script>

<style scoped>
/* Hide scrollbar but allow scrolling */
.overflow-y-auto {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

.overflow-y-auto::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

/* Smooth transitions */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}
</style>
