<template>
  <div class="flex-1 min-h-0 relative overflow-hidden">
    <div class="rounded-2xl border border-white/[0.06] bg-[#0a0a0f]/80 backdrop-blur-xl flex flex-col h-full min-h-0 shadow-2xl shadow-black/20">
      <!-- Header with back button and badge -->
      <div class="flex items-center justify-between px-4 py-2.5 border-b border-white/[0.06] bg-gradient-to-r from-[#0a0a0f]/90 to-[#0d0d14]/90">
        <button
          class="inline-flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border border-white/[0.08] bg-white/[0.03] text-gray-300 hover:text-white hover:bg-white/[0.06] hover:border-white/10 transition-all duration-200"
          @click="$emit('back')"
        >
          <i class="fas fa-arrow-left text-[10px]"></i>
          <span>Back</span>
        </button>
        <div class="flex items-center gap-2">
          <div class="inline-flex items-center gap-1.5 text-[11px] px-2.5 py-1 rounded-full border border-violet-500/20 bg-violet-500/10 text-violet-300">
            <i class="fas fa-code text-[9px]"></i>
            <span>Advanced</span>
          </div>
        </div>
      </div>
      
      <!-- Accent gradient line -->
      <div class="h-px w-full bg-gradient-to-r from-transparent via-violet-500/40 to-transparent"></div>
      
      <!-- File browser content -->
      <div class="flex-1 min-h-0 overflow-hidden">
        <VisualFileBrowser
          :files="files"
          :selected-file="selectedFile"
          :file-types="fileTypes"
          :project-id="projectId"
          @select-file="$emit('select-file', $event)"
          @create-file="$emit('create-file', $event)"
          @delete-file="$emit('delete-file', $event)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import VisualFileBrowser from './VisualFileBrowser.vue'

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

