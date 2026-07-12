import { useAgentStore } from '../stores/agentStore'
import { ModelService } from '../services/agentService'
import { FileService } from '../services/fileService'
import type { CreateFileOptions } from '../types/composables'
import type { ProjectFile } from '../types/components'
import type { EditorLanguage } from '@/shared/types/editor'

/**
 * Workspace file/model helpers.
 *
 * AI interaction happens through the single Imagi agent
 * (AgentService.processAgent); this composable only covers the
 * non-agent workspace operations: saving files, creating files,
 * and loading the available models.
 */
export function useBuilderMode() {
  const store = useAgentStore()

  const updateFile = async (projectId: string, filePath: string, content: string) => {
    try {
      await FileService.updateFileContent(projectId, filePath, content)
      store.$patch({ unsavedChanges: false })
    } catch (err) {
      store.$patch({ error: 'Failed to save file changes' })
      throw err
    }
  }

  const createFile = async (options: CreateFileOptions | string, typeOrOptions?: string, content = '') => {
    try {
      let name: string
      let type: string
      let fileContent = ''
      let projectId: string | null = null
      let path: string | undefined

      // Handle both options object and legacy positional arguments
      if (typeof options === 'object') {
        name = options.name
        type = options.type
        fileContent = options.content || ''
        projectId = options.projectId
        path = options.path
      } else {
        name = options
        type = typeOrOptions || ''
        fileContent = content
        projectId = store.projectId
      }

      if (!projectId) {
        return null
      }

      store.setProcessing(true)

      // Normalize file path
      let filePath = path || name

      // If no explicit path was provided, add extension based on type
      if (!path && !filePath.includes('.') && !['html', 'css', 'js', 'py', 'json', 'txt'].includes(type)) {
        filePath = `${name}.${type}`
      }

      const fileServiceResult = await FileService.createFile(projectId, filePath, fileContent)

      const newFile: ProjectFile = {
        path: fileServiceResult.path,
        type: (fileServiceResult.type || type) as EditorLanguage,
        content: fileContent,
        lastModified: fileServiceResult.lastModified || new Date().toISOString()
      }

      store.addFile(newFile)
      return newFile
    } catch (error: any) {
      console.error('Failed to create file:', error)
      return null
    } finally {
      store.setProcessing(false)
    }
  }

  // Load models from the backend or use default models
  const loadModels = async () => {
    try {
      const defaultModels = ModelService.getDefaultModels()

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

  return {
    updateFile,
    createFile,
    loadModels
  }
}
