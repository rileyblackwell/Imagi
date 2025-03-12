<template>
  <div class="flex-1 overflow-y-auto">
    <!-- File Tree -->
    <div class="p-4">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-sm font-medium text-gray-200">Project Files</h3>
        <button
          class="p-1 text-gray-400 hover:text-white transition-colors"
          @click="showNewForm = true"
          title="New File"
        >
          <i class="fas fa-plus" />
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
        <div v-if="showNewForm" class="mb-4">
          <form @submit.prevent="handleCreateFile" class="space-y-3">
            <input
              v-model="newFileName"
              type="text"
              class="w-full bg-dark-900 border-dark-700 rounded-lg focus:border-primary-500 focus:ring-primary-500"
              placeholder="File name (with extension)"
              required
            />
            <div class="flex justify-end space-x-2">
              <button
                type="button"
                class="px-3 py-1 text-sm text-gray-400 hover:text-white transition-colors"
                @click="cancelNewFile"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="px-3 py-1 text-sm bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
                :disabled="!isValidFileName"
              >
                Create
              </button>
            </div>
          </form>
        </div>
      </Transition>

      <!-- File List -->
      <div class="space-y-1">
        <FileTreeItem
          v-for="file in sortedFiles"
          :key="file.path"
          :file="file"
          :is-selected="selectedFile?.path === file.path"
          @select="handleFileSelect"
        />
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
    // Sort by directory first, then by name
    const aIsDir = a.path.endsWith('/')
    const bIsDir = b.path.endsWith('/')
    if (aIsDir && !bIsDir) return -1
    if (!aIsDir && bIsDir) return 1
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

const handleCreateFile = () => {
  if (!isValidFileName.value) return
  
  // Extract file extension from the filename
  const fileExtension = newFileName.value.split('.').pop() || ''
  
  console.log('Creating file:', { name: newFileName.value, type: fileExtension })
  
  emit('createFile', {
    name: newFileName.value,
    type: fileExtension
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
