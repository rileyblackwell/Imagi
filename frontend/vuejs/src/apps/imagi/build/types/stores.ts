// Types used in stores
import type { ProjectFile } from './components'
import type { AIModel, AgentInstance } from './services'

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
