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
  provider: 'openai' | 'anthropic' | 'google' | 'local'
  context_window: number
  features: ('chat' | 'code' | 'analysis')[]
  default?: boolean
  description: string
  costPerRequest: number
  capabilities?: string[]
  maxTokens?: number
  type?: 'openai' | 'anthropic'
}

export interface ProjectFile {
  path: string
  type: EditorLanguage
  content?: string
  lastModified?: string
}

export interface CodeGenerationResponse {
  success: boolean
  code: string
  response: string
  messages: any[]
}

export type BuilderMode = 'build' | 'chat'

export type EditorMode = 'split' | 'editor' | 'preview'

export interface UndoResponse {
  success: boolean
  message: string
  details?: any
}

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
