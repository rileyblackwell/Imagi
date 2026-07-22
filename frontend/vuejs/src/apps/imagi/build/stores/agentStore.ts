import { defineStore } from 'pinia'
import type {
  AIModel,
  AIMessage,
  AgentActivityStep,
  AgentInstance,
  AgentPlanStep,
  ConversationDto,
  ConversationKind,
  ReasoningEffort
} from '../types/services'
import { DEFAULT_REASONING_EFFORT } from '../types/services'
import type { AgentState } from '../types/stores'
import type { ProjectFile } from '../types/components'
import { FileService } from '../services/fileService'
import { AgentService } from '../services/agentService'

const DEFAULT_MODEL_ID = 'gpt-5.6-terra'

// The catalog's `default: true` entry wins over list order, so the effective
// default stays Terra even if the served ordering changes.
function pickDefaultModelId(models: AIModel[]): string {
  return models.find(m => m.default)?.id ?? models[0]?.id ?? DEFAULT_MODEL_ID
}

// Live stream controllers keyed by instance id. Module scope and non-reactive
// on purpose: AbortController instances must never be wrapped in Pinia proxies.
const abortControllers = new Map<string, AbortController>()

// Instance ids whose current run was explicitly stopped by the user. Consulted
// (and cleared) when processing flips false: a queued prompt must not auto-send
// into a run the user just killed.
const userAbortedRuns = new Set<string>()

// Registered by the workspace so a queued prompt can be re-submitted through
// its normal handlePrompt path when the blocking run finishes.
let queuedPromptSender: ((instanceId: string, prompt: string) => void) | null = null

// Single poller for server-side runs restored without a live stream.
let resyncTimer: ReturnType<typeof setInterval> | null = null
const RESYNC_INTERVAL_MS = 5000

function newLocalId(): string {
  return `inst-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

function dtoToInstance(dto: ConversationDto, fallbackModelId: string | null): AgentInstance {
  return {
    id: newLocalId(),
    conversationId: dto.id,
    title: dto.title || '',
    kind: dto.kind || 'chat',
    parentId: dto.parent ?? null,
    reviewStatus: dto.review_status || '',
    variantGroup: dto.variant_group || '',
    hasWorktree: !!dto.has_worktree,
    // null means the tokens were never captured (unknown), never "0 tokens"
    totalTokens: typeof dto.total_tokens === 'number' ? dto.total_tokens : null,
    selectedModelId: dto.model_name || fallbackModelId,
    selectedEffort: DEFAULT_REASONING_EFFORT,
    selectedFile: null,
    conversation: [],
    isProcessing: !!dto.is_running,
    statusText: dto.is_running ? 'Working…' : '',
    archivedAt: dto.archived_at,
    updatedAt: dto.updated_at,
    lastMessagePreview: dto.last_message_preview || '',
    messagesLoaded: false,
    hasUnread: false,
    queuedPrompt: null,
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

    /** The project's one pinned lead thread (ensured by loadInstances). */
    leadInstance(state): AgentInstance | null {
      return state.instances.find(i => i.kind === 'lead' && !i.archivedAt) || null
    },

    /** Tasks still being worked on, newest first. A running task always
     *  belongs here — a re-prompted 'ready' task flips back to active
     *  server-side before the local status resyncs. */
    taskFeedInstances(state): AgentInstance[] {
      return state.instances
        .filter(
          i => i.kind === 'task' && !i.archivedAt &&
            (i.reviewStatus === 'active' || (i.reviewStatus === 'ready' && i.isProcessing))
        )
        .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
    },

    /** Finished tasks whose worktree awaits an accept/dismiss decision.
     *  Excludes running tasks: accepting mid-run would just 409. */
    reviewInboxInstances(state): AgentInstance[] {
      return state.instances.filter(
        i => i.reviewStatus === 'ready' && !i.archivedAt && !i.isProcessing
      )
    },

    /** Everything demoted out of the live team view: archived threads,
     *  legacy plain chats, tasks already accepted or dismissed — plus any
     *  duplicate live lead (a backend race can leave two): it matches no
     *  other section, so History is where it stays reachable for
     *  archiving/deleting instead of becoming an invisible orphan. */
    historyInstances(state): AgentInstance[] {
      const primaryLead =
        state.instances.find(i => i.kind === 'lead' && !i.archivedAt) || null
      return state.instances.filter(
        i =>
          !!i.archivedAt ||
          i.kind === 'chat' ||
          i.reviewStatus === 'accepted' ||
          i.reviewStatus === 'dismissed' ||
          (i.kind === 'lead' && !i.archivedAt && i !== primaryLead)
      )
    },

    /** How many runs are live across all instances (lead + parallel tasks). */
    processingCount(state): number {
      return state.instances.filter(i => i.isProcessing).length
    },

    selectedModel(state): AIModel | undefined {
      const active = state.instances.find(i => i.id === state.activeInstanceId)
      return state.availableModels.find(m => m.id === active?.selectedModelId)
    },

    // Back-compat getters delegating to active instance
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
        const fallback = pickDefaultModelId(this.availableModels)
        this.instances = dtos.map(d => dtoToInstance(d, fallback))

        // Every project pins exactly one lead thread; the backend dedupes
        // lead creation, so racing tabs converge on the same conversation.
        if (!this.instances.some(i => i.kind === 'lead' && !i.archivedAt)) {
          await this.createInstance({ kind: 'lead', activate: false })
        }

        // Pick active: remembered id from localStorage, else the lead
        const remembered = localStorage.getItem(`activeAgentInstance_${projectId}`)
        const activeConvId: number | null = remembered ? Number(remembered) : null
        let picked = this.instances.find(i => i.conversationId === activeConvId && !i.archivedAt)
        if (!picked) {
          picked = this.leadInstance
            || this.instances.find(i => !i.archivedAt)
            || this.instances[0]
        }
        if (picked) {
          this.activeInstanceId = picked.id
          await this.ensureMessagesLoaded(picked.id)
        }

        // Restored instances may have runs still executing server-side.
        this.resyncRunningInstances()
      } finally {
        this.instancesLoading = false
      }
    },

    // --- Run control (stop button / server-tracked runs) ---

    registerAbortController(instanceId: string, controller: AbortController) {
      abortControllers.set(instanceId, controller)
      userAbortedRuns.delete(instanceId) // fresh run, stale stop marks don't apply
    },

    /** Stop this instance's run. Aborts the live stream when this tab owns
     *  one; otherwise (restored after reload / opened elsewhere / crashed
     *  worker) releases the server-side run marker and clears local state so
     *  Stop is never a dead button. */
    abortInstanceRun(instanceId: string) {
      const controller = abortControllers.get(instanceId)
      if (controller) {
        abortControllers.delete(instanceId)
        userAbortedRuns.add(instanceId)
        controller.abort()
        return
      }
      const instance = this._findInstance(instanceId)
      if (!instance?.isProcessing) return
      userAbortedRuns.add(instanceId)
      if (instance.conversationId != null) {
        // Best-effort: lifts the project's agent_busy guard. A run streaming
        // into another tab keeps executing there; if it is genuinely still
        // going, the next submit gets the backend's 409.
        AgentService.cancelConversationRun(instance.conversationId)
          .catch(e => console.error('Failed to release server-side run', e))
      }
      this.setInstanceProcessing(instanceId, false)
    },

    /** Abort every live stream (e.g. before rebuilding the instance list,
     *  which would orphan in-flight runs on dead local ids). */
    abortAllRuns() {
      for (const instanceId of abortControllers.keys()) {
        userAbortedRuns.add(instanceId)
      }
      for (const controller of abortControllers.values()) {
        controller.abort()
      }
      abortControllers.clear()
    },

    // --- Queued prompts (one pending prompt per instance) ---

    /** Register how a queued prompt gets submitted (the workspace's
     *  handlePrompt). Pass null on teardown. */
    setQueuedPromptSender(sender: ((instanceId: string, prompt: string) => void) | null) {
      queuedPromptSender = sender
    },

    /** Hold one prompt to auto-send when this instance's run finishes.
     *  Submitting again while still running replaces it. */
    queuePrompt(instanceId: string, prompt: string) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      instance.queuedPrompt = prompt
    },

    clearQueuedPrompt(instanceId: string) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      instance.queuedPrompt = null
    },

    /**
     * Poll conversations that are running server-side but have no live stream
     * in this tab (restored after reload / opened elsewhere). When a run
     * finishes, refetch its messages and flag it unread if not active.
     */
    resyncRunningInstances() {
      if (resyncTimer !== null) {
        clearInterval(resyncTimer)
        resyncTimer = null
      }

      const restoredRunning = () => this.instances.filter(
        i => i.isProcessing && i.conversationId != null && !abortControllers.has(i.id)
      )
      if (restoredRunning().length === 0) return

      resyncTimer = setInterval(async () => {
        const running = restoredRunning()
        if (running.length === 0) {
          if (resyncTimer !== null) {
            clearInterval(resyncTimer)
            resyncTimer = null
          }
          return
        }
        await Promise.all(running.map(async (instance) => {
          try {
            const dto = await AgentService.getConversation(instance.conversationId!)
            if (dto.is_running) return
            // Re-check after the await: a local run may have started (and
            // registered its controller) while the fetch was in flight — its
            // fresh transcript must not be wiped from under it.
            if (!instance.isProcessing || abortControllers.has(instance.id)) return
            // Run finished on the server: pull the authoritative transcript.
            instance.messagesLoaded = false
            instance.conversation = []
            await this.ensureMessagesLoaded(instance.id)
            instance.updatedAt = dto.updated_at
            instance.lastMessagePreview = dto.last_message_preview || ''
            // A finished task may now be ready for review; sync the
            // review-lifecycle fields the run end changed server-side.
            instance.reviewStatus = dto.review_status || ''
            instance.hasWorktree = !!dto.has_worktree
            if (typeof dto.total_tokens === 'number') instance.totalTokens = dto.total_tokens
            this.setInstanceProcessing(instance.id, false)
          } catch (e) {
            console.error('Failed to resync running conversation', instance.conversationId, e)
          }
        }))
      }, RESYNC_INTERVAL_MS)
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
          // Persisted run telemetry, already hydrated by the service into
          // the same shapes the live stream writes.
          plan: m.plan,
          activity: m.activity,
          filesChanged: m.filesChanged,
          usage: m.usage,
          dbId: m.id,
          checkpoint: m.checkpoint,
        } as AIMessage))
        instance.messagesLoaded = true
      } catch (e) {
        console.error('Failed to load messages for conversation', instance.conversationId, e)
      }
    },

    async createInstance(opts: {
      modelId?: string
      kind?: ConversationKind
      /** conversationId of the lead thread (for kind='task') */
      parentId?: number | null
      /** Shared uuid grouping best-of-N sibling tasks */
      variantGroup?: string
      /** false leaves the current active instance in place (task dispatch) */
      activate?: boolean
    } = {}) {
      if (!this.projectId) return null
      const fallbackModel = opts.modelId || pickDefaultModelId(this.availableModels)
      const dto = await AgentService.createConversation(this.projectId, {
        modelName: fallbackModel,
        kind: opts.kind,
        parent: opts.parentId ?? undefined,
        variantGroup: opts.variantGroup,
      })
      // Lead creation is deduped server-side — the response may be a
      // conversation this store already tracks.
      const existing = this.instances.find(
        i => i.conversationId != null && i.conversationId === dto.id
      )
      if (existing) {
        if (opts.activate !== false) await this.switchInstance(existing.id)
        return existing
      }
      const instance = dtoToInstance(dto, fallbackModel)
      // A deduped lead may arrive with history; anything with a preview
      // still needs its messages fetched lazily.
      instance.messagesLoaded = !dto.last_message_preview
      this.instances.unshift(instance)
      if (opts.activate !== false) {
        this.activeInstanceId = instance.id
        if (this.projectId) {
          localStorage.setItem(
            `activeAgentInstance_${this.projectId}`,
            String(instance.conversationId ?? '')
          )
        }
      }
      return instance
    },

    async switchInstance(instanceId: string) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      this.activeInstanceId = instance.id
      instance.hasUnread = false
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
        // If the archived instance was active, fall back to the lead thread
        // (never auto-create plain chats; the lead is recreated on demand).
        if (this.activeInstanceId === instance.id) {
          const next = this.leadInstance
            || this.instances.find(i => !i.archivedAt && i.id !== instance.id)
          if (next) {
            await this.switchInstance(next.id)
          } else {
            await this.createInstance({ kind: 'lead' })
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
      if (instance.conversationId) {
        // The server delete can be refused (409 agent_busy while a task's
        // run is live). Keep the instance and rethrow: removing it locally
        // would show a deletion that never happened and resurrects on
        // reload.
        await AgentService.deleteConversation(instance.conversationId)
      }
      this.instances = this.instances.filter(i => i.id !== instance.id)
      if (wasActive) {
        // Fall back to the lead thread; never auto-create plain chats.
        const next = this.leadInstance
          || this.instances.find(i => !i.archivedAt)
          || this.instances[0]
        if (next) {
          await this.switchInstance(next.id)
        } else {
          await this.createInstance({ kind: 'lead' })
        }
      }
    },

    /**
     * Re-pull one conversation's DTO and patch the instance in place.
     * Deliberately NOT loadInstances: rebuilding the whole list regenerates
     * local ids and aborts every live stream, which would orphan parallel
     * task runs still streaming into this tab.
     */
    async refreshInstanceFromServer(instanceId: string) {
      const instance = this._findInstance(instanceId)
      if (!instance || instance.conversationId == null) return
      try {
        const dto = await AgentService.getConversation(instance.conversationId)
        instance.title = dto.title || ''
        instance.kind = dto.kind || instance.kind
        instance.parentId = dto.parent ?? instance.parentId
        instance.reviewStatus = dto.review_status || ''
        instance.variantGroup = dto.variant_group || ''
        instance.hasWorktree = !!dto.has_worktree
        if (typeof dto.total_tokens === 'number') instance.totalTokens = dto.total_tokens
        instance.archivedAt = dto.archived_at
        instance.updatedAt = dto.updated_at
        instance.lastMessagePreview = dto.last_message_preview || ''
      } catch (e) {
        console.error('Failed to refresh conversation', instance.conversationId, e)
      }
    },

    /**
     * Accept a ready task: the backend merges its worktree into the
     * canonical tree. Errors (409 merge_conflict / agent_busy) propagate to
     * the caller so the review UI can surface their detail.
     */
    async acceptTaskInstance(instanceId: string) {
      const instance = this._findInstance(instanceId)
      if (!instance || instance.conversationId == null) return
      await AgentService.acceptTask(instance.conversationId)
      instance.reviewStatus = 'accepted'
      instance.hasWorktree = false
      await this.refreshInstanceFromServer(instanceId)
    },

    /** Dismiss a ready task: its worktree is discarded without merging. */
    async dismissTaskInstance(instanceId: string) {
      const instance = this._findInstance(instanceId)
      if (!instance || instance.conversationId == null) return
      await AgentService.dismissTask(instance.conversationId)
      instance.reviewStatus = 'dismissed'
      instance.hasWorktree = false
      await this.refreshInstanceFromServer(instanceId)
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

    // Reasoning effort is a per-request tuning knob kept in client state only
    // (there is no backend field to persist it to).
    setInstanceEffort(instanceId: string, effort: ReasoningEffort) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      instance.selectedEffort = effort
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
      if (!value) {
        // Read-and-clear: was this run ended by an explicit user stop?
        const aborted = userAbortedRuns.delete(instanceId)
        instance.statusText = ''
        // The run is over — its stream controller (if any) is dead weight.
        abortControllers.delete(instanceId)
        // Completion signal: runs that finish off-screen get a dot.
        if (instanceId !== this.activeInstanceId) instance.hasUnread = true
        // A queued prompt fires now — unless the user just stopped the run,
        // in which case it stays queued for them to send or cancel.
        const queued = instance.queuedPrompt
        if (queued && !aborted && queuedPromptSender) {
          instance.queuedPrompt = null
          const send = queuedPromptSender
          // Deferred so the finishing run's call stack fully unwinds before
          // the next run starts flipping processing back on.
          queueMicrotask(() => send(instanceId, queued))
        }
      }
    },

    /**
     * Describe what the running agent is doing ("Thinking…", "Editing project
     * files…"). Cleared while reply text is streaming, so the status line and
     * the growing message never show together.
     */
    setInstanceStatus(instanceId: string, text: string) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      instance.statusText = text
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

    /**
     * Replace the content of a message already in the conversation.
     *
     * Used while streaming: the assistant's message is added empty and then
     * rewritten as each chunk arrives, so the reply appears to type itself
     * rather than landing all at once when the run ends.
     */
    setMessageContent(instanceId: string, messageId: string, content: string) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      const message = instance.conversation.find(m => m.id === messageId)
      if (!message) return
      message.content = content
      instance.updatedAt = new Date().toISOString()
      instance.lastMessagePreview = content.split('\n')[0]?.slice(0, 140) || ''
    },

    /**
     * Merge streamed metadata (activity, plan, filesChanged) into an existing
     * message. Content updates stay in setMessageContent, which also bumps
     * updatedAt/preview — metadata patches deliberately do not.
     */
    patchMessage(instanceId: string, messageId: string, patch: Partial<AIMessage>) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      const message = instance.conversation.find(m => m.id === messageId)
      if (!message) return
      Object.assign(message, patch)
    },

    /** Append one live tool-call step to a message's activity feed. */
    appendMessageActivity(instanceId: string, messageId: string, step: AgentActivityStep) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      const message = instance.conversation.find(m => m.id === messageId)
      if (!message) return
      if (!message.activity) message.activity = []
      message.activity.push(step)
    },

    /** Replace a message's plan snapshot (rewritten whole on each update). */
    setMessagePlan(instanceId: string, messageId: string, plan: AgentPlanStep[]) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      const message = instance.conversation.find(m => m.id === messageId)
      if (!message) return
      message.plan = [...plan]
    },

    /** Attach end-of-run metadata (changed files, usage) to a message. */
    setMessageMeta(
      instanceId: string,
      messageId: string,
      meta: { filesChanged?: string[]; usage?: AIMessage['usage'] }
    ) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      const message = instance.conversation.find(m => m.id === messageId)
      if (!message) return
      if (meta.filesChanged !== undefined) message.filesChanged = [...meta.filesChanged]
      if (meta.usage !== undefined) message.usage = { ...meta.usage }
    },

    /** Drop a message (e.g. an assistant bubble whose run produced nothing). */
    removeMessage(instanceId: string, messageId: string) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      instance.conversation = instance.conversation.filter(m => m.id !== messageId)
    },

    /**
     * Tie an optimistic user bubble to its persisted row: the stream's start
     * event carries the backend message id and the pre-run checkpoint, which
     * the inline restore control needs without waiting for a reload.
     */
    setMessageCheckpoint(instanceId: string, messageId: string, dbId?: number, checkpoint?: string) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      const message = instance.conversation.find(m => m.id === messageId)
      if (!message) return
      if (dbId !== undefined) message.dbId = dbId
      if (checkpoint) message.checkpoint = checkpoint
    },

    /**
     * Rewind this instance to just before a user message: restore the
     * message's checkpoint (backend resets files + deletes the message and
     * everything after), then truncate the local transcript to match.
     * Returns the removed prompt text (for the composer), or null on failure.
     */
    async restoreToCheckpoint(instanceId: string, message: AIMessage): Promise<string | null> {
      const instance = this._findInstance(instanceId)
      if (!instance || !instance.conversationId || !message.dbId || !message.checkpoint) return null
      const result = await AgentService.restoreCheckpoint(instance.conversationId, message.dbId)
      if (!result?.success) return null
      const index = instance.conversation.findIndex(m => m.id === message.id)
      if (index >= 0) {
        instance.conversation = instance.conversation.slice(0, index)
      }
      instance.lastMessagePreview =
        (instance.conversation[instance.conversation.length - 1]?.content || '')
          .split('\n')[0]?.slice(0, 140) || ''
      return result.prompt ?? message.content
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

    updateFile(file: ProjectFile) {
      const index = this.files.findIndex(f => f.path === file.path)
      if (index >= 0) this.files[index] = { ...this.files[index], ...file }
    },

    setUnsavedChanges(value: boolean) {
      this.unsavedChanges = value
    },

    // --- Legacy shims (for any callers still using the singleton API) ---
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
