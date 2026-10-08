import { defineStore } from 'pinia'
import type {
  AIModel,
  AIMessage,
  AgentActivityStep,
  AgentInstance,
  AgentPlanStep,
  CheckInDto,
  ConversationDto,
  ConversationKind,
  DispatchedTaskDto,
  ReasoningEffort
} from '../types/services'
import { AI_MODELS, DEFAULT_REASONING_EFFORT, canonicalModelId, clampEffortToModel } from '../types/services'
import type { AgentState } from '../types/stores'
import type { ProjectFile } from '../types/components'
import { AgentService } from '../services/agentService'

const DEFAULT_MODEL_ID = 'claude-opus-5-5'

// The user's pick of model for new threads. Kept per browser, like the rest
// of the workspace's view settings; unset or unreadable falls back to Opus 5.5.
const THREAD_MODEL_KEY = 'imagi.threadModel'

/** A model id the lineup offers, re-seating a retired one; anything else is
 *  the default. */
function threadModelOrDefault(modelId: string | null | undefined): string {
  const id = canonicalModelId(modelId)
  return id && AI_MODELS.some(m => m.id === id) ? id : DEFAULT_MODEL_ID
}

function readThreadModelId(): string {
  try {
    return threadModelOrDefault(localStorage.getItem(THREAD_MODEL_KEY))
  } catch {
    return DEFAULT_MODEL_ID
  }
}

// The catalog's `default: true` entry wins over list order, so the effective
// default stays Opus 5.5 even if the served ordering changes.
function pickDefaultModelId(models: AIModel[]): string {
  return models.find(m => m.default)?.id ?? models[0]?.id ?? DEFAULT_MODEL_ID
}

// Live stream controllers keyed by instance id. Module scope and non-reactive
// on purpose: AbortController instances must never be wrapped in Pinia proxies.
const abortControllers = new Map<string, AbortController>()

// Instance ids whose current run was explicitly stopped by the user. Consulted
// (and cleared) when processing flips false: a queued prompt must not auto-send
// into a run the user just killed.
const userAbortedRuns = new Set<string>()

// Registered by the workspace so a queued prompt can be re-submitted through
// its normal handlePrompt path when the blocking run finishes.
let queuedPromptSender: ((instanceId: string, prompt: string) => void) | null = null

// Single poller for server-side runs restored without a live stream.
let resyncTimer: ReturnType<typeof setInterval> | null = null
const RESYNC_INTERVAL_MS = 5000

// Threads run on the server, which starts them itself; this tab only watches
// the ones it has room to show. A check-in poller runs whenever the workspace
// is open — the queue must fill even when the user is idle and no run is
// being watched.
let checkInTimer: ReturnType<typeof setInterval> | null = null
const CHECK_IN_INTERVAL_MS = 6000

// Conversation ids whose dispatched run this tab already fired. Module scope
// and non-reactive: a re-dispatch of the same task (stream backstop, a
// reload's pendingBrief sweep) must never start a second run.
const firedDispatches = new Set<number>()

// How many subagent runs this tab starts at once. Mirrors the backend's own
// ceiling (MAX_CONCURRENT_TASK_RUNS): dispatches past it wait their turn here
// instead of being fired and refused, and the backstop for a mismatch is the
// re-queue on a 429 — a refused subagent keeps its brief and starts when a
// slot frees, rather than being stranded mid-dispatch with nothing running.
const MAX_PARALLEL_TASK_RUNS = 5

// Conversation ids the backend refused a run for, and when they may try again.
// The two ceilings can legitimately disagree — the server counts a user's runs
// across every project, this tab only sees one — so a refusal must cost a
// pause. Without it, re-queue and retry chase each other as fast as the
// network allows.
const dispatchRetryAt = new Map<number, number>()
const DISPATCH_RETRY_MS = 6000

// Check-in ids this tab has already reacted to. Module scope and
// non-reactive: it is bookkeeping about what has been noticed, not state
// anything renders, and a pending card the user has not cleared must not
// re-trigger its side effects on every poll.
const adoptedCheckIns = new Set<number>()

// Threads whose conversation this tab is fetching to add to the list, so two
// check-ins from the same unknown thread do not add it twice.
const adoptingThreads = new Set<number>()

// Registered by the workspace: how a background task's run is shown (the
// same handlePrompt path, targeted at the task's instance, which watches the
// run the server started rather than starting one).
let taskRunner: ((instanceId: string, prompt: string) => void) | null = null

// What a subagent is told when the user asks it to try again after a run
// that died with its brief already consumed. The job itself is in its
// transcript (the brief is its opening message) and whatever it managed to
// change is still in its worktree, so it continues rather than starting over.
const TASK_RETRY_PROMPT =
  'Your previous run was cut off before you finished. Pick the job back up ' +
  'from where it stopped: check what you have already changed, finish what ' +
  'remains, and sign off as usual.'

// Registered by the workspace: a subagent's work just merged into the project,
// so whatever mirrors the project files (the tree, the preview) is now stale.
let taskAppliedHandler: (() => void) | null = null

// Subagent conversations whose merge this tab has already refreshed for. A
// finished run announces itself twice — the conversation flips to 'accepted'
// and a report lands in the main thread — and either can arrive first, so the
// refresh is claimed by conversation id rather than by whichever noticed.
// Cleared when that subagent starts a new run, which can merge again.
const refreshedForTask = new Set<number>()

function newLocalId(): string {
  return `inst-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

/** A dispatched brief as one status line. The server trims briefs the same
 *  way (_conversation_brief); this covers the window before the first DTO
 *  refresh, when the only copy of the brief is the one the dispatch carried. */
const BRIEF_LINE_LIMIT = 160
function briefLine(brief: string): string {
  return (brief || '')
    .split('\n')
    .map(line => line.replace(/^[#>*\-\s]+/, '').trim())
    .filter(Boolean)
    .join(' ')
    .slice(0, BRIEF_LINE_LIMIT)
}

function dtoToInstance(dto: ConversationDto, fallbackModelId: string | null): AgentInstance {
  return {
    id: newLocalId(),
    conversationId: dto.id,
    title: dto.title || '',
    kind: dto.kind || 'chat',
    parentId: dto.parent ?? null,
    reviewStatus: dto.review_status || '',
    variantGroup: dto.variant_group || '',
    hasWorktree: !!dto.has_worktree,
    // null means the tokens were never captured (unknown), never "0 tokens"
    totalTokens: typeof dto.total_tokens === 'number' ? dto.total_tokens : null,
    // A conversation stored on a retired model reopens on its successor.
    selectedModelId: canonicalModelId(dto.model_name) || fallbackModelId,
    selectedEffort: DEFAULT_REASONING_EFFORT,
    fastMode: !!dto.fast_mode,
    selectedFile: null,
    conversation: [],
    isProcessing: !!dto.is_running,
    statusText: dto.is_running ? 'Working…' : '',
    archivedAt: dto.archived_at,
    updatedAt: dto.updated_at,
    lastMessagePreview: dto.last_message_preview || '',
    lastAssistantSummary: dto.last_assistant_summary || '',
    brief: dto.brief || dto.queued_prompt || '',
    overview: dto.overview || '',
    messagesLoaded: false,
    hasUnread: false,
    queuedPrompt: null,
    pendingBrief: dto.queued_prompt || null,
  }
}

export const useAgentStore = defineStore('agent', {
  state: (): AgentState => ({
    projectId: null,
    availableModels: [],
    instances: [],
    activeInstanceId: null,
    openedThreadId: null,
    files: [],
    error: null,
    instancesLoading: false,
    checkIns: [],
    checkInsLoaded: false,
    threadModelId: readThreadModelId(),
  }),

  getters: {
    activeInstance(state): AgentInstance | null {
      if (!state.activeInstanceId) return null
      return state.instances.find(i => i.id === state.activeInstanceId) || null
    },

    /** Threads still able to run (not archived, not discarded) on a model
     *  other than the one new threads start on — what "switch all threads"
     *  would change. */
    threadsOffThreadModel(state): AgentInstance[] {
      return state.instances.filter(
        i => i.kind === 'task' && !i.archivedAt && i.reviewStatus !== 'dismissed' &&
          i.selectedModelId !== state.threadModelId
      )
    },

    /** The project's one pinned lead thread (ensured by loadInstances). */
    leadInstance(state): AgentInstance | null {
      return state.instances.find(i => i.kind === 'lead' && !i.archivedAt) || null
    },

    /** The subagent the Subagents pane is reading, or null when it is showing
     *  the list. */
    openedThread(state): AgentInstance | null {
      if (!state.openedThreadId) return null
      return state.instances.find(i => i.id === state.openedThreadId) || null
    },

    /** Every subagent whose work is not finished yet, newest first: running,
     *  parked on a question, stopped by a failed run, or done but not yet
     *  accepted/discarded. They are one list because they are one thing to
     *  the user — an agent still on the hook. What separates them is a status
     *  line, not a section. A failed task belongs here rather than in History:
     *  it still holds a worktree and still wants a decision. */
    activeAgentInstances(state): AgentInstance[] {
      return state.instances
        .filter(
          i => i.kind === 'task' && !i.archivedAt &&
            (i.reviewStatus === 'active' || i.reviewStatus === 'input' ||
              i.reviewStatus === 'ready' || i.reviewStatus === 'failed')
        )
        .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
    },

    /** How many subagents are actually working right now — what the main
     *  thread's Subagents switch badges itself with.
     *
     *  Deliberately not activeAgentInstances.length. That list also holds work
     *  that has finished and is waiting on you, which is a different thing with
     *  its own queue: counting it left the badge lit with a number that named
     *  nothing the user could act on from there. */
    workingAgentCount(): number {
      return this.activeAgentInstances.filter(i => i.isProcessing).length
    },

    /** Tasks the lead dispatched whose run has not started yet, oldest first.
     *
     *  Ordered by conversation id because that is the order they were
     *  dispatched in, and a subagent waiting for a slot should get it before
     *  one dispatched after it — the same first-in-first-out rule the main
     *  thread's queue follows on the way back.
     *
     *  Never a failed one. A dispatch whose run could not start still holds
     *  its brief, but it is the user's to retry: firing it again on every
     *  poll would turn one failure into a loop, and the card would never get
     *  to say what happened. */
    pendingDispatchInstances(state): AgentInstance[] {
      return state.instances
        .filter(
          i => i.kind === 'task' && !!i.pendingBrief && !i.isProcessing &&
            !i.archivedAt && i.reviewStatus !== 'failed'
        )
        .sort((a, b) => (a.conversationId ?? 0) - (b.conversationId ?? 0))
    },

    /** Subagent runs this tab has in flight right now. */
    runningTaskCount(state): number {
      return state.instances.filter(i => i.kind === 'task' && i.isProcessing).length
    },

    /** Threads that are working right now: a live run, or dispatched and
     *  about to start one. Newest first. */
    workingThreads(): AgentInstance[] {
      return this.activeAgentInstances.filter(
        i => i.isProcessing || i.reviewStatus === 'active'
      )
    },

    /** Threads waiting on the user: one asked a question, one of several
     *  takes to pick from, or a run that stopped before finishing. A thread
     *  with a live run is working, whatever it last asked. Newest first. */
    waitingThreads(): AgentInstance[] {
      return this.activeAgentInstances.filter(
        i => !i.isProcessing && i.reviewStatus !== 'active'
      )
    },

    /** Threads whose work is done — in the app, or discarded — and not
     *  archived. Newest first. */
    finishedThreads(state): AgentInstance[] {
      return state.instances
        .filter(
          i => i.kind === 'task' && !i.archivedAt && !i.isProcessing &&
            (i.reviewStatus === 'accepted' || i.reviewStatus === 'dismissed')
        )
        .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
    },

    /** Check-ins that ask the user for something. A 'done' card is news to
     *  read, not a request, so it never counts as waiting. */
    waitingCheckIns(state): CheckInDto[] {
      return state.checkIns.filter(c => c.kind !== 'done')
    },

    /** Archived threads, legacy plain chats and any duplicate live lead (a
     *  backend race can leave two): it matches no other section, so History
     *  is where it stays reachable instead of becoming an invisible orphan.
     *  The live lead is the coordinator's own chat and never appears here. */
    historyInstances(state): AgentInstance[] {
      const primaryLead =
        state.instances.find(i => i.kind === 'lead' && !i.archivedAt) || null
      return state.instances.filter(
        i =>
          !!i.archivedAt ||
          i.kind === 'chat' ||
          (i.kind === 'lead' && !i.archivedAt && i !== primaryLead)
      )
    },

    /** How many runs are live across all instances (lead + parallel tasks). */
    processingCount(state): number {
      return state.instances.filter(i => i.isProcessing).length
    },

  },

  actions: {
    setProjectId(id: string | null) {
      if (id !== this.projectId) this.checkInsLoaded = false
      this.projectId = id
    },

    setModels(models: AIModel[]) {
      this.availableModels = models
    },

    setError(error: string | null) {
      this.error = error
    },

    _findInstance(id: string): AgentInstance | undefined {
      return this.instances.find(i => i.id === id)
    },

    async loadInstances(projectId: string | number) {
      this.instancesLoading = true
      try {
        const dtos = await AgentService.listConversations(projectId)
        const fallback = pickDefaultModelId(this.availableModels)
        this.instances = dtos.map(d => dtoToInstance(d, fallback))
        // Local ids are regenerated above, so any drilled-into subagent id is
        // now stale — the pane falls back to its list.
        this.openedThreadId = null

        // Every project pins exactly one lead thread; the backend dedupes
        // lead creation, so racing tabs converge on the same conversation.
        if (!this.instances.some(i => i.kind === 'lead' && !i.archivedAt)) {
          await this.createInstance({ kind: 'lead', activate: false })
        }

        // Pick active: remembered id from localStorage, else the lead
        const remembered = localStorage.getItem(`activeAgentInstance_${projectId}`)
        const activeConvId: number | null = remembered ? Number(remembered) : null
        // Never a task: a subagent's thread is read in the Subagents pane, so
        // restoring one as the active (composer-bearing) thread would strand
        // the user in a thread they cannot type in.
        let picked = this.instances.find(
          i => i.conversationId === activeConvId && !i.archivedAt && i.kind !== 'task'
        )
        if (!picked) {
          picked = this.leadInstance
            || this.instances.find(i => !i.archivedAt)
            || this.instances[0]
        }
        if (picked) {
          this.activeInstanceId = picked.id
          await this.ensureMessagesLoaded(picked.id)
        }

        // Restored instances may have runs still executing server-side.
        this.resyncRunningInstances()
        // Background tasks report in whether or not anything is streaming
        // here, so the queue polls for as long as the workspace is open.
        void this.loadCheckIns()
        this.startCheckInPolling()
        // A dispatch whose run never fired (the tab closed between the lead
        // staging it and the run starting) is still staged server-side —
        // pick it up so no task is silently stranded.
        this.firePendingDispatches()
      } finally {
        this.instancesLoading = false
      }
    },

    // --- Check-in queue (the main thread's processing queue) ---

    /** Registered by the workspace: how a background task's run is started
     *  (its handlePrompt). Pass null on teardown. */
    setTaskRunner(runner: ((instanceId: string, prompt: string) => void) | null) {
      taskRunner = runner
    },

    /** Registered by the workspace: what to do when a subagent's work merges
     *  into the project (refresh the file tree and the preview, which are now
     *  showing the app as it was before). Pass null on teardown. */
    setTaskAppliedHandler(handler: (() => void) | null) {
      taskAppliedHandler = handler
    },

    async loadCheckIns() {
      if (!this.projectId) return
      try {
        this.checkIns = await AgentService.listCheckIns(this.projectId)
        this.checkInsLoaded = true
      } catch (e) {
        console.error('Failed to load check-ins', e)
        return
      }
      this.adoptSubagentOutcomes()
    },

    /**
     * Catch the workspace up on subagents that came back.
     *
     * The queue is the one signal that a background run ended: they finish in
     * their own time, in parallel, and a tab that is not streaming a given run
     * hears about it here first. Each new entry means that subagent's state on
     * the server has moved on from what this tab is showing, so its card in
     * the main thread — the same card the dispatch put there, which is where a
     * finish is reported — is refreshed to say so, in its own words.
     *
     * Once per check-in, ever. Entries sit in the queue until the user clears
     * them, and re-reacting to the same one on every poll would refetch a
     * conversation every six seconds for as long as the card is up. A task
     * that runs again files a new check-in, which is a new one to react to.
     */
    adoptSubagentOutcomes() {
      const lead = this.leadInstance
      for (const checkIn of this.checkIns) {
        if (adoptedCheckIns.has(checkIn.id)) continue
        adoptedCheckIns.add(checkIn.id)
        const instance = this.instances.find(i => i.conversationId === checkIn.task.id)
        // A thread this tab never saw dispatched (another tab, or one that
        // opened before it existed): bring it in so the Threads pane lists it.
        if (!instance) {
          void this.adoptThread(checkIn.task.id)
          if (lead && lead.id !== this.activeInstanceId) lead.hasUnread = true
          continue
        }
        // Mid-run means this tab is driving it and already has the truth;
        // matching review states mean the card is already current.
        if (
          instance && !instance.isProcessing &&
          instance.reviewStatus !== checkIn.task.review_status
        ) {
          void this.refreshInstanceFromServer(instance.id)
        }
        // A subagent arriving is worth a dot when the user is reading
        // something else.
        if (lead && lead.id !== this.activeInstanceId) lead.hasUnread = true
      }
    },

    /** Add one thread the server knows about and this tab does not. */
    async adoptThread(conversationId: number) {
      if (adoptingThreads.has(conversationId)) return
      adoptingThreads.add(conversationId)
      try {
        const dto = await AgentService.getConversation(conversationId)
        if (this.instances.some(i => i.conversationId === dto.id)) return
        this.instances.unshift(dtoToInstance(dto, pickDefaultModelId(this.availableModels)))
      } catch (e) {
        console.error('Failed to load thread', conversationId, e)
      } finally {
        adoptingThreads.delete(conversationId)
      }
    },

    startCheckInPolling() {
      this.stopCheckInPolling()
      checkInTimer = setInterval(() => {
        void this.loadCheckIns()
        // A subagent whose run the backend refused is waiting on a slot it
        // cannot see free (another project's runs count too), so its retry
        // rides this tick rather than a signal from this tab.
        this.firePendingDispatches()
      }, CHECK_IN_INTERVAL_MS)
    },

    stopCheckInPolling() {
      if (checkInTimer !== null) {
        clearInterval(checkInTimer)
        checkInTimer = null
      }
    },

    /** Drop a check-in from the local queue (the server-side resolve already
     *  happened, or is happening as a side effect of accept/dismiss/answer). */
    removeCheckIn(checkInId: number) {
      this.checkIns = this.checkIns.filter(c => c.id !== checkInId)
    },

    /** Clear one queue entry the user has simply dealt with. */
    async resolveCheckIn(checkInId: number) {
      this.removeCheckIn(checkInId)
      try {
        await AgentService.resolveCheckIn(checkInId)
      } catch (e) {
        console.error('Failed to resolve check-in', e)
        // The server still holds it; the next poll re-surfaces it rather
        // than silently losing the item.
        void this.loadCheckIns()
      }
    },

    /**
     * Answer a subagent's question from the main thread: the answer is sent
     * as the task's next message, which restarts it in the background (and
     * resolves its check-in server-side).
     */
    answerCheckIn(checkIn: CheckInDto, answer: string) {
      const text = answer.trim()
      if (!text) return
      const instance = this.instances.find(i => i.conversationId === checkIn.task.id)
      if (!instance) return
      this.removeCheckIn(checkIn.id)
      void this._sendFromUser(instance, text)
    },

    /**
     * The user steering a thread directly, from inside it. The message is
     * the thread's next turn, exactly as a follow-up the coordinator forwards
     * would be: queued behind a live run, otherwise started as soon as there
     * is a free slot. Starting a run re-opens the thread server-side and
     * supersedes whatever it last asked, so its waiting card goes now.
     *
     * Returns false when the thread cannot take a message: its work was
     * discarded (it no longer has a copy of the project to work in), or it
     * is archived.
     */
    steerThread(instanceId: string, text: string): boolean {
      const message = text.trim()
      const instance = this._findInstance(instanceId)
      if (!message || !instance || instance.kind !== 'task') return false
      if (instance.archivedAt || instance.reviewStatus === 'dismissed') return false
      void this._sendFromUser(instance, message)
      return true
    },

    /**
     * A message the user wrote for a thread goes to the server first: the
     * server stages it and starts the thread itself (now, or after its
     * current run), so it is acted on even if this tab closes a moment
     * later. Then this tab shows it and watches the run, as it would a
     * follow-up the coordinator forwarded.
     */
    async _sendFromUser(instance: AgentInstance, message: string) {
      if (instance.conversationId == null) return
      try {
        await AgentService.sendToThread(instance.conversationId, message)
      } catch (e) {
        console.error('Failed to send to thread', e)
        this.addMessageToInstance(instance.id, {
          role: 'assistant',
          content: "That message didn't reach this thread. Send it again.",
          timestamp: new Date().toISOString(),
          id: `system-error-${Date.now()}`
        })
        return
      }
      this._sendToThread(instance, message)
    },

    // --- Task dispatch (the lead agent's delegation tool) ---

    /**
     * The lead agent staged background tasks: adopt them into the instance
     * list and start their runs in parallel. Each edits its own worktree, so
     * they neither block each other nor the lead thread the user is in.
     *
     * Starting is deliberately left to firePendingDispatches: it holds every
     * staged brief on its instance and fires as many as there is room for,
     * oldest first, so a dispatch beyond the parallel-run ceiling waits its
     * turn instead of being fired and refused.
     */
    startDispatchedTasks(tasks: DispatchedTaskDto[]) {
      const fallback = pickDefaultModelId(this.availableModels)
      for (const task of tasks) {
        if (task.follow_up) {
          this.deliverFollowUp(task)
          continue
        }
        if (firedDispatches.has(task.conversation_id)) continue
        let instance = this.instances.find(i => i.conversationId === task.conversation_id)
        if (!instance) {
          instance = dtoToInstance(
            {
              id: task.conversation_id,
              title: task.title,
              model_name: task.model_name,
              project_id: null,
              kind: 'task',
              parent: task.parent,
              review_status: 'active',
              variant_group: task.variant_group,
              has_worktree: false,
              archived_at: null,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
              last_message_preview: '',
              last_assistant_summary: '',
              // What it is about to work on, straight from the dispatch —
              // the card reports it from the first frame, without waiting for
              // the conversation DTO the run end fetches.
              brief: task.goal || briefLine(task.brief),
              overview: task.overview || '',
              is_running: false,
              total_tokens: null,
            },
            fallback
          )
          // Nothing has been said in it yet, so there is nothing to fetch.
          instance.messagesLoaded = true
          this.instances.unshift(instance)
          // A new thread starts on the user's thread model, whatever the
          // coordinator that dispatched it runs on.
          if (instance.selectedModelId !== this.threadModelId) {
            this.setInstanceModel(instance.id, this.threadModelId)
          }
        }
        // The lead re-dispatched work this subagent already has: the server
        // handed back the running task rather than staging a new one, so it is
        // linked on the reply but must not be re-run underneath itself.
        if (task.already_running || instance.isProcessing) {
          firedDispatches.add(task.conversation_id)
          instance.pendingBrief = null
          continue
        }
        instance.pendingBrief = task.brief
      }
      this.firePendingDispatches()
    },

    /**
     * The lead forwarded a follow-up to a subagent it already has — a change
     * to its work, or the answer to its question — instead of starting a new
     * one. The message is that subagent's next turn: queued behind its current
     * run when it is mid-run, otherwise staged like a dispatch so it still
     * waits for a free slot. A message already waiting there is joined, not
     * replaced, so the subagent hears both — the server stages them the same
     * way. The stream already de-duplicates one run's events, so every
     * follow-up that reaches here is a new message.
     */
    deliverFollowUp(task: DispatchedTaskDto) {
      const instance = this.instances.find(i => i.conversationId === task.conversation_id)
      if (!instance || instance.kind !== 'task' || !task.brief) return
      this._sendToThread(instance, task.brief)
    },

    /** One message into a thread, from the coordinator or from the user
     *  steering it: its next turn, after the live run if there is one. */
    _sendToThread(instance: AgentInstance, message: string) {
      const conversationId = instance.conversationId
      if (conversationId == null) return
      const join = (waiting?: string | null) =>
        waiting ? `${waiting}\n\n${message}` : message
      if (instance.isProcessing) {
        this.queuePrompt(instance.id, join(instance.queuedPrompt))
        return
      }
      // The run's start re-opens it server-side and supersedes whatever it
      // last asked; mirror both now so its card reads "working" at once.
      this.removeCheckInsForTask(conversationId)
      instance.reviewStatus = 'active'
      instance.hasUnread = false
      firedDispatches.delete(conversationId)
      dispatchRetryAt.delete(conversationId)
      instance.pendingBrief = join(instance.pendingBrief)
      this.firePendingDispatches()
    },

    /**
     * Start staged subagent runs, oldest first, up to the parallel ceiling.
     *
     * Covers three arrivals at the same gate: a fresh dispatch, a dispatch
     * whose run never fired (the tab closed mid-flight, so the brief is still
     * staged server-side), and one the backend refused because every slot was
     * taken. All three are the same thing — a subagent with a brief and no
     * run — so they queue together and start in the order they were dispatched.
     */
    firePendingDispatches() {
      if (!taskRunner) return
      const send = taskRunner
      let room = MAX_PARALLEL_TASK_RUNS - this.runningTaskCount
      const now = Date.now()
      for (const instance of this.pendingDispatchInstances) {
        if (room <= 0) return
        const conversationId = instance.conversationId
        const brief = instance.pendingBrief
        if (conversationId == null || !brief) continue
        if (firedDispatches.has(conversationId)) continue
        // Refused a moment ago: let the slot it is waiting on actually free
        // before asking again.
        if ((dispatchRetryAt.get(conversationId) ?? 0) > now) continue
        dispatchRetryAt.delete(conversationId)
        firedDispatches.add(conversationId)
        instance.pendingBrief = null
        room -= 1
        const instanceId = instance.id
        // Deferred so the dispatching run's stream handler unwinds before
        // N more streams open.
        queueMicrotask(() => send(instanceId, brief))
      }
    },

    /**
     * Put a refused subagent run back in the queue.
     *
     * The backend turned this run away because the user already has the most
     * subagents it will run at once. Nothing is wrong and nothing is lost —
     * the prompt goes back on the instance and starts as soon as a slot frees,
     * which is what the user was promised when the work was dispatched.
     * Dropping it instead left a subagent sitting in the pane forever,
     * "working" on a run that was never accepted.
     */
    requeueDispatch(instanceId: string, prompt: string) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      if (instance.conversationId != null) {
        firedDispatches.delete(instance.conversationId)
        dispatchRetryAt.set(instance.conversationId, Date.now() + DISPATCH_RETRY_MS)
      }
      instance.pendingBrief = prompt
    },

    /**
     * A subagent's run ended without reaching its own ending: the stream was
     * aborted, the connection dropped, the request never got through. The
     * task fails — here and on the server — and says so. Left 'active' with
     * no run behind it, it read "starting" forever on a card the user could
     * do nothing about; failed, it reads as what it is and offers a retry.
     *
     * `unsentBrief` is the prompt when the run never started server-side (no
     * start event came back): the brief was not consumed, so it stays on the
     * instance for the retry to fire again. A run that did start has its
     * brief in its transcript, and a retry continues it with a follow-up.
     *
     * The server's word wins on what the task is now: it refuses to relabel
     * work that already finished, and a cancel from this tab may land after
     * the run reported itself elsewhere.
     */
    async failTaskRun(instanceId: string, reason: string, unsentBrief: string | null = null) {
      const instance = this._findInstance(instanceId)
      if (!instance || instance.kind !== 'task') return
      const conversationId = instance.conversationId
      if (conversationId != null) {
        firedDispatches.delete(conversationId)
        dispatchRetryAt.delete(conversationId)
      }
      if (unsentBrief) instance.pendingBrief = unsentBrief
      if (instance.reviewStatus === 'active') instance.reviewStatus = 'failed'
      if (conversationId == null) return
      try {
        const dto = await AgentService.cancelConversationRun(conversationId, reason)
        this._setTaskReviewStatus(instance, dto.review_status || '')
        instance.updatedAt = dto.updated_at
        instance.lastMessagePreview = dto.last_message_preview || ''
        instance.lastAssistantSummary = dto.last_assistant_summary || ''
        // The server filed the error in the queue; show it now rather than
        // on the next poll tick.
        void this.loadCheckIns()
      } catch (e) {
        console.error('Failed to report the stopped subagent run', e)
      }
    },

    /**
     * Run a failed subagent again — at the user's request, and only then.
     *
     * A dispatch whose run never started still holds its brief, so it fires
     * the way it would have the first time (and waits for a slot the same
     * way). One whose run died part-way has the job in its transcript and
     * its half-done edits in its worktree, so it is told to carry on rather
     * than sent the brief a second time. Either way the run's start flips it
     * to 'active' server-side and retires the error in the queue; the local
     * copy flips now so the card reads "starting" the moment it is pressed.
     */
    retryTask(conversationId: number) {
      const instance = this.instances.find(i => i.conversationId === conversationId)
      if (!instance || instance.kind !== 'task' || instance.isProcessing) return
      if (instance.reviewStatus !== 'failed') return
      // The brief it never started on is still staged on the server, which
      // does not stage a resend twice; the server starts the retry itself.
      const message = instance.pendingBrief || TASK_RETRY_PROMPT
      instance.pendingBrief = null
      void this._sendFromUser(instance, message)
    },

    // --- Run control (stop button / server-tracked runs) ---

    registerAbortController(instanceId: string, controller: AbortController) {
      abortControllers.set(instanceId, controller)
      userAbortedRuns.delete(instanceId) // fresh run, stale stop marks don't apply
    },

    /** Stop this instance's run. Aborts the live stream when this tab owns
     *  one; otherwise (restored after reload / opened elsewhere / crashed
     *  worker) releases the server-side run marker and clears local state so
     *  Stop is never a dead button. */
    abortInstanceRun(instanceId: string) {
      const controller = abortControllers.get(instanceId)
      if (controller) {
        abortControllers.delete(instanceId)
        userAbortedRuns.add(instanceId)
        controller.abort()
        // Closing the stream no longer stops the run (it outlives its
        // connection), so the Stop has to reach the server too. A thread's
        // stop is reported by failTaskRun, which carries the reason.
        const instance = this._findInstance(instanceId)
        if (instance && instance.kind !== 'task' && instance.conversationId != null) {
          AgentService.cancelConversationRun(instance.conversationId)
            .catch(e => console.error('Failed to stop the server-side run', e))
        }
        return
      }
      const instance = this._findInstance(instanceId)
      if (!instance?.isProcessing) return
      userAbortedRuns.add(instanceId)
      if (instance.conversationId != null) {
        // Best-effort: lifts the project's agent_busy guard. A run streaming
        // into another tab keeps executing there; if it is genuinely still
        // going, the next submit gets the backend's 409.
        AgentService.cancelConversationRun(instance.conversationId)
          .catch(e => console.error('Failed to release server-side run', e))
      }
      this.setInstanceProcessing(instanceId, false)
    },

    /**
     * Keep following a run whose stream closed before it ended.
     *
     * The run is not tied to the connection — it keeps going on the server
     * and finishes on its own — so the instance stays "working", without a
     * stream, and the resync poll picks up the finished transcript (and a
     * thread's outcome) when the server reports the run is over.
     */
    followRunOnServer(instanceId: string) {
      abortControllers.delete(instanceId)
      const instance = this._findInstance(instanceId)
      if (!instance) return
      instance.statusText = 'Working…'
      this.resyncRunningInstances()
    },

    /** Abort every live stream (e.g. before rebuilding the instance list,
     *  which would orphan in-flight runs on dead local ids). */
    abortAllRuns() {
      for (const instanceId of abortControllers.keys()) {
        userAbortedRuns.add(instanceId)
      }
      for (const controller of abortControllers.values()) {
        controller.abort()
      }
      abortControllers.clear()
    },

    // --- Queued prompts (one pending prompt per instance) ---

    /** Register how a queued prompt gets submitted (the workspace's
     *  handlePrompt). Pass null on teardown. */
    setQueuedPromptSender(sender: ((instanceId: string, prompt: string) => void) | null) {
      queuedPromptSender = sender
    },

    /** Hold one prompt to auto-send when this instance's run finishes.
     *  Submitting again while still running replaces it. */
    queuePrompt(instanceId: string, prompt: string) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      instance.queuedPrompt = prompt
    },

    clearQueuedPrompt(instanceId: string) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      instance.queuedPrompt = null
    },

    /**
     * Poll conversations that are running server-side but have no live stream
     * in this tab (restored after reload / opened elsewhere). When a run
     * finishes, refetch its messages and flag it unread if not active.
     */
    resyncRunningInstances() {
      if (resyncTimer !== null) {
        clearInterval(resyncTimer)
        resyncTimer = null
      }

      const restoredRunning = () => this.instances.filter(
        i => i.isProcessing && i.conversationId != null && !abortControllers.has(i.id)
      )
      if (restoredRunning().length === 0) return

      resyncTimer = setInterval(async () => {
        const running = restoredRunning()
        if (running.length === 0) {
          if (resyncTimer !== null) {
            clearInterval(resyncTimer)
            resyncTimer = null
          }
          return
        }
        await Promise.all(running.map(async (instance) => {
          try {
            const dto = await AgentService.getConversation(instance.conversationId!)
            if (dto.is_running) return
            // Re-check after the await: a local run may have started (and
            // registered its controller) while the fetch was in flight — its
            // fresh transcript must not be wiped from under it.
            if (!instance.isProcessing || abortControllers.has(instance.id)) return
            // Run finished on the server: pull the authoritative transcript.
            instance.messagesLoaded = false
            instance.conversation = []
            await this.ensureMessagesLoaded(instance.id)
            instance.updatedAt = dto.updated_at
            instance.lastMessagePreview = dto.last_message_preview || ''
            instance.lastAssistantSummary = dto.last_assistant_summary || ''
            if (dto.brief) instance.brief = dto.brief
            if (dto.overview) instance.overview = dto.overview
            // A finished task may now be ready for review — or have merged
            // itself into the project; sync the review-lifecycle fields the
            // run end changed server-side.
            this._setTaskReviewStatus(instance, dto.review_status || '')
            instance.hasWorktree = !!dto.has_worktree
            if (typeof dto.total_tokens === 'number') instance.totalTokens = dto.total_tokens
            this.setInstanceProcessing(instance.id, false)
            // The finished run filed its check-in; surface it now rather than
            // on the next tick.
            if (instance.kind === 'task') void this.loadCheckIns()
          } catch (e) {
            console.error('Failed to resync running conversation', instance.conversationId, e)
          }
        }))
      }, RESYNC_INTERVAL_MS)
    },

    async ensureMessagesLoaded(instanceId: string) {
      const instance = this._findInstance(instanceId)
      if (!instance || instance.messagesLoaded || !instance.conversationId) return
      try {
        const msgs = await AgentService.getConversationMessages(instance.conversationId)
        instance.conversation = msgs.map(m => ({
          role: m.role,
          content: m.content,
          timestamp: m.timestamp,
          id: `db-${m.id}`,
          // Persisted run telemetry, already hydrated by the service into
          // the same shapes the live stream writes.
          plan: m.plan,
          activity: m.activity,
          filesChanged: m.filesChanged,
          dispatchedTasks: m.dispatchedTasks,
          question: m.question,
          usage: m.usage,
          dbId: m.id,
          checkpoint: m.checkpoint,
        } as AIMessage))
        instance.messagesLoaded = true
      } catch (e) {
        console.error('Failed to load messages for conversation', instance.conversationId, e)
      }
    },

    async createInstance(opts: {
      modelId?: string
      kind?: ConversationKind
      /** conversationId of the lead thread (for kind='task') */
      parentId?: number | null
      /** Shared uuid grouping best-of-N sibling tasks */
      variantGroup?: string
      /** false leaves the current active instance in place (task dispatch) */
      activate?: boolean
    } = {}) {
      if (!this.projectId) return null
      const fallbackModel = opts.modelId || pickDefaultModelId(this.availableModels)
      const dto = await AgentService.createConversation(this.projectId, {
        modelName: fallbackModel,
        kind: opts.kind,
        parent: opts.parentId ?? undefined,
        variantGroup: opts.variantGroup,
      })
      // Lead creation is deduped server-side — the response may be a
      // conversation this store already tracks.
      const existing = this.instances.find(
        i => i.conversationId != null && i.conversationId === dto.id
      )
      if (existing) {
        if (opts.activate !== false) await this.switchInstance(existing.id)
        return existing
      }
      const instance = dtoToInstance(dto, fallbackModel)
      // A deduped lead may arrive with history; anything with a preview
      // still needs its messages fetched lazily.
      instance.messagesLoaded = !dto.last_message_preview
      this.instances.unshift(instance)
      if (opts.activate !== false) {
        this.activeInstanceId = instance.id
        if (this.projectId) {
          localStorage.setItem(
            `activeAgentInstance_${this.projectId}`,
            String(instance.conversationId ?? '')
          )
        }
      }
      return instance
    },

    /**
     * Read a subagent's thread inside the Subagents pane. Deliberately not
     * switchInstance: a subagent's thread is a record you look at, not one you
     * talk in, so opening it must leave the main thread — and the composer's
     * draft — exactly where they were. Pass null to go back to the list.
     */
    async openThread(instanceId: string | null) {
      this.openedThreadId = instanceId
      if (!instanceId) return
      const instance = this._findInstance(instanceId)
      if (!instance) return
      instance.hasUnread = false
      await this.ensureMessagesLoaded(instance.id)
    },

    async switchInstance(instanceId: string) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      this.activeInstanceId = instance.id
      instance.hasUnread = false
      if (this.projectId && instance.conversationId != null) {
        localStorage.setItem(
          `activeAgentInstance_${this.projectId}`,
          String(instance.conversationId)
        )
      }
      await this.ensureMessagesLoaded(instance.id)
    },

    /** Apply a title the backend already persisted (e.g. the AI auto-name from
     *  the first exchange). Local-only — no server write, since the row is
     *  already saved. Matched by conversationId because the stream reports the
     *  conversation, not the local instance id. */
    applyInstanceTitle(conversationId: number, title: string) {
      const trimmed = (title || '').trim()
      if (!trimmed) return
      const instance = this.instances.find(i => i.conversationId === conversationId)
      if (instance) instance.title = trimmed.slice(0, 120)
    },

    async renameInstance(instanceId: string, title: string) {
      const instance = this._findInstance(instanceId)
      if (!instance || !instance.conversationId) return
      const trimmed = title.trim().slice(0, 120)
      instance.title = trimmed
      try {
        await AgentService.updateConversation(instance.conversationId, { title: trimmed })
      } catch (e) {
        console.error('Failed to rename conversation:', e)
      }
    },

    async archiveInstance(instanceId: string) {
      const instance = this._findInstance(instanceId)
      if (!instance || !instance.conversationId) return
      try {
        const dto = await AgentService.updateConversation(instance.conversationId, { archived: true })
        instance.archivedAt = dto.archived_at
        // If the archived instance was active, fall back to the lead thread
        // (never auto-create plain chats; the lead is recreated on demand).
        if (this.activeInstanceId === instance.id) {
          const next = this.leadInstance
            || this.instances.find(i => !i.archivedAt && i.id !== instance.id)
          if (next) {
            await this.switchInstance(next.id)
          } else {
            await this.createInstance({ kind: 'lead' })
          }
        }
      } catch (e) {
        console.error('Failed to archive conversation:', e)
      }
    },

    async unarchiveInstance(instanceId: string) {
      const instance = this._findInstance(instanceId)
      if (!instance || !instance.conversationId) return
      try {
        const dto = await AgentService.updateConversation(instance.conversationId, { archived: false })
        instance.archivedAt = dto.archived_at
      } catch (e) {
        console.error('Failed to unarchive conversation:', e)
      }
    },

    /**
     * Re-pull one conversation's DTO and patch the instance in place.
     * Deliberately NOT loadInstances: rebuilding the whole list regenerates
     * local ids and aborts every live stream, which would orphan parallel
     * task runs still streaming into this tab.
     */
    async refreshInstanceFromServer(instanceId: string) {
      const instance = this._findInstance(instanceId)
      if (!instance || instance.conversationId == null) return
      try {
        const dto = await AgentService.getConversation(instance.conversationId)
        // A task's run end files its check-in server-side; pull the queue so
        // the main thread shows it without waiting for the next poll tick.
        if (dto.kind === 'task') void this.loadCheckIns()
        instance.title = dto.title || ''
        instance.kind = dto.kind || instance.kind
        instance.parentId = dto.parent ?? instance.parentId
        this._setTaskReviewStatus(instance, dto.review_status || '')
        instance.variantGroup = dto.variant_group || ''
        instance.hasWorktree = !!dto.has_worktree
        if (typeof dto.total_tokens === 'number') instance.totalTokens = dto.total_tokens
        instance.archivedAt = dto.archived_at
        instance.updatedAt = dto.updated_at
        instance.lastMessagePreview = dto.last_message_preview || ''
        instance.lastAssistantSummary = dto.last_assistant_summary || ''
        // Keep the locally-carried brief and overview if the server has none
        // to give (a dispatch whose run has not written its opening message
        // yet).
        if (dto.brief) instance.brief = dto.brief
        if (dto.overview) instance.overview = dto.overview
      } catch (e) {
        console.error('Failed to refresh conversation', instance.conversationId, e)
      }
    },

    /**
     * Accept a ready task: the backend merges its worktree into the
     * canonical tree. Errors (409 merge_conflict / agent_busy) propagate to
     * the caller so the review UI can surface their detail.
     */
    async acceptTaskInstance(instanceId: string) {
      const instance = this._findInstance(instanceId)
      if (!instance || instance.conversationId == null) return
      await AgentService.acceptTask(instance.conversationId)
      instance.reviewStatus = 'accepted'
      instance.hasWorktree = false
      // The backend resolved this task's check-ins as part of the accept;
      // drop them locally so the queue advances without waiting for a poll.
      this.removeCheckInsForTask(instance.conversationId)
      await this.refreshInstanceFromServer(instanceId)
    },

    /** Dismiss a ready task: its worktree is discarded without merging. */
    async dismissTaskInstance(instanceId: string) {
      const instance = this._findInstance(instanceId)
      if (!instance || instance.conversationId == null) return
      await AgentService.dismissTask(instance.conversationId)
      instance.reviewStatus = 'dismissed'
      instance.hasWorktree = false
      this.removeCheckInsForTask(instance.conversationId)
      await this.refreshInstanceFromServer(instanceId)
    },

    /** Drop every local queue entry belonging to one task. */
    removeCheckInsForTask(conversationId: number) {
      this.checkIns = this.checkIns.filter(c => c.task.id !== conversationId)
    },

    /** A subagent's work is now part of the project — tell the workspace once,
     *  whichever signal noticed it first. */
    _announceTaskApplied(conversationId: number | null | undefined) {
      if (conversationId == null || refreshedForTask.has(conversationId)) return
      refreshedForTask.add(conversationId)
      if (taskAppliedHandler) taskAppliedHandler()
    },

    /** Apply a task's review status from the server, announcing the moment its
     *  work merges into the project. */
    _setTaskReviewStatus(instance: AgentInstance, next: string) {
      const previous = instance.reviewStatus
      instance.reviewStatus = (next || '') as AgentInstance['reviewStatus']
      if (next === 'accepted' && previous !== 'accepted') {
        this._announceTaskApplied(instance.conversationId)
      }
    },

    /** The model new threads start on. */
    setThreadModel(modelId: string) {
      const id = threadModelOrDefault(modelId)
      this.threadModelId = id
      try {
        localStorage.setItem(THREAD_MODEL_KEY, id)
      } catch {
        // Private mode or storage blocked: the pick holds for this session.
      }
    },

    /** Move every thread that can still run onto the thread model. A live
     *  run finishes on the model it started with; its next turn uses this. */
    switchAllThreadsToThreadModel(): number {
      const threads = this.threadsOffThreadModel
      for (const thread of threads) this.setInstanceModel(thread.id, this.threadModelId)
      return threads.length
    },

    setInstanceModel(instanceId: string, modelId: string) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      instance.selectedModelId = modelId
      // Every model shares one reasoning ladder, but the effort riding along
      // may predate it (a 'minimal' or 'none' restored from an older session),
      // so it is re-seated onto the ladder here rather than sent as-is.
      instance.selectedEffort = clampEffortToModel(instance.selectedEffort, modelId)
      if (instance.conversationId) {
        AgentService.updateConversation(instance.conversationId, { model_name: modelId })
          .catch(e => console.error('Failed to persist model:', e))
      }
    },

    // Reasoning effort is a per-request tuning knob kept in client state only
    // (there is no backend field to persist it to). The clamp re-seats a
    // legacy rung ('minimal' or 'none' → 'low') and drops anything
    // unknown back to the default, so the ladder is all that ever gets sent.
    setInstanceEffort(instanceId: string, effort: ReasoningEffort) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      instance.selectedEffort = clampEffortToModel(effort, instance.selectedModelId)
    },

    // Fast mode rides along with each message; the server saves it on the
    // conversation, so there is nothing to persist from here.
    setInstanceFastMode(instanceId: string, on: boolean) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      instance.fastMode = on
    },

    setInstanceFile(instanceId: string, file: ProjectFile | null) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      instance.selectedFile = file
    },

    setInstanceProcessing(instanceId: string, value: boolean) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      instance.isProcessing = value
      if (value) {
        // A subagent running again can merge again, so the next merge is a
        // fresh one to refresh for.
        if (instance.conversationId != null) refreshedForTask.delete(instance.conversationId)
      } else {
        // Read-and-clear: was this run ended by an explicit user stop?
        const aborted = userAbortedRuns.delete(instanceId)
        instance.statusText = ''
        // The run is over — its stream controller (if any) is dead weight.
        abortControllers.delete(instanceId)
        // Completion signal: runs that finish off-screen get a dot.
        if (instanceId !== this.activeInstanceId && instanceId !== this.openedThreadId) {
          instance.hasUnread = true
        }
        // A queued prompt fires now — unless the user just stopped the run,
        // in which case it stays queued for them to send or cancel.
        const queued = instance.queuedPrompt
        if (queued && !aborted && queuedPromptSender) {
          instance.queuedPrompt = null
          const send = queuedPromptSender
          // Deferred so the finishing run's call stack fully unwinds before
          // the next run starts flipping processing back on.
          queueMicrotask(() => send(instanceId, queued))
        }
        // A subagent finishing frees one of the parallel slots — whoever has
        // been waiting longest for it starts now.
        if (instance.kind === 'task') this.firePendingDispatches()
      }
    },

    /**
     * Describe what the running agent is doing ("Thinking…", "Editing project
     * files…"). Cleared while reply text is streaming, so the status line and
     * the growing message never show together.
     */
    setInstanceStatus(instanceId: string, text: string) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      instance.statusText = text
    },

    addMessageToInstance(instanceId: string, message: AIMessage) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      const validMessage: AIMessage = {
        ...message,
        role: message.role || 'user',
        content: message.content || '',
        timestamp: message.timestamp || new Date().toISOString(),
      }
      instance.conversation.push(validMessage)
      instance.updatedAt = new Date().toISOString()
      instance.lastMessagePreview = (validMessage.content || '').split('\n')[0]?.slice(0, 140) || ''
      // An assistant message is this instance's latest word on what it did —
      // keep the whole thing for surfaces that render it in full (the
      // dispatch card), not just the clipped list-row preview.
      if (validMessage.role === 'assistant') {
        instance.lastAssistantSummary = validMessage.content || ''
      }
    },

    /**
     * Replace the content of a message already in the conversation.
     *
     * Used while streaming: the assistant's message is added empty and then
     * rewritten as each chunk arrives, so the reply appears to type itself
     * rather than landing all at once when the run ends.
     */
    setMessageContent(instanceId: string, messageId: string, content: string) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      const message = instance.conversation.find(m => m.id === messageId)
      if (!message) return
      message.content = content
      instance.updatedAt = new Date().toISOString()
      instance.lastMessagePreview = content.split('\n')[0]?.slice(0, 140) || ''
      if (message.role === 'assistant') {
        instance.lastAssistantSummary = content
      }
    },

    /**
     * Merge streamed metadata (activity, plan, filesChanged) into an existing
     * message. Content updates stay in setMessageContent, which also bumps
     * updatedAt/preview — metadata patches deliberately do not.
     */
    patchMessage(instanceId: string, messageId: string, patch: Partial<AIMessage>) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      const message = instance.conversation.find(m => m.id === messageId)
      if (!message) return
      Object.assign(message, patch)
    },

    /** Append one live tool-call step to a message's activity feed. */
    appendMessageActivity(instanceId: string, messageId: string, step: AgentActivityStep) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      const message = instance.conversation.find(m => m.id === messageId)
      if (!message) return
      if (!message.activity) message.activity = []
      message.activity.push(step)
    },

    /** Replace a message's plan snapshot (rewritten whole on each update). */
    setMessagePlan(instanceId: string, messageId: string, plan: AgentPlanStep[]) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      const message = instance.conversation.find(m => m.id === messageId)
      if (!message) return
      message.plan = [...plan]
    },

    /** Attach end-of-run metadata (changed files, usage) to a message. */
    setMessageMeta(
      instanceId: string,
      messageId: string,
      meta: { filesChanged?: string[]; usage?: AIMessage['usage']; question?: AIMessage['question'] }
    ) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      const message = instance.conversation.find(m => m.id === messageId)
      if (!message) return
      if (meta.filesChanged !== undefined) message.filesChanged = [...meta.filesChanged]
      if (meta.usage !== undefined) message.usage = { ...meta.usage }
      if (meta.question !== undefined) message.question = { ...meta.question }
    },

    /** Drop a message (e.g. an assistant bubble whose run produced nothing). */
    removeMessage(instanceId: string, messageId: string) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      instance.conversation = instance.conversation.filter(m => m.id !== messageId)
    },

    /**
     * Tie an optimistic user bubble to its persisted row: the stream's start
     * event carries the backend message id and the pre-run checkpoint, which
     * the inline restore control needs without waiting for a reload.
     */
    setMessageCheckpoint(instanceId: string, messageId: string, dbId?: number, checkpoint?: string) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      const message = instance.conversation.find(m => m.id === messageId)
      if (!message) return
      if (dbId !== undefined) message.dbId = dbId
      if (checkpoint) message.checkpoint = checkpoint
    },

    /**
     * Rewind this instance to just before a user message: restore the
     * message's checkpoint (backend resets files + deletes the message and
     * everything after), then truncate the local transcript to match.
     * Returns the removed prompt text (for the composer), or null on failure.
     */
    async restoreToCheckpoint(instanceId: string, message: AIMessage): Promise<string | null> {
      const instance = this._findInstance(instanceId)
      if (!instance || !instance.conversationId || !message.dbId || !message.checkpoint) return null
      const result = await AgentService.restoreCheckpoint(instance.conversationId, message.dbId)
      if (!result?.success) return null
      const index = instance.conversation.findIndex(m => m.id === message.id)
      if (index >= 0) {
        instance.conversation = instance.conversation.slice(0, index)
      }
      instance.lastMessagePreview =
        (instance.conversation[instance.conversation.length - 1]?.content || '')
          .split('\n')[0]?.slice(0, 140) || ''
      instance.lastAssistantSummary =
        [...instance.conversation].reverse().find(m => m.role === 'assistant')?.content || ''
      return result.prompt ?? message.content
    },

    updateInstanceConversationId(instanceId: string, conversationId: number) {
      const instance = this._findInstance(instanceId)
      if (!instance) return
      if (!instance.conversationId) instance.conversationId = conversationId
    },

    // --- Files (project-wide) ---
    setFiles(files: ProjectFile[]) {
      if (Array.isArray(files)) {
        this.files = [...files]
        // Prune any instance's selectedFile that no longer exists
        for (const instance of this.instances) {
          if (instance.selectedFile && !this.files.some(f => f.path === instance.selectedFile?.path)) {
            instance.selectedFile = null
          }
        }
      } else {
        this.files = []
      }
    },

    addFile(file: ProjectFile) {
      const existingIndex = this.files.findIndex(f => f.path === file.path)
      if (existingIndex >= 0) {
        this.files[existingIndex] = file
      } else {
        this.files.push(file)
      }
    },

    setProcessing(value: boolean) {
      if (this.activeInstanceId) this.setInstanceProcessing(this.activeInstanceId, value)
    },
  }
})
