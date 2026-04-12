<template>
  <button
    @click.stop.prevent="handlePreviewClick"
    :disabled="isPreviewLoading"
    :class="[
      'group relative',
      isPreviewLoading ? 'cursor-wait' : 'cursor-pointer'
    ]"
  >
    <div :class="[
      'relative px-4 py-1.5 rounded-lg border border-gray-200 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] transition-all duration-300 flex items-center gap-2',
      isPreviewLoading ? 'opacity-70' : 'hover:bg-gray-50 dark:hover:bg-white/[0.06]'
    ]">
      <i :class="[
        'text-xs text-gray-700 dark:text-white/70',
        isPreviewLoading ? 'fas fa-spinner fa-spin' : 'fas fa-play'
      ]"></i>
      <span class="text-sm font-semibold text-gray-900 dark:text-white/90">{{ isPreviewLoading ? 'Loading...' : 'Preview App' }}</span>
    </div>
  </button>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { PreviewService } from '../../../services/previewService'
import { useNotification } from '@/shared/composables/useNotification'

const props = defineProps<{
  projectId: string
}>()

const isPreviewLoading = ref(false)
const localClickGuard = ref(false)

function handlePreviewClick() {
  if (isPreviewLoading.value || localClickGuard.value) return
  localClickGuard.value = true
  handlePreview()
  setTimeout(() => { localClickGuard.value = false }, 2000)
}

async function handlePreview() {
  if (isPreviewLoading.value) {
    return
  }

  isPreviewLoading.value = true

  const { showNotification } = useNotification()

  try {
    if (!props.projectId) {
      showNotification({
        type: 'error',
        message: 'No project selected for preview',
        duration: 3000
      })
      return
    }

    const response = await PreviewService.generatePreview(props.projectId)

    if (response && response.previewUrl) {
      window.open(response.previewUrl, '_blank')
      showNotification({
        type: 'success',
        message: 'Preview opened in new tab',
        duration: 3000
      })
    } else {
      showNotification({
        type: 'error',
        message: 'Failed to start preview server',
        duration: 4000
      })
    }
  } catch (error) {
    console.error('Error starting preview server:', error)
    showNotification({
      type: 'error',
      message: `Preview failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
      duration: 5000
    })
  } finally {
    setTimeout(() => {
      isPreviewLoading.value = false
    }, 1000)
  }
}
</script>
