// Types used in stores
import type { BuilderMode, ProjectFile } from './components'
import type { AIModel, AIMessage } from './services'

/**
 * Agent store state interface
 */
export interface AgentState {
  projectId: string | null;
  mode: BuilderMode;
  selectedModelId: string | null;
  availableModels: AIModel[];
  conversation: AIMessage[];
  selectedFile: ProjectFile | null;
  files: ProjectFile[];
  unsavedChanges: boolean;
  isProcessing: boolean;
  error: string | null;
}

/**
 * Builder state interface
 */
export interface BuilderState {
  projectId: string | null;
  mode: BuilderMode;
  selectedModelId: string | null;
  availableModels: AIModel[];
  conversation: AIMessage[];
  selectedFile: ProjectFile | null;
  unsavedChanges: boolean;
  isProcessing: boolean;
  error: string | null;
} 