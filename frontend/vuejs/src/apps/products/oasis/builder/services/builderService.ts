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
 * Service for handling builder workspace and AI-related API calls
 */
export const BuilderService = {
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
    
    // Get the model provider (openai or anthropic)
    const modelInfo = AI_MODELS.find(m => m.id === modelId);
    const provider = modelInfo?.provider || 'openai';

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
      const storedConversationId = localStorage.getItem(`builder_conversation_${projectId}`)
      
      // Prepare request payload
      const messagePayload: any = {
        message: data.prompt,
        model: modelId,
        provider: provider,
        mode: data.mode,
        file_path: data.file_path
      }
      
      let response;
      
      // If we have a conversation ID, use it
      if (storedConversationId) {
        messagePayload.conversation_id = storedConversationId
        response = await api.post('/products/oasis/agents/send-message/', messagePayload)
      } else {
        // Create a new conversation first
        const conversationResponse = await api.post('/products/oasis/agents/conversations/', {
          model_name: modelId,
          provider: provider,
          mode: data.mode
        })
        const newConversationId = conversationResponse.data.id
        localStorage.setItem(`builder_conversation_${projectId}`, newConversationId)
        
        // Then send the message with the new conversation ID
        messagePayload.conversation_id = newConversationId
        response = await api.post('/products/oasis/agents/send-message/', messagePayload)
      }
      
      return {
        success: true,
        code: response.data.assistant_message.content,
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
    // Check rate limits before making request
    await this.checkRateLimit(data.model)
    
    // Get the model provider (openai or anthropic)
    const modelInfo = AI_MODELS.find(m => m.id === data.model);
    const provider = modelInfo?.provider || 'openai';

    // Validate message length
    const config = this.getConfig({ id: data.model } as AIModel)
    const estimatedTokens = this.estimateTokens(data.prompt)
    
    if (estimatedTokens > config.maxTokens) {
      throw new Error(`Message is too long for selected model. Please reduce length or choose a different model.`)
    }

    try {
      // Get conversation ID from localStorage
      const storedConversationId = localStorage.getItem(`chat_conversation_${projectId}`)
      
      // Prepare request payload
      const messagePayload: any = {
        message: data.prompt,
        model: data.model,
        provider: provider,
        mode: data.mode || 'chat'
      }
      
      let response;
      
      // If we have a conversation ID, use it
      if (storedConversationId) {
        messagePayload.conversation_id = storedConversationId
        response = await api.post('/products/oasis/agents/send-message/', messagePayload)
      } else {
        // Create a new conversation first
        const conversationResponse = await api.post('/products/oasis/agents/conversations/', {
          model_name: data.model,
          provider: provider,
          mode: data.mode || 'chat'
        })
        const newConversationId = conversationResponse.data.id
        localStorage.setItem(`chat_conversation_${projectId}`, newConversationId)
        
        // Then send the message with the new conversation ID
        messagePayload.conversation_id = newConversationId
        response = await api.post('/products/oasis/agents/send-message/', messagePayload)
      }
      
      return {
        response: response.data.assistant_message.content,
        messages: [
          response.data.user_message,
          response.data.assistant_message
        ]
      }
    } catch (error) {
      throw handleAPIError(error)
    }
  },

  async clearConversation(projectId: string): Promise<void> {
    try {
      // Get conversation ID for this project
      const chatConversationId = localStorage.getItem(`chat_conversation_${projectId}`)
      const builderConversationId = localStorage.getItem(`builder_conversation_${projectId}`)
      
      if (chatConversationId) {
        await api.post('/products/oasis/agents/clear-conversation/', {
          conversation_id: chatConversationId
        })
      }
      
      if (builderConversationId) {
        await api.post('/products/oasis/agents/clear-conversation/', {
          conversation_id: builderConversationId
        })
      }
    } catch (error) {
      throw handleAPIError(error)
    }
  },

  // Get available AI models
  async getAvailableModels(): Promise<AIModel[]> {
    // Return default models directly from the frontend
    // No API call needed as models should be handled on the frontend
    return AI_MODELS;
  },

  // Undo action
  async undoAction(projectId: string): Promise<UndoResponse> {
    try {
      const response = await api.post(`/project-manager/projects/${projectId}/undo/`)
      return response.data
    } catch (error) {
      throw handleAPIError(error)
    }
  },

  // Preview project
  async generatePreview(projectId: string): Promise<{ previewUrl: string }> {
    try {
      const response = await api.post(`/project-manager/projects/${projectId}/preview/`)
      return {
        previewUrl: response.data.preview_url || response.data.previewUrl
      }
    } catch (error) {
      throw handleAPIError(error)
    }
  },

  // Deploy project
  async deployProject(projectId: string, options: { environment: string }): Promise<{ deploymentUrl: string }> {
    try {
      const response = await api.post(`/project-manager/projects/${projectId}/deploy/`, options)
      return {
        deploymentUrl: response.data.deployment_url || response.data.deploymentUrl
      }
    } catch (error) {
      throw handleAPIError(error)
    }
  }
}

// Export ModelService for backward compatibility
export const ModelService = {
  getConfig: BuilderService.getConfig,
  checkRateLimit: BuilderService.checkRateLimit,
  canGenerateCode: BuilderService.canGenerateCode,
  estimateTokens: BuilderService.estimateTokens,
  getDefaultModels: BuilderService.getDefaultModels
} 