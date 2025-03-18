import { computed } from 'vue'
import { useAgentStore } from '../stores/agentStore'
import { AgentService, ModelService } from '../services/agentService'
import { ProjectService } from '../services/projectService'
import { FileService } from '../services/fileService'
// Use types from builder.ts since that's what the store uses
import type { AIModel } from '../types/index'
import type { ProjectFile } from '../types/builder'
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

    if (!store.selectedFile) {
      throw new Error('Please select a file to edit')
    }

    store.$patch({ isProcessing: true, error: null })

    try {
      // Add user message to conversation
      store.addMessage({
        role: 'user',
        content: prompt,
        timestamp: new Date().toISOString()
      })

      // Call the agent service to generate code
      const response = await AgentService.generateCode(store.projectId, {
        prompt,
        mode: store.mode,
        model: store.selectedModel.id,
        file_path: store.selectedFile.path
      })

      // Add assistant response to conversation
      if (response) {
        store.addMessage({
          role: 'assistant',
          content: response.response || 'Generated code successfully',
          code: response.code || '',
          timestamp: new Date().toISOString()
        })

        // Update the file with generated code if provided
        if (response.code && store.selectedFile) {
          await updateFile(store.projectId, store.selectedFile.path, response.code)
          
          // Update the selected file in the store
          store.selectFile({
            ...store.selectedFile,
            content: response.code
          })
        }
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
    try {
      const targetProjectId = projectId || store.projectId
      
      if (!targetProjectId) {
        notify({ type: 'error', message: 'No project selected' })
        return null
      }
      
      store.setProcessing(true)
      
      // Normalize file path
      let filePath = path || name
      let fileName = name
      
      // If a file path was provided, use it for file creation
      if (path) {
        filePath = path
      } else {
        // Add extension if needed based on type
        if (!fileName.includes('.') && !['html', 'css', 'js', 'py', 'json', 'txt'].includes(type)) {
          filePath = `${fileName}.${type}`
        } else {
          filePath = fileName
        }
      }
      
      // Create file via FileService 
      const fileServiceResult = await FileService.createFile(targetProjectId, filePath || fileName, content)
      
      // Convert the result to the ProjectFile format expected by the store
      const newFile: ProjectFile = {
        path: fileServiceResult.path,
        type: fileServiceResult.type as any, // Type casting to handle potential incompatibility
        content: content,
        lastModified: fileServiceResult.lastModified || new Date().toISOString()
      }
      
      // Add file to store
      if (newFile) {
        // Refresh project files from server to get the most up-to-date list
        const updatedFiles = await FileService.getProjectFiles(targetProjectId)
        
        // Update store with newest files
        store.$patch((state) => {
          state.files = updatedFiles as any;
        });
        
        notify({ type: 'success', message: `File ${fileName} created successfully` })
        return newFile
      }
      
      return null
    } catch (error: any) {
      notify({ 
        type: 'error', 
        message: error.message || `Failed to create file ${name}` 
      })
      return null
    } finally {
      store.setProcessing(false)
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
