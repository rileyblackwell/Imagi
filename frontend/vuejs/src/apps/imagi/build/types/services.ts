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
  inputPricePerMTokens?: number;
  outputPricePerMTokens?: number;
  capabilities?: string[];
  maxTokens?: number;
  type?: 'openai' | 'anthropic';
  backend_model?: string;
  api_version?: 'chat' | 'messages' | 'responses'; // Different API versions: chat = OpenAI chat completions, messages = Anthropic messages, responses = OpenAI responses
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
  'gpt-5.6-sol': {
    maxTokens: 128000,
    rateLimits: {
      tokensPerMinute: 60000,
      requestsPerMinute: 250
    },
    contextWindow: 128000,
    capabilities: ['code_generation', 'chat', 'analysis']
  },
  'gpt-5.6-terra': {
    maxTokens: 128000,
    rateLimits: {
      tokensPerMinute: 60000,
      requestsPerMinute: 250
    },
    contextWindow: 128000,
    capabilities: ['code_generation', 'chat', 'analysis']
  },
  'gpt-5.6-luna': {
    maxTokens: 128000,
    rateLimits: {
      tokensPerMinute: 60000,
      requestsPerMinute: 250
    },
    contextWindow: 128000,
    capabilities: ['code_generation', 'chat', 'analysis']
  }
};

// List of standard models — the GPT 5.6 suite (Sol, Terra, Luna)
export const AI_MODELS: AIModel[] = [
  {
    id: 'gpt-5.6-sol',
    name: 'GPT 5.6 Sol',
    provider: 'openai',
    type: 'openai',
    context_window: 128000,
    features: ['chat', 'code', 'analysis'],
    description: 'OpenAI | GPT 5.6 Sol — flagship model for the most demanding building tasks',
    capabilities: ['code_generation', 'chat', 'analysis'],
    maxTokens: 128000,
    inputPricePerMTokens: 6,
    outputPricePerMTokens: 30,
    api_version: 'responses'
  },
  {
    id: 'gpt-5.6-terra',
    name: 'GPT 5.6 Terra',
    provider: 'openai',
    type: 'openai',
    context_window: 128000,
    features: ['chat', 'code', 'analysis'],
    description: 'OpenAI | GPT 5.6 Terra — balanced model for everyday chat and building assistance',
    capabilities: ['code_generation', 'chat', 'analysis'],
    maxTokens: 128000,
    inputPricePerMTokens: 3,
    outputPricePerMTokens: 15,
    api_version: 'responses'
  },
  {
    id: 'gpt-5.6-luna',
    name: 'GPT 5.6 Luna',
    provider: 'openai',
    type: 'openai',
    context_window: 128000,
    features: ['chat', 'code', 'analysis'],
    description: 'OpenAI | GPT 5.6 Luna — light, fast and economical model for quick tasks',
    capabilities: ['code_generation', 'chat', 'analysis'],
    maxTokens: 128000,
    inputPricePerMTokens: 1,
    outputPricePerMTokens: 5,
    api_version: 'responses'
  }
];

/**
 * Reasoning effort levels — how much reasoning the model uses per request.
 */
export type ReasoningEffort = 'low' | 'medium' | 'high';

export interface ReasoningEffortOption {
  id: ReasoningEffort;
  name: string;
}

export const REASONING_EFFORTS: ReasoningEffortOption[] = [
  { id: 'low', name: 'Low' },
  { id: 'medium', name: 'Medium' },
  { id: 'high', name: 'High' },
];

export const DEFAULT_REASONING_EFFORT: ReasoningEffort = 'medium';

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

// Conversation / agent instance types
export interface ConversationDto {
  id: number;
  title: string;
  model_name: string;
  project_id: number | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
  last_message_preview: string;
  /** True while a run is active server-side (staleness-guarded to 10 min) */
  is_running: boolean;
}

export interface AgentInstance {
  id: string;                      // local UUID
  conversationId: number | null;   // backend AgentConversation id
  title: string;
  selectedModelId: string | null;
  selectedEffort: ReasoningEffort;
  selectedFile: any | null;
  conversation: AIMessage[];
  isProcessing: boolean;
  /** What the running agent is doing right now ("Thinking…", "Editing project
   *  files…"). Transient — empty while text is streaming or when idle. */
  statusText: string;
  archivedAt: string | null;
  updatedAt: string;
  lastMessagePreview: string;
  messagesLoaded: boolean;
  /** Client-only: a run finished while this instance was not active */
  hasUnread?: boolean;
  /** Client-only: one prompt submitted mid-run, auto-sent when the run ends
   *  (unless the user explicitly stopped it). A second submit replaces it. */
  queuedPrompt?: string | null;
}

/**
 * One entry in the agent's live activity feed (a tool call surfaced to the UI)
 */
export type AgentActivityStep = { name: string; label: string; detail?: string };

// AI-specific response types
export interface AIMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string | number;
  code?: string;
  id?: string;
  isStreaming?: boolean;  // Flag for streaming message
  isTyping?: boolean;     // Flag for typing animation
  /** The agent's working-plan snapshot attached to this reply */
  plan?: AgentPlanStep[];
  /** Tool activity recorded while the agent produced this reply */
  activity?: AgentActivityStep[];
  /** Project files the agent changed during this reply */
  filesChanged?: string[];
  /** What this reply cost, when the backend reported run usage */
  usage?: { costUsd?: number };
}

export interface AIGenerationResponse {
  code?: string;
  response?: string;
  messages?: AIMessage[];
  success: boolean;
  error?: string;
}

/**
 * One step of the agent's working plan, maintained via its update_plan tool
 */
export interface AgentPlanStep {
  step: string;
  status: 'pending' | 'in_progress' | 'completed';
}

/**
 * Response from the Imagi agent (a single agent that chats + edits files)
 */
export interface AgentResponse {
  response: string;
  conversation_id?: string;
  files_changed?: string[];
  /** Names of the tools the agent called during the run, in order */
  tool_calls?: string[];
  /** The agent's working plan for multi-step tasks */
  plan?: AgentPlanStep[];
  /** Token usage for the run; omitted when the backend could not track it */
  usage?: { input_tokens?: number; output_tokens?: number; cost_usd?: number };
  single_message?: boolean;
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