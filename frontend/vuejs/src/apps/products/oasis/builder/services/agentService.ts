import api from './api'
import { handleAPIError } from '../utils/errors'
import type { 
  CodeGenerationResponse, 
  AIModel, 
  UndoResponse,
  ModelConfig
} from '../types/services'
import { AI_MODELS, MODEL_CONFIGS } from '../types/services'
import { usePaymentsStore } from '@/apps/payments/store'
import { notify } from '@/shared/utils'
import axios from 'axios'
import { ref } from 'vue'

// Static variables for rate limiting
let requestCounts: Map<string, number> = new Map()
let lastResetTime: number = Date.now()
const RESET_INTERVAL = 60000 // 1 minute

// Define the ChatPayload interface
interface ChatPayload {
  message: string;
  model: string;
  project_id: string;
  conversation_id?: string;
  mode?: string;
  current_file?: any;
}

function getPaymentsStore() {
  // Get the payments store using function to avoid SSR issues
  return usePaymentsStore()
}

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
    if (!data.prompt || !data.model || !projectId) {
      console.error('AgentService: Missing required parameters for chat');
      throw new Error('Missing required parameters for chat');
    }
    
    // Get conversation ID from localStorage
    const storedConversationId = localStorage.getItem(`chat_conversation_${projectId}`);
    
    // Prepare request payload
    const payload: {
      message: string;
      model: string;
      project_id: string;
      conversation_id?: string;
      mode: string;
      stream?: boolean;
      current_file?: {
        path: string;
        type: string;
        content: string;
      };
    } = {
      message: data.prompt,
      model: data.model,
      project_id: String(projectId),
      conversation_id: storedConversationId || undefined,
      mode: data.mode || 'chat',
    };
    
    // Add current file if available - but omit content which can cause 400 errors
    if (data.file) {
      payload.current_file = {
        path: data.file.path,
        type: data.file.type,
        content: data.file.content || ''
      }
    }
    
    try {
      // Check for valid project_id
      if (!payload.project_id) {
        console.error('Missing required project_id parameter');
        throw new Error('Project ID is required for chat API');
      }
      
      // Use the chat endpoint from agents/api
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
      let assistantResponse = response.data.response || '';
      
      // Handle potential null response
      if (assistantResponse === null) {
        console.warn('AgentService: Null assistant response received from API');
        assistantResponse = '';
      }
      
      // Additional validation and normalization for response format
      let validatedResponse = assistantResponse;
      
      // If response is an object (possible with some model responses), convert to string
      if (typeof validatedResponse === 'object') {
        console.warn('AgentService: Object response received:', validatedResponse);
        try {
          validatedResponse = JSON.stringify(validatedResponse);
        } catch (e) {
          validatedResponse = String(validatedResponse);
        }
      }
      
      // Create the assistant message with complete data
      const assistantMessage = {
        role: 'assistant',
        content: validatedResponse,
        timestamp: new Date().toISOString(),
        code: response.data.code || null
      };
      
      // Refresh the user's balance after successful API call
      try {
        const paymentsStore = getPaymentsStore();
        paymentsStore.fetchBalance(false); // silent refresh
      } catch (err) {
        console.warn('Failed to refresh balance:', err);
      }
      
      return {
        response: validatedResponse,
        messages: [userMessage, assistantMessage]
      };
    } catch (error: any) {
      // Log the error for debugging
      console.error('Chat API error:', error);
      
      // Improved error handling
      if (error.response?.status === 400) {
        // Parse specific error details for 400 Bad Request
        const errorDetail = error.response.data?.error || 'Bad request';
        throw new Error(`API Error: ${errorDetail}`);
      }
      
      // Check if the error contains an HTML response (Django error page)
      if (error.response && error.response.data && 
          typeof error.response.data === 'string' && 
          error.response.data.includes('<!DOCTYPE html>')) {
        console.error('Received HTML error page instead of JSON response');
        error.message = 'Server returned an HTML error page instead of JSON response';
      }
      
      // Check if the error is due to authentication (401)
      if (error.response && error.response.status === 401) {
        console.error('Authentication error in chat request. Attempting to reauth.');
        
        // Force refresh the token or redirect to login if needed
        window.dispatchEvent(new CustomEvent('auth:refresh-needed'));
      }
      
      // Check if the error is a server error (500)
      if (error.response && error.response.status === 500) {
        console.error('Server error (500) in chat request:');
        
        // Try to log useful information about the error
        if (error.response.data) {
          console.error('Error data:', 
            typeof error.response.data === 'string' 
              ? error.response.data.substring(0, 200) 
              : error.response.data);
        }
        
        error.message = 'Server error (500). The request failed due to an internal server problem.';
      }
      
      throw handleAPIError(error);
    }
  },

  /**
   * Process a chat message with a simulated typing effect
   * This simulates streaming but uses the regular chat API
   */
  async processChatWithTypingEffect(
    payload: ChatPayload,
    onChunk: (chunk: string) => void,
    onError: (error: string) => void,
    onDone: () => void,
    onConversationId?: (id: string) => void
  ): Promise<void> {
    try {
      // console.log('Starting chat request with typing effect simulation...');
      
      // Enhanced logging for debugging
      // console.log('Chat API Request:', {
      //   payload: { 
      //     ...payload, 
      //     message: payload.message.length > 50 ? payload.message.substring(0, 50) + '...' : payload.message 
      //   }
      // });
      
      // Process the message with regular chat API
      const chatResponse = await this.processChat(
        payload.project_id,
        {
          prompt: payload.message,
          model: payload.model,
          mode: payload.mode,
          file: payload.current_file
        }
      );
      
      // Extract the response text
      const responseText = chatResponse.response;
      
      // If we have a conversation ID and callback, use it
      if (chatResponse.messages[0] && payload.conversation_id) {
        if (onConversationId) {
          onConversationId(payload.conversation_id);
        }
      }
      
      // Simulate typing effect by chunking the response
      await this.simulateTypingEffect(responseText, onChunk);
      
      // Call onDone when complete
      onDone();
    } catch (error: any) {
      console.error('Error in processChatWithTypingEffect:', error);
      onError(`Error: ${error.message || 'Unknown error'}`);
    }
  },
  
  /**
   * Simulates a typing effect by chunking a string over time
   */
  async simulateTypingEffect(
    text: string, 
    onChunk: (chunk: string) => void
  ): Promise<void> {
    if (!text) return;
    
    // Configuration for typing simulation
    const avgCharsPerSecond = 40; // Adjust for slower/faster typing
    const minChunkSize = 1;
    const maxChunkSize = 5;
    const variability = 0.3; // Randomness in timing (0-1)
    
    // Calculate base delay between chunks
    const baseDelayMs = 1000 / avgCharsPerSecond;
    
    // Process the text in small chunks to simulate typing
    let processedLength = 0;
    
    while (processedLength < text.length) {
      // Determine chunk size with some randomness
      const remainingChars = text.length - processedLength;
      const maxPossibleChunk = Math.min(maxChunkSize, remainingChars);
      const chunkSize = Math.max(
        minChunkSize, 
        Math.floor(Math.random() * (maxPossibleChunk - minChunkSize + 1)) + minChunkSize
      );
      
      // Extract the next chunk
      const chunk = text.substr(processedLength, chunkSize);
      processedLength += chunkSize;
      
      // Send the chunk
      onChunk(chunk);
      
      // Add natural variability to typing speed
      const delayVariability = 1 + (Math.random() * 2 * variability - variability);
      const delay = baseDelayMs * chunkSize * delayVariability;
      
      // Add a longer pause at natural breakpoints (periods, commas, etc.)
      const lastChar = chunk.charAt(chunk.length - 1);
      const isPunctuation = ['.', '!', '?', ',', ';', ':'].includes(lastChar);
      const breakpointMultiplier = isPunctuation ? (lastChar === '.' ? 5 : 2) : 1;
      
      // Wait before next chunk
      await new Promise(resolve => setTimeout(resolve, delay * breakpointMultiplier));
    }
  },

  // Replace processChatStream with the new function that uses typing effect
  async processChatStream(
    payload: ChatPayload,
    onChunk: (chunk: string) => void,
    onError: (error: string) => void,
    onDone: () => void,
    onConversationId?: (id: string) => void
  ): Promise<void> {
    return this.processChatWithTypingEffect(payload, onChunk, onError, onDone, onConversationId);
  },

  // Helper method to get auth token
  getAuthToken(): string | null {
    try {
      const tokenData = localStorage.getItem('token');
      if (!tokenData) return null;
      
      const parsedToken = JSON.parse(tokenData);
      return parsedToken?.value || null;
    } catch {
      return null;
    }
  },

  // Helper to format error messages
  formatError(error: any): string {
    if (error.response) {
      // Server responded with error
      if (error.response.status === 401) {
        return '401: Unauthorized - Please log in again';
      }
      
      // Handle bad request errors (400) with more detail
      if (error.response.status === 400) {
        let detail = '';
        
        // Try to extract useful information from response
        if (error.response.data) {
          if (typeof error.response.data === 'string') {
            detail = error.response.data.substring(0, 200);
          } else if (typeof error.response.data === 'object') {
            // Format object data
            detail = JSON.stringify(error.response.data);
          }
        }
        
        return `400: Bad Request - ${detail || error.response.statusText}`;
      }
      
      return `Server error ${error.response.status}: ${error.response.data?.detail || error.response.statusText}`;
    } else if (error.request) {
      // Request made but no response
      return 'No response received from server. Please check your connection.';
    } else {
      // Something else went wrong
      return error.message || 'Unknown error occurred';
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
