import { defineStore } from 'pinia'
import type { AIModel, AIMessage, AgentInstance, ConversationDto } from '../types/services'
import type { AgentState } from '../types/stores'
import type { BuilderMode, ProjectFile } from '../types/components'
import { FileService } from '../services/fileService'
import { AgentService } from '../services/agentService'

const DEFAULT_MODEL_ID = 'gpt-5.5'

function newLocalId(): string {
  return `inst-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

function dtoToInstance(dto: ConversationDto, fallbackModelId: string | null): AgentInstance {
  return {
    id: newLocalId(),
    conversationId: dto.id,
    title: dto.title || '',
    mode: dto.mode,
    selectedModelId: dto.model_name || fallbackModelId,
    selectedFile: null,
    conversation: [],
    isProcessing: false,
    archivedAt: dto.archived_at,
    updatedAt: dto.updated_at,
    lastMessagePreview: dto.last_message_preview || '',
    messagesLoaded: false,
  }
}

export const useAgentStore = defineStore('agent', {
  state: (): AgentState => ({
    projectId: null,
    availableModels: [],
    instances: [],
    activeInstanceId: null,
    files: [],
    unsavedChanges: false,
    error: null,
    instancesLoading: false,
  }),

  getters: {
    activeInstance(state): AgentInstance | null {
      if (!state.activeInstanceId) return null
      return state.instances.find(i => i.id === state.activeInstanceId) || null
    },

    activeInstances(state): AgentInstance[] {
      return state.instances.filter(i => !i.archivedAt)
    },

    archivedInstances(state): AgentInstance[] {
      return state.instances.filter(i => !!i.archivedAt)
    },

    selectedModel(state): AIModel | undefined {
      const active = state.instances.find(i => i.id === state.activeInstanceId)
      return state.availableModels.find(m => m.id === active?.selectedModelId)
    },

    // Back-compat getters delegating to active instance
    mode(): BuilderMode {
      return (this.activeInstance?.mode ?? 'chat') as BuilderMode
    },
    selectedModelId(): string | null {
      return this.activeInstance?.selectedModelId ?? null
    },
    conversation(): AIMessage[] {
      return this.activeInstance?.conversation ?? []
    },
    selectedFile(): ProjectFile | null {
      return (this.activeInstance?.selectedFile as ProjectFile | null) ?? null
    },
    isProcessing(): boolean {
      return !!this.activeInstance?.isProcessing
    },
    canSubmitPrompt(): boolean {
      const active = this.activeInstance
      return !!active && !!active.selectedModelId && !active.isProcessing
    },
  },

  actions: {
    setProjectId(id: string | null) {
      this.projectId = id
    },

    setModels(models: AIModel[]) {
      this.availableModels = models
    },

    setError(error: string | null) {
      this.error = error
    },

    _findInstance(id: string): AgentInstance | undefined {
      return this.instances.find(i => i.id === id)
    },

    async loadInstances(projectId: string | number) {
      this.instancesLoading = true
      try {
        const dtos = await AgentService.listConversations(projectId)
        const fallback = this.availableModels[0]?.id ?? DEFAULT_MODEL_ID
        this.instances = dtos.map(d => dtoToInstance(d, fallback))

        // If user has no conversations yet, create a starter one
        if (this.instances.length === 0) {
          await this.createInstance()
        }

        // Pick active: remembered id from localStorage, else first non-archived
        const remembered = localStorage.getItem(`activeAgentInstance_${projectId}`)
        let activeConvId: number | null = remembered ? Number(remembered) : null
        let picked = this.instances.find(i => i.conversationId === activeConvId && !i.archivedAt)
        if (!picked) {
          picked = this.instances.find(i => !i.archivedAt) || this.instances[0]
        }
        if (picked) {
          this.activeInstanceId = picked.id
          await this.ensureMessagesLoaded(picked.id)
        }
      } finally {
        this.instancesLoading = false
      }
    },

    async ensureMessagesLoaded(instanceId: string) {
      const instance = this._findInstance(instanceId)
      if (!instance || instance.messagesLoaded || !instance.conversationId) return
      try {
        const msgs = await AgentService.getConversationMessages(instance.conversationId)
        instance.conversation = msgs.map(m => ({
          role: m.role,
          content: m.content,
          timestamp: m.timestamp,
          id: `db-${m.id}`,
        } as AIMessage))
        instance.messagesLoaded = true
      } catch (e) {
        console.error('Failed to load messages for conversation', instance.conversationId, e)
      }
    },

    async createInstance(opts: { mode?: BuilderMode; modelId?: string } = {}) {
      if (!this.projectId) return null
      const fallbackModel = opts.modelId
        || this.availableModels[0]?.id
        || DEFAULT_MODEL_ID
      const dto = await AgentService.createConversation(this.projectId, {
        mode: opts.mode ?? 'chat',
        modelName: fallbackModel,
      })
      const instance = dtoToInstance(dto, fallbackModel)
      instance.messagesLoaded = true
      this.instances.unshift(instance)
      this.activeInstanceId = instance.id
      if (this.projectId) {
        localStorage.setItem(
          `activeAgentInstance_${this.projectId}`,
          String(instance.conversationId ?? '')
        )
      }
      return instance
    },

    async switchInstance(instanceId: string) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      this.activeInstanceId = instance.id
      if (this.projectId && instance.conversationId != null) {
        localStorage.setItem(
          `activeAgentInstance_${this.projectId}`,
          String(instance.conversationId)
        )
      }
      await this.ensureMessagesLoaded(instance.id)
    },

    async renameInstance(instanceId: string, title: string) {
      const instance = this._findInstance(instanceId)
      if (!instance || !instance.conversationId) return
      const trimmed = title.trim().slice(0, 120)
      instance.title = trimmed
      try {
        await AgentService.updateConversation(instance.conversationId, { title: trimmed })
      } catch (e) {
        console.error('Failed to rename conversation:', e)
      }
    },

    async archiveInstance(instanceId: string) {
      const instance = this._findInstance(instanceId)
      if (!instance || !instance.conversationId) return
      try {
        const dto = await AgentService.updateConversation(instance.conversationId, { archived: true })
        instance.archivedAt = dto.archived_at
        // If the archived instance was active, switch to another non-archived one
        if (this.activeInstanceId === instance.id) {
          const next = this.instances.find(i => !i.archivedAt && i.id !== instance.id)
          if (next) {
            await this.switchInstance(next.id)
          } else {
            await this.createInstance()
          }
        }
      } catch (e) {
        console.error('Failed to archive conversation:', e)
      }
    },

    async unarchiveInstance(instanceId: string) {
      const instance = this._findInstance(instanceId)
      if (!instance || !instance.conversationId) return
      try {
        const dto = await AgentService.updateConversation(instance.conversationId, { archived: false })
        instance.archivedAt = dto.archived_at
      } catch (e) {
        console.error('Failed to unarchive conversation:', e)
      }
    },

    async deleteInstance(instanceId: string) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      const wasActive = this.activeInstanceId === instance.id
      try {
        if (instance.conversationId) {
          await AgentService.deleteConversation(instance.conversationId)
        }
      } catch (e) {
        console.error('Failed to delete conversation:', e)
      }
      this.instances = this.instances.filter(i => i.id !== instance.id)
      if (wasActive) {
        const next = this.instances.find(i => !i.archivedAt) || this.instances[0]
        if (next) {
          await this.switchInstance(next.id)
        } else {
          await this.createInstance()
        }
      }
    },

    setInstanceMode(instanceId: string, mode: BuilderMode) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      if (instance.mode === mode) return
      instance.mode = mode
      if (instance.conversationId) {
        AgentService.updateConversation(instance.conversationId, { mode })
          .catch(e => console.error('Failed to persist mode:', e))
      }
    },

    setInstanceModel(instanceId: string, modelId: string) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      instance.selectedModelId = modelId
      if (instance.conversationId) {
        AgentService.updateConversation(instance.conversationId, { model_name: modelId })
          .catch(e => console.error('Failed to persist model:', e))
      }
    },

    setInstanceFile(instanceId: string, file: ProjectFile | null) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      instance.selectedFile = file
    },

    setInstanceProcessing(instanceId: string, value: boolean) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      instance.isProcessing = value
    },

    addMessageToInstance(instanceId: string, message: AIMessage) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      const validMessage: AIMessage = {
        ...message,
        role: message.role || 'user',
        content: message.content || '',
        timestamp: message.timestamp || new Date().toISOString(),
      }
      instance.conversation.push(validMessage)
      instance.updatedAt = new Date().toISOString()
      instance.lastMessagePreview = (validMessage.content || '').split('\n')[0]?.slice(0, 140) || ''
    },

    updateInstanceConversationId(instanceId: string, conversationId: number) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      if (!instance.conversationId) instance.conversationId = conversationId
    },

    // --- Files (project-wide) ---
    setFiles(files: ProjectFile[]) {
      if (Array.isArray(files)) {
        this.files = [...files]
        // Prune any instance's selectedFile that no longer exists
        for (const instance of this.instances) {
          if (instance.selectedFile && !this.files.some(f => f.path === instance.selectedFile?.path)) {
            instance.selectedFile = null
          }
        }
      } else {
        this.files = []
      }
    },

    addFile(file: ProjectFile) {
      const existingIndex = this.files.findIndex(f => f.path === file.path)
      if (existingIndex >= 0) {
        this.files[existingIndex] = file
      } else {
        this.files.push(file)
      }
    },

    removeFile(file: ProjectFile) {
      const index = this.files.findIndex(f => f.path === file.path)
      if (index >= 0) this.files.splice(index, 1)
    },

    updateFile(file: ProjectFile) {
      const index = this.files.findIndex(f => f.path === file.path)
      if (index >= 0) this.files[index] = { ...this.files[index], ...file }
    },

    setUnsavedChanges(value: boolean) {
      this.unsavedChanges = value
    },

    // --- Legacy shims (for any callers still using the singleton API) ---
    setMode(mode: BuilderMode) {
      if (this.activeInstanceId) this.setInstanceMode(this.activeInstanceId, mode)
    },

    setSelectedModelId(modelId: string) {
      if (this.activeInstanceId) this.setInstanceModel(this.activeInstanceId, modelId)
    },

    selectModel(modelId: string) {
      this.setSelectedModelId(modelId)
    },

    setSelectedFile(file: ProjectFile | null) {
      if (this.activeInstanceId) this.setInstanceFile(this.activeInstanceId, file)
    },

    selectFile(file: ProjectFile | null) {
      this.setSelectedFile(file)
    },

    setProcessing(value: boolean) {
      if (this.activeInstanceId) this.setInstanceProcessing(this.activeInstanceId, value)
    },

    addMessage(message: AIMessage) {
      if (this.activeInstanceId) this.addMessageToInstance(this.activeInstanceId, message)
    },

    clearConversation() {
      const active = this.activeInstance
      if (active) active.conversation = []
    },

    reset() {
      this.$reset()
    },

    async undoFileChanges() {
      const active = this.activeInstance
      if (!this.projectId) throw new Error('No project selected')
      if (!active?.selectedFile) throw new Error('No file selected')
      this.setInstanceProcessing(active.id, true)
      try {
        const updatedContent = await FileService.undoFileChanges(this.projectId, active.selectedFile.path)
        if (updatedContent) {
          this.setInstanceFile(active.id, { ...active.selectedFile, content: updatedContent } as ProjectFile)
        }
        return true
      } finally {
        this.setInstanceProcessing(active.id, false)
      }
    },
  }
})
