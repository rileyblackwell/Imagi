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
 * Map of model configurations by model ID
 */
export const MODEL_CONFIGS: Record<string, ModelConfig> = {
  'gpt-6-luna': {
    maxTokens: 1000000,
    rateLimits: {
      tokensPerMinute: 60000,
      requestsPerMinute: 250
    },
    contextWindow: 1000000,
    capabilities: ['code_generation', 'chat', 'analysis']
  },
  'claude-opus-5-5': {
    maxTokens: 1000000,
    rateLimits: {
      tokensPerMinute: 60000,
      requestsPerMinute: 250
    },
    contextWindow: 1000000,
    capabilities: ['code_generation', 'chat', 'analysis']
  },
  'gpt-6-astra': {
    maxTokens: 1000000,
    rateLimits: {
      tokensPerMinute: 60000,
      requestsPerMinute: 250
    },
    contextWindow: 1000000,
    capabilities: ['code_generation', 'chat', 'analysis']
  }
};

// The three models on offer, one per tier and ordered faster → smarter —
// the order the composer's intelligence slider runs in. The lineup blends
// providers on purpose: each tier gets the best current fit, and it is
// revisited as better fits ship. Mirrors the backend registry, including
// prices (the provider's list price, no markup). Opus 5.5 carries the
// `default` flag: createInstance prefers it over list order.
export const AI_MODELS: AIModel[] = [
  {
    id: 'gpt-6-luna',
    name: 'GPT 6 Luna',
    provider: 'openai',
    type: 'openai',
    context_window: 1000000,
    features: ['chat', 'code', 'analysis'],
    default: false,
    description: 'OpenAI | GPT 6 Luna — fast and inexpensive, yet capable at most tasks',
    capabilities: ['code_generation', 'chat', 'analysis'],
    maxTokens: 1000000,
    inputPricePerMTokens: 0.1,
    outputPricePerMTokens: 0.5,
    api_version: 'responses'
  },
  {
    id: 'claude-opus-5-5',
    name: 'Claude Opus 5.5',
    provider: 'anthropic',
    type: 'anthropic',
    context_window: 1000000,
    features: ['chat', 'code', 'analysis'],
    default: true,
    description: 'Anthropic | Claude Opus 5.5 — thoughtful and dependable, with strong judgment on code and design',
    capabilities: ['code_generation', 'chat', 'analysis'],
    maxTokens: 1000000,
    inputPricePerMTokens: 4,
    outputPricePerMTokens: 20,
    api_version: 'messages'
  },
  {
    id: 'gpt-6-astra',
    name: 'GPT 6 Astra',
    provider: 'openai',
    type: 'openai',
    context_window: 1000000,
    features: ['chat', 'code', 'analysis'],
    default: false,
    description: 'OpenAI | GPT 6 Astra — frontier intelligence for the hardest work',
    capabilities: ['code_generation', 'chat', 'analysis'],
    maxTokens: 1000000,
    inputPricePerMTokens: 10,
    outputPricePerMTokens: 50,
    api_version: 'responses'
  }
];

/** Models the platform used to offer, mapped to the current model for their
 *  tier. A stored conversation or an older tab can still carry one. Mirrors
 *  the backend's LEGACY_MODEL_ALIASES. */
export const LEGACY_MODEL_ALIASES: Record<string, string> = {
  'gpt-5.6-luna': 'gpt-6-luna',
  'gpt-5.6-terra': 'claude-opus-5-5',
  'gpt-5.6-sol': 'claude-opus-5-5',
};

/** The current id for a model: a retired id becomes its successor. */
export function canonicalModelId(modelId: string): string;
export function canonicalModelId(modelId: string | null | undefined): string | null;
export function canonicalModelId(modelId: string | null | undefined): string | null {
  if (!modelId) return null;
  return Object.prototype.hasOwnProperty.call(LEGACY_MODEL_ALIASES, modelId)
    ? LEGACY_MODEL_ALIASES[modelId]!
    : modelId;
}

/**
 * Reasoning effort levels — how much reasoning the model uses per request.
 */
// One reasoning-effort ladder for every model, ordered faster → smarter. The
// OpenAI SDK's ReasoningEffort literal is none / minimal / low / medium / high /
// xhigh, with nothing above xhigh: a 'max' rung was never real (the SDK rejects
// it, and the backend then silently sent the request with no reasoning effort
// at all). 'minimal' is left off so every model offers the same choices, and
// 'none' — no reasoning — is a different concept than "think less", not a
// point on this speed/intelligence ladder. Must stay in step with the
// backend's REASONING_EFFORT_CHOICES.
export type ReasoningEffort = 'low' | 'medium' | 'high' | 'xhigh';

export interface ReasoningEffortOption {
  id: ReasoningEffort;
  name: string;
  /** One short line the picker shows under the name. */
  description: string;
}

export const REASONING_EFFORTS: ReasoningEffortOption[] = [
  { id: 'low', name: 'Low', description: 'Quick answers for small edits' },
  { id: 'medium', name: 'Medium', description: 'The balanced default for everyday building' },
  { id: 'high', name: 'High', description: 'Deeper thinking for multi-step work' },
  { id: 'xhigh', name: 'Extra High', description: 'The most thorough, for the hardest tasks' },
];

export const DEFAULT_REASONING_EFFORT: ReasoningEffort = 'medium';

// Rungs the platform used to offer (or claimed to), mapped onto the ladder.
// A client tab from before the ladder was unified can still send them, and a
// selection persisted back then can still be restored from storage.
export const LEGACY_REASONING_EFFORT_ALIASES: Record<string, ReasoningEffort> = {
  minimal: 'low',
  max: 'xhigh',
};

/** The effort options a model accepts, ordered faster → smarter. Every model
 *  shares the one ladder; the model id is accepted so callers read the same
 *  either way, and so a per-model difference has one place to land if a
 *  provider ever introduces one. */
export function reasoningEffortsForModel(modelId?: string | null): ReasoningEffortOption[] {
  void modelId; // every model, known or not, gets the same ladder
  return REASONING_EFFORTS;
}

/** Re-seat an effort onto the ladder: an effort already on it passes through,
 *  a legacy alias ('minimal', 'max') lands on its nearest rung, and anything
 *  else — empty, unknown, or garbage from another session — falls back to the
 *  default. Takes a plain string because the value may come from storage or an
 *  older client rather than from typed code. */
export function clampEffortToModel(
  effort: string | null | undefined,
  modelId?: string | null
): ReasoningEffort {
  if (!effort) return DEFAULT_REASONING_EFFORT;
  const options = reasoningEffortsForModel(modelId);
  const onLadder = options.find(option => option.id === effort);
  if (onLadder) return onLadder.id;
  return Object.prototype.hasOwnProperty.call(LEGACY_REASONING_EFFORT_ALIASES, effort)
    ? LEGACY_REASONING_EFFORT_ALIASES[effort]!
    : DEFAULT_REASONING_EFFORT;
}

// Conversation / agent instance types

/** What role a conversation plays in the workspace (lead thread / task / plain chat). */
export type ConversationKind = 'chat' | 'lead' | 'task';

/** Review lifecycle for kind='task' conversations ('' for everything else).
 *  'input' = the subagent asked a question and is parked until it's answered. */
export type TaskReviewStatus =
  | ''
  | 'active'
  | 'input'
  | 'ready'
  /** Its run died (error, or a cap hit mid-stream): nothing merged, worktree kept */
  | 'failed'
  | 'accepted'
  | 'dismissed';

/** How a background task surfaces back into the main thread's queue. */
/** What a subagent put in the main thread's queue on its way out.
 *  'done' is finished work already applied to the project — a notice to read,
 *  never an approval to give; 'question' is the one thing a subagent needs
 *  back; 'ready' is one of several takes waiting to be picked between; 'error'
 *  is a run that died. */
export type CheckInKind = 'done' | 'ready' | 'question' | 'error';

/** One entry in the main thread's processing queue. */
export interface CheckInDto {
  id: number;
  kind: CheckInKind;
  /** Question text, completion summary, or error message */
  body: string;
  status: 'pending' | 'resolved';
  created_at: string;
  resolved_at: string | null;
  project_id: number | null;
  lead_id: number | null;
  /** Enough of the checking-in task to render and act on the card */
  task: {
    id: number;
    title: string;
    /** The job in the user's own language — the name its card goes by */
    goal: string;
    kind: ConversationKind;
    review_status: TaskReviewStatus;
    variant_group: string;
    has_worktree: boolean;
    is_running: boolean;
  };
}

/** One background task staged by the lead agent's dispatch_task tool. The
 *  client fires its run; the brief is also persisted server-side. */
export interface DispatchedTaskDto {
  conversation_id: number;
  title: string;
  brief: string;
  /** The same job in the user's language, for the main thread's card */
  goal: string;
  /** What the subagent is about to do, in the user's language — the card's
   *  body while it works (three to five sentences from the lead) */
  overview: string;
  variant_group: string;
  parent: number;
  model_name: string;
  /** The lead asked for work a subagent is already doing: the server returned
   *  that existing task instead of staging a new one, so it is linked on the
   *  reply but its run is NOT started again. */
  already_running?: boolean;
}

/** A transcript's link to a subagent the lead kicked off during that reply —
 *  just enough to render the card and jump to the task's thread. */
export interface DispatchedTaskRef {
  conversationId: number;
  title: string;
}

export interface ConversationDto {
  id: number;
  title: string;
  model_name: string;
  project_id: number | null;
  kind: ConversationKind;
  /** Lead conversation this task was dispatched from */
  parent: number | null;
  review_status: TaskReviewStatus;
  /** Groups best-of-N sibling tasks spawned from one prompt */
  variant_group: string;
  /** True while this task has an unmerged worktree to review */
  has_worktree: boolean;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
  last_message_preview: string;
  /** The last assistant message, whole (generously capped server-side): a
   *  finished task's summary of its changes, or the question it stopped on.
   *  The dispatch card renders this in full — the preview above is for list
   *  rows and may cut the summary short. */
  last_assistant_summary?: string;
  /** What a task was asked to do, in the user's language (the lead's goal, or
   *  a trimmed brief for a task without one). Empty for other kinds. */
  brief?: string;
  /** What a task is about to do, in the user's language — the lead's overview
   *  at dispatch. The dispatch card's body while the run is live. */
  overview?: string;
  /** True while a run is active server-side (staleness-guarded to 10 min) */
  is_running: boolean;
  /** Tokens used across the conversation; null when never captured (unknown, not free) */
  total_tokens: number | null;
  /** A dispatched task's brief, waiting for its run to fire (cleared server-side
   *  when the run starts). Empty for everything else. */
  queued_prompt?: string;
}

export interface AgentInstance {
  id: string;                      // local UUID
  conversationId: number | null;   // backend AgentConversation id
  title: string;
  kind: ConversationKind;
  /** conversationId of the lead thread this task was dispatched from */
  parentId: number | null;
  reviewStatus: TaskReviewStatus;
  variantGroup: string;
  hasWorktree: boolean;
  /** Conversation-wide token total; null when never captured (unknown, not free) */
  totalTokens: number | null;
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
  /** The task's closing words, whole: its summary of the changes when it
   *  finished, or the question it stopped to ask. The dispatch card renders
   *  it in full; lastMessagePreview is the clipped list-row version. */
  lastAssistantSummary: string;
  /** What this task was asked to do, in the user's language — the dispatch
   *  card in the main thread shows it for the whole life of the task. */
  brief: string;
  /** What this task is doing, in the user's language — the dispatch card's
   *  body while the run is live; the sign-off takes over once it lands. */
  overview: string;
  messagesLoaded: boolean;
  /** Client-only: a run finished while this instance was not active */
  hasUnread?: boolean;
  /** Client-only: one prompt submitted mid-run, auto-sent when the run ends
   *  (unless the user explicitly stopped it). A second submit replaces it. */
  queuedPrompt?: string | null;
  /** A dispatched brief this task has not started running yet. Cleared when
   *  the client fires the run (the backend clears its own copy then too). */
  pendingBrief?: string | null;
}

/**
 * One entry in the agent's live activity feed (a tool call surfaced to the UI)
 */
export type AgentActivityStep = { name: string; label: string };

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
  /** Subagents the lead kicked off during this reply — rendered as links
   *  into their threads so the work is one click away from the main thread */
  dispatchedTasks?: DispatchedTaskRef[];
  /** Run usage, when the backend reported it (absent means unknown, never free) */
  usage?: { costUsd?: number; inputTokens?: number; outputTokens?: number };
  /** Backend AgentMessage id, once known (hydration or the start event) */
  dbId?: number;
  /**
   * Commit hash of the project state this user message started from.
   * Present only on user messages; powers the inline restore-checkpoint
   * control (conversation and files rewind together).
   */
  checkpoint?: string;
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
  /** Background tasks the lead agent staged during this run (dispatch_task) */
  dispatched_tasks?: DispatchedTaskDto[];
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