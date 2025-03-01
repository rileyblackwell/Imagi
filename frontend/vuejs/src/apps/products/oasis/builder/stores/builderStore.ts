import { defineStore } from 'pinia'
import type { AIModel, BuilderMode, ProjectFile } from '../types/builder'
import type { AIMessage } from '../types/api'

interface BuilderState {
  projectId: string | null
  mode: BuilderMode
  selectedModelId: string | null
  availableModels: AIModel[]
  conversation: AIMessage[]
  selectedFile: ProjectFile | null
  files: ProjectFile[]
  unsavedChanges: boolean
  isProcessing: boolean
  error: string | null
}

export const useBuilderStore = defineStore('builder', {
  state: (): BuilderState => ({
    projectId: null,
    mode: 'build',
    selectedModelId: null,
    availableModels: [],
    conversation: [],
    selectedFile: null,
    files: [],
    unsavedChanges: false,
    isProcessing: false,
    error: null
  }),

  getters: {
    selectedModel: (state) => 
      state.availableModels.find(m => m.id === state.selectedModelId),
    
    canSubmitPrompt: (state) => 
      !!state.selectedModelId && !state.isProcessing,
    
    canSwitchMode: (state) => 
      !state.isProcessing && (!state.unsavedChanges || confirm('You have unsaved changes. Continue?'))
  },

  actions: {
    setProjectId(id: string | null) {
      this.projectId = id
    },

    setMode(mode: BuilderMode) {
      if (this.canSwitchMode) {
        this.mode = mode
        // Clear conversation when switching to build mode
        if (mode === 'build') {
          this.conversation = []
        }
      }
    },

    setModels(models: AIModel[]) {
      this.availableModels = models
      // Set default model if none selected
      if (!this.selectedModelId && models.length > 0) {
        this.selectedModelId = models[0].id
      }
    },

    selectModel(modelId: string) {
      const model = this.availableModels.find(m => m.id === modelId)
      if (model) {
        this.selectedModelId = modelId
      }
    },

    addMessage(message: AIMessage) {
      this.conversation.push(message)
    },

    selectFile(file: ProjectFile | null) {
      if (this.unsavedChanges) {
        if (!confirm('You have unsaved changes. Switch files anyway?')) {
          return
        }
      }
      this.selectedFile = file
      this.unsavedChanges = false
    },

    setUnsavedChanges(value: boolean) {
      this.unsavedChanges = value
    },

    setProcessing(value: boolean) {
      this.isProcessing = value
    },

    setError(error: string | null) {
      this.error = error
    },

    reset() {
      this.$reset()
    }
  }
})