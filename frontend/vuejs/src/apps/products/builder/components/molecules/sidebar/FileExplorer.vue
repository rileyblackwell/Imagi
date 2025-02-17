<template>
  <div class="p-4">
    <div class="flex items-center justify-between mb-2">
      <label class="text-sm font-medium text-gray-400">Files</label>
      <button
        @click="showNewForm = true"
        class="text-xs text-primary-400 hover:text-primary-300"
      >
        <i class="fas fa-plus mr-1"></i>
        New
      </button>
    </div>

    <!-- File Select Dropdown -->
    <div class="relative mb-4">
      <select
        v-model="selectedFilePath"
        class="w-full appearance-none bg-dark-900 border border-dark-600 rounded-lg text-white px-3 py-2.5 text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-500/20 pr-10"
        @change="handleFileSelect"
      >
        <option value="" disabled>Select File</option>
        <option
          v-for="file in files"
          :key="file.path"
          :value="file.path"
          class="py-2"
        >
          {{ file.path }}
        </option>
      </select>
      <div class="absolute inset-y-0 right-0 flex items-center px-3 pointer-events-none">
        <i class="fas fa-chevron-down text-gray-400 text-xs"></i>
      </div>
    </div>

    <!-- New File Form -->
    <div v-if="showNewForm" class="mt-4 p-4 bg-dark-800/50 rounded-lg">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-400 mb-1">File Name</label>
          <input
            v-model="newFileName"
            type="text"
            placeholder="Enter file name"
            class="w-full bg-dark-900 border border-dark-600 rounded-lg text-white px-3 py-2 text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-500/20"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-400 mb-1">File Type</label>
          <select
            v-model="newFileType"
            class="w-full appearance-none bg-dark-900 border border-dark-600 rounded-lg text-white px-3 py-2 text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-500/20"
          >
            <option value="" disabled>Select Type</option>
            <option
              v-for="(label, type) in fileTypes"
              :key="type"
              :value="type"
            >
              {{ label }}
            </option>
          </select>
        </div>
        <div class="flex justify-end space-x-2">
          <button
            @click="showNewForm = false"
            class="px-3 py-1.5 text-sm text-gray-400 hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            @click="handleCreateFile"
            :disabled="!canCreateFile"
            :class="[
              'px-3 py-1.5 text-sm rounded-md transition-colors',
              canCreateFile
                ? 'bg-primary-500 text-white hover:bg-primary-600'
                : 'bg-dark-700 text-gray-400 cursor-not-allowed'
            ]"
          >
            Create
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ProjectFile } from '@/apps/products/builder/types/builder'

const props = defineProps<{
  files: ProjectFile[]
  selectedFile: ProjectFile | null
  showNewForm?: boolean
  fileTypes: Record<string, string>
}>()

const emit = defineEmits<{
  (e: 'selectFile', file: ProjectFile): void
  (e: 'createFile', data: { name: string; type: string }): void
}>()

const selectedFilePath = ref(props.selectedFile?.path || '')
const showNewForm = ref(props.showNewForm || false)
const newFileName = ref('')
const newFileType = ref('')

const canCreateFile = computed(() => 
  newFileName.value.trim() && newFileType.value
)

const handleFileSelect = () => {
  const file = props.files.find(f => f.path === selectedFilePath.value)
  if (file) {
    emit('selectFile', file)
  }
}

const handleCreateFile = () => {
  if (canCreateFile.value) {
    emit('createFile', {
      name: newFileName.value.trim(),
      type: newFileType.value
    })
    // Reset form
    newFileName.value = ''
    newFileType.value = ''
    showNewForm.value = false
  }
}
</script>
