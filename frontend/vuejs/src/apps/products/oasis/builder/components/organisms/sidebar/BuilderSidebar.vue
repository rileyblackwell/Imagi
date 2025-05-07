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
        <div class="oasis-project-card bg-gradient-to-br from-dark-800/80 via-dark-900/80 to-dark-950/90 shadow-xl backdrop-blur-lg rounded-2xl p-4 border border-dark-700/60 relative overflow-visible">
          <!-- Project label with badge -->
          <div class="flex items-center mb-3">
            <div class="inline-flex px-2 py-1 rounded-full bg-primary-600/10 border border-primary-500/20">
              <span class="text-xxs font-bold text-primary-400 uppercase tracking-wider">Project</span>
            </div>
          </div>
          <!-- Project name with accent and enhanced styling -->
          <div class="group relative flex items-center">

            <!-- Icon with glow -->
            <span class="relative mr-2">
              <i class="fas fa-cube text-primary-400 opacity-90 oasis-project-icon-glow"></i>
            </span>
            <!-- Project name -->
            <h2 class="relative px-2 py-1 text-2xl font-extrabold oasis-project-gradient-text truncate group-hover:text-primary-300 transition-colors duration-300 drop-shadow-md">
              {{ currentProject?.name || 'Untitled Project' }}
            </h2>
          </div>
          <!-- Editable Project Description -->
          <div v-if="!isCollapsed" class="relative px-2 mt-2">
            <div v-if="!editingDescription" class="group flex items-start">
              <p v-if="currentProject?.description" class="text-sm text-gray-400 italic truncate flex-1 cursor-pointer hover:text-gray-300 transition-colors" @click="startEditingDescription">
                {{ currentProject.description }}
              </p>
              <p v-else class="text-sm text-gray-500 italic cursor-pointer hover:text-gray-300 transition-colors" @click="startEditingDescription">
                Add a company description...
              </p>
              <button class="ml-2 text-xs text-gray-500 hover:text-primary-400 transition-colors" @click="startEditingDescription" title="Edit description">
                <i class="fas fa-edit"></i>
              </button>
            </div>
            <div v-else class="flex items-start w-full">
              <textarea
                v-model="editableDescription"
                class="w-full min-h-[2.2rem] rounded-md bg-dark-900/70 border border-dark-700/50 text-sm text-gray-200 px-2 py-1 outline-none focus:ring-2 focus:ring-primary-500 resize-none transition"
                @blur="saveDescription"
                @keydown.enter.prevent="saveDescription"
                @keydown.esc="cancelEditingDescription"
                maxlength="180"
                placeholder="Add a company description..."
                ref="descInputRef"
                rows="2"
                aria-label="Edit company description"
              ></textarea>
              <button class="ml-2 text-xs text-gray-500 hover:text-primary-400 transition-colors mt-1" @mousedown.prevent="saveDescription" title="Save">
                <i class="fas fa-check"></i>
              </button>
              <button class="ml-1 text-xs text-gray-500 hover:text-red-400 transition-colors mt-1" @mousedown.prevent="cancelEditingDescription" title="Cancel">
                <i class="fas fa-times"></i>
              </button>
            </div>
          </div>
        </div>
        <!-- Divider below project card -->
        <div class="w-full flex justify-center mt-4 mb-2" aria-hidden="true">
          <div class="h-[1.5px] w-4/5 bg-gradient-to-r from-transparent via-dark-700/70 to-transparent rounded-full shadow-sm"></div>
        </div>
      </div>
      
      <!-- Model Selector -->
      <div :class="{'mb-4': !isCollapsed}">
        <div v-if="!isCollapsed" class="mb-2">
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Model</span>
        </div>
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
              :class="[getModelTypeIcon(selectedModel), getModelTypeClass(selectedModel)]"
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
    
    <!-- Version Control Section - New Design -->
    <div class="shrink-0 py-4" :class="{'border-b border-dark-700/50': !isCollapsed}">
      <div v-if="!isCollapsed" class="mb-2">
        <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Version History</span>
      </div>
      
      <div v-if="!isCollapsed" class="w-full">
        <VersionControlDropdown 
          :project-id="projectId"
          @version-reset="handleVersionReset"
        />
      </div>
      
      <template v-else>
        <div class="tooltip-container mb-4">
          <button 
            class="w-10 h-10 rounded-md flex items-center justify-center bg-dark-800/70 hover:bg-dark-700/70 border border-dark-700/50 transition-colors"
            title="Version History"
          >
            <i class="fas fa-history text-primary-400"></i>
          </button>
          <div class="sidebar-label">Versions</div>
        </div>
      </template>
    </div>
    
    <!-- Action Buttons - Updated Design (Preview Button Only) -->
    <div :class="{'p-4': !isCollapsed, 'px-2 py-3': isCollapsed}" class="flex justify-center border-t border-dark-700/50">
      <!-- Preview button -->
      <button
        v-if="!isCollapsed"
        class="group relative flex items-center justify-center py-2 px-4 rounded-lg transition-all duration-300 bg-dark-800/70 hover:bg-dark-800 border border-dark-700/50 hover:border-primary-500/30 transform hover:scale-[1.02] w-full"
        title="Preview Project"
        :disabled="isLoading"
        @click="$emit('preview')"
      >
        <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500/30 to-violet-500/30 rounded-lg blur opacity-0 group-hover:opacity-75 transition duration-300"></div>
        <div class="relative flex items-center justify-center">
          <i class="fas fa-eye mr-2 text-primary-400 group-hover:text-primary-300 transition-colors"></i>
          <span class="text-white text-sm font-medium">Preview Project</span>
        </div>
      </button>
      
      <button 
        v-else
        class="tooltip-container w-10 h-10 rounded-md flex items-center justify-center bg-dark-800/70 hover:bg-dark-700/70 border border-dark-700/50 transition-colors"
        title="Preview Project"
        :disabled="isLoading"
        @click="$emit('preview')"
      >
        <i class="fas fa-eye text-primary-400"></i>
        <div class="sidebar-label">Preview</div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { useProjectStore } from '@/apps/products/oasis/builder/stores/projectStore'
import ModelSelector from '../../molecules/sidebar/ModelSelector.vue'
import FileExplorer from '../../molecules/sidebar/FileExplorer.vue'
import VersionControlDropdown from '../../molecules/VersionControlDropdown.vue'
import type { 
  AIModel, 
  BuilderMode,
  ProjectFile,
  EditorMode,
  ProjectType
} from '@/apps/products/oasis/builder/types'
import { AI_MODELS } from '@/apps/products/oasis/builder/types/services'

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


// Editable description state
const editingDescription = ref(false)
const editableDescription = ref(props.currentProject?.description || '')
const descInputRef = ref<HTMLInputElement | null>(null)

function startEditingDescription() {
  editableDescription.value = props.currentProject?.description || ''
  editingDescription.value = true
  nextTick(() => {
    descInputRef.value?.focus()
  })
}
const projectStore = useProjectStore()

async function saveDescription() {
  editingDescription.value = false
  const newDesc = editableDescription.value.trim()
  if (props.currentProject && newDesc !== (props.currentProject.description || '')) {
    try {
      await projectStore.updateProject(String(props.currentProject.id), { description: newDesc })
      // Optionally, update the local project description optimistically
      if (props.currentProject) props.currentProject.description = newDesc
    } catch (err) {
      // Optionally, show an error toast or revert the UI
      console.error('Failed to update project description:', err)
    }
  }
}
function cancelEditingDescription() {
  editingDescription.value = false
  editableDescription.value = props.currentProject?.description || ''
}

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

// Use shared icon utilities for consistency
// getModelTypeIcon and getModelTypeClass are imported from ModelSelector.vue

// Computed property for mode options with icons
const modeOptions = computed(() => ([
  { id: 'chat', icon: 'fa-comments', label: 'Chat Mode' },
  { id: 'build', icon: 'fa-code', label: 'Build Mode' }
]))

// Function to toggle the new file form visibility
const toggleNewFileForm = () => {
  showNewFileFormValue.value = !showNewFileFormValue.value
}

// Handle version reset event
const handleVersionReset = (version: Record<string, any>) => {
  console.log('Version reset to:', version)
  // Additional handling if needed
}

// Fix for the getModelTypeIcon and getModelTypeClass methods
const getModelTypeIcon = (model: AIModel | null) => {
  if (!model) return 'fa-robot';
  // existing implementation
}

const getModelTypeClass = (model: AIModel | null) => {
  if (!model) return 'text-gray-400';
  // existing implementation
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

/* Oasis Project Card Enhancements */
.oasis-project-card {
  box-shadow: 0 4px 32px 0 rgba(80, 100, 250, 0.08), 0 1.5px 8px 0 rgba(30, 30, 50, 0.16);
  transition: box-shadow 0.3s;
}
.oasis-project-card:hover {
  box-shadow: 0 6px 36px 0 rgba(99, 102, 241, 0.16), 0 2px 12px 0 rgba(30,30,50,0.22);
}
.oasis-project-gradient-text {
  background: linear-gradient(90deg, #a5b4fc 10%, #60a5fa 50%, #a78bfa 90%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}


.oasis-project-icon-glow {
  text-shadow: 0 0 8px #6366f1cc, 0 0 2px #a5b4fc99;
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
