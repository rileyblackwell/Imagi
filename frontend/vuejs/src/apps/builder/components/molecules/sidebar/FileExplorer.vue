<template>
  <div class="flex-1 overflow-y-auto">
    <div class="p-4 border-b border-dark-700">
      <h3 class="text-sm font-medium text-gray-400 mb-2">Current File</h3>
      
      <!-- File Selection Dropdown -->
      <div class="relative mb-4">
        <select
          :value="selectedFile?.path"
          @change="selectFileByPath($event)"
          class="w-full appearance-none bg-dark-900 border border-dark-600 rounded-lg text-white px-3 py-2.5 pr-10"
        >
          <option value="index.html" selected>index.html</option>
          <option v-for="file in files" :key="file.path" :value="file.path">
            {{ file.path }}
          </option>
        </select>
        <div class="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
          <i class="fas fa-chevron-down text-gray-400"></i>
        </div>
      </div>

      <!-- New File Section -->
      <div class="mb-4">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-sm font-medium text-gray-400">New File</h3>
          <IconButton
            icon-class="fa-plus"
            size="sm"
            :title="showNewForm ? 'Cancel' : 'New File'"
            @click="toggleNewFileForm"
          />
        </div>

        <div v-if="showNewForm" class="space-y-3">
          <input
            v-model="newFileName"
            type="text"
            placeholder="Enter file name (e.g. styles.css)"
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
          <ActionButton
            text="Create File"
            icon="plus"
            :disabled="!canCreateFile"
            :full-width="true"
            @click="handleCreateFile"
          />
        </div>
      </div>

      <!-- File List -->
      <div class="space-y-1">
        <h3 class="text-sm font-medium text-gray-400 mb-2">All Files</h3>
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
import { IconButton, ActionButton } from '@/apps/builder/components/atoms'
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

const selectFileByPath = (event: Event) => {
  const target = event.target as HTMLSelectElement
  const path = target.value
  const existingFile = props.files.find(f => f.path === path)
  
  if (existingFile) {
    emit('select-file', existingFile)
  } else {
    emit('select-file', {
      path: 'index.html',
      type: 'html',
      content: '' // Adding required content property
    })
  }
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
