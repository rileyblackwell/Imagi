import api from './api'
import { handleAPIError } from '../utils/errors'
import { API_CONFIG } from './api'
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
        project_id: projectId,
        file_path: data.file_path,
        mode: data.mode,
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
        code: response.data.code || response.data.response,
        response: response.data.response || "Generated code successfully",
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
    file?: any;
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
      const payload: {
        message: string;
        model: string;
        project_id: string;
        conversation_id?: string;
        mode: string;
        current_file?: {
          path: string;
          content: string;
          type: string;
        }
      } = {
        message: data.prompt,
        model: data.model,
        project_id: projectId,
        conversation_id: storedConversationId || undefined,
        mode: data.mode || 'chat'
      }
      
      // Add the current file if it exists
      if (data.file) {
        payload.current_file = {
          path: data.file.path,
          content: data.file.content,
          type: data.file.type
        }
      }
      
      // Use the chat endpoint from agents/api - ensure the path is correct
      const response = await api.post('/api/v1/agents/chat/', payload)
      
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

  async processChatStream(
    projectId: string,
    data: {
      prompt: string;
      model: string;
      mode?: string;
      file?: any;
    },
    onChunk: (chunk: string) => void,
    onConversationId: (id: string) => void,
    onDone: () => void,
    onError: (error: string) => void
  ): Promise<void> {
    if (!projectId) {
      throw new Error('Project ID is required')
    }

    try {
      // Only continue if the model is an OpenAI model
      if (!data.model.includes('gpt')) {
        throw new Error('Streaming is only supported for OpenAI models')
      }

      // Get conversation ID from localStorage
      const storedConversationId = localStorage.getItem(`chat_conversation_${projectId}`)
      
      // Prepare request payload
      const payload: {
        message: string;
        model: string;
        project_id: string;
        conversation_id?: string;
        mode: string;
        stream: boolean;
        current_file?: {
          path: string;
          content: string;
          type: string;
        }
      } = {
        message: data.prompt,
        model: data.model,
        project_id: projectId,
        conversation_id: storedConversationId || undefined,
        mode: data.mode || 'chat',
        stream: true
      }
      
      // Add the current file if it exists
      if (data.file) {
        payload.current_file = {
          path: data.file.path,
          content: data.file.content,
          type: data.file.type
        }
      }

      // Create event source for SSE
      const body = JSON.stringify(payload)
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/v1/agents/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
        },
        body
      })

      // Check if the response is ok
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to stream response')
      }

      // Create reader to read the streaming response
      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('Failed to create reader for streaming response')
      }

      // Read the stream
      const decoder = new TextDecoder()
      let buffer = ''

      // Process chunks
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        // Decode the chunk
        const chunk = decoder.decode(value, { stream: true })
        buffer += chunk

        // Process the buffer line by line
        const lines = buffer.split('\n\n')
        buffer = lines.pop() || '' // Keep the last (potentially incomplete) line in the buffer

        for (const line of lines) {
          if (line.trim() && line.startsWith('data:')) {
            try {
              const eventData = JSON.parse(line.substring(5).trim())
              
              // Handle different event types
              if (eventData.event === 'content') {
                onChunk(eventData.data)
              } else if (eventData.event === 'conversation_id') {
                localStorage.setItem(`chat_conversation_${projectId}`, eventData.data)
                onConversationId(eventData.data)
              } else if (eventData.event === 'error') {
                onError(eventData.data)
              } else if (eventData.event === 'done') {
                onDone()
              }
            } catch (e) {
              console.error('Error parsing SSE event:', e)
            }
          }
        }
      }
    } catch (error: any) {
      console.error('Chat streaming API error:', error)
      onError(error.message || 'An error occurred while streaming the response')
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
    if (!projectId) {
      throw new Error('Project ID is required')
    }
    
    if (!filePath) {
      throw new Error('File path is required for undo action')
    }

    try {
      // Use the new undo-interaction endpoint
      const response = await api.post(`/api/v1/builder/${projectId}/files/${filePath}/undo-interaction/`)
      
      return {
        success: response.data.success,
        message: response.data.message || 'Successfully undid the last AI interaction',
        details: response.data.details || {}
      }
    } catch (error) {
      throw handleAPIError(error)
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
      
      // Ensure project ID is a string
      const sanitizedProjectId = String(projectId)
      
      // Prepare request payload
      const payload = {
        message: data.prompt,
        model: data.model,
        project_id: sanitizedProjectId,
        file_path: data.file_path,
        conversation_id: storedConversationId || undefined
      }
      
      // Use the stylesheet endpoint
      const response = await api.post('/api/v1/agents/build/stylesheet/', payload)
      
      // Store the conversation ID for future requests
      if (response.data && response.data.conversation_id) {
        localStorage.setItem(`stylesheet_conversation_${projectId}`, response.data.conversation_id)
      }
      
      // Create a proper response object matching the expected format
      // Handle various response formats from the server
      return {
        success: true,
        code: response.data.stylesheet || response.data.code || response.data.response || '',
        response: response.data.response || "Generated stylesheet successfully",
        messages: Array.isArray(response.data.messages) ? response.data.messages : 
          (response.data.user_message && response.data.assistant_message 
            ? [response.data.user_message, response.data.assistant_message]
            : [])
      }
    } catch (error: any) {
      console.error('[ERROR] Stylesheet generation error:', error)
      
      // Log detailed error information
      if (error.response) {
        console.error('[ERROR] API error details:', {
          status: error.response.status,
          statusText: error.response.statusText,
          data: error.response.data,
          headers: error.response.headers
        })
        
        // If the server returned data with a stylesheet despite the error, use it
        if (error.response.data && (error.response.data.stylesheet || error.response.data.code)) {
          return {
            success: true,
            code: error.response.data.stylesheet || error.response.data.code,
            response: error.response.data.response || "Generated stylesheet with warnings",
            messages: []
          }
        }
        
        // If there's a specific error message from the server, show it
        if (error.response.data && error.response.data.error) {
          console.error('[ERROR] Server error message:', error.response.data.error)
        }
      } else if (error.request) {
        console.error('[ERROR] No response received:', error.request)
      } else {
        console.error('[ERROR] Request setup error:', error.message)
      }
      
      throw handleAPIError(error)
    }
  },

  // Preview project - migrated from BuilderService
  async generatePreview(projectId: string): Promise<{ previewUrl: string }> {
    try {
      const response = await api.get(`/api/v1/builder/${projectId}/preview/`)
      
      if (!response.data || !response.data.preview_url) {
        throw new Error('Invalid response from preview API')
      }
      
      return {
        previewUrl: response.data.preview_url
      }
    } catch (error) {
      console.error('Error generating preview:', error)
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
      const response = await api.post(`/api/v1/builder/${projectId}/initialize/`)
      
      // Return success or the actual data if available
      return response.data?.success !== undefined 
        ? response.data 
        : { success: true }
    } catch (error: any) {
      // If we get a 409 status, it means the project is already initialized
      if (error.response?.status === 409) {
        return { success: true }
      }

      console.error('Error initializing project:', error)
      
      // For 404 errors, we will treat this as "not yet created" and return success: false
      // rather than throwing an error, as the project might still be in the creation process
      if (error.response?.status === 404) {
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
