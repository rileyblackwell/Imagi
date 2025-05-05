import api from './api'
import type { 
  CodeGenerationResponse, 
  AIModel, 
  UndoResponse,
  ModelConfig,
  ChatPayload,
  ChatResponse,
  GenerateStylesheetOptions,
  CodeGenerationRequest
} from '../types/services'
import { AI_MODELS, MODEL_CONFIGS } from '../types/services'
import { usePaymentsStore } from '@/apps/payments/store'
import { FileService } from '@/apps/products/oasis/builder/services/fileService'
import axios from 'axios'

// Create a custom API instance with longer timeout
const longTimeoutApi = axios.create({
  baseURL: api.defaults.baseURL,
  timeout: 90000, // 90 seconds timeout
  headers: api.defaults.headers
})

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
  async generateCode(projectId: string, data: CodeGenerationRequest): Promise<CodeGenerationResponse> {
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
      
      // Ensure file_path has a value and proper format
      let filePath = data.file_path || 'templates/index.html';
      
      // For HTML files, make sure they are in the templates directory
      if (filePath.endsWith('.html') && !filePath.startsWith('templates/')) {
        filePath = `templates/${filePath.replace(/^\//, '')}`;
      }
      
      // Determine file type from extension
      const fileExtension = filePath.split('.').pop()?.toLowerCase() || '';
      
      // For CSS files, use the specialized stylesheet generation method
      if (fileExtension === 'css') {
        try {
          // Use the dedicated stylesheet generator
          const stylesheetResponse = await this.generateStylesheet({
            prompt: data.prompt,
            projectId: projectId,
            filePath: filePath,
            model: modelId,
            onProgress: (progress) => {
              // Progress callback
            }
          });
          
          // Return the stylesheet response in the expected format
          return {
            success: true,
            code: stylesheetResponse.response,
            response: stylesheetResponse.response,
            messages: stylesheetResponse.messages || [],
            single_message: stylesheetResponse.single_message || false
          };
        } catch (cssError) {
          notify({ type: 'error', message: `Error generating stylesheet: ${cssError instanceof Error ? cssError.message : 'Unknown error'}` });
          throw cssError;
        }
      }
      
      // For non-CSS files, continue with the standard approach
      // Get conversation ID from localStorage
      const storedConversationId = localStorage.getItem(`agent_conversation_${projectId}`)
      
      // Get all project files
      const files = await FileService.getProjectFiles(projectId);
      
      // Prepare request payload with all required fields
      const payload = {
        message: data.prompt,
        model: modelId,
        project_id: String(projectId), // Ensure project_id is a string
        file_path: filePath,
        mode: 'build', // Always set to build mode for code generation
        is_build_mode: true, // Explicitly flag this as build mode for backend
        conversation_id: storedConversationId || undefined,
        project_files: files.map(file => ({
          path: file.path,
          type: file.type,
          content: file.content || ''
        }))
      }
      
      // Determine which endpoint to use based on file extension
      let endpoint = '/api/v1/agents/build/template/';
      
      // Use the appropriate endpoint based on file type
      const response = await longTimeoutApi.post(endpoint, payload)
      
      // Store the conversation ID for future requests based on file type
      if (response.data.conversation_id) {
        localStorage.setItem(`agent_conversation_${projectId}`, response.data.conversation_id);
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
          // Clean success
          notify({ 
            type: 'success', 
            message: 'Code generated successfully!'
          });
        }
      }
      
      // Log credits usage if provided
      if (response.data.credits_used) {
        const paymentsStore = getPaymentsStore();
        if (paymentsStore) {
          // Track credit usage in a generic way - just refresh the balance
          paymentsStore.fetchBalance(false, true);
        }
      }
      
      return {
        success: response.data.success !== false,
        code: response.data.code || response.data.response || "",
        response: response.data.response || response.data.code || "",
        messages: response.data.messages || [],
        single_message: response.data.single_message || false
      }
    } catch (error) {
      // Show error notification
      const { notify } = await import('@/shared/utils');
      notify({ 
        type: 'error', 
        message: `Code generation failed: ${this.formatError(error)}`
      });
      
      // Create a proper CodeGenerationResponse error object
      return {
        success: false,
        response: this.formatError(error),
        messages: [],
        error: this.formatError(error)
      };
    }
  },

  async processChat(projectId: string, data: {
    prompt: string;
    model: string;
    mode?: string;
    is_build_mode?: boolean;
    file?: any;
  }): Promise<ChatResponse> {
    if (!data.prompt || !data.model) {
      throw new Error('Prompt and model are required')
    }
    
    if (!projectId) {
      throw new Error('Project ID is required')
    }
    
    // Check rate limits before making request
    await this.checkRateLimit(data.model)
    
    // Validate prompt length against model context window
    const config = this.getConfig({ id: data.model } as AIModel)
    const estimatedTokens = this.estimateTokens(data.prompt)
    
    if (estimatedTokens > config.maxTokens) {
      throw new Error(`Prompt is too long for selected model. Please reduce length or choose a different model.`)
    }
    
    try {
      // Get conversation ID from localStorage if exists
      const storedConversationId = localStorage.getItem(`agent_conversation_${projectId}`)
      
      // Get project files
      const files: Array<any> = [];
      try {
        files.push(...await FileService.getProjectFiles(projectId));
      } catch (fileError) {
        // Continue even if we can't get project files
      }
      
      // Prepare file info if provided
      let currentFile = null;
      if (data.file) {
        currentFile = {
          path: data.file.path,
          type: data.file.type || this.getFileType(data.file.path),
          content: data.file.content || ''
        }
      }
      
      // Prepare request payload
      const payload = {
        message: data.prompt,
        model: data.model,
        project_id: String(projectId),
        conversation_id: storedConversationId || undefined,
        mode: data.mode || 'chat',
        is_build_mode: data.is_build_mode === true,
        file: currentFile,
        project_files: files.map(file => ({
          path: file.path,
          type: file.type,
          content: file.content || ''
        }))
      }
      
      // API call
      const response = await api.post('/api/v1/agents/chat/', payload)
      
      // Store the conversation ID for future requests
      if (response.data.conversation_id) {
        localStorage.setItem(`agent_conversation_${projectId}`, response.data.conversation_id);
      }
      
      // Log credits usage if provided
      if (response.data.credits_used) {
        const paymentsStore = getPaymentsStore();
        if (paymentsStore) {
          // Track credit usage in a generic way - just refresh the balance
          paymentsStore.fetchBalance(false, true);
        }
      }
      
      return {
        response: response.data.response,
        messages: response.data.messages || [],
        conversation_id: response.data.conversation_id
      } as ChatResponse; // Cast to ensure TS is happy
    } catch (error) {
      // Create a proper ChatResponse error object
      return {
        response: this.formatError(error),
        messages: []
      };
    }
  },

  async processChatWithTypingEffect(
    payload: ChatPayload,
    onChunk: (chunk: string) => void,
    onError: (error: string) => void,
    onDone: () => void,
    onConversationId?: (id: string) => void
  ): Promise<void> {
    try {
      // Get auth token for SSE connection
      const token = this.getAuthToken();
      if (!token) {
        throw new Error('Authentication required');
      }
      
      // First make a regular request to get the full response
      const response = await this.processChat(
        payload.project_id,
        {
          prompt: payload.message,
          model: payload.model,
          mode: payload.mode || 'chat',
          is_build_mode: payload.is_build_mode === true,
          file: payload.current_file
        }
      );
      
      // Store conversation ID if provided and callback exists
      if ((response as any).conversation_id && onConversationId) {
        onConversationId((response as any).conversation_id);
      }
      
      // Simulate typing effect with the response
      await this.simulateTypingEffect(response.response, onChunk);
      
      // Signal completion
      onDone();
    } catch (error) {
      onError(this.formatError(error));
    }
  },
  
  async simulateTypingEffect(
    text: string, 
    onChunk: (chunk: string) => void
  ): Promise<void> {
    if (!text) return;
    
    const minDelay = 5;  // Minimum delay in milliseconds
    const maxDelay = 20; // Maximum delay in milliseconds
    
    // Helper to get a random delay between min and max
    const getRandomDelay = () => 
      Math.floor(Math.random() * (maxDelay - minDelay + 1)) + minDelay;
    
    // Split text into words
    const words = text.split(/(\s+)/);
    
    // Process each word with a small delay
    for (let i = 0; i < words.length; i++) {
      const word = words[i];
      onChunk(word);
      
      // Add a random delay between words
      await new Promise(resolve => setTimeout(resolve, getRandomDelay()));
    }
  },
  
  async processChatStream(
    payload: ChatPayload,
    onChunk: (chunk: string) => void,
    onError: (error: string) => void,
    onDone: () => void,
    onConversationId?: (id: string) => void
  ): Promise<void> {
    try {
      // For now, just use the typing effect simulation
      await this.processChatWithTypingEffect(
        payload,
        onChunk,
        onError,
        onDone,
        onConversationId
      );
    } catch (error) {
      onError(this.formatError(error));
    }
  },
  
  getAuthToken(): string | null {
    // Try to get token from localStorage first
    const token = localStorage.getItem('auth_token');
    
    if (token) {
      return token;
    }
    
    // If not in localStorage, try to get from cookie
    const cookies = document.cookie.split('; ').reduce((acc, cookie) => {
      const [key, value] = cookie.split('=');
      acc[key] = value;
      return acc;
    }, {} as Record<string, string>);
    
    return cookies['auth_token'] || null;
  },
  
  formatError(error: any): string {
    if (error instanceof Error) {
      // If it's a standard Error object
      return error.message;
    } else if (typeof error === 'string') {
      // If it's already a string
      return error;
    } else if (error && error.response && error.response.data) {
      // If it's an Axios error with a data payload
      const data = error.response.data;
      
      if (data.detail) {
        return data.detail;
      } else if (data.message) {
        return data.message;
      } else if (data.error) {
        return data.error;
      } else if (typeof data === 'string') {
        return data;
      } else {
        try {
          // Try to stringify the response data
          return JSON.stringify(data);
        } catch (e) {
          return 'Unknown error occurred';
        }
      }
    } else if (error && error.message) {
      // Object with message property
      return error.message;
    } else {
      try {
        // Try to stringify whatever we got
        return JSON.stringify(error);
      } catch (e) {
        return 'Unknown error occurred';
      }
    }
  },
  
  async clearConversation(projectId: string): Promise<void> {
    if (!projectId) {
      throw new Error('Project ID is required');
    }
    
    // Get the stored conversation ID
    const conversationId = localStorage.getItem(`agent_conversation_${projectId}`);
    
    if (!conversationId) {
      // If no conversation exists, nothing to clear
      return;
    }
    
    try {
      // Make API call to clear conversation history
      await api.post(`/api/v1/agents/conversation/${conversationId}/clear/`);
      
      // Remove the stored conversation ID
      localStorage.removeItem(`agent_conversation_${projectId}`);
    } catch (error) {
      // Handle errors
      const { notify } = await import('@/shared/utils');
      notify({
        type: 'error',
        message: `Failed to clear conversation: ${this.formatError(error)}`
      });
      
      throw error;
    }
  },

  async getAvailableModels(): Promise<AIModel[]> {
    try {
      // Try to get from API first
      const response = await api.get('/api/v1/agents/models/');
      
      if (response.data && Array.isArray(response.data.models)) {
        return response.data.models.map((model: any) => ({
          id: model.id,
          name: model.name,
          description: model.description || '',
          capabilities: model.capabilities || ['chat'],
          contextWindow: model.context_window || 4096,
          provider: model.provider || 'Unknown'
        }));
      }
    } catch (error) {
      // If API request fails, fall back to default models
    }
    
    // Fall back to defaults if API request failed or returned invalid data
    return this.getDefaultModels();
  },
  
  async undoAction(projectId: string, filePath?: string): Promise<UndoResponse> {
    if (!projectId) {
      throw new Error('Project ID is required');
    }
    
    try {
      const endpoint = filePath
        ? `/api/v1/agents/project/${projectId}/file/undo/?file_path=${encodeURIComponent(filePath)}`
        : `/api/v1/agents/project/${projectId}/undo/`;
      
      const response = await api.post(endpoint);
      
      return {
        success: true,
        message: response.data.message || 'Undo successful',
        details: {
          code: response.data.code || null,
          file_path: response.data.file_path || filePath
        }
      };
    } catch (error) {
      // Create a proper UndoResponse error object
      return {
        success: false,
        message: this.formatError(error),
        details: error
      };
    }
  },

  async generateStylesheet(options: GenerateStylesheetOptions): Promise<any> {
    const { prompt, projectId, filePath, model, onProgress } = options;
    
    if (!prompt || !projectId || !filePath) {
      throw new Error('Prompt, project ID, and file path are required');
    }
    
    // Use the provided model or default to claude-3-haiku
    const modelId = model || 'claude-3-haiku';
    
    try {
      // Get conversation ID if available
      const conversationId = localStorage.getItem(`agent_conversation_${projectId}`);
      
      // Get project files
      const files = await FileService.getProjectFiles(projectId);
      
      // Update progress if callback provided
      if (onProgress) {
        onProgress({ status: 'Getting project files', percent: 10 });
      }
      
      // Find the current file content if it exists
      const currentFile = files.find(file => file.path === filePath);
      const currentContent = currentFile?.content || '';
      
      // Prepare request payload
      const payload = {
        prompt,
        project_id: String(projectId),
        file_path: filePath,
        model: modelId,
        conversation_id: conversationId || undefined,
        current_content: currentContent,
        project_files: files.map(file => ({
          path: file.path,
          type: file.type || this.getFileType(file.path),
          content: file.content || ''
        }))
      };
      
      // Update progress
      if (onProgress) {
        onProgress({ status: 'Generating stylesheet', percent: 30 });
      }
      
      // Make API call
      const response = await longTimeoutApi.post('/api/v1/agents/build/stylesheet/', payload);
      
      // Store conversation ID for future requests
      if (response.data.conversation_id) {
        localStorage.setItem(`agent_conversation_${projectId}`, response.data.conversation_id);
      }
      
      // Update progress
      if (onProgress) {
        onProgress({ status: 'Processing response', percent: 90 });
      }
      
      // Handle credits tracking
      if (response.data.credits_used) {
        const paymentsStore = getPaymentsStore();
        if (paymentsStore) {
          // Track credit usage in a generic way - just refresh the balance
          paymentsStore.fetchBalance(false, true);
        }
      }
      
      // Final progress update
      if (onProgress) {
        onProgress({ status: 'Complete', percent: 100 });
      }
      
      // Return the response
      return {
        success: true,
        response: response.data.code || response.data.response || '',
        messages: response.data.messages || [],
        single_message: response.data.single_message || false
      };
    } catch (error) {
      // Handle errors
      const { notify } = await import('@/shared/utils');
      notify({
        type: 'error',
        message: `Failed to generate stylesheet: ${this.formatError(error)}`
      });
      
      throw error;
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
  
  async generatePreview(projectId: string): Promise<{ previewUrl: string }> {
    try {
      const response = await api.post(`/api/v1/projects/${projectId}/preview/`);
      return {
        previewUrl: response.data.preview_url
      };
    } catch (error) {
      throw new Error(`Failed to generate preview: ${this.formatError(error)}`);
    }
  },
  
  async deployProject(projectId: string, options: { environment: string }): Promise<{ deploymentUrl: string }> {
    try {
      const response = await api.post(`/api/v1/projects/${projectId}/deploy/`, options);
      return {
        deploymentUrl: response.data.deployment_url
      };
    } catch (error) {
      throw new Error(`Failed to deploy project: ${this.formatError(error)}`);
    }
  },
  
  async initializeProject(projectId: string): Promise<{ success: boolean }> {
    try {
      await api.post(`/api/v1/projects/${projectId}/initialize/`);
      return { success: true };
    } catch (error) {
      throw new Error(`Failed to initialize project: ${this.formatError(error)}`);
    }
  }
};

// Export ModelService for backward compatibility
export const ModelService = {
  getConfig: AgentService.getConfig,
  checkRateLimit: AgentService.checkRateLimit,
  canGenerateCode: AgentService.canGenerateCode,
  estimateTokens: AgentService.estimateTokens,
  getDefaultModels: AgentService.getDefaultModels
}