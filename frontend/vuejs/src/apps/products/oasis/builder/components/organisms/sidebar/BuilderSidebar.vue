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
      
      <template v-if="isCollapsed">
        <!-- Files Icon -->
        <div class="sidebar-icon-container">
          <div class="sidebar-icon">
            <i class="fas fa-folder text-primary-400"></i>
          </div>
          <div class="sidebar-label">Files</div>
        </div>
        
        <!-- Version Icon -->
        <div class="sidebar-icon-container">
          <div class="sidebar-icon">
            <i class="fas fa-history text-primary-400"></i>
          </div>
          <div class="sidebar-label">Version</div>
        </div>
        
        <!-- Preview Button -->
        <button 
          class="sidebar-icon-container"
          :disabled="isLoading"
          @click="$emit('preview')"
        >
          <div class="sidebar-icon">
            <i class="fas fa-eye text-primary-400"></i>
          </div>
          <div class="sidebar-label">Preview</div>
        </button>
      </template>
    </div>
    
    <!-- Apps Section - Updated Design (expanded mode only) -->
    <div v-if="!isCollapsed" class="flex-1 py-4 border-b border-dark-700/50">
      <div class="mb-3">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Apps</span>
          <span class="text-xs text-gray-500">{{ appsCount }} app{{ appsCount !== 1 ? 's' : '' }}</span>
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
    </div>
    
    <!-- Version Control Section - New Design (expanded mode only) -->
    <div v-if="!isCollapsed" class="shrink-0 py-4">
      <div class="mb-2">
        <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Version History</span>
      </div>
      
      <div class="w-full">
        <VersionControlDropdown 
          :project-id="projectId"
          @version-reset="handleVersionReset"
        />
      </div>
    </div>
    
    <!-- Action Buttons - Updated Design (Preview Button Only in expanded mode) -->
    <div v-if="!isCollapsed" class="p-4 flex justify-center border-t border-dark-700/50">
      <!-- Preview button -->
      <button
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { useProjectStore } from '@/apps/products/oasis/builder/stores/projectStore'
import FileExplorer from '../../molecules/sidebar/FileExplorer.vue'
import VersionControlDropdown from '../../molecules/sidebar/VersionControlDropdown.vue'
import type { 
  ProjectFile,
  EditorMode,
  ProjectType
} from '@/apps/products/oasis/builder/types'

// Local state
const showNewFileFormValue = ref(false)

const props = defineProps<{
  currentProject: ProjectType | null
  files: ProjectFile[]
  selectedFile: ProjectFile | null
  fileTypes: Record<string, string>
  isLoading: boolean
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

// (Model/mode selectors moved to WorkspaceChat header)

// Computed property for apps count (unique apps with files)
const appsCount = computed(() => {
  const apps = new Set()
  props.files.forEach(file => {
    const path = file.path.toLowerCase().replace(/\\/g, '/')
    // Extract app name from path like: frontend/vuejs/src/apps/{appname}/
    const appMatch = path.match(/\/src\/apps\/([^\/]+)\//)
    if (appMatch) {
      apps.add(appMatch[1])
    }
  })
  return apps.size
})

// Function to toggle the new file form visibility
const toggleNewFileForm = () => {
  showNewFileFormValue.value = !showNewFileFormValue.value
}

// Handle version reset event
const handleVersionReset = (version: Record<string, any>) => {
  console.log('Version reset to:', version)
  // Additional handling if needed
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

/* Sidebar icon styles */
.sidebar-icon-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 0;
  transition: transform 0.2s;
}

.sidebar-icon-container:hover {
  transform: translateY(-1px);
}

.sidebar-icon-container.active .sidebar-label {
  color: #a5b4fc;
  font-weight: 600;
}

.sidebar-icon {
  width: 2.6rem;
  height: 2.6rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  background-color: rgba(30, 30, 40, 0.7);
  border: 1px solid rgba(70, 70, 90, 0.5);
  transition: all 0.2s ease-in-out;
  position: relative;
  backdrop-filter: blur(4px);
  color: #a5a5b5;
}

.sidebar-icon:hover {
  background-color: rgba(40, 40, 55, 0.8);
  border-color: rgba(99, 102, 241, 0.3);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  color: white;
}

.sidebar-icon.active-icon {
  background: rgba(99, 102, 241, 0.15);
  border-color: rgba(99, 102, 241, 0.4);
  color: #a5b4fc;
  box-shadow: 0 0 12px rgba(99, 102, 241, 0.2);
}

.sidebar-icon-container button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.sidebar-icon-container button:disabled .sidebar-icon:hover {
  transform: none;
  background-color: rgba(30, 30, 40, 0.7);
  border-color: rgba(70, 70, 90, 0.5);
  box-shadow: none;
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
