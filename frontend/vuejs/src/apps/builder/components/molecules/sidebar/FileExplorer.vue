<template>
  <div class="flex-1 min-h-0 flex flex-col overflow-hidden">
    <!-- Fixed Sections -->
    <div class="flex-shrink-0">
      <!-- Current File Section -->
      <div class="p-4 border-b border-dark-700">
        <label class="block text-sm font-medium text-gray-400 mb-2">Current File</label>
        <div class="relative">
          <select
            :value="selectedFile?.path"
            @change="selectFileByPath($event)"
            class="w-full appearance-none bg-dark-900 border border-dark-600 rounded-lg text-white px-3 py-2 text-sm truncate"
          >
            <option value="index.html" selected>index.html</option>
            <option v-for="file in files" :key="file.path" :value="file.path" class="truncate">
              {{ file.path }}
            </option>
          </select>
          <div class="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
            <i class="fas fa-chevron-down text-gray-400 text-sm"></i>
          </div>
        </div>
      </div>

      <!-- New File Section -->
      <div class="p-4 border-b border-dark-700">
        <div class="flex items-center justify-between mb-2">
          <label class="text-sm font-medium text-gray-400">New File</label>
          <IconButton
            icon-class="fa-plus"
            size="sm"
            :variant="showNewForm ? 'primary' : 'default'"
            :title="showNewForm ? 'Cancel' : 'New File'"
            @click="toggleNewFileForm"
          />
        </div>

        <div v-if="showNewForm" class="space-y-2">
          <input
            v-model="newFileName"
            type="text"
            placeholder="Enter file name"
            class="w-full bg-dark-900 border border-dark-600 rounded-lg text-white px-3 py-2 text-sm focus:outline-none focus:border-primary-500"
          />
          <select
            v-model="newFileType"
            class="w-full bg-dark-900 border border-dark-600 rounded-lg text-white px-3 py-2 text-sm focus:outline-none focus:border-primary-500"
          >
            <option value="" disabled>Select type</option>
            <option v-for="(type, key) in fileTypes" :key="key" :value="type">
              {{ key.toLowerCase() }}
            </option>
          </select>
          <ActionButton
            text="Create"
            icon="plus"
            :disabled="!canCreateFile"
            :full-width="true"
            variant="primary"
            @click="handleCreateFile"
          />
        </div>
      </div>
    </div>

    <!-- Scrollable File List -->
    <div class="flex-1 overflow-y-auto min-h-0">
      <div class="p-4">
        <label class="block text-sm font-medium text-gray-400 mb-2">Project Files</label>
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
            <i :class="[getFileIcon(file.type), 'mr-2 text-sm flex-shrink-0']"></i>
            <span class="truncate">{{ file.path }}</span>
          </button>
        </div>
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
