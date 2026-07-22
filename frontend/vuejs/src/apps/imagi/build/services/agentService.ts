import api, { getAuthToken } from '@/shared/services/api'
import type {
  AIModel,
  AgentActivityStep,
  AgentResponse,
  AgentPlanStep,
  ConversationKind,
  VersionControlResponse,
  ConversationDto
} from '../types/services'
import { ModelsService } from '@/apps/imagi/build/services/modelsService'

/**
 * Service for talking to the Imagi agent and workspace APIs.
 *
 * A single agent handles all AI interaction (chat + file editing) via
 * streamAgent; the rest of the service covers conversation CRUD and
 * version control.
 */
/** Events the agent stream emits, in the order a run produces them. */
export interface AgentStreamHandlers {
  /** info identifies the persisted user message this run started from and
   *  the pre-run checkpoint commit it can be restored to. */
  onStart?: (conversationId: number, info?: { userMessageId?: number; checkpoint?: string }) => void
  /** A chunk of the agent's reply. Chunks concatenate into the final text. */
  onDelta?: (text: string) => void
  /** args is a small allowlisted extract of the tool's arguments (path,
   *  pattern, query, …) — values are backend-truncated strings. */
  onToolCall?: (name: string, args?: Record<string, string>) => void
  onPlan?: (plan: AgentPlanStep[]) => void
}

/**
 * A failed agent run. Carries the HTTP status for pre-stream rejections
 * (409 agent_busy, 401, …) and the backend's error code for in-stream
 * failures ('max_turns' when the run hit its turn cap).
 */
export class AgentStreamError extends Error {
  status?: number
  code?: string
  /** Parsed JSON body of a pre-stream rejection (e.g. the 429
   *  usage_limit_exceeded payload carries window + resets_at). */
  body?: Record<string, unknown>

  constructor(
    message: string,
    opts: { status?: number; code?: string; body?: Record<string, unknown> } = {}
  ) {
    super(message)
    this.name = 'AgentStreamError'
    this.status = opts.status
    this.code = opts.code
    this.body = opts.body
  }
}

/** Basename of the file a tool touched, from its display-safe args. */
function toolFileName(args?: Record<string, string>): string {
  const path = args?.path || args?.file_path || ''
  return path.split('/').filter(Boolean).pop() || 'a file'
}

/**
 * Founder-language label for a tool call. Shared by the live activity feed
 * and persisted-metadata hydration so a replayed transcript reads exactly
 * like it did while streaming.
 */
export function labelForTool(name: string, args?: Record<string, string>): string {
  switch (name) {
    case 'read_file': return `Read ${toolFileName(args)}`
    case 'edit_file':
    case 'update_file': return `Edited ${toolFileName(args)}`
    case 'create_file': return `Created ${toolFileName(args)}`
    case 'delete_file': return `Deleted ${toolFileName(args)}`
    case 'grep_files':
    case 'glob_files':
    case 'get_project_tree':
    case 'list_project_files': return 'Searched the project'
    case 'update_plan': return 'Updated the plan'
    case 'web_search':
    case 'web_search_call': return 'Searched the web'
    case 'create_app': return 'Created an app'
    case 'create_directory':
    case 'delete_directory': return 'Organized project folders'
    default: return 'Worked on the project'
  }
}

/** One activity-feed entry for a tool call (live event or persisted record). */
export function toolCallToActivityStep(
  name: string,
  args?: Record<string, string>
): AgentActivityStep {
  const step: AgentActivityStep = { name, label: labelForTool(name, args) }
  const detail = args?.path || args?.file_path || args?.pattern
  if (detail) step.detail = detail
  return step
}

/** AgentMessage.metadata as persisted by the backend (see contract shape). */
interface PersistedMessageMetadata {
  tool_calls?: Array<{ name: string; args?: Record<string, string> }>
  files_changed?: string[]
  plan?: AgentPlanStep[]
  usage?: { input_tokens?: number; output_tokens?: number; cost_usd?: number }
  /** Pre-run project snapshot, stamped on user messages only */
  checkpoint?: string
}

/** One conversation message with its persisted telemetry hydrated. */
export interface ConversationMessageDto {
  id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  plan?: AgentPlanStep[]
  activity?: AgentActivityStep[]
  filesChanged?: string[]
  usage?: { costUsd?: number; inputTokens?: number; outputTokens?: number }
  checkpoint?: string
}

export const AgentService = {
  /**
   * Run the agent, surfacing output as it arrives.
   *
   * Uses fetch rather than the shared axios client because axios is built on
   * XHR, which cannot expose a response body before it completes.
   */
  async streamAgent(
    projectId: string,
    data: {
      prompt: string;
      model: string;
      reasoningEffort?: string;
      file?: any;
      conversationId?: number | string | null;
    },
    handlers: AgentStreamHandlers = {},
    signal?: AbortSignal,
  ): Promise<AgentResponse> {
    if (!data.prompt || !data.model) {
      throw new Error('Prompt and model are required')
    }
    if (!projectId) {
      throw new Error('Project ID is required')
    }

    await ModelsService.checkRateLimit(data.model)

    const config = ModelsService.getConfig({ id: data.model } as AIModel)
    if (ModelsService.estimateTokens(data.prompt) > config.maxTokens) {
      throw new Error(`Prompt is too long for selected model. Please reduce length or choose a different model.`)
    }

    let currentFile = null
    if (data.file) {
      currentFile = {
        path: data.file.path,
        type: data.file.type || this.getFileType(data.file.path),
        content: data.file.content || ''
      }
    }

    const token = getAuthToken()
    const response = await fetch('/api/v1/agents/agent/stream/', {
      method: 'POST',
      signal,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
        ...(token ? { Authorization: `Token ${token}` } : {}),
      },
      body: JSON.stringify({
        message: data.prompt,
        model: data.model,
        reasoning_effort: data.reasoningEffort,
        project_id: String(projectId),
        conversation_id: data.conversationId ?? undefined,
        current_file: currentFile,
      }),
    })

    if (!response.ok || !response.body) {
      // Errors before the stream opens are plain JSON, not SSE. DRF-style
      // rejections use "detail" (e.g. the 409 {"detail": "agent_busy"} when
      // another run holds the project); our own errors use "error".
      let detail = ''
      let errorBody: Record<string, unknown> | undefined
      try {
        const body = await response.json()
        detail = body?.error || body?.detail || ''
        if (body && typeof body === 'object') errorBody = body
      } catch { /* non-JSON body */ }
      throw new AgentStreamError(
        detail || `Agent request failed (${response.status})`,
        { status: response.status, body: errorBody }
      )
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let done: AgentResponse | null = null
    let streamError = ''
    let streamErrorCode: string | undefined
    const text: string[] = []
    const toolCalls: string[] = []
    let plan: AgentPlanStep[] = []
    let conversationId: number | undefined

    const handleEvent = (event: any) => {
      switch (event.type) {
        case 'start':
          conversationId = event.conversation_id
          handlers.onStart?.(event.conversation_id, {
            userMessageId: event.user_message_id,
            checkpoint: event.checkpoint,
          })
          break
        case 'delta':
          text.push(event.text)
          handlers.onDelta?.(event.text)
          break
        case 'tool_call':
          toolCalls.push(event.name)
          handlers.onToolCall?.(event.name, event.args)
          break
        case 'plan':
          plan = event.plan || []
          handlers.onPlan?.(plan)
          break
        case 'done':
          done = {
            response: event.response ?? text.join(''),
            conversation_id: event.conversation_id,
            files_changed: event.files_changed || [],
            tool_calls: event.tool_calls || toolCalls,
            plan: event.plan || plan,
            // Usage (and its cost) is best-effort on the backend; absent
            // means "unknown", never "free".
            usage: event.usage,
            single_message: event.single_message ?? true,
          }
          break
        case 'error':
          streamError = event.error || 'Agent run failed'
          streamErrorCode = event.code
          break
      }
    }

    while (true) {
      const { value, done: finished } = await reader.read()
      if (finished) break
      buffer += decoder.decode(value, { stream: true })

      // SSE frames are separated by a blank line; the last chunk may be partial.
      const frames = buffer.split('\n\n')
      buffer = frames.pop() ?? ''
      for (const frame of frames) {
        const line = frame.split('\n').find(l => l.startsWith('data: '))
        if (!line) continue
        try {
          handleEvent(JSON.parse(line.slice(6)))
        } catch {
          console.warn('Skipping malformed agent stream frame')
        }
      }
    }

    if (streamError) throw new AgentStreamError(streamError, { code: streamErrorCode })
    if (done) return done

    // Stream ended without a terminal event (server died, connection dropped).
    // Keep whatever text arrived rather than discarding a partial reply.
    return {
      response: text.join(''),
      conversation_id: conversationId as any,
      files_changed: [],
      tool_calls: toolCalls,
      plan,
      single_message: true,
    }
  },

  formatError(error: any): string {
    return ModelsService.formatError(error);
  },

  async getVersionHistory(projectId: string): Promise<VersionControlResponse> {
    if (!projectId) {
      throw new Error('Project ID is required')
    }

    try {
      const response = await api.get(`/v1/builder/${projectId}/versions/`)

      return {
        success: response.data.success !== false,
        versions: response.data.versions || [],
        error: response.data.error || null
      }
    } catch (error: any) {
      console.error('Error getting version history:', error)
      return {
        success: false,
        versions: [],
        error: this.formatError(error)
      }
    }
  },

  async resetToVersion(projectId: string, commitHash: string): Promise<VersionControlResponse> {
    if (!projectId || !commitHash) {
      throw new Error('Project ID and commit hash are required')
    }

    try {
      const response = await api.post(`/v1/builder/${projectId}/versions/reset/`, {
        commit_hash: commitHash
      })

      return {
        success: response.data.success !== false,
        message: response.data.message || 'Project reset successful',
        error: response.data.error || null
      }
    } catch (error: any) {
      console.error('Error resetting to version:', error)
      return {
        success: false,
        versions: [],
        // Restores are refused while an agent run holds the project
        // (agent_busy contract) — say so instead of a generic failure.
        error: error?.response?.status === 409
          ? 'Another agent is still working on this project — wait for it to finish or stop it.'
          : this.formatError(error)
      }
    }
  },

  async createVersion(projectId: string, data: { file_path?: string, description?: string }): Promise<VersionControlResponse> {
    if (!projectId) {
      throw new Error('Project ID is required')
    }

    try {
      // Normalize file path
      let filePath = data.file_path || '/';
      if (filePath !== '/' && !filePath.startsWith('/')) {
        filePath = '/' + filePath;
      }

      // Create payload
      const payload = {
        file_path: filePath,
        description: data.description || 'Project update'
      }

      const response = await api.post(`/v1/builder/${projectId}/versions/`, payload)

      return {
        success: response.data.success !== false,
        message: response.data.message || 'Version created successfully',
        commitHash: response.data.commit_hash || null,
        error: response.data.error || null
      }
    } catch (error: any) {
      return {
        success: false,
        error: this.formatError(error)
      }
    }
  },

  getFileType(filePath: string): string {
    if (!filePath) return 'unknown';

    const extension = filePath.split('.').pop()?.toLowerCase();

    switch (extension) {
      case 'html':
        return 'html';
      case 'css':
        return 'css';
      case 'js':
        return 'javascript';
      case 'json':
        return 'json';
      case 'py':
        return 'python';
      case 'md':
        return 'markdown';
      case 'txt':
        return 'text';
      case 'svg':
        return 'svg';
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
        return 'image';
      default:
        return extension || 'unknown';
    }
  },

  // ------------------------------------------------------------
  // Conversation (agent instance) CRUD
  // ------------------------------------------------------------

  async listConversations(projectId: string | number): Promise<ConversationDto[]> {
    const response = await api.get('/v1/agents/conversations/', {
      params: { project_id: String(projectId) }
    })
    return response.data as ConversationDto[]
  },

  async createConversation(projectId: string | number, data: {
    modelName?: string
    title?: string
    /** 'lead' requests are deduped server-side: a project keeps at most one
     *  live lead thread, so racing clients converge on the same one. */
    kind?: ConversationKind
    /** conversationId of the lead thread a task was dispatched from */
    parent?: number | null
    /** Shared uuid grouping best-of-N sibling tasks from one prompt */
    variantGroup?: string
  } = {}): Promise<ConversationDto> {
    const response = await api.post('/v1/agents/conversations/', {
      project_id: Number(projectId),
      model_name: data.modelName,
      title: data.title ?? '',
      ...(data.kind ? { kind: data.kind } : {}),
      ...(data.parent != null ? { parent: data.parent } : {}),
      ...(data.variantGroup ? { variant_group: data.variantGroup } : {}),
    })
    return response.data as ConversationDto
  },

  async getConversation(conversationId: number): Promise<ConversationDto> {
    const response = await api.get(`/v1/agents/conversations/${conversationId}/`)
    return response.data as ConversationDto
  },

  async updateConversation(conversationId: number, patch: {
    title?: string
    model_name?: string
    archived?: boolean
  }): Promise<ConversationDto> {
    const response = await api.patch(
      `/v1/agents/conversations/${conversationId}/`,
      patch
    )
    return response.data as ConversationDto
  },

  async deleteConversation(conversationId: number): Promise<void> {
    await api.delete(`/v1/agents/conversations/${conversationId}/`)
  },

  /**
   * Release a conversation's server-side running-run marker (clears
   * is_running and lifts the project's agent_busy guard). Cannot halt a run
   * driven by another tab's live stream — there is no server task handle.
   */
  async cancelConversationRun(conversationId: number): Promise<ConversationDto> {
    const response = await api.post(`/v1/agents/conversations/${conversationId}/cancel/`)
    return response.data as ConversationDto
  },

  /**
   * Accept a reviewed task: the backend merges its worktree into the
   * canonical tree and marks it accepted. Errors keep the axios shape —
   * a conflicted merge rejects with response.status 409 and response.data
   * { error: 'merge_conflict', detail: <git conflict detail> } (and a live
   * canonical run rejects with the usual { detail: 'agent_busy' } 409).
   */
  async acceptTask(conversationId: number): Promise<{ status: string }> {
    const response = await api.post(`/v1/agents/conversations/${conversationId}/accept/`)
    return response.data as { status: string }
  },

  /** Dismiss a reviewed task: discard its worktree without merging. */
  async dismissTask(conversationId: number): Promise<{ status: string }> {
    const response = await api.post(`/v1/agents/conversations/${conversationId}/dismiss/`)
    return response.data as { status: string }
  },

  async getConversationMessages(conversationId: number): Promise<ConversationMessageDto[]> {
    const response = await api.get(
      `/v1/agents/conversations/${conversationId}/messages/`
    )
    // Hydrate persisted run metadata into the same shapes the live stream
    // produces, so a reloaded transcript replays its activity feed verbatim.
    return (response.data as any[]).map((m) => {
      const dto: ConversationMessageDto = {
        id: m.id,
        role: m.role,
        content: m.content,
        timestamp: m.timestamp,
      }
      const meta = m.metadata as PersistedMessageMetadata | null | undefined
      if (!meta) return dto
      if (Array.isArray(meta.tool_calls) && meta.tool_calls.length > 0) {
        dto.activity = meta.tool_calls.map(tc => toolCallToActivityStep(tc.name, tc.args))
      }
      if (Array.isArray(meta.plan) && meta.plan.length > 0) {
        dto.plan = meta.plan
      }
      if (Array.isArray(meta.files_changed) && meta.files_changed.length > 0) {
        dto.filesChanged = meta.files_changed
      }
      // Hydrate whatever usage fields were captured — tokens can exist
      // without cost and vice versa. No fields at all means unknown, so the
      // usage object stays absent entirely (never a phantom zero).
      if (meta.usage) {
        const usage: { costUsd?: number; inputTokens?: number; outputTokens?: number } = {}
        if (typeof meta.usage.cost_usd === 'number') usage.costUsd = meta.usage.cost_usd
        if (typeof meta.usage.input_tokens === 'number') usage.inputTokens = meta.usage.input_tokens
        if (typeof meta.usage.output_tokens === 'number') usage.outputTokens = meta.usage.output_tokens
        if (Object.keys(usage).length > 0) dto.usage = usage
      }
      if (typeof meta.checkpoint === 'string' && meta.checkpoint) {
        dto.checkpoint = meta.checkpoint
      }
      return dto
    })
  },

  /**
   * Rewind a conversation (and the project files) to just before the given
   * user message was sent. The backend restores the message's checkpoint
   * commit and deletes the message plus everything after it; the removed
   * prompt text comes back so the composer can offer it for editing.
   */
  async restoreCheckpoint(
    conversationId: number,
    messageId: number
  ): Promise<{ success: boolean; checkpoint: string; prompt: string }> {
    const response = await api.post(
      `/v1/agents/conversations/${conversationId}/restore/`,
      { message_id: messageId }
    )
    return response.data
  }
};

// Export ModelService for backward compatibility
export const ModelService = ModelsService;
