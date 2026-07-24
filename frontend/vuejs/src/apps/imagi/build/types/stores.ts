// Types used in stores
import type { ProjectFile } from './components'
import type { AIModel, AgentInstance, CheckInDto } from './services'

/**
 * Agent store state interface
 */
export interface AgentState {
  projectId: string | null;
  availableModels: AIModel[];
  instances: AgentInstance[];
  activeInstanceId: string | null;
  /** The subagent whose transcript the Subagents pane is drilled into, if
   *  any. Separate from activeInstanceId on purpose: reading a subagent's
   *  thread must never move the thread the user is talking in. */
  openedSubagentId: string | null;
  files: ProjectFile[];
  unsavedChanges: boolean;
  error: string | null;
  instancesLoading: boolean;
  /** Pending check-ins from background tasks, oldest first — the main
   *  thread's processing queue. */
  checkIns: CheckInDto[];
}
