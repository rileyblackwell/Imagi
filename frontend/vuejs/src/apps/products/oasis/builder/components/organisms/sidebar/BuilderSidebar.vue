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
          <div class="pointer-events-none absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-indigo-500/30 via-violet-500/30 to-indigo-500/30 opacity-70 rounded-t-2xl"></div>
          <!-- Project header -->
          <div class="flex items-center justify-between gap-3 mt-1 mb-3">
            <div class="flex items-center gap-3 min-w-0">
              <!-- Gradient ring avatar -->
              <div class="gradient-ring p-[2px] rounded-xl">
                <div class="w-8 h-8 rounded-[10px] flex items-center justify-center bg-dark-900/80 border border-dark-700/60 text-primary-300">
                  <i class="fas fa-cube"></i>
                </div>
              </div>
              <div class="min-w-0">
                <div class="flex items-center gap-2 min-w-0">
                  <h2 class="relative text-[1.15rem] font-extrabold oasis-project-gradient-text truncate drop-shadow-md">
                    {{ currentProject?.name || 'Untitled Project' }}
                  </h2>
                </div>
                <!-- subtle shimmer underline under name -->
                <div class="shimmer-underline mt-1"></div>
              </div>
            </div>
          </div>
          <!-- Read-only Project Description -->
          <div v-if="!isCollapsed" class="relative px-2 mt-2">
            <p v-if="currentProject?.description" class="text-sm text-gray-400 italic truncate">
              {{ currentProject.description }}
            </p>
            <p v-else class="text-sm text-gray-500 italic">
              Add a company description...
            </p>
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
          <div class="sidebar-label"><span class="bg-gradient-to-r from-indigo-300 to-violet-300 bg-clip-text text-transparent">Preview</span></div>
        </button>
      </template>
    </div>
    
    <!-- Apps Section removed: now shown in main content area -->
    
    <!-- Version Control Section - New Design (expanded mode only) -->
    <div v-if="!isCollapsed" class="shrink-0 py-4">
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
        class="relative flex items-center justify-center py-2 px-3 rounded-lg bg-dark-800/70 border border-dark-700/60 w-full text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/40 disabled:opacity-60 disabled:cursor-not-allowed shadow-sm"
        title="Preview Project"
        :disabled="isLoading"
        @click="$emit('preview')"
      >
        <span class="mr-2 w-6 h-6 rounded-md flex items-center justify-center border bg-gradient-to-br from-primary-500/15 to-violet-500/15 border-primary-500/30 text-primary-300">
          <i class="fas fa-eye"></i>
        </span>
        <span class="font-medium bg-gradient-to-r from-indigo-300 to-violet-300 bg-clip-text text-transparent">Preview Project</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
// No local reactive state required post Apps-section removal
import VersionControlDropdown from '../../molecules/sidebar/VersionControlDropdown.vue'
import type { 
  ProjectFile,
  EditorMode,
  ProjectType
} from '@/apps/products/oasis/builder/types'

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

// Description is read-only now; no edit state or methods.
// (Model/mode selectors moved to WorkspaceChat header)

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

/* Gradient ring avatar */
.gradient-ring {
  background: linear-gradient(135deg, rgba(99,102,241,0.6), rgba(139,92,246,0.6));
}

/* Name underline shimmer */
.shimmer-underline {
  height: 2px;
  width: 100%;
  background: linear-gradient(90deg, transparent, rgba(99,102,241,0.5), rgba(139,92,246,0.5), transparent);
  background-size: 200% 100%;
  animation: shimmer 3s linear infinite;
  opacity: 0.6;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
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
