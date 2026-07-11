// Types used in composables
import type { ProjectFile } from './components'

/**
 * Options for generateCode function
 */
export interface GenerateCodeOptions {
  prompt: string;
  file: ProjectFile;
  projectId: string;
  modelId: string;
  mode?: string;
}

/**
 * Options for creating a new file
 */
export interface CreateFileOptions {
  name: string;
  type: string;
  content?: string;
  projectId: string;
  path?: string;
}

/**
 * Options for applying generated code
 */
export interface ApplyCodeOptions {
  code: string;
  file: ProjectFile;
  projectId: string;
}

/**
 * Chat message interface
 */
export interface Message {
  id: string;
  role: string;
  content: string;
  timestamp: string;
  isStreaming?: boolean;
}

/**
 * Chat conversation interface
 */
export interface Conversation {
  id: string;
  messages: Message[];
}

/**
 * Confirmation dialog options
 */
export interface ConfirmOptions {
  title?: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  type?: 'info' | 'warning' | 'danger' | 'success';
} 