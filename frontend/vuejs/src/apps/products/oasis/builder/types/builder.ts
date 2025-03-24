import type { EditorLanguage } from '@/shared/types/editor'
import type { AIMessage } from './api'

export interface ProjectType {
  id: string | number;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface AIModel {
  id: string
  name: string
  provider?: 'openai' | 'anthropic'
  type?: 'openai' | 'anthropic'
  description: string
  capabilities: string[]
  maxTokens: number
  costPerRequest: number
  disabled?: boolean
}

export interface ProjectFile {
  path: string
  type: EditorLanguage
  content: string
  lastModified?: string
}

export interface CodeGenerationResponse {
  code?: string;
  response?: string;
  messages?: Array<{
    role: 'user' | 'assistant';
    content: string;
  }>;
  success: boolean;
}

export type BuilderMode = 'chat' | 'build'
export type EditorMode = 'split' | 'editor' | 'preview'

export const AI_MODELS: AIModel[] = [
  {
    id: 'claude-3-7-sonnet-20250219',
    name: 'Claude 3.7 Sonnet',
    provider: 'anthropic',
    type: 'anthropic',
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
    description: 'OpenAI | Fast and cost-effective performance',
    capabilities: ['code_generation', 'chat', 'analysis'],
    maxTokens: 128000,
    costPerRequest: 0.005
  }
]

export interface BuilderState {
  projectId: string | null
  mode: BuilderMode
  selectedModelId: string | null
  availableModels: AIModel[]
  conversation: AIMessage[]
  selectedFile: ProjectFile | null
  unsavedChanges: boolean
  isProcessing: boolean
  error: string | null
}

// Re-export types from other files
export type { APIResponse } from './index'
export type { ProjectData } from './project'
export type { UndoResponse } from './index'
