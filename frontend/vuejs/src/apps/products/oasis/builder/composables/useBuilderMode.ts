import { computed } from 'vue'
import { useAgentStore } from '../stores/agentStore'
import { AgentService, ModelService } from '../services/agentService'
import { ProjectService } from '../services/projectService'
import type { ProjectFile, AIModel } from '../types/builder'
import { notify } from '@/shared/utils/notifications'

interface CodeChange {
  file_path: string
  content: string
}

export function useBuilderMode() {
  // Support both old and new store for backward compatibility
  const agentStore = useAgentStore()
  // Use the agent store if available, otherwise fallback to builder store
  const store = agentStore

  const generateCodeFromPrompt = async (prompt: string) => {
    if (!store.projectId || !store.selectedModel) {
      throw new Error('Project and AI Model must be selected')
    }

    store.$patch({ isProcessing: true, error: null })

    try {
      const response = await AgentService.generateCode(store.projectId, {
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
      store.$patch({ error })
      throw err
    } finally {
      store.$patch({ isProcessing: false })
    }
  }

  const updateFile = async (projectId: string, filePath: string, content: string) => {
    if (!store.selectedFile) return

    try {
      await ProjectService.updateFileContent(projectId, filePath, content)
      store.$patch({ unsavedChanges: false })
    } catch (err) {
      store.$patch({ error: 'Failed to save file changes' })
      throw err
    }
  }

  const selectFile = async (file: ProjectFile) => {
    if (!store.projectId) {
      throw new Error('No project selected')
    }

    try {
      const fileData = await ProjectService.getFile(store.projectId, file.path)
      store.selectFile({
        ...file,
        content: fileData.content
      })
    } catch (err) {
      store.$patch({ error: 'Failed to load file content' })
      throw err
    }
  }

  const createFile = async (name: string, type: string, content = '', projectId?: string, path?: string): Promise<ProjectFile | null> => {
    console.log(`useBuilderMode: Creating file "${name}" (${type})${path ? ` at path ${path}` : ''} for project ${projectId || store.projectId}`)
    
    if (!name) {
      console.error('useBuilderMode: Cannot create file - name is required')
      notify({ type: 'error', message: 'File name is required' })
      return null
    }
    
    if (!type) {
      console.error('useBuilderMode: Cannot create file - type is required')
      notify({ type: 'error', message: 'File type is required' })
      return null
    }
    
    // Use store project ID if none provided
    const targetProjectId = projectId || store.projectId
    
    if (!targetProjectId) {
      console.error('useBuilderMode: Cannot create file - no project ID available')
      notify({ type: 'error', message: 'No project ID available. Please reload the page.' })
      return null
    }
    
    try {
      // Extract extension from name if needed and generate path
      let fileName = name
      let filePath = path

      // If path is not provided, construct it from name
      if (!filePath) {
        // Only handle extension extraction if type is not already an extension
        if (!fileName.includes('.') && !['html', 'css', 'js', 'py', 'json', 'txt'].includes(type)) {
          filePath = `${fileName}.${type}`
        } else {
          filePath = fileName
        }
      }
      
      console.log(`useBuilderMode: Final file details - name: ${fileName}, type: ${type}, path: ${filePath}, projectId: ${targetProjectId}`)
      
      // Create file via ProjectService - pass the required 3 parameters (projectId, filePath, content)
      const newFile = await ProjectService.createFile(targetProjectId, filePath || fileName, content)
      
      // Add file to store
      if (newFile) {
        console.log('useBuilderMode: File created successfully, updating store')
        // Check if store.files exists before pushing
        if (!store.files) {
          console.log('useBuilderMode: Initializing store.files as empty array')
          store.$patch({ files: [] });
        }
        
        // Now safely push to store.files
        if (Array.isArray(store.files)) {
          store.files.push(newFile);
        } else {
          console.log('useBuilderMode: store.files is not an array, setting it directly')
          store.$patch({ files: [newFile] });
        }
        
        notify({ type: 'success', message: `File ${fileName} created successfully` })
        return newFile
      } else {
        console.error('useBuilderMode: Empty response when creating file')
        notify({ type: 'error', message: 'Error creating file: Empty response from server' })
        return null
      }
    } catch (error: any) {
      // Enhanced error handling with more specific messages
      let errorMessage = 'Error creating file'
      
      if (error?.response) {
        // Handle specific HTTP errors
        if (error.response.status === 400) {
          errorMessage = `Invalid file data: ${error.response.data?.detail || error.response.data?.message || 'Please check file details'}`
        } else if (error.response.status === 404) {
          errorMessage = `Project not found: ${targetProjectId}`
        } else if (error.response.status === 403) {
          errorMessage = 'You don\'t have permission to create files in this project'
        } else if (error.response.status === 413) {
          errorMessage = 'File content is too large'
        } else if (error.response.status === 429) {
          errorMessage = 'Rate limit exceeded. Please try again later.'
        } else {
          errorMessage = `Server error (${error.response.status}): ${error.response.data?.detail || error.response.data?.message || 'Unknown error'}`
        }
      } else if (error?.message) {
        errorMessage = error.message
      }
      
      console.error(`useBuilderMode: Error creating file:`, error)
      notify({ type: 'error', message: errorMessage })
      return null
    }
  }

  const undoLastAction = async (filePath?: string) => {
    if (!store.projectId) {
      throw new Error('No project selected')
    }

    try {
      store.$patch({ isProcessing: true })
      const result = await AgentService.undoAction(store.projectId, filePath)
      
      // Refresh file content if needed
      if (store.selectedFile && (!filePath || store.selectedFile.path === filePath)) {
        const fileData = await ProjectService.getFile(store.projectId, store.selectedFile.path)
        store.selectFile({
          ...store.selectedFile,
          content: fileData.content
        })
      }
      
      return result
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Failed to undo last action'
      store.$patch({ error })
      throw err
    } finally {
      store.$patch({ isProcessing: false })
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

    store.$patch({ isProcessing: true, error: null })

    try {
      // Instead of using a direct axios call to a non-existent endpoint,
      // we should use the AgentService to generate code suggestions
      // This could use the build/template endpoint with a specific mode
      const response = await AgentService.generateCode(store.projectId, {
        prompt: `Please suggest improvements or alternatives for the code in ${filePath}`,
        mode: 'suggest',
        model: store.selectedModel?.id || 'claude-3-5-sonnet-20241022',
        file_path: filePath
      })
      
      return response.code ? [response.code] : []
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Failed to get code suggestions'
      store.$patch({ error })
      throw err
    } finally {
      store.$patch({ isProcessing: false })
    }
  }

  const applyCodeChanges = async (changes: CodeChange) => {
    if (!store.projectId) {
      throw new Error('No project selected')
    }

    store.$patch({ isProcessing: true, error: null })

    try {
      // Instead of using a direct axios call to a non-existent endpoint,
      // we should update the file using ProjectService
      await ProjectService.updateFileContent(
        store.projectId, 
        changes.file_path, 
        changes.content
      )
      
      return { success: true }
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Failed to apply code changes'
      store.$patch({ error })
      throw err
    } finally {
      store.$patch({ isProcessing: false })
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
    applyCodeChanges
  }
}
