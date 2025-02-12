import { ref, computed } from 'vue'
import type { Ref } from 'vue'
import { useProjectStore } from '../stores/projectStore'
import { useAI } from './useAI'
import { BuilderAPI } from '../services/api'
import type { Project } from '@/shared/types/project'
import type { AIModel, ProjectFile, BuilderMode, EditorMode, CodeGenerationResponse } from '../types/builder'

// Constants
export const FILE_TYPES = {
  HTML: 'html',
  CSS: 'css',
  JAVASCRIPT: 'javascript',
  TYPESCRIPT: 'typescript',
  PYTHON: 'python',
  MARKDOWN: 'markdown',
  TEXT: 'text'
} as const

export function useBuilder() {
  // Store and composables
  const store = useProjectStore()
  const { sendPrompt, isGenerating: aiGenerating } = useAI()
  
  // Local state
  const currentProject = ref<Project | null>(null)
  const isLoading = ref(false)
  const currentMode = ref<BuilderMode>('chat')
  const error = ref<string | null>(null)
  const componentTree = ref<any[]>([]) // TODO: Add proper type
  const selectedComponent = ref<any | null>(null) // TODO: Add proper type

  // File management state
  const files = ref<ProjectFile[]>([])
  const selectedFile = ref<ProjectFile | null>(null)
  const fileContent = ref('')
  const hasUnsavedChanges = ref(false)
  const undoStack = ref<{ action: string; data: any }[]>([])

  // Computed properties
  const projectId = computed(() => currentProject.value?.id)
  const availableModels = computed(() => store.availableModels)
  const selectedModel = computed({
    get: () => store.selectedModel,
    set: (value: string | null) => store.setSelectedModel(value)
  })

  /**
   * Load project details and related data
   */
  const loadProject = async (id: string) => {
    if (!id) return
    try {
      isLoading.value = true
      const project = await store.fetchProject(id)
      currentProject.value = project
      await loadFiles()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load project'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Load the component tree for the current project
   */
  const loadComponentTree = async () => {
    if (!projectId.value) return

    isLoading.value = true
    error.value = null

    try {
      const components = await BuilderAPI.getComponentTree(projectId.value)
      componentTree.value = components
    } catch (err) {
      console.error('Failed to load component tree:', err)
      error.value = err instanceof Error ? err.message : 'Failed to load component tree'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * File management methods
   */
  const loadFiles = async () => {
    if (!projectId.value) return

    isLoading.value = true
    error.value = null

    try {
      const projectFiles = await BuilderAPI.getProjectFiles(projectId.value)
      files.value = projectFiles
    } catch (err) {
      console.error('Failed to load files:', err)
      error.value = err instanceof Error ? err.message : 'Failed to load files'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const selectFile = async (file: ProjectFile) => {
    if (!projectId.value) return

    try {
      const { content } = await BuilderAPI.getFileContent(projectId.value, file.path)
      selectedFile.value = file
      fileContent.value = content
      hasUnsavedChanges.value = false
    } catch (err) {
      console.error('Failed to select file:', err)
      error.value = err instanceof Error ? err.message : 'Failed to load file content'
      throw err
    }
  }

  const updateFile = async (content: string) => {
    if (!projectId.value || !selectedFile.value) return

    try {
      await BuilderAPI.updateFileContent(projectId.value, selectedFile.value.path, content)
      fileContent.value = content
      hasUnsavedChanges.value = false
    } catch (err) {
      console.error('Failed to update file:', err)
      error.value = err instanceof Error ? err.message : 'Failed to update file'
      throw err
    }
  }

  const createFile = async (name: string, type: string) => {
    if (!projectId.value) return

    try {
      const newFile = await BuilderAPI.createFile(projectId.value, {
        name,
        type,
        content: ''
      })
      await loadFiles()
      return newFile
    } catch (err) {
      console.error('Failed to create file:', err)
      error.value = err instanceof Error ? err.message : 'Failed to create file'
      throw err
    }
  }

  /**
   * AI code generation methods
   */
  const generateCode = async (prompt: string): Promise<CodeGenerationResponse> => {
    if (!projectId.value) throw new Error('No project selected')

    try {
      const response = await BuilderAPI.generateCode(projectId.value, {
        prompt,
        mode: currentMode.value,
        model: selectedModel.value,
        file: selectedFile.value?.path
      })
      return response
    } catch (err) {
      console.error('Failed to generate code:', err)
      error.value = err instanceof Error ? err.message : 'Failed to generate code'
      throw err
    }
  }

  /**
   * Model management methods
   */
  const loadAvailableModels = async () => {
    try {
      await store.fetchAvailableModels()
    } catch (err) {
      console.error('Failed to load models:', err)
      error.value = err instanceof Error ? err.message : 'Failed to load AI models'
    }
  }

  /**
   * Undo last action in the current workspace
   */
  const undoLastAction = async () => {
    if (!projectId.value) return
    
    try {
      isLoading.value = true
      const response = await BuilderAPI.undoAction(projectId.value)
      
      // Refresh relevant state based on the undone action
      if (response.type === 'file') {
        await loadFiles()
        if (selectedFile.value) {
          await selectFile(selectedFile.value)
        }
      } else if (response.type === 'component') {
        await loadComponentTree()
      }
    } catch (err) {
      console.error('Failed to undo action:', err)
      error.value = err instanceof Error ? err.message : 'Failed to undo last action'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    // State
    currentProject,
    availableModels,
    selectedModel,
    isLoading: computed(() => isLoading.value || store.loading),
    error: computed(() => error.value || store.error),
    files,
    selectedFile,
    fileContent,
    hasUnsavedChanges,
    currentMode,
    aiGenerating,
    componentTree,
    selectedComponent,
    FILE_TYPES,

    // Methods
    loadProject,
    loadFiles,
    selectFile,
    updateFile,
    createFile,
    generateCode,
    loadAvailableModels,
    loadComponentTree,
    undoLastAction // Add undoLastAction to returned methods
  }
}
