import { useAgentStore } from '../stores/agentStore'
import { AgentService, ModelService } from '../services/agentService'
import { ProjectService } from '../services/projectService'
import { FileService } from '../services/fileService'
import type { ProjectFile } from '../types/components'
import type { GenerateCodeOptions, CreateFileOptions, ApplyCodeOptions } from '../types/composables'
import { notify } from '@/shared/utils/notifications'
import type { EditorLanguage } from '@/shared/types/editor'

export function useBuilderMode() {
  // Support both old and new store for backward compatibility
  const agentStore = useAgentStore()
  // Use the agent store if available, otherwise fallback to builder store
  const store = agentStore

  const generateCodeFromPrompt = async (options: GenerateCodeOptions | string) => {
    let prompt: string;
    let file: ProjectFile | null = null;
    let projectId: string | null = null;
    let modelId: string | null = null;
    let mode: string = 'build'; // Default mode is build

    // Handle both new options object and legacy string argument
    if (typeof options === 'string') {
      prompt = options;
      file = store.selectedFile;
      projectId = store.projectId;
      modelId = store.selectedModelId;
    } else {
      prompt = options.prompt;
      file = options.file;
      projectId = options.projectId;
      modelId = options.modelId;
      mode = options.mode || 'build'; // Use provided mode or default to build
    }

    if (!projectId) {
      const { notify } = await import('@/shared/utils');
      notify({ type: 'error', message: 'No project selected. Please select or create a project first.' });
      throw new Error('Project ID must be provided')
    }

    if (!file) {
      const { notify } = await import('@/shared/utils');
      notify({ type: 'error', message: 'No file selected. Please select or create a file first.' });
      throw new Error('Please select a file to edit')
    }

    if (!modelId) {
      const { notify } = await import('@/shared/utils');
      notify({ type: 'error', message: 'No AI model selected. Please select a model first.' });
      throw new Error('AI Model must be selected')
    }

    store.$patch({ isProcessing: true, error: null })

    try {
      // Set processing state
      store.setProcessing(true)
      
      // Get model by ID for validation
      const model = store.availableModels.find(m => m.id === modelId)
      if (!model) {
        throw new Error(`Model not found: ${modelId}`)
      }
      
      // Prepare required data for code generation
      const codeGenData = {
        prompt,
        model: modelId,
        mode,
        file_path: file?.path
      }
      
      // Log the request parameters (sanitized)
      console.info('Generating code with parameters:', {
        prompt: prompt.substring(0, 50) + '...',
        modelId,
        mode,
        filePath: file?.path,
        projectId
      })
      
      // Check if this is a CSS file and use stylesheet API endpoint
      const isCSS = file.path.endsWith('.css') || file.type === 'css';
      
      let response;
      if (isCSS) {
        // Use stylesheet-specific endpoint
        console.info('Using stylesheet agent for CSS file');
        response = await AgentService.generateStylesheet({
          prompt,
          projectId,
          filePath: file.path,
          model: modelId
        });
      } else {
        // Use regular code generation endpoint
        response = await AgentService.generateCode(projectId, codeGenData);
      }
      
      // Add user message to conversation immediately
      store.addMessage({
        role: 'user',
        content: prompt,
        timestamp: new Date().toISOString(),
      })
      
      // Add assistant message to conversation
      store.addMessage({
        role: 'assistant',
        content: response.response,
        code: response.code || response.response, // Use response as code if code is not available
        timestamp: new Date().toISOString(),
      })
      
      if (file) {
        // Refresh the file content to show latest version
        try {
          const updatedFile = await FileService.getFile(projectId, file.path)
          
          // Update the file in the store
          store.updateFile({
            ...file,
            content: updatedFile.content
          })
          
          // Update the selected file
          store.selectFile(updatedFile)
          
          console.log(`File ${file.path} updated successfully`)
        } catch (refreshError) {
          console.error('Error refreshing file content:', refreshError)
          // Still proceed with the operation even if refresh fails
        }
      }

      // Don't return the response as void return type is expected
    } catch (error) {
      console.error('Error generating code:', error)
      
      // If this is a user-facing error (like API error), wrap it to make it clearer
      if (error instanceof Error) {
        throw new Error(`BuilderAPIError: ${error.message}`)
      }
      
      // Otherwise rethrow
      throw error
    } finally {
      // Reset processing state
      store.setProcessing(false)
    }
  }

  const updateFile = async (projectId: string, filePath: string, content: string) => {
    try {
      await FileService.updateFileContent(projectId, filePath, content)
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
      store.setSelectedFile({
        ...file,
        content: fileData.content
      })
    } catch (err) {
      store.$patch({ error: 'Failed to load file content' })
      throw err
    }
  }

  const createFile = async (options: CreateFileOptions | string, typeOrOptions?: string, content = '') => {
    try {
      let name: string;
      let type: string;
      let fileContent: string = '';
      let projectId: string | null = null;
      let path: string | undefined;

      // Handle both new options object and legacy arguments
      if (typeof options === 'object') {
        name = options.name;
        type = options.type;
        fileContent = options.content || '';
        projectId = options.projectId;
        path = options.path;
      } else {
        name = options;
        type = typeOrOptions || '';
        fileContent = content;
        projectId = store.projectId;
      }
      
      if (!projectId) {
        notify({ message: 'No project selected', type: 'error' })
        return null
      }
      
      store.setProcessing(true)
      
      // Normalize file path
      let filePath = path || name
      
      // If no explicit path was provided, add extension based on type
      if (!path && !filePath.includes('.') && !['html', 'css', 'js', 'py', 'json', 'txt'].includes(type)) {
        filePath = `${name}.${type}`
      }
      
      // Create file via FileService 
      const fileServiceResult = await FileService.createFile(projectId, filePath, fileContent)
      
      // Convert the result to the ProjectFile format expected by the store
      const newFile: ProjectFile = {
        path: fileServiceResult.path,
        type: (fileServiceResult.type || type) as EditorLanguage,
        content: fileContent,
        lastModified: fileServiceResult.lastModified || new Date().toISOString()
      }
      
      // Add file to store
      if (newFile) {
        // Add or update the file in the store
        store.addFile(newFile)
        
        return newFile
      }
      
      return null
    } catch (error: any) {
      console.error('Failed to create file:', error)
      notify({ message: 'Failed to create file', type: 'error' })
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
        store.setSelectedFile({
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

  // Load models from the backend or use default models
  const loadModels = async () => {
    try {
      // Get default models from ModelService
      const defaultModels = ModelService.getDefaultModels()
      
      // Update store with models
      if (defaultModels.length > 0) {
        try {
          store.setModels(defaultModels)
        } catch (storeError) {
          // Fallback: directly update the store state
          store.$patch({ availableModels: defaultModels })
        }
      }
      
      return { success: true }
    } catch (err) {
      console.error('Failed to initialize models', err)
      return { success: false }
    }
  }

  // Apply code to a file
  const applyCode = async (options: ApplyCodeOptions) => {
    const { code, file, projectId } = options;
    
    if (!projectId) {
      throw new Error('Project ID must be provided');
    }
    
    if (!file) {
      throw new Error('File information must be provided');
    }
    
    if (!code) {
      throw new Error('Code content must be provided');
    }
    
    store.setProcessing(true);
    
    try {
      // Update the file with the code
      await updateFile(projectId, file.path, code);
      
      // Update the file in the store
      store.updateFile({
        ...file,
        content: code
      });
      
      return true;
    } catch (error) {
      console.error('Error applying code:', error);
      throw error;
    } finally {
      store.setProcessing(false);
    }
  }

  return {
    generateCodeFromPrompt,
    updateFile,
    selectFile,
    createFile,
    undoLastAction,
    loadModels,
    applyCode
  }
}
