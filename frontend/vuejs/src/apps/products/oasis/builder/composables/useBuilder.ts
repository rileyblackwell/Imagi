import { computed } from 'vue'
import { useBuilderStore } from '../stores/builderStore'
import { BuilderAPI } from '../services/api'
import type { ProjectFile } from '../types/builder'

export function useBuilder() {
  const store = useBuilderStore()

  const generateCodeFromPrompt = async (prompt: string) => {
    if (!store.projectId || !store.selectedModel) {
      throw new Error('Project and AI Model must be selected')
    }

    store.setProcessing(true)
    store.setError(null)

    try {
      const response = await BuilderAPI.generateCode(store.projectId, {
        prompt,
        mode: store.mode,
        model: store.selectedModel.id,
        file_path: store.selectedFile?.path
      })

      if (response.code && store.selectedFile) {
        await updateFile(store.projectId, store.selectedFile.path, response.code)
      }

      return response
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Failed to generate code'
      store.setError(error)
      throw err
    } finally {
      store.setProcessing(false)
    }
  }

  const updateFile = async (projectId: string, filePath: string, content: string) => {
    if (!store.selectedFile) return

    try {
      await BuilderAPI.updateFileContent(projectId, filePath, content)
      store.setUnsavedChanges(false)
    } catch (err) {
      store.setError('Failed to save file changes')
      throw err
    }
  }

  const selectFile = async (file: ProjectFile) => {
    if (!store.projectId) {
      throw new Error('No project selected')
    }

    try {
      const content = await BuilderAPI.getFileContent(store.projectId, file.path)
      store.selectFile({
        ...file,
        content: content.content
      })
    } catch (err) {
      store.setError('Failed to load file content')
      throw err
    }
  }

  const createFile = async (name: string, type: string) => {
    if (!store.projectId) {
      throw new Error('No project selected')
    }

    try {
      store.setProcessing(true)
      const file = await BuilderAPI.createFile(store.projectId, {
        name,
        type,
        content: ''
      })
      return file
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Failed to create file'
      store.setError(error)
      throw err
    } finally {
      store.setProcessing(false)
    }
  }

  return {
    mode: computed(() => store.mode),
    selectedFile: computed(() => store.selectedFile),
    isProcessing: computed(() => store.isProcessing),
    error: computed(() => store.error),
    generateCodeFromPrompt,
    updateFile,
    selectFile,
    createFile,
    setMode: store.setMode,
    setError: store.setError
  }
}
