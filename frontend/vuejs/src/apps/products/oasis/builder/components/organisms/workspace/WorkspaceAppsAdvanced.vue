<template>
  <div class="flex-1 min-h-0 relative rounded-2xl border overflow-hidden bg-dark-800/60 backdrop-blur-md border-dark-700/60">
    <!-- Advanced header with Back button -->
    <div class="flex items-center justify-between p-2 border-b border-white/10 bg-dark-900/50">
      <button
        class="text-xs px-2 py-1 rounded-md border border-white/10 text-gray-200 hover:text-white hover:bg-white/10 transition"
        @click="$emit('back')"
      >
        <i class="fas fa-arrow-left mr-1"></i> Back
      </button>
      <div class="text-[11px] px-2 py-0.5 rounded-full border bg-dark-800/60 border-dark-700/50 text-gray-300">Advanced</div>
    </div>
    <div class="h-0.5 w-full bg-gradient-to-r from-indigo-500/30 via-violet-500/30 to-indigo-500/30 opacity-70"></div>
    <div class="p-2 h-[calc(100%-2px)] min-h-0 overflow-y-auto">
      <FileExplorer
        :files="files"
        :selected-file="selectedFile"
        :file-types="fileTypes"
        :show-new-form="false"
        :project-id="projectId"
        @select-file="$emit('select-file', $event)"
        @create-file="$emit('create-file', $event)"
        @delete-file="$emit('delete-file', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import FileExplorer from '@/apps/products/oasis/builder/components/molecules/sidebar/FileExplorer.vue'

withDefaults(defineProps<{
  files: any[]
  selectedFile: any | null
  fileTypes: Record<string, string>
  projectId: string
}>(), {
  files: () => [],
  selectedFile: null,
  fileTypes: () => ({}),
  projectId: ''
})

defineEmits(['back', 'select-file', 'create-file', 'delete-file'])
</script>
