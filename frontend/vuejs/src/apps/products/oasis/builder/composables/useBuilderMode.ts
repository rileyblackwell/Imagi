import { computed } from 'vue'
import { useAgentStore } from '../stores/agentStore'
import { AgentService, ModelService } from '../services/agentService'
import { ProjectService } from '../services/projectService'
import { FileService } from '../services/fileService'
// Use types from builder.ts since that's what the store uses
import type { AIModel, ProjectFile } from '../types/builder'
import { notify } from '@/shared/utils/notifications'
import type { EditorLanguage } from '@/shared/types/editor'

interface CodeChange {
  file_path: string
  content: string
}

interface GenerateCodeOptions {
  prompt: string
  file: ProjectFile
  projectId: string
  modelId: string
}

interface CreateFileOptions {
  name: string
  type: string
  content?: string
  projectId: string
  path?: string
}

interface ApplyCodeOptions {
  code: string
  file: ProjectFile
  projectId: string
}

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
    }

    if (!projectId) {
      throw new Error('Project ID must be provided')
    }

    if (!file) {
      throw new Error('Please select a file to edit')
    }

    if (!modelId) {
      throw new Error('AI Model must be selected')
    }

    store.$patch({ isProcessing: true, error: null })

    try {
      // Add user message to conversation
      store.addMessage({
        role: 'user',
        content: prompt,
        timestamp: new Date().toISOString()
      })

      // Determine file type to use appropriate API endpoint
      const fileExtension = file.path.split('.').pop()?.toLowerCase() || '';
      
      console.log(`Builder mode: Processing ${file.path} with extension ${fileExtension}`);
      
      let response;
      
      // Call the appropriate service method based on file type
      if (fileExtension === 'css') {
        console.log('Builder mode: Using stylesheet endpoint for CSS file');
        response = await AgentService.generateStylesheet(projectId, {
          prompt,
          model: modelId,
          file_path: file.path
        });
      } else if (['html', 'htm', 'django-html', 'jinja', 'tpl'].includes(fileExtension)) {
        console.log('Builder mode: Using template endpoint for HTML file');
        response = await AgentService.generateCode(projectId, {
          prompt,
          mode: store.mode,
          model: modelId,
          file_path: file.path
        });
      } else {
        // For other file types, use the general code generation endpoint
        console.log(`Builder mode: Using general code endpoint for ${fileExtension} file`);
        response = await AgentService.generateCode(projectId, {
          prompt,
          mode: store.mode,
          model: modelId,
          file_path: file.path
        });
      }

      // Add assistant response to conversation
      if (response) {
        store.addMessage({
          role: 'assistant',
          content: response.response || 'Generated code successfully',
          code: response.code || '',
          timestamp: new Date().toISOString()
        })

        // Update the file with generated code if provided
        if (response.code) {
          await updateFile(projectId, file.path, response.code)
          
          // Update the selected file in the store
          store.setSelectedFile({
            ...file,
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
