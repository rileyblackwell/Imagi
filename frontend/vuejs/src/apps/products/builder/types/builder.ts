import type { EditorLanguage } from '@/shared/types/editor'

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
  description: string
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
  code: string
  message?: string
}

export type BuilderMode = 'chat' | 'build'
export type EditorMode = 'split' | 'editor' | 'preview'

export const AI_MODELS: AIModel[] = [
  {
    id: 'claude-3.5-sonnet',
    name: 'Claude 3.5 Sonnet',
    description: 'Anthropic\'s most capable model, best for complex tasks and creative work.',
    costPerRequest: 0.03
  },
  {
    id: 'gpt-4',
    name: 'GPT-4',
    description: 'OpenAI\'s most capable model, excellent for complex reasoning and creative tasks.',
    costPerRequest: 0.04
  },
  {
    id: 'gpt-4-mini',
    name: 'GPT-4 Mini',
    description: 'A more cost-effective version of GPT-4, good for simpler tasks.',
    costPerRequest: 0.01
  }
]
