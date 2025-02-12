import type { EditorLanguage } from '@/shared/types/editor'

export interface AIModel {
  id: string
  name: string
  description?: string
  costPerRequest: number
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
