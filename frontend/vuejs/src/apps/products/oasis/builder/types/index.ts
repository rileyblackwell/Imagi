export * from './builder'  // Export everything from builder.ts

// Import shared EditorLanguage type to avoid conflicts
import type { EditorLanguage as SharedEditorLanguage } from '@/shared/types/editor'

export interface Project {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
  status: ProjectStatus;
}

export type ProjectStatus = 'active' | 'draft' | 'archived';

// Remove duplicate ProjectType interface since it's now in builder.ts

export interface ProjectListItemProps {
  project: Project;
}

export interface StatusClasses {
  [key: string]: string;
  active: string;
  draft: string;
  archived: string;
}

export type BuilderMode = 'chat' | 'build';

// API Response Types
export interface APIResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

/**
 * Represents a message in the AI chat conversation
 */
export interface AIMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  code?: string;
  timestamp: string | number;
  id?: string;
}

export interface CodeGenerationResponse {
  code?: string;
  response?: string;
  messages?: AIMessage[];
  success: boolean;
  error?: string;
}

// Builder Types
export type EditorMode = 'split' | 'editor' | 'preview';
// Re-export the shared EditorLanguage instead of redefining
export type EditorLanguage = SharedEditorLanguage;

export interface ProjectFile {
  id: string;
  name: string;
  path: string;
  type: EditorLanguage;
  content?: string;
  lastModified: string;
  size?: number;
  isDirectory?: boolean;
  children?: ProjectFile[];
}

export interface UndoResponse {
  success: boolean;
  message: string;
  changes?: {
    file: string;
    content: string;
  }[];
  details?: {
    removed_user_message?: string;
    removed_assistant_message?: string;
    [key: string]: any;
  };
}

/**
 * AI Model definition
 */
export interface AIModel {
  id: string;
  name: string;
  description?: string;
  capabilities?: string[];
  isDefault?: boolean;
}
