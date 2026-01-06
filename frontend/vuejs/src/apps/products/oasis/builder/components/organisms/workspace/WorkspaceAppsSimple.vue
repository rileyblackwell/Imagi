<template>
  <div class="flex-1 min-h-0 relative overflow-hidden">
    <!-- Premium App Gallery Container -->
    <div class="h-full flex flex-col">
      <!-- App Gallery Content -->
      <div class="flex-1 min-h-0 overflow-hidden">
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
