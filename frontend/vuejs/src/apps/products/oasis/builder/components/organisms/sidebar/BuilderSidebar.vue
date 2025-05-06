<template>
  <div 
    class="h-full max-h-screen flex flex-col overflow-auto pb-2 bg-dark-900/80 backdrop-blur-md border-r border-dark-800/50 relative"
    :class="{'px-4': !isCollapsed, 'items-center': isCollapsed}"
  >
    <!-- Decorative elements -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <!-- Gradient top edge -->
      <div class="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-primary-500/30 to-transparent"></div>
      
      <!-- Glow effect in top corner -->
      <div class="absolute -top-10 -left-10 w-40 h-40 bg-primary-600/20 rounded-full filter blur-xl opacity-40"></div>
    </div>

    <!-- Project Info Section - Updated Design -->
    <div class="shrink-0 py-4" :class="{'border-b border-dark-700/50': !isCollapsed}">
      <div v-if="!isCollapsed" class="mb-4">
        <!-- Project section with enhanced design -->
        <div class="bg-dark-800/70 backdrop-blur-sm rounded-xl p-3 border border-dark-700/50">
          <!-- Project label with badge -->
          <div class="flex items-center mb-3">
            <div class="inline-flex px-2 py-1 rounded-full bg-primary-600/10 border border-primary-500/20">
              <span class="text-xxs font-bold text-primary-400 uppercase tracking-wider">Project</span>
            </div>
          </div>
          
          <!-- Project name with enhanced styling -->
          <div class="group relative">
            <!-- Project name -->
            <h2 class="relative px-2 py-1 text-lg font-semibold text-white truncate group-hover:text-indigo-300 transition-colors duration-300">
              <i class="fas fa-cube mr-2 text-primary-400 opacity-80"></i>
              {{ currentProject?.name || 'Untitled Project' }}
            </h2>
          </div>
          
          <!-- Project description with improved styling -->
          <p v-if="currentProject?.description" class="relative px-2 mt-1.5 text-sm text-gray-400 truncate italic">
            {{ currentProject.description }}
          </p>
        </div>
      </div>
      
      <!-- Model Selector -->
      <div :class="{'mb-4': !isCollapsed}">
        <ModelSelector 
          v-if="!isCollapsed"
          :models="models"
          :model-id="modelId"
          :mode="mode"
          @update:model-id="(id) => $emit('update:modelId', id)"
        />
        <div 
          v-else
          class="tooltip-container mb-4"
        >
          <button 
            class="w-10 h-10 rounded-md flex items-center justify-center bg-dark-800/70 hover:bg-dark-700/70 border border-dark-700/50 transition-colors"
            :title="selectedModel?.name || 'AI Model'"
          >
            <i 
              class="fas" 
              :class="[
                selectedModel?.id === 'claude-3-7-sonnet-20250219' || selectedModel?.id === 'gpt-4.1' ? 'fa-brain text-primary-400' :
                selectedModel?.id === 'gpt-4.1-nano' ? 'fa-bolt text-warning-500' : 'fa-robot'
              ]"
            ></i>
          </button>
          <div class="sidebar-label">Models</div>
        </div>
      </div>
    </div>
    
    <!-- Mode Selector -->
    <div 
      class="shrink-0 py-4" 
      :class="{'border-b border-dark-700/50': !isCollapsed}"
    >
      <div v-if="!isCollapsed" class="mb-2">
        <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Mode</span>
      </div>
      
      <div class="flex items-center" :class="{'justify-center': isCollapsed, 'space-x-2': !isCollapsed}">
        <template v-if="!isCollapsed">
          <!-- Enhanced Mode Selector with modern design -->
          <div class="w-full">
            <div class="bg-dark-800/70 backdrop-blur-sm rounded-xl p-2 border border-dark-700/50">
              <div class="grid grid-cols-2 gap-2">
                <button
                  v-for="m in modes"
                  :key="m"
                  class="relative group flex items-center justify-center py-3 px-4 rounded-lg transition-all duration-300"
                  :class="[
                    mode === m 
                      ? 'bg-gradient-to-r from-primary-500/20 to-violet-500/20 border border-primary-500/40' 
                      : 'bg-dark-850/50 hover:bg-dark-800 border border-dark-700/50 hover:border-primary-500/30'
                  ]"
                  @click="$emit('update:mode', m)"
                >
                  <!-- Subtle glow effect on hover -->
                  <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500/30 to-violet-500/30 rounded-lg blur opacity-0 group-hover:opacity-75 transition duration-300"></div>
                  
                  <div class="relative flex items-center space-x-3">
                    <i :class="['fas', getModeIcon(m), mode === m ? 'text-primary-400' : 'text-gray-400 group-hover:text-white']"></i>
                    <span :class="[mode === m ? 'text-white' : 'text-gray-400 group-hover:text-white']">{{ formatMode(m) }}</span>
                  </div>
                </button>
              </div>
              
              <!-- Mode description -->
              <div class="mt-3 px-2 text-sm text-gray-400">
                <p v-if="mode === 'chat'">
                  Have a conversation about your project and get assistance
                </p>
                <p v-else-if="mode === 'build'">
                  Generate and modify code directly in your project
                </p>
              </div>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="space-y-4">
            <button 
              v-for="m in modes" 
              :key="m"
              class="tooltip-container w-10 h-10 rounded-md flex items-center justify-center transition-colors"
              :class="[
                mode === m 
                  ? 'bg-primary-600/30 border border-primary-500/40 text-primary-400' 
                  : 'bg-dark-800/70 hover:bg-dark-700/70 border border-dark-700/50 text-gray-400 hover:text-white'
              ]"
              @click="$emit('update:mode', m)"
            >
              <i :class="['fas', getModeIcon(m)]"></i>
              <div class="sidebar-label">{{ formatMode(m) }}</div>
            </button>
          </div>
        </template>
      </div>
    </div>
    
    <!-- Files Section - Updated Design -->
    <div class="flex-1 py-4" :class="{'border-b border-dark-700/50': !isCollapsed}">
      <div v-if="!isCollapsed" class="mb-3">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Files</span>
          <span class="text-xs text-gray-500">{{ files.length }} item{{ files.length !== 1 ? 's' : '' }}</span>
        </div>
        
        <!-- Files container with enhanced styling -->
        <div class="mt-2 bg-dark-800/70 backdrop-blur-sm rounded-xl border border-dark-700/50 overflow-hidden">
          <FileExplorer
            :files="files"
            :selected-file="selectedFile"
            :file-types="fileTypes"
            :show-new-form="showNewFileFormValue"
            :project-id="projectId"
            @select-file="$emit('selectFile', $event)"
            @create-file="$emit('createFile', $event)"
            @delete-file="$emit('deleteFile', $event)"
          />
        </div>
      </div>
      
      <template v-else>
        <div class="tooltip-container">
          <button 
            class="w-10 h-10 rounded-md flex items-center justify-center bg-dark-800/70 hover:bg-dark-700/70 border border-dark-700/50 transition-colors"
            title="Files"
          >
            <i class="fas fa-folder text-primary-400"></i>
          </button>
          <div class="sidebar-label">Files</div>
        </div>
      </template>
    </div>
    
    <!-- Action Buttons - Updated Design -->
    <div :class="{'p-4': !isCollapsed, 'px-2 py-3': isCollapsed}" class="flex justify-between border-t border-dark-700/50">
      <!-- Undo button -->
      <button
        v-if="!isCollapsed"
        class="group relative flex items-center justify-center py-2 px-4 rounded-lg transition-all duration-300 bg-dark-800/70 hover:bg-dark-800 border border-dark-700/50 hover:border-primary-500/30 transform hover:scale-[1.02]"
        title="Undo Last Action"
        :disabled="isLoading"
        @click="$emit('undo')"
      >
        <div class="absolute -inset-0.5 bg-gradient-to-r from-indigo-500/30 to-primary-500/30 rounded-lg blur opacity-0 group-hover:opacity-75 transition duration-300"></div>
        <div class="relative flex items-center">
          <i class="fas fa-undo mr-2 text-primary-400 group-hover:text-primary-300 transition-colors"></i>
          <span class="text-white text-sm font-medium">Undo</span>
        </div>
      </button>
      
      <!-- Preview button -->
      <button
        v-if="!isCollapsed"
        class="group relative flex items-center justify-center py-2 px-4 rounded-lg transition-all duration-300 bg-dark-800/70 hover:bg-dark-800 border border-dark-700/50 hover:border-primary-500/30 transform hover:scale-[1.02]"
        title="Preview Project"
        :disabled="isLoading"
        @click="$emit('preview')"
      >
        <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500/30 to-violet-500/30 rounded-lg blur opacity-0 group-hover:opacity-75 transition duration-300"></div>
        <div class="relative flex items-center">
          <i class="fas fa-eye mr-2 text-primary-400 group-hover:text-primary-300 transition-colors"></i>
          <span class="text-white text-sm font-medium">Preview</span>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import ModelSelector from '@/apps/products/oasis/builder/components/molecules/sidebar/ModelSelector.vue'
import ModeSelector from '@/apps/products/oasis/builder/components/molecules/sidebar/ModeSelector.vue'
import FileExplorer from '@/apps/products/oasis/builder/components/molecules/sidebar/FileExplorer.vue'
import { ActionButton, IconButton } from '@/apps/products/oasis/builder/components'
import { AI_MODELS } from '@/apps/products/oasis/builder/types/services'
import type { 
  AIModel, 
  BuilderMode,
  ProjectFile,
  EditorMode,
  ProjectType
} from '@/apps/products/oasis/builder/types'

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
  projectId: string
}>()

const emit = defineEmits<{
  (e: 'update:modelId', value: string): void
  (e: 'update:mode', value: BuilderMode): void
  (e: 'selectFile', file: ProjectFile): void
  (e: 'createFile', data: { name: string; type: string; content?: string }): void
  (e: 'deleteFile', file: ProjectFile): void
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

// Function to toggle the new file form visibility
const toggleNewFileForm = () => {
  showNewFileFormValue.value = !showNewFileFormValue.value
}
</script>

<style scoped>
.tooltip-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.tooltip {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: #1e1e2a;
  color: white;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  white-space: nowrap;
  z-index: 50;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s;
  border: 1px solid rgba(99, 102, 241, 0.2);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(99, 102, 241, 0.1);
}

.sidebar-label {
  font-size: 0.7rem;
  color: #a5a5b5;
  text-align: center;
  margin-top: 0.35rem;
  font-weight: 500;
}

.tooltip-container:hover .tooltip {
  opacity: 1;
}

.text-xxs {
  font-size: 0.65rem;
  line-height: 1rem;
}

/* Scrollbar styling */
.overflow-auto {
  scrollbar-width: thin;
  scrollbar-color: theme('colors.dark.600') transparent;
}

.overflow-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-auto::-webkit-scrollbar-thumb {
  background-color: theme('colors.dark.600');
  border-radius: 3px;
}

/* New styles for enhanced mode selector */
.bg-dark-850\/50 {
  background-color: rgba(15, 15, 25, 0.5);
}
</style>
