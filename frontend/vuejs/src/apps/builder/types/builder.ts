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
