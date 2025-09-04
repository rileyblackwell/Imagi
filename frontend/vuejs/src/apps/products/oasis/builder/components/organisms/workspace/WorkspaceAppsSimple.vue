<template>
  <div class="flex-1 min-h-0 relative grid grid-cols-1 gap-4 overflow-hidden auto-rows-[minmax(0,1fr)]">
    <div class="rounded-2xl border bg-dark-800/60 backdrop-blur-md border-dark-700/60 flex flex-col h-full min-h-0">
      <div class="flex items-center justify-between px-3 py-2 border-b border-white/10 bg-dark-900/50">
        <div class="text-[11px] font-medium tracking-wide uppercase text-white/70"></div>
        <div class="flex items-center gap-2"></div>
      </div>
      <div class="h-0.5 w-full bg-gradient-to-r from-indigo-500/30 via-violet-500/30 to-indigo-500/30 opacity-70"></div>
      <div class="p-2 flex-1 min-h-0 overflow-hidden">
        <AppGallery
          class="h-full"
          :files="files"
          :project-id="projectId"
          :version-history="versionHistory"
          :is-loading-versions="isLoadingVersions"
          :selected-version-hash="selectedVersionHash"
          @selectFile="$emit('selectFile', $event)"
          @createApp="$emit('createApp')"
          @preview="$emit('preview', $event)"
          @update:selectedVersionHash="$emit('update:selectedVersionHash', $event)"
          @version-select="$emit('version-select')"
          @version-reset="$emit('version-reset', $event)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppGallery from './AppGallery.vue'

withDefaults(defineProps<{
  files: any[]
  projectId: string
  versionHistory: Array<Record<string, any>>
  isLoadingVersions: boolean
  selectedVersionHash: string
}>(), {
  files: () => [],
  projectId: '',
  versionHistory: () => [],
  isLoadingVersions: false,
  selectedVersionHash: ''
})

defineEmits([
  'selectFile',
  'createApp',
  'preview',
  'update:selectedVersionHash',
  'version-select',
  'version-reset'
])
</script>
