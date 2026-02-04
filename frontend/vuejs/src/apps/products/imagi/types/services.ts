/**
 * Model configuration interface
 */
export interface ModelConfig {
  maxTokens: number;
  rateLimits: {
    tokensPerMinute: number;
    requestsPerMinute: number;
  };
  contextWindow: number;
  capabilities: string[];
}

/**
 * AI Model definition
 */
export interface AIModel {
  id: string;
  name: string;
  provider: 'openai' | 'anthropic' | 'google' | 'local';
  context_window?: number;
  features?: ('chat' | 'code' | 'analysis')[];
  default?: boolean;
  description?: string;
  costPerRequest?: number;
  capabilities?: string[];
  maxTokens?: number;
  type?: 'openai' | 'anthropic';
  backend_model?: string;
  api_version?: 'chat' | 'messages' | 'responses'; // Different API versions: chat = OpenAI chat completions, messages = Anthropic messages, responses = OpenAI responses
}

/**
 * Response from code generation API
 */
export interface CodeGenerationResponse {
  success: boolean;
  code?: string;
  response: string;
  messages: any[];
  error?: string;
  single_message?: boolean;
}

/**
 * Undo Response
 */
export interface UndoResponse {
  success: boolean;
  message: string;
  details?: any;
}

/**
 * Map of model configurations by model ID
 */
export const MODEL_CONFIGS: Record<string, ModelConfig> = {
  'gpt-5.2': {
    maxTokens: 128000,
    rateLimits: {
      tokensPerMinute: 60000,
      requestsPerMinute: 250
    },
    contextWindow: 128000,
    capabilities: ['code_generation', 'chat', 'analysis']
  }
};

// List of standard models
export const AI_MODELS: AIModel[] = [
  {
    id: 'gpt-5.2',
    name: 'GPT 5.2',
    provider: 'openai',
    type: 'openai',
    context_window: 128000,
    features: ['chat', 'code', 'analysis'],
    description: 'OpenAI | GPT 5.2 for chat and building assistance',
    capabilities: ['code_generation', 'chat', 'analysis'],
    maxTokens: 128000,
    costPerRequest: 0.04,
    api_version: 'responses'
  }
];

// Types for API responses
export interface APIErrorResponse {
  error?: string;
  message?: string;
  detail?: string;
}

export interface APIPagination {
  count: number;
  next: string | null;
  previous: string | null;
}

export interface APIListResponse<T> {
  data: T[];
  pagination?: APIPagination;
}

export interface APIDetailResponse<T> {
  data: T;
  message?: string;
}

export interface APIResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

// AI-specific response types
export interface AIMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string | number;
  code?: string;
  id?: string;
  isStreaming?: boolean;  // Flag for streaming message
  isTyping?: boolean;     // Flag for typing animation
}

export interface AIGenerationResponse {
  code?: string;
  response?: string;
  messages?: AIMessage[];
  success: boolean;
  error?: string;
}

/**
 * Chat payload for agent service
 */
export interface ChatPayload {
  message: string;
  model: string;
  project_id: string;
  conversation_id?: string;
  mode?: string;
  is_build_mode?: boolean;
  current_file?: any;
}

/**
 * Chat Processing Payload with additional file properties
 */
export interface ChatProcessingPayload {
  message: string;
  model: string;
  project_id: string;
  conversation_id?: string;
  mode: string;
  is_build_mode?: boolean;
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
}

/**
 * Chat response interface
 */
export interface ChatResponse {
  response: string;
  messages: any[];
  conversation_id?: string;
  single_message?: boolean;
}

/**
 * Generate stylesheet options
 */
export interface GenerateStylesheetOptions {
  prompt: string;
  projectId: string;
  filePath: string;
  model?: string;
  conversationId?: string;
  onProgress?: (progress: { status: string; percent: number }) => void;
}

/**
 * Code generation request data
 */
export interface CodeGenerationRequest {
  prompt: string;
  mode: string;
  model: string | null;
  file_path?: string;
}

// Add the VersionControlResponse interface
export interface VersionControlResponse {
  success: boolean;
  message?: string;
  versions?: Array<{
    hash: string;
    message: string;
    author: string;
    date: string;
    relative_date: string;
  }>;
  commitHash?: string | null;
  error?: string | null;
} 