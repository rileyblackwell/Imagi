<template>
  <div class="h-full flex flex-col bg-dark-900/90 backdrop-blur-sm border-r border-dark-700/70">
    <!-- Content that adapts to collapsed state -->
    <div class="flex-1 overflow-y-auto overflow-x-hidden relative">
      <template v-if="!isCollapsed">
        <!-- Project Info -->
        <div class="p-4 border-b border-dark-700/50">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500/30 to-primary-600/20 flex items-center justify-center text-primary-400 shadow-sm">
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
        <div class="p-4 border-b border-dark-700/50">
          <h4 class="text-xs font-medium text-gray-400 uppercase mb-3 flex items-center">
            <i class="fas fa-robot mr-1.5 text-primary-400/70"></i>
            AI Model
          </h4>
          <ModelSelector
            :models="models || []"
            :model-id="modelId"
            :mode="mode"
            @update:model-id="handleModelChange"
          />
          <!-- Debug info (hidden in production) -->
          <div v-if="false" class="mt-2 p-2 bg-dark-800 rounded text-xs text-gray-400">
            Models count: {{ models?.length || 0 }}
          </div>
        </div>
        
        <!-- Mode Toggle -->
        <div class="p-4 border-b border-dark-700/50">
          <h4 class="text-xs font-medium text-gray-400 uppercase mb-3 flex items-center">
            <i class="fas fa-code-branch mr-1.5 text-primary-400/70"></i>
            Mode
          </h4>
          <ModeSelector
            :mode="mode"
            :modes="modes"
            @update:mode="handleModeChange"
          />
        </div>

        <!-- File Explorer -->
        <div class="p-4">
          <h4 class="text-xs font-medium text-gray-400 uppercase mb-3 flex items-center">
            <i class="fas fa-folder-open mr-1.5 text-primary-400/70"></i>
            Project Files
          </h4>
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
        <div class="py-6 flex flex-col items-center space-y-8">
          <!-- Mode Icons (Chat and Build) -->
          <div class="space-y-6">
            <IconButton
              v-for="modeOption in modes"
              :key="modeOption"
              :icon-class="getModeIcon(modeOption)"
              :variant="mode === modeOption ? 'primary' : 'default'"
              :title="formatMode(modeOption) + ' Mode'"
              size="md"
              class-name="sidebar-collapsed-icon"
              :is-sidebar-icon="true"
              @click="handleModeChange(modeOption)"
            />
          </div>

          <!-- Action Icons (Undo and Preview) -->
          <div class="space-y-6">
            <IconButton
              icon-class="fa-undo"
              title="Undo Last Action"
              size="md"
              :variant="'default'"
              :disabled="isLoading"
              class-name="sidebar-collapsed-icon"
              :is-sidebar-icon="true"
              @click="$emit('undo')"
            />
            <IconButton
              icon-class="fa-eye"
              title="Preview Project"
              size="md"
              :variant="'default'"
              :disabled="isLoading"
              class-name="sidebar-collapsed-icon"
              :is-sidebar-icon="true"
              @click="$emit('preview')"
            />
          </div>
        </div>
      </template>
    </div>

    <!-- Bottom Actions (only visible when not collapsed) -->
    <div v-if="!isCollapsed" class="p-4 border-t border-dark-700/50 bg-dark-800/30">
      <div class="flex justify-between items-center">
        <button 
          @click="$emit('undo')"
          class="px-3 py-2 bg-dark-800 hover:bg-dark-700 text-gray-300 rounded-lg text-sm transition-colors flex items-center"
          :disabled="isLoading"
          :class="{'opacity-50 cursor-not-allowed': isLoading}"
        >
          <i class="fas fa-undo mr-2"></i>
          <span>Undo</span>
        </button>
        
        <button 
          @click="$emit('preview')"
          class="px-3 py-2 bg-primary-500/20 hover:bg-primary-500/30 text-primary-300 rounded-lg text-sm transition-colors flex items-center"
          :disabled="isLoading"
          :class="{'opacity-50 cursor-not-allowed': isLoading}"
        >
          <i class="fas fa-eye mr-2"></i>
          <span>Preview</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import ModelSelector from '@/apps/products/oasis/builder/components/molecules/sidebar/ModelSelector.vue'
import ModeSelector from '@/apps/products/oasis/builder/components/molecules/sidebar/ModeSelector.vue'
import FileExplorer from '@/apps/products/oasis/builder/components/molecules/sidebar/FileExplorer.vue'
import { ActionButton, IconButton } from '@/apps/products/oasis/builder/components'
import { AI_MODELS } from '@/apps/products/oasis/builder/types/builder'
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
  (e: 'createFile', data: { name: string; type: string; content?: string }): void
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
const selectedModel = computed(() => {
  // First try to find the model in the provided models
  const model = props.models.find(m => m.id === props.modelId)
  if (model) return model
  
  // If not found, check in the default models
  const defaultModel = AI_MODELS.find(m => m.id === props.modelId)
  return defaultModel || null
})

// Add validation before emitting model changes
const handleModelChange = (modelId: string) => {
  // Check if the model exists in props.models or default models
  const modelInProps = props.models.find(m => m.id === modelId)
  const modelInDefaults = AI_MODELS.find(m => m.id === modelId)
  
  if (modelInProps || modelInDefaults) {
    // Force immediate update
    emit('update:modelId', modelId)
    
    // Add a small delay to ensure the UI updates
    setTimeout(() => {
      // Use window instead of document for event dispatching
      const event = new CustomEvent('model-changed', { 
        detail: modelId,
        bubbles: true,
        cancelable: true
      })
      window.dispatchEvent(event)
    }, 50)
  }
}

// Add validation before emitting mode changes
const handleModeChange = (mode: BuilderMode) => {
  if (['chat', 'build'].includes(mode)) {
    // Force immediate update
    emit('update:mode', mode)
    
    // Add a small delay to ensure the UI updates
    setTimeout(() => {
      // Use window instead of document for event dispatching
      const event = new CustomEvent('mode-changed', { 
        detail: mode,
        bubbles: true,
        cancelable: true
      })
      window.dispatchEvent(event)
    }, 50)
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

/* Custom styling for collapsed sidebar tooltips */
:deep(.sidebar-collapsed-icon span) {
  font-size: 0.75rem;
  background-color: rgba(15, 15, 15, 0.95);
  border: 1px solid rgba(55, 65, 81, 0.7);
  padding: 0.4rem 0.7rem;
  border-radius: 0.375rem;
  font-weight: 500;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
  color: white;
  z-index: 100;
  margin-left: 1rem;
  min-width: 120px;
  text-align: center;
}

/* Ensure sidebar icons have proper z-index for tooltips */
.sidebar-collapsed-icon {
  position: relative;
  z-index: 20;
}

/* Override any potential overflow issues */
:deep(.sidebar-tooltip) {
  visibility: visible;
  z-index: 999;
}
</style>
