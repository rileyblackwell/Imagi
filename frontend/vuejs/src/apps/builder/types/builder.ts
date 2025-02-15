import type { EditorLanguage } from '@/shared/types/editor'

export interface ProjectType {
  id: string | number;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface AIModel {
  id: string;
  name: string;
  description?: string;
  costPerRequest?: number;
  disabled?: boolean;
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

export const DEFAULT_AI_MODELS: AIModel[] = [
  {
    id: 'claude-3-sonnet',
    name: 'Claude 3.5 Sonnet',
    description: 'Balanced model for most tasks',
    costPerRequest: 0.03
  },
  {
    id: 'gpt-4',
    name: 'GPT-4',
    description: 'Most capable model for complex tasks',
    costPerRequest: 0.04
  },
  {
    id: 'gpt-4-mini',
    name: 'GPT-4 Mini',
    description: 'Faster, more cost-effective option',
    costPerRequest: 0.01
  }
];
