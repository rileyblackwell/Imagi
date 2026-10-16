// Types used in stores
import type { ProjectFile } from './components'
import type { AIModel, AgentInstance, CheckInDto, ProjectMemory, ReasoningEffort } from './services'

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
  /** Queue cards put off with "Later", in the order they were put off — they
   *  wait at the back of the queue. This tab only. */
  deferredCheckIns: number[];
  /** The model and effort new threads start on — the workspace settings,
   *  saved on the coordinator so the server dispatches with them. Opus 5.5
   *  on Medium unless the user picks otherwise. */
  threadModelId: string;
  threadEffort: ReasoningEffort;
  /** The project's shared memory, its recent changes and threads' notes
   *  waiting to land; null until loaded. */
  memory: ProjectMemory | null;
  /** The memory version the user last saw (per project, this browser), so
   *  the book icon can say when something new was saved. */
  memorySeenVersion: number;
  /** The memory view is open: refresh it on every poll tick. */
  memoryViewing: boolean;
}
