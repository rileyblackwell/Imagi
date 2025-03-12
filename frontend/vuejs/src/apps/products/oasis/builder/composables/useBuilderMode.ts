import { computed } from 'vue'
import { useBuilderStore } from '../stores/builderStore'
import { BuilderService, ProjectService, ModelService } from '../services'
import type { ProjectFile, AIModel } from '../types/builder'
import axios from 'axios'

interface CodeChange {
  file_path: string
  content: string
}

export function useBuilderMode() {
  const store = useBuilderStore()

  const generateCodeFromPrompt = async (prompt: string) => {
    if (!store.projectId || !store.selectedModel) {
      throw new Error('Project and AI Model must be selected')
    }

    store.setProcessing(true)
    store.setError(null)

    try {
      const response = await BuilderService.generateCode(store.projectId, {
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
      await ProjectService.updateFileContent(projectId, filePath, content)
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
      const content = await ProjectService.getFileContent(store.projectId, file.path)
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
      const file = await ProjectService.createFile(store.projectId, {
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

  const undoLastAction = async () => {
    if (!store.projectId) {
      throw new Error('No project selected')
    }

    try {
      store.setProcessing(true)
      const result = await BuilderService.undoAction(store.projectId)
      
      // Refresh file content if needed
      if (store.selectedFile) {
        const content = await ProjectService.getFileContent(store.projectId, store.selectedFile.path)
        store.selectFile({
          ...store.selectedFile,
          content: content.content
        })
      }
      
      return result
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Failed to undo last action'
      store.setError(error)
      throw err
    } finally {
      store.setProcessing(false)
    }
  }

  // Simplified loadModels function that only uses frontend data
  const loadModels = async () => {
    try {
      // Get default models from the ModelService
      const defaultModels = ModelService.getDefaultModels()
      
      // Update store with models
      try {
        store.setModels(defaultModels)
      } catch (storeError) {
        // Fallback: directly update the store state if the action fails
        store.$patch({ availableModels: defaultModels })
      }
      
      // Set a default selected model if none is selected
      if (!store.selectedModelId && defaultModels.length > 0) {
        try {
          store.selectModel(defaultModels[0].id)
        } catch (storeError) {
          // Fallback: directly update the store state if the action fails
          store.$patch({ selectedModelId: defaultModels[0].id })
        }
      }
      
      // Force a store update to ensure reactivity
      store.$patch({})
      
      return { success: true }
    } catch (err) {
      console.error('Failed to initialize models', err)
      return { success: true }
    }
  }

  const getCodeSuggestions = async (filePath: string) => {
    if (!store.projectId) {
      throw new Error('No project selected')
    }

    store.setProcessing(true)
    store.setError(null)

    try {
      const response = await axios.post('/api/v1/products/oasis/builder/suggest/', {
        project_id: store.projectId,
        file_path: filePath
      })
      return response.data.suggestions
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Failed to get code suggestions'
      store.setError(error)
      throw err
    } finally {
      store.setProcessing(false)
    }
  }

  const applyCodeChanges = async (changes: CodeChange) => {
    if (!store.projectId) {
      throw new Error('No project selected')
    }

    store.setProcessing(true)
    store.setError(null)

    try {
      const response = await axios.post(`/api/v1/products/oasis/builder/apply/${store.projectId}/`, changes)
      return response.data
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Failed to apply code changes'
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
    undoLastAction,
    loadModels,
    getCodeSuggestions,
    applyCodeChanges,
    setMode: store.setMode,
    setError: store.setError
  }
}
