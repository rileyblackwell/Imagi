<template>
  <div v-if="!isCollapsed" class="iw-surface flex flex-col h-full bg-canvas transition-colors duration-300">
    <!-- Header: the ways out of here, and — on a subagent's thread — whose
         thread it is. The main thread goes unnamed: it is the one the user
         drives and the one the workspace opens on, so "Main agent" was a
         caption on the thing you were already looking at. A subagent's
         read-only thread does keep its own name, which is now the whole way
         you tell the two apart at a glance: a name means you have stepped into
         somebody else's transcript. What the
         agent is doing right now is not here: it belongs under the message
         that set it going, so the transcript says it. Version restores live
         inline in the transcript (the
         per-message checkpoint chips), so the header carries no history
         controls.

         This is the workspace's junction: everything else in it is one hop
         from here, which is why the main thread is the only pane offering more
         than one destination. -->
    <WorkspacePaneHeader
      :title="headerTitle"
      :status="headerStatus"
      :state="headerState"
      :switches="paneSwitches"
      @switch="onPaneSwitch"
    />

    <!-- Conversation Area (scrollable) -->
    <div class="flex-1 min-h-0 overflow-hidden flex flex-col">
      <!-- Keyed by instance so switching remounts the conversation: scroll
           position and the pinned-to-bottom state belong to one transcript
           and must not leak into another (a fresh mount lands at the latest
           message). -->
      <ChatConversation
        :key="activeInstance?.id || 'none'"
        :messages="ensureValidMessages(activeInstance?.conversation || [])"
        :is-processing="!!activeInstance?.isProcessing"
        :status-text="activeInstance?.statusText || ''"
        :can-restore="canRestoreCheckpoints"
        :show-activity="!isLeadThread"
        agent-kind="coordinator"
        @restore-checkpoint="emit('restore-checkpoint', $event)"
        @open-task="onOpenTask"
        @answer="onAnswerQuestion"
        class="flex-1"
      />
    </div>

    <!-- The composer, the same one a thread wears: what differs is where
         the words go. On the coordinator it is the next message; on a thread
         opened here it steers that thread (ThreadComposer). -->
    <ThreadComposer
      v-if="isTaskThread && activeInstance"
      :instance="activeInstance"
      back-label="Back to coordinator"
      @back="goToLead"
    />

    <AgentComposer
      v-else
      ref="composer"
      :instance="activeInstance"
      :submit="submitToCoordinator"
      @stop="emit('stop')"
    >
      <!-- Check-in queue: threads reporting back, one card at a time —
           a question to answer, or the news that one finished -->
      <CheckInQueue
        v-if="isLeadThread"
        :queue="queueCards"
        :busy="resolvingCheckIn"
        @accept="emit('check-in-accept', $event)"
        @dismiss="emit('check-in-dismiss', $event)"
        @answer="onAnswerCheckIn"
        @skip="onSkipCheckIn"
        @view="onViewCheckIn"
        @retry="onRetryCheckIn"
      />
    </AgentComposer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAgentStore } from '../../../stores/agentStore'
// The workspace's shared motion + material vocabulary (curves, durations,
// radii, elevation, focus ring). Imported by each pane that spends it rather
// than by an ancestor layout: a var(--iw-*) with no token behind it resolves
// to nothing, which would leave this pane's popovers transparent.
import '../../../styles/workspace.css'
import { ChatConversation } from '../../organisms/chat'
import CheckInQueue from '../../molecules/sidebar/CheckInQueue.vue'
import WorkspacePaneHeader from '../../molecules/sidebar/WorkspacePaneHeader.vue'
import ThreadComposer from '../../molecules/sidebar/ThreadComposer.vue'
import AgentComposer from '../../molecules/chat/AgentComposer.vue'
import { useWorkspaceSettings } from '../../../composables/useWorkspaceSettings'
import type { AIMessage } from '../../../types/index'
import type { CheckInDto } from '../../../types/services'

// Props
const props = defineProps<{
  onPromptSubmit: (prompt: string) => Promise<void>
  isCollapsed?: boolean
  /** An accept/dismiss from the check-in queue is in flight */
  resolvingCheckIn?: boolean
}>()

const emit = defineEmits<{
  (e: 'toggleManager'): void
  (e: 'stop'): void
  (e: 'restore-checkpoint', message: AIMessage): void
  /** Merge a finished background task's work into the app */
  (e: 'check-in-accept', checkIn: CheckInDto): void
  /** Discard a finished background task's work */
  (e: 'check-in-dismiss', checkIn: CheckInDto): void
  /** Look in on a subagent — it opens in the Subagents pane, never here */
  (e: 'open-task', conversationId: number): void
  /** Go and watch the app being built. Only reachable from here below the md
   *  breakpoint; on desktop the preview already sits beside this pane. */
  (e: 'open-preview'): void
}>()

const store = useAgentStore()
const activeInstance = computed(() => store.activeInstance)

// The user drives most work from the coordinator (the lead conversation); a
// task is one of its threads, which the user can also steer directly.
const isTaskThread = computed(() => activeInstance.value?.kind === 'task')
const isLeadThread = computed(() => activeInstance.value?.kind === 'lead')

// The main thread wears no name at all. Its conversation name is never
// surfaced, and labelling it "Main agent" only told you what the pane you were
// already typing into was. Subagent threads do show their own name — that is
// what makes an unnamed masthead legible, because a name now means you are
// reading somebody else's thread rather than your own.
const headerTitle = computed(() =>
  isTaskThread.value ? (activeInstance.value?.title || 'Thread') : ''
)

/** Where you can go from the main thread. Subagents first — it is the nearer
 *  room, and the one that reports back here. The preview is the outer wall of
 *  the workspace, so it sits outermost; on desktop it is already on screen
 *  beside this pane, which is what `mobileOnly` says. */
const paneSwitches = computed(() => [
  {
    id: 'manager',
    icon: 'fas fa-layer-group',
    label: 'Threads',
    // Both read the same number, and that is the point rather than a
    // duplication: the dot on the icon says something is alive over there and
    // can be caught without looking, the badge says how much. Working right
    // now, not how many exist — see workingAgentCount for why.
    live: store.workingAgentCount > 0,
    count: store.workingAgentCount,
    direction: 'forward' as const,
  },
  {
    id: 'preview',
    icon: 'fas fa-globe',
    label: 'Preview',
    direction: 'forward' as const,
    mobileOnly: true,
  },
  // Not a destination but the workspace's settings, so the icon alone.
  {
    id: 'settings',
    icon: 'fas fa-gear',
    label: 'Workspace settings',
    iconOnly: true,
  },
])

const { openSettings } = useWorkspaceSettings()

function onPaneSwitch(id: string) {
  if (id === 'manager') emit('toggleManager')
  else if (id === 'preview') emit('open-preview')
  else if (id === 'settings') openSettings()
}

/** The header's second line: where this thread stands while nothing is
 *  running. A live run is narrated in the transcript instead, directly under
 *  the message that started it — that is where you are looking when you have
 *  just sent something, and it puts "Thinking…" next to the thing being
 *  thought about rather than in a corner of the masthead. So the plate goes
 *  quiet the moment a run starts and only speaks between them. */
const headerStatus = computed(() => {
  const instance = activeInstance.value
  if (instance?.isProcessing) return ''
  // No "background agent" prefix: the muted mark and the note above the
  // composer already say that, and the sidebar is too narrow to spend
  // characters twice. These match the manager's card labels word for word.
  if (isTaskThread.value) {
    switch (instance?.reviewStatus) {
      case 'input': return 'Asked you a question'
      case 'ready': return 'Thread complete — one of your options'
      case 'failed': return 'Stopped before finishing'
      case 'accepted': return 'Thread complete'
      case 'dismissed': return 'Discarded'
      default: return ''
    }
  }
  // Not everything in the queue is owed an answer: a subagent that finished
  // put its work in the app on its own, so its card is news to read. Saying
  // "1 agent is waiting on you" over a card with nothing to decide sends the
  // user looking for a decision that does not exist.
  const waiting = store.waitingCheckIns.length
  if (waiting > 0) {
    return `${waiting} ${waiting === 1 ? 'thread is' : 'threads are'} waiting on you`
  }
  const finished = store.checkIns.length
  if (finished > 0) {
    return `${finished} ${finished === 1 ? 'thread' : 'threads'} finished`
  }
  // Nothing running and nothing waiting: the plate is just the thread's name.
  // "Ready when you are" was a line spent saying that no line was needed.
  return ''
})

/** The dot beside that line, in the crew ledger's three-token vocabulary.
 *  Never 'working' — a live run has no line here to mark. */
const headerState = computed<'waiting' | 'idle'>(() => {
  const instance = activeInstance.value
  if (isTaskThread.value) {
    const status = instance?.reviewStatus
    return status === 'input' || status === 'ready' || status === 'failed'
      ? 'waiting'
      : 'idle'
  }
  // Same split as the line above it: only a card that owes the user something
  // lights the dot.
  return store.checkIns.some(c => c.kind !== 'done') ? 'waiting' : 'idle'
})

/** What the queue above the composer still carries. A thread's question is
 *  not one of them: it is asked and answered on that thread's own card in the
 *  chat, where the job it belongs to is named, so the queue would only be a
 *  second copy of the same question. */
const queueCards = computed(() => store.checkIns.filter(c => c.kind !== 'question'))

async function goToLead() {
  const lead = store.leadInstance
  if (lead) await store.switchInstance(lead.id)
}

/** The answer restarts the subagent in the background — the user stays here. */
function onAnswerCheckIn(checkIn: CheckInDto, answer: string) {
  store.answerCheckIn(checkIn, answer)
}

/** A one-tap answer to the question the agent ended on. On a thread it is
 *  the thread's next turn; on the coordinator it is simply the next message. */
function onAnswerQuestion(option: string) {
  const instance = activeInstance.value
  if (!instance || instance.isProcessing) return
  if (isTaskThread.value) {
    store.steerThread(instance.id, option)
    return
  }
  void props.onPromptSubmit(option)
}

/** Clear an entry the user has dealt with (or wants out of the way). */
function onSkipCheckIn(checkIn: CheckInDto) {
  void store.resolveCheckIn(checkIn.id)
}

/** Open the task's read-only thread to see what it actually did. */
function onViewCheckIn(checkIn: CheckInDto) {
  emit('open-task', checkIn.task.id)
}

/** Run a failed subagent again. The store drops this card as it goes: the
 *  run's start retires the error server-side, and the run end files whatever
 *  comes next. */
function onRetryCheckIn(checkIn: CheckInDto) {
  store.retryTask(checkIn.task.id)
}

/** A dispatch card in the transcript was clicked — open that subagent's
 *  thread over in the Subagents pane, so this thread keeps its place. */
function onOpenTask(conversationId: number) {
  emit('open-task', conversationId)
}

// Restores git-reset the canonical working tree. Only canonical-tree
// (chat/lead) runs write to it — kind='task' runs edit their own git
// worktrees — so restores stay enabled while tasks run in parallel and are
// blocked only by a live canonical run (the workspace and backend enforce
// the same rule as backstops).
const anyRunActive = computed(() =>
  store.instances.some(i => i.kind !== 'task' && i.isProcessing)
)

// Restore chips belong to canonical-tree threads: a task's edits live in its
// worktree and land (or not) through the review inbox, so its transcript
// never offers canonical-timeline restores.
const canRestoreCheckpoints = computed(() =>
  activeInstance.value?.kind !== 'task' && !anyRunActive.value
)

// Methods
function ensureValidMessages(messages: any[]): AIMessage[] {
  if (!messages || !Array.isArray(messages)) {
    return []
  }
  
  const filteredMessages = messages.filter(m => {
    if (m && m.role === 'system') {
      if (m.content && (
        m.content.includes('Switched to file:') || 
        m.content.includes('Switched to build mode') ||
        m.content.includes('previously selected file')
      )) {
        return false
      }
    }
    return true
  })
  
  // Spread, never a field whitelist: everything a message carries beyond the
  // four fields defaulted here — activity feed, plan, files-changed chip, cost
  // caption, dispatch cards, checkpoint — is the transcript's content, and a
  // whitelist silently drops whatever it was not updated to know about.
  const validMessages = filteredMessages
    .filter(m => m && typeof m === 'object' && m.role)
    .map(m => ({
      ...m,
      content: m.content || '',
      code: m.code || '',
      timestamp: m.timestamp || new Date().toISOString(),
      id: m.id || `msg-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
    })) as AIMessage[]

  return validMessages
}

// After a checkpoint restore, the removed prompt comes back to the composer
// so the user can edit and resend it (the Cursor rewind flow).
const composer = ref<InstanceType<typeof AgentComposer> | null>(null)
function setPromptText(text: string) {
  composer.value?.setPromptText(text)
}

defineExpose({ setPromptText })

/** The coordinator's next message. Mid-run it is held (one per instance — a
 *  second submit replaces it) and sent when the run finishes. */
async function submitToCoordinator(text: string) {
  const instance = activeInstance.value
  if (!instance) return
  if (instance.isProcessing) {
    store.queuePrompt(instance.id, text)
    return
  }
  await props.onPromptSubmit(text)
}
</script>
