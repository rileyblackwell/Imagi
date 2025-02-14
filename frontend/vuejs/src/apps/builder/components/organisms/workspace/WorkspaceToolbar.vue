<template>
  <div class="flex items-center justify-between h-12 px-4 bg-dark-800 border-b border-dark-700">
    <!-- Left Section -->
    <div class="flex items-center space-x-4">
      <div class="flex flex-col">
        <h2 class="text-sm font-medium text-white">{{ title }}</h2>
        <p class="text-xs text-gray-400">{{ subtitle }}</p>
      </div>
      <div v-if="showSave" class="flex items-center space-x-2">
        <span
          v-if="hasUnsavedChanges"
          class="text-xs text-yellow-400"
        >
          <i class="fas fa-circle"></i>
          Unsaved changes
        </span>
        <button
          @click="$emit('save')"
          class="px-3 py-1 text-sm bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          :disabled="loading || !hasUnsavedChanges"
        >
          <i class="fas fa-save mr-1"></i>
          Save
        </button>
      </div>
    </div>

    <!-- Right Section -->
    <div class="flex items-center space-x-3">
      <!-- Mode Toggle -->
      <div class="flex items-center bg-dark-900 rounded-lg p-1">
        <button
          v-for="mode in modes"
          :key="mode"
          @click="$emit('modeChange', mode)"
          class="px-3 py-1 text-sm rounded-md transition-colors"
          :class="[
            currentMode === mode
              ? 'bg-primary-500 text-white'
              : 'text-gray-400 hover:text-white'
          ]"
        >
          <i :class="getModeIcon(mode)" class="mr-1"></i>
          {{ mode.charAt(0).toUpperCase() + mode.slice(1) }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Add type for view modes
type ViewMode = 'split' | 'editor' | 'preview'

// Add constant array of valid modes
const modes: ViewMode[] = ['split', 'editor', 'preview']

const props = defineProps<{
  title: string
  subtitle?: string
  hasUnsavedChanges: boolean
  loading: boolean
  showSave: boolean
  currentMode: ViewMode
}>()

const getModeIcon = (mode: ViewMode): string => {
  const icons: Record<ViewMode, string> = {
    split: 'fas fa-columns',
    editor: 'fas fa-code',
    preview: 'fas fa-eye'
  }
  return icons[mode]
}
</script>
