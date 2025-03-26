<template>
  <div class="flex-1 overflow-y-auto">
    <!-- File Tree -->
    <div class="p-3">
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-sm font-medium text-gray-200 flex items-center">
          <i class="fas fa-folder-open text-primary-400 mr-1.5"></i>
          <span>Project Files</span>
        </h3>
        <!-- Add file button now visible for better UX -->
        <button 
          @click="toggleNewFileForm" 
          class="text-xs rounded-md px-2 py-1 bg-primary-500 hover:bg-primary-600 text-white transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-opacity-50"
          title="Create new file"
        >
          <i class="fas fa-plus mr-1"></i> 
          <span>New</span>
        </button>
      </div>

      <!-- New File Form - Enhanced -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-300 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <div v-if="showNewForm" class="mb-4 p-3 bg-dark-800/70 rounded-lg border border-dark-700/50 space-y-2">
          <h3 class="text-xs font-medium text-gray-300">Create New File</h3>
          
          <input
            v-model="newFileName"
            type="text"
            placeholder="filename.ext"
            class="w-full text-xs bg-dark-950 border border-dark-700 rounded-md p-2 text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500"
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
              class="text-xs rounded-md px-2 py-1 bg-primary-500 disabled:bg-gray-700 disabled:text-gray-500 hover:bg-primary-600 text-white transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-opacity-50"
            >
              Create
            </button>
          </div>
        </div>
      </Transition>

      <!-- Directory Structure - More dynamic implementation -->
      <div>
        <!-- Group files by directory -->
        <div 
          v-for="(dirFiles, dirName) in filesByDirectory"
          :key="dirName"
          class="mb-4 p-2 bg-dark-850/60 rounded-lg border border-dark-700/30"
          :class="{'border-primary-500/30 bg-primary-900/10': currentDirectory === dirName}"
        >
          <div 
            class="flex items-center text-xs py-1.5 px-2.5 rounded-md transition-colors cursor-pointer mb-2"
            :class="[
              currentDirectory === dirName 
                ? 'bg-primary-500/20 text-white' 
                : 'text-primary-300 hover:bg-dark-800/80'
            ]"
            @click="selectDirectory(dirName)"
          >
            <i 
              class="fas fa-folder-open mr-2 w-4 text-center"
              :class="getDirectoryIconClass(dirName)"
            ></i>
            <span class="font-medium">{{ formatDirectoryName(dirName) }}</span>
            <span class="ml-auto text-xxs bg-dark-700/80 text-primary-300 py-0.5 px-1.5 rounded-full">
              {{ dirFiles.length }}
            </span>
          </div>
          
          <!-- Files List -->
          <div v-if="currentDirectory === dirName" class="space-y-1 pl-2">
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
        
        <!-- No files message -->
        <div v-if="Object.keys(filesByDirectory).length === 0" class="text-center text-sm text-gray-500 py-4">
          <div><i class="fas fa-info-circle text-primary-400 mb-2 text-xl"></i></div>
          <div>No project files found</div>
          <div class="text-xs mt-1">Click 'New' to create your first file</div>
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
      const fileName = filePath.split('/').pop() || ''
      filePath = `static/css/${fileName}`
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

.text-xxs {
  font-size: 0.65rem;
  line-height: 1rem;
}

/* Additional styles for enhanced UI */
.bg-dark-850\/60 {
  background-color: rgba(18, 20, 25, 0.6);
}

.bg-dark-750\/70 {
  background-color: rgba(28, 30, 35, 0.7);
}
</style>
