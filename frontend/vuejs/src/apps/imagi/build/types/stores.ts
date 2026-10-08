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
  /** The thread the Threads pane is drilled into, if any. Separate from
   *  activeInstanceId on purpose: opening a thread must never move the
   *  coordinator chat the user is talking in. */
  openedThreadId: string | null;
  files: ProjectFile[];
  error: string | null;
  instancesLoading: boolean;
  /** Pending check-ins from background tasks, oldest first — the main
   *  thread's processing queue. */
  checkIns: CheckInDto[];
  /** The check-in queue has been read from the server at least once, so
   *  anything that appears in it from now on is news. */
  checkInsLoaded: boolean;
}
