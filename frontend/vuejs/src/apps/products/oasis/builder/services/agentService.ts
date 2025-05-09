import api from './api'
import type { 
  CodeGenerationResponse, 
  AIModel, 
  ChatPayload,
  ChatResponse,
  GenerateStylesheetOptions,
  CodeGenerationRequest,
  VersionControlResponse
} from '../types/services'
import { usePaymentsStore } from '@/apps/payments/store'
import { FileService } from '@/apps/products/oasis/builder/services/fileService'
import { ModelsService } from '@/apps/products/oasis/builder/services/modelsService'
import axios from 'axios'

// Create a custom API instance with longer timeout
const longTimeoutApi = axios.create({
  baseURL: api.defaults.baseURL,
  timeout: 90000, // 90 seconds timeout
  headers: api.defaults.headers
})

function getPaymentsStore() {
  // Get the payments store using function to avoid SSR issues
  return usePaymentsStore()
}

/**
 * Service for handling agent workspace and AI-related API calls
 */
export const AgentService = {
  // AI interaction methods - using Agents API
  async generateCode(projectId: string, data: CodeGenerationRequest): Promise<CodeGenerationResponse> {
    if (!data.model) {
      throw new Error('AI model must be selected')
    }

    // Now data.model is guaranteed to be a string (not null)
    const modelId: string = data.model;
    
    // Check rate limits before making request
    await ModelsService.checkRateLimit(modelId)

    // Validate prompt length against model context window
    const config = ModelsService.getConfig({ id: modelId } as AIModel)
    const estimatedTokens = ModelsService.estimateTokens(data.prompt)
    
    if (estimatedTokens > config.maxTokens) {
      throw new Error(`Prompt is too long for selected model. Please reduce length or choose a different model.`)
    }

    // Validate project ID
    if (!projectId) {
      throw new Error('Project ID is required')
    }

    try {
      // Ensure file_path has a value and proper format
      let filePath = data.file_path || 'templates/index.html';
      
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
          throw cssError;
        }
      }
      
      // For HTML files, ensure they're handled properly
      if (fileExtension === 'html') {
        // Add template-specific preparations
        if (!filePath.includes('/templates/') && !filePath.startsWith('templates/')) {
          // Ensure HTML files are in templates directory
          filePath = `templates/${filePath.replace(/^\//, '')}`;
        }
      }
      
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
          type: file.type || this.getFileType(file.path),
          content: file.content || ''
        }))
      }
      
      // Determine which endpoint to use based on file extension
      let endpoint;
      
      // Use the appropriate endpoint based on file type
      if (fileExtension === 'html') {
        endpoint = '/api/v1/agents/build/template/';
      } else if (fileExtension === 'css') {
        endpoint = '/api/v1/agents/build/stylesheet/';
      } else {
        // For other file types, use the chat API in build mode
        endpoint = '/api/v1/agents/chat/';
        payload.mode = 'build';
        payload.is_build_mode = true;
      }
      
      const response = await longTimeoutApi.post(endpoint, payload)
      
      // Store the conversation ID for future requests based on file type
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
        success: response.data.success !== false,
        code: response.data.code || response.data.response || "",
        response: response.data.response || response.data.code || "",
        messages: response.data.messages || [],
        single_message: response.data.single_message || false
      }
    } catch (error: any) {
      // Enhanced error logging
      console.error('Code generation API error:', error);
      
      // Get more detailed error information if it's an Axios error
      let errorDetails = '';
      if (error.response) {
        // Server responded with an error status
        console.error('Response error data:', error.response.data);
        console.error('Response status:', error.response.status);
        errorDetails = error.response.data?.error || error.response.data?.detail || 
                      (typeof error.response.data === 'string' ? error.response.data : '');
      }
      
      // Create a proper CodeGenerationResponse error object
      return {
        success: false,
        response: errorDetails || this.formatError(error),
        messages: [],
        error: errorDetails || this.formatError(error)
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
    await ModelsService.checkRateLimit(data.model)
    
    // Validate prompt length against model context window
    const config = ModelsService.getConfig({ id: data.model } as AIModel)
    const estimatedTokens = ModelsService.estimateTokens(data.prompt)
    
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
        mode: 'chat', // Always set to chat mode for chat processing
        is_build_mode: false, // Explicitly set to false for chat mode
        file: currentFile,
        project_files: files.map(file => ({
          path: file.path,
          type: file.type,
          content: file.content || ''
        }))
      }
      
      // Log the endpoint we're using
      console.log(`Using chat endpoint for processing message in chat mode`);
      
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
    } catch (error: any) {
      // Enhanced error logging
      console.error('Chat processing API error:', error);
      
      // Get more detailed error information if it's an Axios error
      let errorDetails = '';
      if (error.response) {
        // Server responded with an error status
        console.error('Response error data:', error.response.data);
        console.error('Response status:', error.response.status);
        errorDetails = error.response.data?.error || error.response.data?.detail || 
                      (typeof error.response.data === 'string' ? error.response.data : '');
      }
      
      // Create a proper ChatResponse error object
      return {
        response: errorDetails || this.formatError(error),
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
    return ModelsService.formatError(error);
  },
  
  async getVersionHistory(projectId: string): Promise<VersionControlResponse> {
    if (!projectId) {
      throw new Error('Project ID is required')
    }

    try {
      const response = await api.get(`/api/v1/builder/${projectId}/versions/`)
      
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
      const response = await api.post(`/api/v1/builder/${projectId}/versions/reset/`, {
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
      const response = await api.post(`/api/v1/builder/${projectId}/versions/`, {
        file_path: data.file_path || '',
        description: data.description || 'Project update'
      })
      
      return {
        success: response.data.success !== false,
        message: response.data.message || 'Version created successfully',
        commitHash: response.data.commit_hash || null,
        error: response.data.error || null
      }
    } catch (error: any) {
      console.error('Error creating version:', error)
      return {
        success: false,
        error: this.formatError(error)
      }
    }
  },

  async generateStylesheet(options: GenerateStylesheetOptions): Promise<any> {
    const { prompt, projectId, filePath, model, onProgress } = options;
    
    if (!prompt || !projectId || !filePath) {
      throw new Error('Prompt, project ID, and file path are required');
    }
    
    // Use the provided model or default to claude-3-7-sonnet-20250219
    const modelId = model || 'claude-3-7-sonnet-20250219';
    
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
      
      // Prepare request payload - use the correct field names matching the backend API
      const payload = {
        message: prompt,
        project_id: String(projectId),
        file_path: filePath,
        model: modelId,
        mode: 'build',
        is_build_mode: true,
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
      
      console.log('Stylesheet API request payload:', {
        endpoint: '/api/v1/agents/build/stylesheet/',
        projectId,
        filePath,
        modelId,
        promptLength: prompt.length,
        filesCount: files.length
      });
      
      // Make API call to the stylesheet-specific endpoint
      const response = await longTimeoutApi.post('/api/v1/agents/build/stylesheet/', payload);
      
      // Log the response structure for debugging
      console.log('Stylesheet API response structure:', {
        status: response.status,
        hasData: !!response.data,
        hasCode: !!response.data?.code,
        hasResponse: !!response.data?.response,
        dataKeys: response.data ? Object.keys(response.data) : []
      });
      
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
      
      // Check if we have actual content in the response
      const responseContent = response.data.code || response.data.response || '';
      if (!responseContent.trim()) {
        console.warn('Stylesheet API returned empty content');
      }
      
      // Return the response in a consistent format matching generateCode
      return {
        success: response.data.success !== false,
        response: response.data.code || response.data.response || '',
        code: response.data.code || response.data.response || '',
        messages: response.data.messages || [],
        single_message: response.data.single_message || false
      };
    } catch (error: any) {
      console.error('Stylesheet generation error:', error);
      
      // Enhanced error logging
      if (error.response) {
        console.error('API Error Response:', {
          status: error.response.status,
          statusText: error.response.statusText,
          data: error.response.data
        });
      }
      
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
  }
};

// Export ModelService for backward compatibility
export const ModelService = ModelsService;