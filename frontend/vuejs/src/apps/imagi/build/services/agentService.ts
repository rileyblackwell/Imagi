import api from '@/shared/services/api'
import type {
  AIModel,
  AgentResponse,
  VersionControlResponse,
  ConversationDto
} from '../types/services'
import { usePaymentStore } from '@/apps/payments/stores/payments'
import { ModelsService } from '@/apps/imagi/build/services/modelsService'

// Use the shared API instance with extended timeout for AI operations
const AI_TIMEOUT = 90000 // 90 seconds for AI processing

function getPaymentsStore() {
  // Get the payments store using function to avoid SSR issues
  return usePaymentStore()
}

/**
 * Service for talking to the Imagi agent and workspace APIs.
 *
 * A single agent handles all AI interaction (chat + file editing) via
 * processAgent; the rest of the service covers conversation CRUD and
 * version control.
 */
export const AgentService = {
  async processAgent(projectId: string, data: {
    prompt: string;
    model: string;
    reasoningEffort?: string;
    file?: any;
    conversationId?: number | string | null;
  }): Promise<AgentResponse> {
    if (!data.prompt || !data.model) {
      throw new Error('Prompt and model are required')
    }

    if (!projectId) {
      throw new Error('Project ID is required')
    }

    // Check rate limits before making request
    await ModelsService.checkRateLimit(data.model)

    // Validate prompt length against model context window
    const config = ModelsService.getConfig({ id: data.model } as AIModel)
    const estimatedTokens = ModelsService.estimateTokens(data.prompt)

    if (estimatedTokens > config.maxTokens) {
      throw new Error(`Prompt is too long for selected model. Please reduce length or choose a different model.`)
    }

    try {
      // Prepare file info if provided
      let currentFile = null
      if (data.file) {
        currentFile = {
          path: data.file.path,
          type: data.file.type || this.getFileType(data.file.path),
          content: data.file.content || ''
        }
      }

      const payload = {
        message: data.prompt,
        model: data.model,
        reasoning_effort: data.reasoningEffort,
        project_id: String(projectId),
        conversation_id: data.conversationId ?? undefined,
        current_file: currentFile,
      }

      const response = await api.post('/v1/agents/agent/', payload, { timeout: AI_TIMEOUT })

      // Log credits usage if provided
      if (response.data.credits_used) {
        const paymentsStore = getPaymentsStore()
        if (paymentsStore) {
          await paymentsStore.fetchBalance()
        }
      }

      return {
        response: response.data.response,
        conversation_id: response.data.conversation_id,
        files_changed: response.data.files_changed || [],
        tool_calls: response.data.tool_calls || [],
        plan: response.data.plan || [],
        single_message: response.data.single_message || false,
      }
    } catch (error: any) {
      console.error('Agent processing API error:', error)

      let errorDetails = ''
      if (error.response) {
        console.error('Response error data:', error.response.data)
        console.error('Response status:', error.response.status)
        errorDetails = error.response.data?.error || error.response.data?.detail ||
                      (typeof error.response.data === 'string' ? error.response.data : '')
      }

      return {
        response: errorDetails || this.formatError(error),
        files_changed: [],
        tool_calls: [],
        plan: [],
      }
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
        error: this.formatError(error)
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
  } = {}): Promise<ConversationDto> {
    const response = await api.post('/v1/agents/conversations/', {
      project_id: Number(projectId),
      model_name: data.modelName,
      title: data.title ?? ''
    })
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

  async getConversationMessages(conversationId: number): Promise<Array<{
    id: number
    role: 'user' | 'assistant' | 'system'
    content: string
    timestamp: string
  }>> {
    const response = await api.get(
      `/v1/agents/conversations/${conversationId}/messages/`
    )
    return response.data
  }
};

// Export ModelService for backward compatibility
export const ModelService = ModelsService;
