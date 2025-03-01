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
    id: 'claude-3-5-sonnet-20241022',
    name: 'Claude 3.5 Sonnet',
    provider: 'anthropic',
    type: 'anthropic',
    description: 'Anthropic\'s most capable model, best for complex tasks and creative work.',
    capabilities: ['code_generation', 'chat', 'analysis'],
    maxTokens: 200000,
    costPerRequest: 0.03
  },
  {
    id: 'gpt-4o',
    name: 'GPT-4o',
    provider: 'openai',
    type: 'openai',
    description: 'OpenAI\'s most capable model, excellent for complex reasoning and creative tasks.',
    capabilities: ['code_generation', 'chat', 'analysis'],
    maxTokens: 128000,
    costPerRequest: 0.04
  },
  {
    id: 'gpt-4o-mini',
    name: 'GPT-4o Mini',
    provider: 'openai',
    type: 'openai',
    description: 'A more cost-effective version of GPT-4o, good for simpler tasks.',
    capabilities: ['code_generation', 'chat', 'analysis'],
    maxTokens: 128000,
    costPerRequest: 0.01
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
