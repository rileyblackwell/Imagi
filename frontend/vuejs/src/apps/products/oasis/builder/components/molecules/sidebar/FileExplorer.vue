<template>
  <div class="flex-1 overflow-y-auto">
    <!-- File Tree -->
    <div class="p-3">
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-sm font-medium text-gray-200 flex items-center">
          <i class="fas fa-folder-open text-primary-400 mr-1.5"></i>
          <span>Project Files</span>
        </h3>
        <button
          class="p-1 text-gray-400 hover:text-white transition-colors rounded-full hover:bg-dark-700/50"
          @click="showNewForm = true"
          title="New File"
        >
          <i class="fas fa-plus text-xs"></i>
        </button>
      </div>

      <!-- New File Form -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-300 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <div v-if="showNewForm" class="mb-3 bg-dark-800/80 p-2 rounded-lg border border-dark-700/70">
          <form @submit.prevent="handleCreateFile" class="space-y-2">
            <div class="text-xs font-medium text-gray-300 mb-1">New File</div>
            <input
              v-model="newFileName"
              type="text"
              class="w-full py-1 px-2 text-sm bg-dark-900 border-dark-700 rounded-lg focus:border-primary-500 focus:ring-primary-500"
              placeholder="File name (with extension)"
              required
            />
            <div class="flex justify-end space-x-2">
              <button
                type="button"
                class="px-2 py-1 text-xs text-gray-400 hover:text-white transition-colors"
                @click="cancelNewFile"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="px-2 py-1 text-xs bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
                :disabled="!isValidFileName"
              >
                Create
              </button>
            </div>
          </form>
        </div>
      </Transition>

      <!-- Directory structure -->
      <div class="space-y-0.5 pb-1 mb-2 border-b border-dark-700/30">
        <div 
          class="flex items-center text-xs py-1 px-2 rounded hover:bg-dark-800/80 transition-colors text-primary-300 cursor-pointer"
          @click="emitSelectDirectoryFile('templates')"
        >
          <i class="fas fa-folder text-primary-400 mr-1.5 w-4 text-center"></i>
          <span>Templates</span>
        </div>
        <div
          class="flex items-center text-xs py-1 px-2 rounded hover:bg-dark-800/80 transition-colors text-primary-300 cursor-pointer"
          @click="emitSelectDirectoryFile('static/css')"
        >
          <i class="fas fa-folder text-primary-400 mr-1.5 w-4 text-center"></i>
          <span>Styles</span>
        </div>
      </div>

      <!-- File List -->
      <div v-if="sortedFiles.length > 0" class="space-y-0.5">
        <FileTreeItem
          v-for="file in sortedFiles"
          :key="file.path"
          :file="file"
          :is-selected="selectedFile?.path === file.path"
          @select="handleFileSelect"
        />
      </div>
      <div v-else class="text-center text-xs text-gray-500 py-2">
        <div class="mb-1"><i class="fas fa-info-circle"></i></div>
        No project files yet.
        <div class="mt-1">Create a new file to get started.</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ProjectFile } from '../../../types/builder'
import FileTreeItem from '../../atoms/navigation/FileTreeItem.vue'

const props = defineProps<{
  files: ProjectFile[]
  selectedFile: ProjectFile | null
  fileTypes: Record<string, string>
}>()

const emit = defineEmits<{
  (e: 'selectFile', file: ProjectFile): void
  (e: 'createFile', data: { name: string; type: string; content?: string }): void
}>()

// Local state
const showNewForm = ref(false)
const newFileName = ref('')

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

// Methods
const handleFileSelect = (file: ProjectFile) => {
  emit('selectFile', file)
}

const emitSelectDirectoryFile = (dirPath: string) => {
  // Find first file in directory or mock one if none exists
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
</style>
