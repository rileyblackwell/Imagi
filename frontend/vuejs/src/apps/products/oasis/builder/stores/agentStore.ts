import { defineStore } from 'pinia'
import type { AIModel } from '../types/services'
import type { AIMessage } from '../types/services'
import type { AgentState } from '../types/stores'
import type { BuilderMode, ProjectFile } from '../types/components'
import { FileService } from '../services/fileService'

export const useAgentStore = defineStore('agent', {
  state: (): AgentState => ({
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
      } else {
        console.warn('Cannot switch mode due to unsaved changes or processing')
      }
    },

    setModels(models: AIModel[]) {
      this.availableModels = models
      
      // Set default model if none selected
      if (!this.selectedModelId && models.length > 0) {
        this.selectedModelId = models[0].id
      }
    },

    setSelectedModelId(modelId: string) {
      const model = this.availableModels.find(m => m.id === modelId)
      if (model) {
        this.selectedModelId = modelId
      } else {
        // Just use the model ID as-is if not found in available models
        this.selectedModelId = modelId
      }
    },

    selectModel(modelId: string) {
      this.setSelectedModelId(modelId)
    },

    addMessage(message: AIMessage) {
      // console.log('AgentStore: Adding message to conversation:', message)
      
      // Ensure message has valid properties
      const validMessage = {
        ...message,
        role: message.role || 'user',
        content: message.content || '',
        timestamp: message.timestamp || new Date().toISOString()
      }
      
      // Check for truncated content with ellipsis that might come from console logs
      if (validMessage.content && validMessage.content.includes('…')) {
        console.warn('AgentStore: Message content contains truncation characters (…)')
      }
      
      this.conversation.push(validMessage)
      // console.log('AgentStore: Conversation after adding message:', [...this.conversation])
    },

    updateLastAssistantMessage(content: string) {
      const lastMessageIndex = this.conversation.length - 1
      if (lastMessageIndex >= 0 && this.conversation[lastMessageIndex].role === 'assistant') {
        this.conversation[lastMessageIndex].content = content
      }
    },

    removeLastMessage() {
      if (this.conversation.length > 0) {
        this.conversation.pop()
      }
    },

    clearConversation() {
      this.conversation = []
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

    setSelectedFile(file: ProjectFile | null) {
      this.selectedFile = file
      this.unsavedChanges = false
    },

    // Files management
    setFiles(files: ProjectFile[]) {
      if (Array.isArray(files)) {
        this.files = [...files]
      } else {
        console.error('Files is not an array:', files)
        this.files = []
      }
    },

    addFile(file: ProjectFile) {
      // Check if file already exists by path
      const existingIndex = this.files.findIndex(f => f.path === file.path)
      if (existingIndex >= 0) {
        // Update existing file
        this.files[existingIndex] = file
      } else {
        // Add new file
        this.files.push(file)
      }
    },

    removeFile(file: ProjectFile) {
      const index = this.files.findIndex(f => f.path === file.path)
      if (index >= 0) {
        this.files.splice(index, 1)
      }
    },

    updateFile(file: ProjectFile) {
      const index = this.files.findIndex(f => f.path === file.path)
      if (index >= 0) {
        this.files[index] = { ...this.files[index], ...file }
      }
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
    },

    /**
     * Undo changes to the currently selected file
     */
    async undoFileChanges() {
      try {
        // Make sure we have a project and a selected file
        if (!this.projectId) {
          throw new Error('No project selected')
        }
        
        if (!this.selectedFile) {
          throw new Error('No file selected')
        }
        
        this.isProcessing = true
        
        // Call the file-specific undo endpoint
        const updatedContent = await FileService.undoFileChanges(this.projectId, this.selectedFile.path)
        
        // Update the selected file with the new content
        if (updatedContent) {
          this.selectFile({
            ...this.selectedFile,
            content: updatedContent
          })
        }
        
        return true
      } catch (error: any) {
        throw error
      } finally {
        this.isProcessing = false
      }
    }
  }
}) 