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
import axios from 'axios'

// Static variables for rate limiting
let requestCounts: Map<string, number> = new Map()
let lastResetTime: number = Date.now()
const RESET_INTERVAL = 60000 // 1 minute

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
      // Debug log the payload
      console.log('Chat API payload:', JSON.stringify(payload, null, 2));
      
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
   * Process a chat message using streaming
   * This allows for real-time response updates for OpenAI and Anthropic models
   */
  async processChatStream(
    message: string,
    modelId: string,
    projectId: string | number,
    options: {
      conversationId?: string;
      mode?: string;
      currentFile?: any;
      callbacks: {
        onContent: (content: string) => void;
        onConversationId?: (id: string) => void;
        onDone: () => void;
        onError: (error: string) => void;
      };
    }
  ): Promise<boolean> {
    try {
      const api = axios.create({
        baseURL: `${import.meta.env.VITE_API_URL || ''}`,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        }
      });
      
      // Try to get stored conversation ID
      const storedConversationId = localStorage.getItem(`chat_conversation_${projectId}`);
      
      // Prepare payload for the API
      const payload: {
        message: string;
        model: string;
        project_id: string;
        conversation_id?: string;
        mode: string;
        stream: boolean;
        current_file?: {
          path: string;
          type: string;
          content: string;
        };
      } = {
        message,
        model: modelId,
        project_id: String(projectId),
        conversation_id: options.conversationId || storedConversationId || undefined,
        mode: options.mode || 'chat',
        stream: true // Request streaming responses
      };
      
      // Add current file if available - but omit content which can cause 400 errors
      if (options.currentFile) {
        payload.current_file = {
          path: options.currentFile.path,
          type: options.currentFile.type,
          content: options.currentFile.content || ''
        };
      }
      
      // Debug log the streaming payload
      console.log('Streaming API payload:', JSON.stringify(payload, null, 2));
      
      // Validate required fields
      if (!payload.message || !payload.model || !payload.project_id) {
        console.error('Missing required parameters for streaming chat');
        options.callbacks.onError('Missing required parameters: message, model, or project_id');
        return false;
      }
      
      // Ensure project_id is a string (backend might expect string format)
      payload.project_id = String(payload.project_id);
      
      // Set up EventSource for server-sent events
      const queryParams = new URLSearchParams();
      queryParams.append('stream', 'true');
      
      // Use the standard chat endpoint with streaming
      const response = await fetch(`${api.defaults.baseURL}/api/v1/agents/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${this.getAuthToken()}`
        },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) {
        // Try to extract error details from response for better debugging
        let errorDetail = '';
        try {
          const errorData = await response.text();
          console.error('Error response from server:', errorData);
          
          // Try to parse the error data as JSON
          try {
            const jsonError = JSON.parse(errorData);
            if (jsonError.detail) {
              errorDetail = jsonError.detail;
            } else if (jsonError.error) {
              errorDetail = jsonError.error;
            } else if (jsonError.message) {
              errorDetail = jsonError.message;
            } else {
              errorDetail = JSON.stringify(jsonError);
            }
            
            // Check if it's a credit-related error
            if (response.status === 402 || 
                errorDetail.includes('insufficient credit') || 
                errorDetail.includes('need more credit')) {
              
              // Format credit error nicely
              const amountMatch = errorDetail.match(/\$?([0-9.]+)/);
              if (amountMatch) {
                errorDetail = `Insufficient credits: You need $${amountMatch[1]} more to use ${modelId}. Please add more credits.`;
              } else {
                errorDetail = `Insufficient credits to use ${modelId}. Please add more credits.`;
              }
            }
          } catch {
            // If not JSON, use the text directly
            errorDetail = errorData.substring(0, 200);
          }
        } catch (textError) {
          errorDetail = 'Could not read error details';
        }
        
        const errorMessage = `HTTP error! status: ${response.status}${errorDetail ? ` - ${errorDetail}` : ''}`;
        console.error(errorMessage);
        options.callbacks.onError(errorMessage);
        return false;
      }
      
      if (!response.body) {
        options.callbacks.onError('ReadableStream not supported');
        return false;
      }
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';
      
      const processStream = async () => {
        try {
          while (true) {
            const { done, value } = await reader.read();
            
            if (done) {
              options.callbacks.onDone();
              
              // Refresh the user's balance after successful API call
              try {
                const paymentsStore = getPaymentsStore();
                paymentsStore.fetchBalance(false); // silent refresh
              } catch (err) {
                console.warn('Failed to refresh balance after streaming:', err);
              }
              
              break;
            }
            
            // Decode the chunk and add to buffer
            buffer += decoder.decode(value, { stream: true });
            
            // Process any complete Server-Sent Events
            const lines = buffer.split('\n\n');
            buffer = lines.pop() || ''; // Keep the last incomplete chunk in the buffer
            
            for (const line of lines) {
              if (line.trim() === '') continue;
              if (!line.startsWith('data: ')) continue;
              
              const data = line.substring(6); // Remove 'data: ' prefix
              
              try {
                const parsed = JSON.parse(data);
                
                if (parsed.event === 'content' && parsed.data) {
                  options.callbacks.onContent(parsed.data);
                } else if (parsed.event === 'error' && parsed.data) {
                  // Enhanced error handling for improved UX
                  let errorMsg = parsed.data;
                  
                  // Check for specific error types
                  if (parsed.data.includes('insufficient credit') || parsed.data.includes('need more credit')) {
                    // Credit-related errors
                    const amountMatch = parsed.data.match(/\$?([0-9.]+)/);
                    if (amountMatch) {
                      errorMsg = `Insufficient credits: You need $${amountMatch[1]} more to use ${modelId}. Please add more credits.`;
                    }
                  }
                  
                  options.callbacks.onError(errorMsg);
                  return false;
                } else if (parsed.event === 'conversation_id' && parsed.data) {
                  localStorage.setItem(`chat_conversation_${projectId}`, parsed.data);
                  if (options.callbacks.onConversationId) {
                    options.callbacks.onConversationId(parsed.data);
                  }
                } else if (parsed.event === 'done') {
                  options.callbacks.onDone();
                  
                  // Refresh the user's balance after successful API call
                  try {
                    const paymentsStore = getPaymentsStore();
                    paymentsStore.fetchBalance(false); // silent refresh
                  } catch (err) {
                    console.warn('Failed to refresh balance after streaming:', err);
                  }
                  
                  return true;
                }
              } catch (e) {
                console.error('Error parsing SSE data:', e, data);
                options.callbacks.onError(`Error parsing server response: ${e instanceof Error ? e.message : String(e)}`);
              }
            }
          }
          return true;
        } catch (error) {
          console.error('Error reading stream:', error);
          options.callbacks.onError(error instanceof Error ? error.message : String(error));
          return false;
        }
      };
      
      return await processStream();
    } catch (error) {
      // Handle errors and provide details to the callback
      const errorMessage = this.formatError(error);
      options.callbacks.onError(errorMessage);
      return false;
    }
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
