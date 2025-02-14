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
  costPerRequest: number;
  maxTokens?: number;
  type?: 'chat' | 'completion';
  capabilities?: string[];
  disabled?: boolean;  // Add disabled property
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
    costPerRequest: 0.03,
    maxTokens: 200000,
    type: 'chat',
    capabilities: ['code', 'analysis', 'chat']
  },
  {
    id: 'gpt-4o',
    name: 'GPT-4o',
    description: 'Advanced reasoning and code generation',
    costPerRequest: 0.05,
    maxTokens: 128000,
    type: 'completion',
    capabilities: ['code', 'analysis']
  },
  {
    id: 'gpt-4o-mini',
    name: 'GPT-4o-mini',
    description: 'Faster, cost-effective option',
    costPerRequest: 0.01,
    maxTokens: 64000,
    type: 'completion',
    capabilities: ['code']
  }
];
