// Types used in stores
import type { BuilderMode, ProjectFile } from './components'
import type { AIModel, AIMessage, AgentInstance } from './services'

/**
 * Agent store state interface
 */
export interface AgentState {
  projectId: string | null;
  availableModels: AIModel[];
  instances: AgentInstance[];
  activeInstanceId: string | null;
  files: ProjectFile[];
  unsavedChanges: boolean;
  error: string | null;
  instancesLoading: boolean;
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