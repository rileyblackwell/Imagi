import api from './api'
import { handleAPIError } from '../utils/errors'
import type { 
  CodeGenerationResponse, 
  AIModel, 
  UndoResponse 
} from '../types/builder'
import { AI_MODELS } from '../types/builder'

// Model configuration types and constants from ModelService
interface ModelConfig {
  maxTokens: number
  rateLimits: {
    tokensPerMinute: number
    requestsPerMinute: number
  }
  contextWindow: number
  capabilities: string[]
}

const MODEL_CONFIGS: Record<string, ModelConfig> = {
  'gpt-4': {
    maxTokens: 8192,
    rateLimits: {
      tokensPerMinute: 40000,
      requestsPerMinute: 200
    },
    contextWindow: 8192,
    capabilities: ['code_generation', 'chat', 'analysis']
  },
  'claude-2': {
    maxTokens: 100000,
    rateLimits: {
      tokensPerMinute: 100000,
      requestsPerMinute: 300
    },
    contextWindow: 100000,
    capabilities: ['code_generation', 'chat', 'analysis']
  },
  'claude-3-5-sonnet-20241022': {
    maxTokens: 200000,
    rateLimits: {
      tokensPerMinute: 100000,
      requestsPerMinute: 300
    },
    contextWindow: 200000,
    capabilities: ['code_generation', 'chat', 'analysis']
  },
  'gpt-4o': {
    maxTokens: 128000,
    rateLimits: {
      tokensPerMinute: 60000,
      requestsPerMinute: 250
    },
    contextWindow: 128000,
    capabilities: ['code_generation', 'chat', 'analysis']
  },
  'gpt-4o-mini': {
    maxTokens: 128000,
    rateLimits: {
      tokensPerMinute: 80000,
      requestsPerMinute: 350
    },
    contextWindow: 128000,
    capabilities: ['code_generation', 'chat', 'analysis']
  }
}

// Static variables for rate limiting
let requestCounts: Map<string, number> = new Map()
let lastResetTime: number = Date.now()
const RESET_INTERVAL = 60000 // 1 minute

/**
 * Service for handling agent workspace and AI-related API calls
 */
export const AgentService = {
  // Model service methods (merged from ModelService)
  getConfig(model: AIModel): ModelConfig {
    return MODEL_CONFIGS[model.id] || {
      maxTokens: 4096,
      rateLimits: {
        tokensPerMinute: 20000,
        requestsPerMinute: 150
      },
      contextWindow: 4096,
      capabilities: ['chat']
    }
  },

  async checkRateLimit(modelId: string): Promise<boolean> {
    // Reset counters if minute has passed
    if (Date.now() - lastResetTime > RESET_INTERVAL) {
      requestCounts.clear()
      lastResetTime = Date.now()
    }

    const currentCount = requestCounts.get(modelId) || 0
    const config = MODEL_CONFIGS[modelId]
    
    if (!config) return true // Allow if no config found
    
    if (currentCount >= config.rateLimits.requestsPerMinute) {
      throw new Error(`Rate limit exceeded for model ${modelId}. Please wait a moment.`)
    }

    requestCounts.set(modelId, currentCount + 1)
    return true
  },

  canGenerateCode(model: AIModel): boolean {
    const config = this.getConfig(model)
    return config.capabilities.includes('code_generation')
  },

  estimateTokens(text: string): number {
    // Rough estimation: ~4 chars per token
    return Math.ceil(text.length / 4)
  },
  
  getDefaultModels(): AIModel[] {
    return AI_MODELS
  },

  // AI interaction methods - using Agents API
  async generateCode(projectId: string, data: {
    prompt: string;
    mode: string;
    model: string | null;
    file_path?: string;
  }): Promise<CodeGenerationResponse> {
    if (!data.model) {
      throw new Error('AI model must be selected')
    }

    // Now data.model is guaranteed to be a string (not null)
    const modelId: string = data.model;
    
    // Check rate limits before making request
    await this.checkRateLimit(modelId)

    // Validate prompt length against model context window
    const config = this.getConfig({ id: modelId } as AIModel)
    const estimatedTokens = this.estimateTokens(data.prompt)
    
    if (estimatedTokens > config.maxTokens) {
      throw new Error(`Prompt is too long for selected model. Please reduce length or choose a different model.`)
    }

    try {
      // Get conversation ID from localStorage
      const storedConversationId = localStorage.getItem(`agent_conversation_${projectId}`)
      
      // Prepare request payload
      const payload = {
        message: data.prompt,
        model: modelId,
        file_path: data.file_path,
        conversation_id: storedConversationId || undefined
      }
      
      // Use the build_template endpoint from agents/api
      const response = await api.post('/api/v1/agents/build/template/', payload)
      
      // Store the conversation ID for future requests
      if (response.data.conversation_id) {
        localStorage.setItem(`agent_conversation_${projectId}`, response.data.conversation_id)
      }
      
      return {
        success: true,
        code: response.data.response,
        messages: [
          response.data.user_message,
          response.data.assistant_message
        ]
      }
    } catch (error) {
      throw handleAPIError(error)
    }
  },

  async processChat(projectId: string, data: {
    prompt: string;
    model: string;
    mode?: string;
  }): Promise<{
    response: string;
    messages: any[];
  }> {
    if (!projectId) {
      throw new Error('Project ID is required')
    }

    try {
      // Get conversation ID from localStorage
      const storedConversationId = localStorage.getItem(`chat_conversation_${projectId}`)
      
      // Prepare request payload
      const payload = {
        message: data.prompt,
        model: data.model,
        project_id: projectId,
        conversation_id: storedConversationId || undefined,
        mode: data.mode || 'chat'
      }
      
      console.log('AgentService: Sending chat request with payload:', payload)
      
      // Use the chat endpoint from agents/api - ensure the path is correct
      const response = await api.post('/api/v1/agents/chat/', payload)
      
      // Full response logging for debugging
      console.log('AgentService: Full chat API response:', response.data)
      
      // Log successful response 
      console.log('AgentService: Chat API response status:', {
        status: response.status,
        conversation_id: response.data.conversation_id,
        has_response: !!response.data.response,
        response_length: response.data.response ? response.data.response.length : 0
      })
      
      // Store the conversation ID for future requests
      if (response.data.conversation_id) {
        localStorage.setItem(`chat_conversation_${projectId}`, response.data.conversation_id)
      }

      // Create properly formatted user and assistant messages
      const userMessage = {
        role: 'user',
        content: data.prompt,
        timestamp: new Date().toISOString()
      };
      
      // Extract assistant response, ensuring it's not empty
      const assistantResponse = response.data.response || '';
      
      if (!assistantResponse) {
        console.warn('AgentService: Empty assistant response received from API')
      }
      
      // Additional validation for response format
      let validatedResponse = assistantResponse;
      // If not a string, convert to string
      if (typeof validatedResponse !== 'string') {
        console.warn('AgentService: Non-string response received:', validatedResponse);
        validatedResponse = JSON.stringify(validatedResponse);
      }
      
      const assistantMessage = {
        role: 'assistant',
        content: validatedResponse,
        timestamp: new Date().toISOString(),
        code: response.data.code || null
      };
      
      console.log('AgentService: Created formatted messages:', {
        userMessage,
        assistantMessage
      })

      // Process and return the response data in the expected format
      return {
        response: assistantResponse,
        messages: [userMessage, assistantMessage]
      }
    } catch (error: any) {
      console.error('Chat API error:', error)
      
      // Log more detailed error information
      if (error.response) {
        // The request was made and the server responded with an error status
        console.error('Response error data:', error.response.data)
        console.error('Response status:', error.response.status)
      } else if (error.request) {
        // The request was made but no response was received
        console.error('No response received from server')
      } else {
        // Something happened in setting up the request
        console.error('Request setup error:', error.message)
      }
      
      throw handleAPIError(error)
    }
  },

  async clearConversation(projectId: string): Promise<void> {
    try {
      // Get conversation IDs for this project
      const chatConversationId = localStorage.getItem(`chat_conversation_${projectId}`)
      const agentConversationId = localStorage.getItem(`agent_conversation_${projectId}`)
      const stylesheetConversationId = localStorage.getItem(`stylesheet_conversation_${projectId}`)
      
      // Just clear local storage items without calling the API
      if (chatConversationId) {
        localStorage.removeItem(`chat_conversation_${projectId}`)
      }
      
      if (agentConversationId) {
        localStorage.removeItem(`agent_conversation_${projectId}`)
      }
      
      if (stylesheetConversationId) {
        localStorage.removeItem(`stylesheet_conversation_${projectId}`)
      }
      
      // Return a resolved promise
      return Promise.resolve()
    } catch (error) {
      throw handleAPIError(error)
    }
  },

  async getAvailableModels(): Promise<AIModel[]> {
    try {
      // For now, return default models
      return this.getDefaultModels()
    } catch (error) {
      throw handleAPIError(error)
    }
  },

  async undoAction(projectId: string, filePath?: string): Promise<UndoResponse> {
    try {
      // Use the file-specific undo endpoint if a file path is provided
      const endpoint = filePath 
        ? `/api/v1/builder/${projectId}/files/${encodeURIComponent(filePath)}/undo/`
        : `/api/v1/builder/${projectId}/undo/`;
      
      const response = await api.post(endpoint);
      return response.data;
    } catch (error) {
      throw handleAPIError(error);
    }
  },

  async generateStylesheet(projectId: string, data: {
    prompt: string;
    model: string;
    file_path: string;
  }): Promise<CodeGenerationResponse> {
    // Check rate limits before making request
    await this.checkRateLimit(data.model)

    // Validate prompt length
    const config = this.getConfig({ id: data.model } as AIModel)
    const estimatedTokens = this.estimateTokens(data.prompt)
    
    if (estimatedTokens > config.maxTokens) {
      throw new Error(`Prompt is too long for selected model. Please reduce length or choose a different model.`)
    }

    try {
      // Get conversation ID from localStorage
      const storedConversationId = localStorage.getItem(`stylesheet_conversation_${projectId}`)
      
      // Prepare request payload
      const payload = {
        message: data.prompt,
        model: data.model,
        file_path: data.file_path,
        conversation_id: storedConversationId || undefined
      }
      
      // Use the stylesheet endpoint
      const response = await api.post('/api/v1/agents/build/stylesheet/', payload)
      
      // Store the conversation ID for future requests
      if (response.data.conversation_id) {
        localStorage.setItem(`stylesheet_conversation_${projectId}`, response.data.conversation_id)
      }
      
      return {
        success: true,
        code: response.data.response,
        messages: [
          response.data.user_message,
          response.data.assistant_message
        ]
      }
    } catch (error) {
      throw handleAPIError(error)
    }
  },

  // Preview project - migrated from BuilderService
  async generatePreview(projectId: string): Promise<{ previewUrl: string }> {
    try {
      const response = await api.post(`/api/v1/builder/${projectId}/preview/`)
      return response.data
    } catch (error) {
      throw handleAPIError(error)
    }
  },

  // Deploy project - migrated from BuilderService
  async deployProject(projectId: string, options: { environment: string }): Promise<{ deploymentUrl: string }> {
    try {
      const response = await api.post(`/api/v1/builder/${projectId}/deploy/`, options)
      return response.data
    } catch (error) {
      throw handleAPIError(error)
    }
  },

  async initializeProject(projectId: string): Promise<{ success: boolean }> {
    if (!projectId) {
      throw new Error('Project ID is required')
    }

    try {
      console.log(`Requesting project initialization for project ${projectId}`)
      const response = await api.post(`/api/v1/builder/${projectId}/initialize/`)
      console.log('Project initialization response:', response.data)
      
      // Return success or the actual data if available
      return response.data?.success !== undefined 
        ? response.data 
        : { success: true }
    } catch (error: any) {
      // If we get a 409 status, it means the project is already initialized
      if (error.response?.status === 409) {
        console.log('Project is already initialized')
        return { success: true }
      }

      console.error('Error initializing project:', error)
      
      // For 404 errors, we will treat this as "not yet created" and return success: false
      // rather than throwing an error, as the project might still be in the creation process
      if (error.response?.status === 404) {
        console.warn('Project not found during initialization check - it might still be creating')
        return { success: false }
      }
      
      // For other errors, throw and let the caller handle it
      throw handleAPIError(error)
    }
  }
}

// Export ModelService for backward compatibility
export const ModelService = {
  getConfig: AgentService.getConfig,
  checkRateLimit: AgentService.checkRateLimit,
  canGenerateCode: AgentService.canGenerateCode,
  estimateTokens: AgentService.estimateTokens,
  getDefaultModels: AgentService.getDefaultModels
} 
