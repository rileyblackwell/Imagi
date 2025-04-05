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
import { FileService } from '@/apps/products/oasis/builder/services/fileService'
import { notify } from '@/shared/utils/notifications'

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

    // Validate project ID
    if (!projectId) {
      throw new Error('Project ID is required')
    }

    try {
      // Show in-progress message
      const { notify } = await import('@/shared/utils');
      notify({ type: 'info', message: 'Generating code and updating file...' });
      
      // Get conversation ID from localStorage
      const storedConversationId = localStorage.getItem(`agent_conversation_${projectId}`)
      
      // Get all project files
      const files = await FileService.getProjectFiles(projectId);
      
      // Ensure file_path has a value and proper format
      let filePath = data.file_path || 'templates/index.html';
      
      // For HTML files, make sure they are in the templates directory
      if (filePath.endsWith('.html') && !filePath.startsWith('templates/')) {
        filePath = `templates/${filePath.replace(/^\//, '')}`;
      }
      
      // Prepare request payload with all required fields
      const payload = {
        message: data.prompt,
        model: modelId,
        project_id: String(projectId), // Ensure project_id is a string
        file_path: filePath,
        mode: data.mode || 'build', // Default to build mode if not specified
        conversation_id: storedConversationId || undefined,
        project_files: files.map(file => ({
          path: file.path,
          type: file.type,
          content: file.content || ''
        }))
      }
      
      console.log('Sending template request with payload:', {
        message_length: payload.message.length,
        model: payload.model,
        project_id: payload.project_id,
        file_path: payload.file_path,
        mode: payload.mode,
        conversation_id: payload.conversation_id ? 'defined' : 'undefined',
        project_files_count: payload.project_files.length
      });
      
      // Use the build_template endpoint from agents/api
      const response = await api.post('/api/v1/agents/build/template/', payload)
      
      // Store the conversation ID for future requests
      if (response.data.conversation_id) {
        localStorage.setItem(`agent_conversation_${projectId}`, response.data.conversation_id)
      }
      
      // Show success notification
      if (response.data.success) {
        if (response.data.warning) {
          // Success but with warnings
          notify({ 
            type: 'warning', 
            message: `Generated code with warning: ${response.data.warning}`
          });
        } else {
          // Complete success
          notify({ 
            type: 'success', 
            message: `Successfully updated file: ${payload.file_path}`
          });
        }
        
        // Refresh file list to show updated file
        setTimeout(async () => {
          try {
            // Force refresh by getting fresh file list
            await FileService.getProjectFiles(projectId);
          } catch (err) {
            console.warn('Error refreshing file list:', err);
          }
        }, 500);
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
    } catch (error: any) {
      // Show error notification
      const { notify } = await import('@/shared/utils');
      notify({ type: 'error', message: `Error generating code: ${error.message || 'Unknown error'}` });
      
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
    
    // Get all project files
    const files = await FileService.getProjectFiles(projectId);
    
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
      project_files?: Array<{
        path: string;
        type: string;
        content: string;
      }>;
    } = {
      message: data.prompt,
      model: data.model,
      project_id: String(projectId),
      conversation_id: storedConversationId || undefined,
      mode: data.mode || 'chat',
      project_files: files.map(file => ({
        path: file.path,
        type: file.type,
        content: file.content || ''
      }))
    };
    
    // Add current file if available
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
        
        // Log the detailed error for debugging
        console.warn('Chat API 400 Bad Request details:', {
          error: errorDetail,
          data: error.response.data,
          request: {
            model: payload.model,
            project_id: payload.project_id,
            has_conversation_id: !!payload.conversation_id,
            has_current_file: !!payload.current_file
          }
        });
        
        // Try to provide more specific error messages for known issues
        if (errorDetail.includes('Insufficient credits')) {
          throw new Error(`You don't have enough credits: ${errorDetail}`);
        } else if (errorDetail.includes('model')) {
          throw new Error(`Model error: ${errorDetail}`);
        } else {
          throw new Error(`API Error: ${errorDetail}`);
        }
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

  /**
   * Generates a CSS stylesheet based on a prompt
   * 
   * This method sends a request to the stylesheet agent API to generate a CSS 
   * stylesheet based on user input.
   * 
   * @param options - Object containing request options 
   * @returns A Promise that resolves with the API response
   */
  async generateStylesheet({
    prompt,
    projectId,
    filePath,
    model = 'claude-3-7-sonnet-20250219',
    conversationId,
    onProgress
  }: {
    prompt: string;
    projectId: string;
    filePath: string;
    model?: string;
    conversationId?: string;
    onProgress?: (progress: { status: string; percent: number }) => void;
  }): Promise<any> {
    try {
      // Notify user that we're generating CSS
      notify({
        type: 'info',
        message: 'Please wait while we generate your stylesheet...',
        duration: 10000, // Longer duration since generation takes time
      });
      
      // Get conversation ID from localStorage if available
      const storedConversationId = conversationId || localStorage.getItem(`stylesheet_conversation_${projectId}_${filePath}`) || undefined;
      
      // Start progress tracking
      if (onProgress) {
        onProgress({ status: 'Starting stylesheet generation', percent: 5 });
      }
      
      // Get all project files to provide context to the stylesheet agent
      const files = await FileService.getProjectFiles(projectId);
      
      // Map files to the format expected by the API
      const projectFiles = files.map((file) => ({
        path: file.path,
        type: this.getFileType(file.path),
        content: file.content,
      }));
      
      // Update progress
      if (onProgress) {
        onProgress({ status: 'Processing project files', percent: 20 });
      }
      
      // Log the request details
      console.log(`Stylesheet request: prompt length=${prompt.length}, model=${model}, projectId=${projectId}, filePath=${filePath}, files=${projectFiles.length}`);
      
      // Send the request to the stylesheet agent API with increased timeout
      const response = await api.post('/api/v1/agents/build/stylesheet/', {
        message: prompt,
        model: model,
        project_id: projectId,
        file_path: filePath,
        conversation_id: storedConversationId,
        project_files: projectFiles,
      }, {
        timeout: 120000, // Increase timeout to 2 minutes
        validateStatus: (status) => status < 500, // Accept any status code below 500
      });
      
      // Update progress
      if (onProgress) {
        onProgress({ status: 'Processing response', percent: 60 });
      }
      
      // If the stylesheet agent returned a conversation ID, store it for future requests
      if (response.data.conversation_id) {
        localStorage.setItem(`stylesheet_conversation_${projectId}_${filePath}`, response.data.conversation_id);
      }
      
      // Handle the response
      if (response.data.success) {
        // Update progress
        if (onProgress) {
          onProgress({ status: 'Stylesheet generated successfully', percent: 100 });
        }
        
        // Show success notification 
        notify({
          type: 'success',
          message: 'Your CSS stylesheet has been updated successfully.',
        });
        
        // Refresh files
        setTimeout(async () => {
          try {
            // Force refresh by getting fresh file list
            await FileService.getProjectFiles(projectId);
          } catch (err) {
            console.warn('Error refreshing file list:', err);
          }
        }, 500);
        
        // Add code property to response for Apply Changes button functionality
        if (response.data.response) {
          response.data.code = response.data.response;
        }
        
        return response.data;
      } else {
        // Show error notification
        notify({
          type: 'error',
          message: response.data.error || 'An error occurred while generating your stylesheet.',
        });
        
        return response.data;
      }
    } catch (error: any) {
      console.error('Error generating stylesheet:', error);
      
      // Show error notification
      notify({
        type: 'error',
        message: error.message || 'An error occurred while generating your stylesheet.',
      });
      
      // End progress tracking on error
      if (onProgress) {
        onProgress({ status: 'Error occurred', percent: 100 });
      }
      
      return {
        success: false,
        error: error.message || 'An unknown error occurred',
      };
    }
  },
  
  /**
   * Get the file type based on file extension
   */
  getFileType(filePath: string): string {
    const extension = filePath.split('.').pop()?.toLowerCase();
    
    switch (extension) {
      case 'html':
      case 'htm':
        return 'html';
      case 'css':
        return 'css';
      case 'js':
        return 'javascript';
      case 'ts':
        return 'typescript';
      case 'json':
        return 'json';
      case 'vue':
        return 'vue';
      case 'jsx':
      case 'tsx':
        return 'react';
      case 'py':
        return 'python';
      default:
        return 'text';
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