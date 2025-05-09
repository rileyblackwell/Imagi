<template>
  <div class="flex-1 overflow-y-auto">
    <!-- File Tree with Enhanced Modern Styling -->
    <div class="p-3">
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-sm font-medium text-gray-200 flex items-center">
          <i class="fas fa-folder-open text-primary-400 mr-1.5"></i>
          <span>Project Files</span>
        </h3>
        <!-- Enhanced Add file button with modern styling -->
        <button 
          @click="toggleNewFileForm" 
          class="group relative text-xs rounded-lg px-2 py-1.5 bg-primary-600/80 hover:bg-primary-600 text-white transition-all duration-200 transform hover:scale-[1.02]"
          title="Create new file"
        >
          <!-- Subtle glow effect on hover -->
          <div class="absolute -inset-0.5 bg-primary-500/30 rounded-lg blur opacity-0 group-hover:opacity-75 transition duration-300"></div>
          <div class="relative flex items-center">
            <i class="fas fa-plus mr-1"></i> 
            <span>New</span>
          </div>
        </button>
      </div>

      <!-- New File Form - Enhanced with modern styling -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-300 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <div v-if="showNewForm" class="mb-4 p-3 bg-dark-800/70 backdrop-blur-sm rounded-lg border border-dark-700/50 space-y-2">
          <h3 class="text-xs font-medium text-gray-300">Create New File</h3>
          
          <input
            v-model="newFileName"
            type="text"
            placeholder="filename.ext"
            class="w-full text-xs bg-dark-950/90 border border-dark-700/80 rounded-md p-2 text-white placeholder-gray-500 focus:outline-none focus:ring-[1.5px] focus:ring-offset-0 focus:ring-primary-500/60 focus:border-transparent shadow-sm focus:shadow-[0_0_8px_rgba(99,102,241,0.25)] transition-all duration-200"
            @keydown.enter="createFile"
          />
          
          <p class="text-xxs text-gray-500">
            Examples: templates/about.html, static/css/about_styles.css
          </p>
          
          <div class="flex justify-end space-x-2">
            <button
              @click="toggleNewFileForm"
              class="text-xs rounded-md px-2 py-1 text-gray-400 hover:text-white transition-colors focus:outline-none"
            >
              Cancel
            </button>
            <button
              @click="createFile"
              :disabled="!isValidFileName"
              class="group relative text-xs rounded-md px-2 py-1 bg-primary-600/80 disabled:bg-gray-700 disabled:text-gray-500 hover:bg-primary-600 text-white transition-all duration-200 focus:outline-none"
            >
              <!-- Subtle glow effect on hover (only when enabled) -->
              <div v-if="isValidFileName" class="absolute -inset-0.5 bg-primary-500/30 rounded-md blur opacity-0 group-hover:opacity-75 transition duration-300"></div>
              <span class="relative">Create</span>
            </button>
          </div>
        </div>
      </Transition>

      <!-- Directory Structure - Enhanced with modern styling -->
      <div class="space-y-2">
        <!-- Group files by directory -->
        <div 
          v-for="(dirFiles, dirName) in filesByDirectory"
          :key="dirName"
          class="p-2 bg-dark-850/60 backdrop-blur-sm rounded-lg border border-dark-700/40 transition-all duration-200"
          :class="{'border-primary-500/30 bg-primary-900/10 shadow-[0_0_10px_rgba(99,102,241,0.1)]': currentDirectory === dirName}"
        >
          <div 
            class="group flex items-center text-xs py-1.5 px-2.5 rounded-md transition-all duration-200 cursor-pointer mb-2"
            :class="[
              currentDirectory === dirName 
                ? 'bg-gradient-to-r from-primary-500/20 to-violet-500/10 text-white border border-primary-500/30' 
                : 'text-primary-300 hover:bg-dark-800/80 border border-transparent hover:border-primary-500/20'
            ]"
            @click="selectDirectory(dirName)"
          >
            <i 
              class="fas fa-folder-open mr-2 w-4 text-center transition-colors duration-200"
              :class="getDirectoryIconClass(dirName)"
            ></i>
            <span class="font-medium">{{ formatDirectoryName(dirName) }}</span>
            <span class="ml-auto text-xxs bg-dark-700/80 text-primary-300 py-0.5 px-1.5 rounded-full">
              {{ dirFiles.length }}
            </span>
          </div>
          
          <!-- Files List with enhanced styling -->
          <div v-if="currentDirectory === dirName" class="space-y-1.5 pl-2">
            <FileTreeItem
              v-for="file in dirFiles"
              :key="file.path"
              :file="file"
              :is-selected="selectedFile?.path === file.path"
              @select="handleFileSelect"
              @delete="handleFileDelete"
            />
            <div v-if="dirFiles.length === 0" class="text-center text-xxs text-gray-500 py-2">
              <div><i class="fas fa-info-circle"></i> No files in this directory</div>
            </div>
          </div>
        </div>
        
        <!-- No files message - Enhanced with modern styling -->
        <div v-if="Object.keys(filesByDirectory).length === 0" class="text-center text-sm text-gray-500 py-6 px-3 bg-dark-850/60 backdrop-blur-sm rounded-lg border border-dark-700/40">
          <div><i class="fas fa-info-circle text-primary-400 mb-2 text-xl opacity-80"></i></div>
          <div>No project files found</div>
          <div class="text-xs mt-1 mb-3">Click 'New' to create your first file</div>
          <button
            @click="toggleNewFileForm"
            class="group relative text-xs rounded-lg px-3 py-1.5 bg-primary-600/80 hover:bg-primary-600 text-white transition-all duration-200 transform hover:scale-[1.02] inline-flex items-center"
          >
            <!-- Subtle glow effect on hover -->
            <div class="absolute -inset-0.5 bg-primary-500/30 rounded-lg blur opacity-0 group-hover:opacity-75 transition duration-300"></div>
            <div class="relative flex items-center">
              <i class="fas fa-plus mr-1.5"></i> 
              <span>Create File</span>
            </div>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ProjectFile } from '../../../types/components'
import FileTreeItem from '../../atoms/navigation/FileTreeItem.vue'
import { FileService } from '../../../services/fileService'

const props = defineProps<{
  files: ProjectFile[]
  selectedFile: ProjectFile | null
  fileTypes: Record<string, string>
  showNewForm?: boolean
  projectId?: string
}>()

const emit = defineEmits<{
  (e: 'selectFile', file: ProjectFile): void
  (e: 'createFile', data: { name: string; type: string; content?: string }): void
  (e: 'deleteFile', file: ProjectFile): void
}>()

// Local state
const showNewForm = ref(props.showNewForm || false)
const newFileName = ref('')
const currentDirectory = ref<string>('') // Default empty, will be set to first directory with files

// Group files by directory
const filesByDirectory = computed(() => {
  const result: Record<string, ProjectFile[]> = {}
  
  props.files.forEach(file => {
    // Extract directory from file path
    let dir = file.path.split('/')[0]
    
    // Handle special case for static/css
    if (file.path.startsWith('static/css/')) {
      dir = 'static/css'
    }
    
    // Create array if it doesn't exist
    if (!result[dir]) {
      result[dir] = []
    }
    
    result[dir].push(file)
  })
  
  // Set current directory to first one if not set
  if (!currentDirectory.value && Object.keys(result).length > 0) {
    currentDirectory.value = Object.keys(result)[0]
  }
  
  return result
})

// Utility functions
const formatDirectoryName = (dirName: string) => {
  if (dirName === 'templates') return 'Templates'
  if (dirName === 'static/css') return 'Styles (CSS)'
  if (dirName === 'static') return 'Static Files'
  
  // Capitalize first letter of each word
  return dirName.split('/').map(part => 
    part.charAt(0).toUpperCase() + part.slice(1)
  ).join(' / ')
}

const getDirectoryIconClass = (dirName: string) => {
  if (dirName === 'templates') return 'text-orange-400'
  if (dirName === 'static/css') return 'text-blue-400'
  if (dirName === 'static') return 'text-yellow-400'
  return 'text-primary-400' // Default
}

const isValidFileName = computed(() => {
  return /^[\w-/]+([./][\w-]+)*\.\w+$/.test(newFileName.value)
})

const getFileExtension = computed(() => {
  if (!newFileName.value.includes('.')) return null
  return newFileName.value.split('.').pop()?.toLowerCase() || null
})

// Methods
const toggleNewFileForm = () => {
  showNewForm.value = !showNewForm.value
  if (!showNewForm.value) {
    newFileName.value = ''
  }
}

const selectDirectory = (dirName: string) => {
  currentDirectory.value = dirName
}

const handleFileSelect = (file: ProjectFile) => {
  emit('selectFile', file)
}

const handleFileDelete = (file: ProjectFile) => {
  emit('deleteFile', file)
}

const createFile = () => {
  if (!isValidFileName.value) return
  
  // Determine file type from extension
  const ext = getFileExtension.value
  let fileType = 'text'
  
  if (ext === 'html') fileType = 'html'
  else if (ext === 'css') fileType = 'css'
  else if (ext === 'js') fileType = 'javascript'
  
  // Ensure directory exists in path
  let filePath = newFileName.value
  
  // Check if a directory is already specified in the file path
  if (!filePath.includes('/')) {
    // If no directory is specified, place it in the appropriate directory based on type
    if (ext === 'html') {
      filePath = `templates/${filePath}`
    } else if (ext === 'css') {
      filePath = `static/css/${filePath}`
    } else if (ext === 'js') {
      filePath = `static/${filePath}`
    } else if (currentDirectory.value) {
      // For other file types, use the current directory
      filePath = `${currentDirectory.value}/${filePath}`
    }
  } else {
    // If a path is already specified, but it's for a CSS file that's not in static/css,
    // and it's not already in static/css, adjust it
    if (ext === 'css' && !filePath.includes('static/css/')) {
      filePath = `static/css/${filePath.replace(/^static\//, '')}`
    }
  }
  
  emit('createFile', {
    name: filePath,
    type: fileType
  })
  
  // Reset form
  newFileName.value = ''
  showNewForm.value = false
}
</script>

<style scoped>
/* Add consistent scrollbar styling to match other sidebar components */
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: theme('colors.dark.600') transparent;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: theme('colors.dark.600');
  border-radius: 3px;
}

/* Custom text size class */
.text-xxs {
  font-size: 0.65rem;
  line-height: 1rem;
}
</style>
