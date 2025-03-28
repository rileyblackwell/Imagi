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
}

/**
 * Code Generation Response
 */
export interface CodeGenerationResponse {
  success: boolean;
  code: string;
  response: string;
  messages: any[];
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
  'claude-3-7-sonnet-20250219': {
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
};

// List of standard models
export const AI_MODELS: AIModel[] = [
  {
    id: 'claude-3-7-sonnet-20250219',
    name: 'Claude 3.7 Sonnet',
    provider: 'anthropic',
    type: 'anthropic',
    context_window: 200000,
    features: ['chat', 'code', 'analysis'],
    default: true,
    description: 'Anthropic | High-performance model for complex tasks',
    capabilities: ['code_generation', 'chat', 'analysis'],
    maxTokens: 200000,
    costPerRequest: 0.04
  },
  {
    id: 'gpt-4o',
    name: 'GPT-4o',
    provider: 'openai',
    type: 'openai',
    context_window: 128000,
    features: ['chat', 'code', 'analysis'],
    description: 'OpenAI | Powerful reasoning and creative capability',
    capabilities: ['code_generation', 'chat', 'analysis'],
    maxTokens: 128000,
    costPerRequest: 0.04
  },
  {
    id: 'gpt-4o-mini',
    name: 'GPT-4o Mini',
    provider: 'openai',
    type: 'openai',
    context_window: 128000,
    features: ['chat', 'code', 'analysis'],
    description: 'OpenAI | Fast and cost-effective performance',
    capabilities: ['code_generation', 'chat', 'analysis'],
    maxTokens: 128000,
    costPerRequest: 0.005
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
}

export interface AIGenerationResponse {
  code?: string;
  response?: string;
  messages?: AIMessage[];
  success: boolean;
  error?: string;
} 