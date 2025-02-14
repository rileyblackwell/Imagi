<template>
  <div class="flex-1 overflow-y-auto">
    <div class="p-4 border-b border-dark-700">
      <div class="flex items-center justify-between mb-2">
        <h3 class="text-sm font-medium text-gray-400">Project Files</h3>
        <IconButton
          icon-class="fa-plus"
          size="sm"
          :title="showNewForm ? 'Cancel' : 'New File'"
          @click="toggleNewFileForm"
        />
      </div>

      <!-- New File Form -->
      <div v-if="showNewForm" class="mb-4 space-y-3">
        <input
          v-model="newFileName"
          type="text"
          placeholder="File name"
          class="w-full bg-dark-900 border border-dark-600 rounded-lg text-white px-3 py-2 text-sm focus:outline-none focus:border-primary-500"
        />
        <select
          v-model="newFileType"
          class="w-full bg-dark-900 border border-dark-600 rounded-lg text-white px-3 py-2 text-sm focus:outline-none focus:border-primary-500"
        >
          <option value="" disabled>Select file type</option>
          <option v-for="(type, key) in fileTypes" :key="key" :value="type">
            {{ key.toLowerCase() }}
          </option>
        </select>
        <div class="flex justify-end space-x-2">
          <button
            @click="toggleNewFileForm"
            class="px-3 py-1 text-sm text-gray-400 hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            @click="handleCreateFile"
            :disabled="!canCreateFile"
            class="px-3 py-1 text-sm bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Create
          </button>
        </div>
      </div>

      <!-- File List -->
      <div class="space-y-1">
        <button
          v-for="file in files"
          :key="file.path"
          @click="selectFile(file)"
          class="w-full text-left px-3 py-2 rounded-lg text-sm flex items-center group transition-colors"
          :class="[
            selectedFile?.path === file.path
              ? 'bg-primary-500/20 text-white'
              : 'text-gray-400 hover:bg-dark-700 hover:text-white'
          ]"
        >
          <i :class="[getFileIcon(file.type), 'mr-2']"></i>
          <span class="truncate">{{ file.path }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { IconButton } from '@/apps/builder/components/atoms'
import type { ProjectFile } from '@/apps/builder/types/builder'

const props = defineProps<{
  files: ProjectFile[]
  selectedFile: ProjectFile | null
  showNewForm?: boolean
  fileTypes: Record<string, string>
}>()

const emit = defineEmits<{
  (e: 'select-file', file: ProjectFile): void
  (e: 'create-file', data: { name: string; type: string }): void
}>()

const newFileName = ref('')
const newFileType = ref('')
const showNewForm = ref(props.showNewForm || false)

const canCreateFile = computed(() => newFileName.value.trim() && newFileType.value)

const getFileIcon = (type: string): string => {
  const icons: Record<string, string> = {
    html: 'fas fa-code',
    css: 'fab fa-css3',
    javascript: 'fab fa-js',
    typescript: 'fab fa-ts',
    python: 'fab fa-python',
    markdown: 'fas fa-file-alt',
    text: 'fas fa-file-alt'
  }
  return icons[type] || 'fas fa-file'
}

const selectFile = (file: ProjectFile) => {
  emit('select-file', file)
}

const handleCreateFile = () => {
  if (!canCreateFile.value) return
  
  emit('create-file', {
    name: newFileName.value.trim(),
    type: newFileType.value
  })
  
  // Reset form
  newFileName.value = ''
  newFileType.value = ''
  showNewForm.value = false
}

const toggleNewFileForm = () => {
  showNewForm.value = !showNewForm.value
  if (!showNewForm.value) {
    newFileName.value = ''
    newFileType.value = ''
  }
}
</script>
