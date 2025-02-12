<template>
  <div class="relative h-full">
    <!-- Preview Header -->
    <div class="absolute top-0 left-0 right-0 h-12 bg-dark-800 border-b border-dark-700 flex items-center px-4 z-10">
      <div class="flex-1 flex items-center space-x-4">
        <!-- Device Selection -->
        <select
          v-model="selectedDevice"
          class="bg-dark-900 border border-dark-600 rounded-lg text-white px-3 py-1 text-sm"
        >
          <option value="desktop">Desktop</option>
          <option value="tablet">Tablet</option>
          <option value="mobile">Mobile</option>
        </select>

        <!-- Refresh Button -->
        <button
          @click="refreshPreview"
          class="text-gray-400 hover:text-white transition-colors"
          :class="{ 'animate-spin': isLoading }"
        >
          <i class="fas fa-sync-alt"></i>
        </button>

        <!-- URL Display -->
        <div class="flex-1 px-3 py-1 bg-dark-900 rounded-lg text-sm text-gray-400 font-mono truncate">
          {{ previewUrl }}
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center space-x-2 ml-4">
        <button
          @click="openInNewTab"
          class="text-gray-400 hover:text-white transition-colors"
          title="Open in new tab"
        >
          <i class="fas fa-external-link-alt"></i>
        </button>
        <button
          @click="$emit('close')"
          class="text-gray-400 hover:text-white transition-colors"
          title="Close preview"
        >
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>

    <!-- Preview Frame -->
    <div class="absolute top-12 left-0 right-0 bottom-0 bg-white">
      <iframe
        ref="previewFrame"
        :src="previewUrl"
        class="w-full h-full border-none"
        :class="deviceClasses"
        @load="handleLoad"
      ></iframe>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Ref } from 'vue'

const props = defineProps<{
  projectId: string
  previewUrl: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'load'): void
}>()

const selectedDevice: Ref<'desktop' | 'tablet' | 'mobile'> = ref('desktop')
const isLoading = ref(false)
const previewFrame = ref<HTMLIFrameElement | null>(null)

const deviceClasses = computed(() => ({
  'max-w-full': selectedDevice.value === 'desktop',
  'max-w-[768px] mx-auto': selectedDevice.value === 'tablet',
  'max-w-[375px] mx-auto': selectedDevice.value === 'mobile'
}))

const refreshPreview = async () => {
  isLoading.value = true
  if (previewFrame.value) {
    previewFrame.value.src = `${props.previewUrl}?t=${Date.now()}`
  }
}

const openInNewTab = () => {
  window.open(props.previewUrl, '_blank')
}

const handleLoad = () => {
  isLoading.value = false
  emit('load')
}
</script>

<style scoped>
.preview-frame-enter-active,
.preview-frame-leave-active {
  transition: opacity 0.3s ease;
}

.preview-frame-enter-from,
.preview-frame-leave-to {
  opacity: 0;
}
</style>
