<template>
  <div class="flex-1 overflow-y-auto">
    <!-- File Tree -->
    <div class="p-3">
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-sm font-medium text-gray-200 flex items-center">
          <i class="fas fa-folder-open text-primary-400 mr-1.5"></i>
          <span>Project Files</span>
        </h3>
        <!-- Remove the add file button per requirement -->
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
        <div 
          class="mb-4 bg-dark-800/80 p-3 rounded-lg border border-dark-700/70 shadow-xl"
        >
          <form @submit.prevent="handleCreateFile" class="space-y-3">
            <div class="text-xs font-medium text-gray-300 mb-1 flex items-center">
              <i class="fas fa-file-plus text-primary-400 mr-1.5"></i>
              <span>Create New File</span>
            </div>
            <input
              v-model="newFileName"
              type="text"
              class="w-full py-1.5 px-2 text-sm bg-dark-900 border border-dark-700 rounded-lg focus:border-primary-500 focus:ring-primary-500"
              placeholder="Enter filename (e.g., about.html)"
              required
            />
            <div class="text-xs text-gray-400 italic" v-if="newFileName">
              <span v-if="getFileExtension">Will be added to <span class="text-primary-300 font-medium">{{ getTargetDirectory }}</span></span>
              <span v-else>Please include a file extension (.html, .css, etc.)</span>
            </div>
            <div class="flex justify-end space-x-2">
              <button
                type="button"
                class="px-3 py-1.5 text-xs text-gray-400 hover:text-white transition-colors"
                @click="cancelNewFile"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="px-3 py-1.5 text-xs bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors flex items-center"
                :disabled="!isValidFileName"
                :class="{'opacity-50 cursor-not-allowed': !isValidFileName}"
              >
                <i class="fas fa-plus-circle mr-1"></i>
                Create
              </button>
            </div>
          </form>
        </div>
      </Transition>

      <!-- Directory Sections with Improved Visuals -->
      <div>
        <!-- Templates Section -->
        <div 
          class="mb-4 p-2 bg-dark-850/60 rounded-lg border border-dark-700/30"
          :class="{'border-primary-500/30 bg-primary-900/10': currentDirectory === 'templates'}"
        >
          <div 
            class="flex items-center text-xs py-1.5 px-2.5 rounded-md transition-colors cursor-pointer mb-2"
            :class="[
              currentDirectory === 'templates' 
                ? 'bg-primary-500/20 text-white' 
                : 'text-primary-300 hover:bg-dark-800/80'
            ]"
            @click="selectDirectory('templates')"
          >
            <i class="fas fa-folder-open text-primary-400 mr-2 w-4 text-center"></i>
            <span class="font-medium">Templates</span>
            <span class="ml-auto text-xxs bg-dark-700/80 text-primary-300 py-0.5 px-1.5 rounded-full">
              {{ filteredFilesByDir('templates').length }}
            </span>
          </div>
          
          <!-- Template Files List -->
          <div v-if="currentDirectory === 'templates'" class="space-y-1 pl-2">
            <FileTreeItem
              v-for="file in filteredFilesByDir('templates')"
              :key="file.path"
              :file="file"
              :is-selected="selectedFile?.path === file.path"
              @select="handleFileSelect"
              @delete="handleFileDelete"
            />
            <div v-if="filteredFilesByDir('templates').length === 0" class="text-center text-xxs text-gray-500 py-2">
              <div><i class="fas fa-info-circle"></i> No template files</div>
            </div>
          </div>
        </div>
        
        <!-- Styles Section -->
        <div 
          class="mb-4 p-2 bg-dark-850/60 rounded-lg border border-dark-700/30"
          :class="{'border-primary-500/30 bg-primary-900/10': currentDirectory === 'static/css'}"
        >
          <div 
            class="flex items-center text-xs py-1.5 px-2.5 rounded-md transition-colors cursor-pointer mb-2"
            :class="[
              currentDirectory === 'static/css' 
                ? 'bg-primary-500/20 text-white' 
                : 'text-primary-300 hover:bg-dark-800/80'
            ]"
            @click="selectDirectory('static/css')"
          >
            <i class="fas fa-folder-open text-blue-400 mr-2 w-4 text-center"></i>
            <span class="font-medium">Styles</span>
            <span class="ml-auto text-xxs bg-dark-700/80 text-primary-300 py-0.5 px-1.5 rounded-full">
              {{ filteredFilesByDir('static/css').length }}
            </span>
          </div>
          
          <!-- CSS Files List -->
          <div v-if="currentDirectory === 'static/css'" class="space-y-1 pl-2">
            <FileTreeItem
              v-for="file in filteredFilesByDir('static/css')"
              :key="file.path"
              :file="file"
              :is-selected="selectedFile?.path === file.path"
              @select="handleFileSelect"
              @delete="handleFileDelete"
            />
            <div v-if="filteredFilesByDir('static/css').length === 0" class="text-center text-xxs text-gray-500 py-2">
              <div><i class="fas fa-info-circle"></i> No CSS files</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ProjectFile } from '../../../types/builder'
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
const currentDirectory = ref<string>('templates') // Default to templates

// Computed
const sortedFiles = computed(() => {
  return [...props.files].sort((a, b) => {
    // Group files by directory
    const aDir = a.path.split('/')[0]
    const bDir = b.path.split('/')[0]
    
    if (aDir !== bDir) {
      // Sort templates first, then static files
      if (aDir === 'templates') return -1
      if (bDir === 'templates') return 1
    }
    
    // Sort by filename within same directory
    return a.path.localeCompare(b.path)
  })
})

const isValidFileName = computed(() => {
  return /^[\w-]+([./][\w-]+)*\.\w+$/.test(newFileName.value)
})

const getFileExtension = computed(() => {
  if (!newFileName.value.includes('.')) return null
  return newFileName.value.split('.').pop()?.toLowerCase() || null
})

const getTargetDirectory = computed(() => {
  const ext = getFileExtension.value
  if (ext === 'html') return 'templates'
  if (ext === 'css') return 'static/css'
  return 'templates' // Default to templates for other types
})

// Methods for filtering files by directory
const filteredFilesByDir = (dirPath: string) => {
  return props.files.filter(file => file.path.startsWith(dirPath + '/'))
}

// Methods
const handleFileSelect = (file: ProjectFile) => {
  emit('selectFile', file)
}

// Enhanced file delete handler (replaces the existing one)
const handleFileDelete = async (file: ProjectFile) => {
  if (!file || !props.projectId) return
  
  // Confirm deletion
  if (!window.confirm(`Are you sure you want to delete ${file.path}?`)) {
    return
  }
  
  try {
    // Delete the file
    await FileService.deleteFile(props.projectId, file.path)
    
    // Emit delete event to parent component to handle store updates
    emit('deleteFile', file)
    
    // Show success message
    console.log('File deleted successfully')
  } catch (error: any) {
    console.error('Error deleting file:', error)
    console.error(error.message || 'Failed to delete file')
  }
}

const selectDirectory = (dirPath: string) => {
  currentDirectory.value = dirPath
  
  // Find first file in directory or show the new file form if empty
  const dirFile = props.files.find(f => f.path.startsWith(dirPath + '/'))
  
  if (dirFile) {
    emit('selectFile', dirFile)
  } else {
    // Show the new file form as fallback
    showNewForm.value = true
    newFileName.value = dirPath === 'templates' ? 'page.html' : 'styles.css'
  }
}

const handleCreateFile = () => {
  if (!isValidFileName.value) return
  
  // Determine file type
  let fileType = 'text'
  const fileExtension = newFileName.value.split('.').pop() || ''
  
  if (fileExtension === 'html') {
    fileType = 'html'
  } else if (fileExtension === 'css') {
    fileType = 'css'
  }
  
  // Determine correct path - ensure templates or static/css prefix
  let filePath = newFileName.value
  if (!filePath.startsWith('templates/') && !filePath.startsWith('static/css/')) {
    if (fileExtension === 'html') {
      filePath = `templates/${filePath}`
    } else if (fileExtension === 'css') {
      filePath = `static/css/${filePath}`
    }
  }
  
  console.log('Creating file:', { name: filePath, type: fileType })
  
  emit('createFile', {
    name: filePath,
    type: fileType
  })
  
  // Also update the current directory based on the file type
  if (fileExtension === 'html') {
    currentDirectory.value = 'templates'
  } else if (fileExtension === 'css') {
    currentDirectory.value = 'static/css'
  }
  
  cancelNewFile()
}

const cancelNewFile = () => {
  showNewForm.value = false
  newFileName.value = ''
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
