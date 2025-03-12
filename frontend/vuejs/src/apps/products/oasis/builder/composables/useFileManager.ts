import { ref, watch } from 'vue'
import { useBuilderStore } from '../stores/builderStore'
import { ProjectService } from '../services'
import { debounce } from 'lodash-es'

const AUTOSAVE_DELAY = 2000 // 2 seconds

export function useFileManager() {
  const store = useBuilderStore()
  const lastSavedContent = ref<string>('')

  // Debounced autosave function
  const autosaveContent = debounce(async (content: string) => {
    if (!store.selectedFile || content === lastSavedContent.value) return

    try {
      store.setProcessing(true)
      await ProjectService.updateFileContent(store.projectId || '', store.selectedFile.path, content)
      lastSavedContent.value = content
      store.setUnsavedChanges(false)
    } catch (error) {
      console.error('Autosave failed:', error)
      // Don't show error notification for autosave failures
    } finally {
      store.setProcessing(false)
    }
  }, AUTOSAVE_DELAY)

  // Handle manual save
  const saveFile = async (content: string) => {
    if (!store.selectedFile) return

    try {
      store.setProcessing(true)
      await ProjectService.updateFileContent(store.projectId || '', store.selectedFile.path, content)
      lastSavedContent.value = content
      store.setUnsavedChanges(false)
    } catch (error) {
      throw error
    } finally {
      store.setProcessing(false)
    }
  }

  // Check for unsaved changes
  const checkUnsavedChanges = (content: string) => {
    if (store.selectedFile) {
      store.setUnsavedChanges(content !== lastSavedContent.value)
    }
  }

  // Reset state when file changes
  watch(
    () => store.selectedFile,
    (newFile) => {
      if (newFile?.content) {
        lastSavedContent.value = newFile.content
      }
    },
    { immediate: true }
  )

  return {
    autosaveContent,
    saveFile,
    checkUnsavedChanges
  }
}