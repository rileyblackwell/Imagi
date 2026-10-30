<template>
  <div class="h-full flex flex-col relative z-10 transition-colors duration-300">
    <!-- Messages Container -->
    <div ref="messagesContainer" class="iw-scroll iw-surface flex-grow overflow-y-auto overflow-x-hidden px-4 py-6">
      <!-- Empty state: one quiet line, nothing to dismiss or click -->
      <div v-if="!processedMessages.length" class="h-full flex items-center justify-center px-6 py-4 text-center min-h-0">
        <p class="text-xs text-ink/45 dark:text-bone/45 max-w-[230px] leading-relaxed">
          Describe a change and the agent will build it into your app.
        </p>
      </div>
      
      <template v-if="processedMessages.length> 0">
        <!-- The rail: the agent's side of the chat hangs off one thin line
             down the left, a node per step coloured by how it went, so the
             transcript reads like a log of the work. The user's messages
             stay as bubbles on the right, off the rail — the rail is the
             agent's story, the bubbles are the user's. The line is the
             ::before; nodes are punched out of it by a ring of the floor
             colour, so it reads as running between them, not through them. -->
        <div
          class="relative mx-auto max-w-3xl
            before:pointer-events-none before:absolute before:bottom-[0.625rem] before:left-[0.5625rem] before:top-[0.625rem] before:w-0.5 before:rounded-[2px] before:content-['']
            before:bg-[image:linear-gradient(180deg,var(--sl-line-strong),var(--sl-line)_85%,transparent)]"
        >
          <template v-for="(message, index) in processedMessages" :key="`msg-${message.id || index}`">
            <!-- When a sitting started: before the first message, and again
                 whenever the user comes back after a break. Centred between
                 two hairlines, on the canvas over the rail, so the rail breaks
                 where the user stepped away; a new sitting gets more room than
                 a new turn. The time is in `faint`, the token kept for
                 timestamps. -->
            <div
              v-if="sessionStarts.has(index)"
              class="session-break relative z-[1] flex items-center gap-3 bg-canvas py-1.5 [.msg-row+&]:mt-8
                before:h-px before:flex-1 before:bg-sl-line before:content-[''] after:h-px after:flex-1 after:bg-sl-line after:content-['']"
              role="separator"
            >
              <span class="shrink-0 text-[0.6875rem] font-semibold uppercase tabular-nums tracking-[0.06em] text-sl-faint">
                <time :datetime="sessionIso(message.timestamp)">{{ formatSessionStart(message.timestamp) }}</time>
              </span>
            </div>

            <!-- A thread opens on the coordinator's hand-off, not on something
                 the user typed, so it hangs on the rail as the brief rather
                 than sitting in a user bubble. -->
            <div v-if="isBrief(message, index)"
              :class="['msg-row rail-entry brief-row', ROW, { 'animate-message-in': message.isNew }]">
              <span :class="['rail-node rail-node--brief', NODE.brief]" aria-hidden="true"><i class="fas fa-share"></i></span>
              <p :class="WHO"><span :class="['rail-name', NAME_QUIET]">From the coordinator</span></p>
              <p :class="['brief-text whitespace-pre-wrap break-words', BRIEF_TEXT]">{{ message.content }}</p>
            </div>

            <!-- Errors the running app reported, which the server handed to
                 the coordinator: on the rail as the app speaking, with a red
                 node, not in a bubble as if the user had typed them. -->
            <div v-else-if="message.role === 'user' && message.appError"
              data-testid="app-error-message"
              :class="['msg-row rail-entry brief-row', ROW, { 'animate-message-in': message.isNew }]">
              <span :class="['rail-node rail-node--error', NODE.error]" aria-hidden="true"><i class="fas fa-exclamation"></i></span>
              <p :class="WHO"><span :class="['rail-name', NAME_QUIET]">Your app reported an error</span></p>
              <p :class="['brief-text whitespace-pre-wrap break-words', BRIEF_TEXT]">{{ appErrorText(message.content) }}</p>
            </div>

            <!-- User Message: a single compact bubble that opens the turn, with
                 extra breathing room above it. -->
            <div v-else-if="message.role === 'user'"
              class="msg-row group flex flex-col items-end [.msg-row+&]:mt-8 [.session-break+&]:mt-3"
              :class="{ 'animate-message-in': message.isNew }"
              :style="message.isNew ? { 'animation-delay': `${message.enterDelay}ms` } : {}">
              <!-- The one element that gets a bubble: solid, off the rail on
                   the right, ink on the daylight floor and a raised surface
                   on the dark one. Long unbroken strings (paths, URLs) wrap
                   instead of widening the chat. -->
              <div
                class="user-bubble min-w-0 max-w-[85%] rounded-[1rem_1rem_0.25rem_1rem] border border-transparent bg-[#1c1d26] px-3.5 py-2.5 text-[#f2f2f6] shadow-sl-card [overflow-wrap:anywhere]
                  dark:border-sl-line-strong dark:bg-sl-surface-2 dark:text-sl-text"
              >
                <p class="whitespace-pre-wrap break-words text-sm leading-relaxed">{{ message.content }}</p>
              </div>
              <!-- Checkpoint: rewind files + conversation to just before this
                   message. Revealed on hover/focus so the transcript stays
                   quiet. Restore chips belong to canonical-tree threads
                   (chat/lead) and hide while a canonical run is live — the
                   parent gates both via can-restore; task transcripts never
                   show them. -->
              <button
                v-if="message.checkpoint && message.dbId && restoreAllowed"
                type="button"
                class="mt-1 inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-[10px] font-medium text-ink/40 dark:text-white/35 hover:text-ink/75 dark:hover:text-white/75 hover:bg-ink/[0.03] dark:hover:bg-white/[0.06] opacity-0 group-hover:opacity-100 focus-visible:opacity-100
                  [transition:opacity_var(--iw-dur-2)_var(--iw-ease-out),background-color_var(--iw-dur-2)_var(--iw-ease-out),color_var(--iw-dur-2)_var(--iw-ease-out)]
                  focus-visible:shadow-iw-focus focus-visible:![outline:none] [@media(hover:none)]:!opacity-[0.55]"
                title="Restore your app and this conversation to the moment before this message"
                @click="emit('restore-checkpoint', message)"
              >
                <i class="fas fa-clock-rotate-left text-[9px]"></i>
                Restore checkpoint
              </button>
            </div>

            <!-- Assistant Message: the agent's work flows directly on the panel
                 background — no box, no label. A question still waiting on the user steps off
                 the rail into an amber tinted box, so it is the one thing in
                 the log that asks to be read. -->
            <div v-else-if="message.role === 'assistant'"
              class="msg-row rail-entry assistant-response min-w-0 text-[0.875rem] leading-[1.6] [overflow-wrap:anywhere] [.msg-row+&]:mt-4 [.session-break+&]:mt-3"
              :class="[
                { 'animate-message-in': message.isNew },
                message.question && isAnswerable(index)
                  ? 'rail-entry--asking relative -ml-3 rounded-[0.875rem] border border-[color:color-mix(in_srgb,var(--sl-wait)_22%,transparent)] bg-[color:color-mix(in_srgb,var(--sl-wait)_7%,transparent)] py-3 pl-11 pr-3'
                  : 'relative pl-8',
              ]"
              :style="message.isNew ? { 'animation-delay': `${message.enterDelay}ms` } : {}">
              <!-- Who is speaking, as the node on the rail: the coordinator's
                   lit mark, or a thread's blue ring. A question still waiting
                   on the user lights its node amber instead. -->
              <span v-if="message.question && isAnswerable(index)" :class="['rail-node rail-node--wait', NODE.wait]" aria-hidden="true">
                <i class="fas fa-question"></i>
              </span>
              <span v-else :class="['rail-node', `rail-node--${agentKind}`, NODE[agentKind]]" aria-hidden="true">{{ agentKind === 'coordinator' ? 'i' : '' }}</span>
              <p :class="WHO">
                <span :class="['rail-name', NAME]">{{ speakerName }}</span>
                <!-- A small mono label in the state's colour, the rail's way
                     of saying how a step went (dispatch cards wear the same). -->
                <span
                  v-if="message.question && isAnswerable(index)"
                  class="rail-tag whitespace-nowrap text-[0.625rem] uppercase tracking-[0.08em] text-sl-wait [font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace]"
                >Needs your answer</span>
              </p>
              <AgentActivityFeed
                v-if="activityVisible && message.activity?.length"
                :steps="message.activity"
                :streaming="isStreamingMessage(index)"
                class="mb-2.5"
              />
              <AgentPlanChecklist
                v-if="message.plan?.length"
                :steps="message.plan"
                class="mb-2.5"
              />
              <!-- The reply in Spotlight ink, with ink-tinted list markers
                   instead of the typography plugin's gray. Markdown inside
                   is styled in <style> (it arrives via v-html). -->
              <div
                class="prose prose-gray dark:prose-invert max-w-none prose-p:my-2 prose-headings:mb-3 prose-headings:mt-4 text-[0.875rem] leading-[1.6] text-sl-text
                  [--tw-prose-body:var(--sl-text)] [--tw-prose-invert-body:var(--sl-text)] [--tw-prose-bold:var(--sl-text)]
                  [--tw-prose-invert-bold:var(--sl-text)] [--tw-prose-headings:var(--sl-text)] [--tw-prose-invert-headings:var(--sl-text)]
                  marker:text-ink/40 dark:marker:text-blue-100/40"
                v-if="message.content && message.content.trim().length> 0"
                v-html="formatMessage(message, index)"
              />
              <!-- A question with one-tap answers or a sketch. Only the newest
                   one can still be answered; older ones show what was picked. -->
              <QuestionChoices
                v-if="message.question"
                :options="message.question.options || []"
                :visual="message.question.visual || ''"
                :disabled="!isAnswerable(index)"
                :picked="pickedAnswer(index)"
                @pick="emit('answer', $event)"
              />
              <!-- Subagents this reply kicked off, one card each. A card is
                   the whole of what the main thread says about a subagent,
                   from kickoff to sign-off: it names the job, reports where
                   the work stands, and opens that subagent's thread. When one
                   finishes it says so here, in place — nothing arrives
                   underneath as a second telling. -->
              <div v-if="message.dispatchedTasks?.length" class="dispatch-list mt-3 flex flex-col gap-3">
                <DispatchCard
                  v-for="task in message.dispatchedTasks"
                  :key="task.conversationId"
                  :title="task.title"
                  :instance="dispatchInstance(task.conversationId)"
                  @open="emit('open-task', task.conversationId)"
                  @retry="agentStore.retryTask(task.conversationId)"
                  @dismiss="discardThread(task.conversationId)"
                />
              </div>
              <!-- The hand-back. A subagent working is only half the news; the
                   other half is that the user is not waiting on it. Said by
                   the workspace rather than by the lead, because it is the
                   same sentence every time and it is a fact about how this
                   place works, not about this job.

                   It appears under the newest hand-off with work still in
                   flight, and goes when that work lands — so it is never a
                   stale invitation sitting under a finished card, and never
                   repeats down a thread full of them. -->
              <!-- Deliberately the quietest thing in the turn: caption-sized
                   muted text rather than the 14px ink the reply is set in. It
                   fades as it leaves, rather than blinking out from under the
                   card that just turned green. -->
              <Transition
                enter-active-class="[transition:opacity_var(--iw-dur-3)_var(--iw-ease-out),transform_var(--iw-dur-3)_var(--iw-ease-out)] motion-reduce:[transition:none]"
                enter-from-class="-translate-y-0.5 opacity-0"
                leave-active-class="[transition:opacity_var(--iw-dur-3)_var(--iw-ease-out),transform_var(--iw-dur-3)_var(--iw-ease-out)] motion-reduce:[transition:none]"
                leave-to-class="-translate-y-0.5 opacity-0"
              >
                <p v-if="index === handbackIndex" class="handback mt-[0.4375rem] pl-px text-[0.6875rem] leading-[1.5] text-ink/45 dark:text-white/40">
                  Running in the background — go ahead and send your next message.
                </p>
              </Transition>
              <div v-if="message.filesChanged?.length" class="mt-2">
                <span
                  class="inline-flex items-center gap-1.5 rounded-full border border-blue-100 dark:border-white/[0.08] bg-ink/[0.03] dark:bg-white/[0.04] px-2.5 py-1 text-[11px] font-medium text-ink/70 dark:text-white/60"
                  :title="message.filesChanged.join('\n')"
                >
                  <i class="fas fa-file-pen text-[9px] text-blue-600/70 dark:text-blue-300/70"></i>
                  {{ message.filesChanged.length }} {{ message.filesChanged.length === 1 ? 'file' : 'files' }} updated
                </span>
              </div>
            </div>

            <!-- System Message: system notes hang on the rail as a small quiet node: part of
                 the log, but nobody speaking. -->
            <div v-else
              :class="['msg-row rail-entry', ROW, { 'animate-fade-in': message.isNew }]"
              :style="message.isNew ? { 'animation-delay': `${message.enterDelay}ms` } : {}">
              <span :class="['rail-node', NODE.note]" aria-hidden="true"></span>
              <p class="flex min-h-[1.25rem] items-center text-[0.75rem] leading-[1.45] text-sl-muted">{{ message.content }}</p>
            </div>
          </template>

          <!-- Agent activity indicator. Hidden while the reply itself is
               streaming in — the growing message already shows progress.
               It fades both ways: when the reply starts arriving this hands
               over to the text rather than vanishing out from under it. -->
          <Transition
            enter-active-class="[transition:opacity_var(--iw-dur-2)_var(--iw-ease-out),transform_var(--iw-dur-2)_var(--iw-ease-out)]"
            enter-from-class="translate-y-1 opacity-0"
            leave-active-class="[transition:opacity_var(--iw-dur-2)_var(--iw-ease-out),transform_var(--iw-dur-2)_var(--iw-ease-out)]"
            leave-to-class="translate-y-1 opacity-0"
          >
            <div v-if="showActivityIndicator" :class="['msg-row rail-entry', ROW]">
              <!-- The live node: the workspace's working dot, whose disc, ring
                   and grid come from .iw-live-node (styles/workspace.css). -->
              <span :class="['rail-node iw-live-node', NODE.live]" aria-hidden="true"><span class="iw-live"></span></span>
              <div class="agent-status flex min-h-[1.25rem] items-center gap-2.5">
                <!-- Keyed on the reading so each new step cross-fades in
                     place, the same way the pane masthead's status does. -->
                <Transition
                  mode="out-in"
                  type="transition"
                  enter-active-class="[transition:opacity_var(--iw-dur-1)_var(--iw-ease-out),transform_var(--iw-dur-1)_var(--iw-ease-out)]"
                  enter-from-class="translate-y-[3px] opacity-0"
                  leave-active-class="[transition:opacity_var(--iw-dur-1)_var(--iw-ease-out),transform_var(--iw-dur-1)_var(--iw-ease-out)]"
                  leave-to-class="-translate-y-[3px] opacity-0"
                >
                  <span :key="statusLabel" class="iw-live-text text-sm font-medium">{{ statusLabel }}</span>
                </Transition>
              </div>
            </div>
          </Transition>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { marked } from 'marked'
import DOMPurify from 'isomorphic-dompurify'
import { ref, nextTick, watch, onMounted, onBeforeUnmount, computed } from 'vue'
import type { AgentInstance, AIMessage } from '@/apps/imagi/build/types/services'
import AgentActivityFeed from '@/apps/imagi/build/components/molecules/chat/AgentActivityFeed.vue'
import AgentPlanChecklist from '@/apps/imagi/build/components/molecules/chat/AgentPlanChecklist.vue'
import DispatchCard from '@/apps/imagi/build/components/molecules/chat/DispatchCard.vue'
import QuestionChoices from '@/apps/imagi/build/components/molecules/chat/QuestionChoices.vue'
import { useAgentStore } from '@/apps/imagi/build/stores/agentStore'
import { sessionStartIndexes, formatSessionStart, sessionIso } from '@/apps/imagi/build/utils/sessionBreaks'

marked.setOptions({
  gfm: true,
  breaks: true,
})

// Extended AIMessage interface to include isNew flag
interface ProcessedMessage extends AIMessage {
  isNew?: boolean;
  isTyping?: boolean;
  /** Milliseconds this message waits before playing its entrance */
  enterDelay?: number;
}

/* Both show* flags are declared through withDefaults on purpose. Vue casts an
   absent Boolean prop to false, so a type-only optional `showActivity?: boolean`
   defaulted OFF — the opposite of what its own comment promised, which is why
   subagent transcripts were quietly dropping their activity feed. Naming the
   default here is what makes "omit it and you get it" true. */
const props = withDefaults(defineProps<{
  messages: AIMessage[]
  isProcessing?: boolean
  /** What the agent is doing right now; empty while its reply is streaming. */
  statusText?: string
  /** Whether restore chips may show: false on task transcripts (their edits
   *  live in a worktree, not the canonical timeline) and while a
   *  canonical-tree run is live. Omitted = fall back to !isProcessing. */
  canRestore?: boolean
  /** Whether to show the per-reply tool-activity feed. Off on the main thread,
   *  where the lead's only tool call is the hand-off itself and the dispatch
   *  card below already reports it — a "Completed 1 step" fold under every
   *  reply is a second, emptier telling of the same thing. Defaults on, so a
   *  subagent's transcript still shows how it worked. */
  showActivity?: boolean
  /** Whose transcript this is. A thread's nodes are blue rings and its first
   *  message is the coordinator's brief; the coordinator wears the lit mark. */
  agentKind?: 'coordinator' | 'thread'
  /** The name over the agent's replies: "Coordinator", or the thread's job. */
  agentName?: string
}>(), { showActivity: true, agentKind: 'coordinator', agentName: '' })

/* ── The rail ─────────────────────────────────────────────────────────────
   One line down the left edge, and a node on it for every step the agent
   takes. Every rail entry is indented by the 2rem gutter the nodes sit in;
   messages within a turn sit 1rem apart, and the first message of a sitting
   sits just under its time. */
const ROW = 'relative pl-8 [.msg-row+&]:mt-4 [.session-break+&]:mt-3'

/** A node: 1.25rem, punched out of the line by a 4px ring of the floor. */
const NODE_AT = 'absolute left-0 top-0 grid h-5 w-5 place-items-center rounded-[50%]'
const RING = '[box-shadow:0_0_0_4px_rgb(var(--app-canvas))]'
const NODE: Record<string, string> = {
  // The coordinator's mark: the Spotlight light, lit.
  coordinator: `${NODE_AT} bg-sl-grad font-sl-display text-[0.6875rem] font-bold text-sl-on-accent [box-shadow:0_0_0_4px_rgb(var(--app-canvas)),0_0_14px_-2px_var(--sl-glow,rgba(255,120,80,0.3))]`,
  // A thread: a blue ring, the colour of work in progress.
  thread: `${NODE_AT} ${RING} border-[1.5px] border-sl-work bg-canvas text-[0.5625rem]`,
  // Waiting on the user: amber and glowing, the one node asking for a hand —
  // set into the asking box's padding rather than on the rail.
  wait: 'absolute left-3 top-3 grid h-5 w-5 place-items-center rounded-[50%] bg-sl-wait text-[0.5625rem] text-canvas [box-shadow:0_0_16px_-2px_var(--sl-wait)]',
  // The app reporting an error: the stopped colour, quiet.
  error: `${NODE_AT} ${RING} border-[1.5px] border-sl-bad bg-canvas text-[0.5rem] text-sl-bad`,
  brief: `${NODE_AT} ${RING} border-[1.5px] border-sl-line-strong bg-canvas text-[0.5rem] text-sl-muted`,
  // A system note: a small quiet dot centred on the line.
  note: `${RING} absolute left-[calc(0.5625rem-3px)] top-[0.4375rem] grid h-2 w-2 place-items-center rounded-[50%] bg-sl-faint text-[0.5625rem]`,
  // Placement over .iw-live-node, which would make it relative and round.
  live: `${RING} !absolute left-0 top-0 h-5 w-5 !rounded-[50%] text-[0.5625rem]`,
}

/** The speaker, on the node's line. */
const WHO = 'mb-[0.1875rem] flex min-h-[1.25rem] items-center gap-2 text-[0.75rem] leading-[1.3]'
const NAME = 'font-semibold text-sl-text [overflow-wrap:anywhere]'
/** The coordinator's brief and the app's errors are quoted, not spoken. */
const NAME_QUIET = 'font-medium text-sl-faint [overflow-wrap:anywhere]'
/** The brief a thread opens on: the coordinator's words, quietly boxed. */
const BRIEF_TEXT = 'rounded-[0.625rem] bg-sl-chip-bg px-3 py-2 text-[0.8125rem] leading-[1.55] text-sl-muted'

const speakerName = computed(() =>
  props.agentName || (props.agentKind === 'thread' ? 'Thread' : 'Coordinator')
)

/** A thread's transcript opens on the brief the coordinator handed it. */
function isBrief(message: AIMessage, index: number): boolean {
  return props.agentKind === 'thread' && index === 0 && message.role === 'user'
}

const activityVisible = computed(() => props.showActivity)

const restoreAllowed = computed(() =>
  props.canRestore !== undefined ? props.canRestore : !props.isProcessing
)

/**
 * Show the activity indicator while the agent works, except when the reply is
 * actively streaming (last message is the assistant's, growing in place) and
 * nothing else is going on — then the indicator would just dangle beneath it.
 * A tool call mid-run sets statusText again, which brings the indicator back.
 */
const showActivityIndicator = computed(() => {
  if (!props.isProcessing) return false
  if (props.statusText) return true
  const last = props.messages[props.messages.length - 1]
  return !(last?.role === 'assistant' && (last.content || '').trim().length > 0)
})

/** The indicator's current reading, with the generic fallback applied once so
 *  the cross-fade keys off the text actually on screen. */
const statusLabel = computed(() => props.statusText || 'Working…')

const emit = defineEmits<{
  (e: 'restore-checkpoint', message: AIMessage): void
  /** A dispatch card was clicked — open that subagent's thread */
  (e: 'open-task', conversationId: number): void
  /** One of a question's one-tap answers was picked */
  (e: 'answer', option: string): void
}>()

/** A question can be answered while it is the last word in the transcript
 *  and nothing is running. */
function isAnswerable(index: number): boolean {
  return !props.isProcessing && index === processedMessages.value.length - 1
}

/** The answer the user gave to the question at `index`, when it was one of
 *  its choices — so an answered question shows what was picked. */
function pickedAnswer(index: number): string {
  const options = processedMessages.value[index]?.question?.options || []
  const reply = processedMessages.value.slice(index + 1).find(m => m.role === 'user')
  const text = (reply?.content || '').trim()
  return options.includes(text) ? text : ''
}

// Dispatch cards show the subagent's live state, so the store is read
// directly — the card in an old reply keeps telling the truth as the task
// progresses (working → complete, with its summary), without threading props
// through.
const agentStore = useAgentStore()

/** The live subagent behind a dispatch card, or null before the store has it
 *  (a card rendered straight from a reloaded transcript, or a dispatch whose
 *  instance has not been adopted yet) — the card falls back to "Starting…". */
function dispatchInstance(conversationId: number): AgentInstance | null {
  return agentStore.instances.find(i => i.conversationId === conversationId) ?? null
}

/** A stopped thread the user is done with: dismissing it frees the
 *  worktree its run was holding. Nothing it did reached the app. */
async function discardThread(conversationId: number) {
  const instance = dispatchInstance(conversationId)
  if (!instance) return
  try {
    await agentStore.dismissTaskInstance(instance.id)
  } catch (e) {
    console.error('Failed to discard thread', e)
  }
}

/**
 * Whether this subagent is still on its way — the two states where its card
 * reads "starting" or "working". A missing instance counts as live for the
 * same reason the card falls back to "starting": it has been dispatched and
 * nothing has come back.
 *
 * A subagent stopped on a question is deliberately NOT live here: it is
 * waiting on the user, and telling them to go do something else is the wrong
 * thing to say next to a card asking them to answer.
 */
function taskIsLive(conversationId: number): boolean {
  const instance = dispatchInstance(conversationId)
  if (!instance) return true
  return instance.isProcessing || instance.reviewStatus === 'active'
}

/**
 * The reply the hand-back note belongs under, or -1 for none.
 *
 * Strictly the NEWEST hand-off, and only while its work is still in flight.
 * The note is the beat right after handing something over — "that's away, you
 * are not waiting on it" — so it belongs at the bottom of the thread, where
 * the user just typed. Searching further back for any live subagent would pin
 * it mid-scroll under an older card (a run stranded by a reload stays "live"
 * forever), which reads as a stray line rather than an answer to what the
 * user just did.
 */
const handbackIndex = computed(() => {
  const messages = processedMessages.value
  for (let i = messages.length - 1; i >= 0; i--) {
    const tasks = messages[i]?.dispatchedTasks
    if (!tasks?.length) continue
    return tasks.some(task => taskIsLive(task.conversationId)) ? i : -1
  }
  return -1
})

// Refs and reactive state
const messagesContainer = ref<HTMLElement | null>(null)
const previousMessageCount = ref(0)

/** How far apart consecutive arrivals are spaced, and how many get spaced. */
const ENTER_STAGGER_MS = 60
const ENTER_STAGGER_MAX = 4

// Process messages to add isNew flag for animations
const processedMessages = computed<ProcessedMessage[]>(() => {
  const firstNew = previousMessageCount.value
  return props.messages.map((message, index) => {
    // Only mark messages as new if they're newly added
    const isNew = index >= firstNew;

    // The stagger counts from the first *new* message, not from the top of
    // the conversation. Keyed off the absolute index it grew with the
    // transcript — message 40 of a long thread waited two seconds to fade in,
    // which read as the reply having stalled. Capped as well, so a batch
    // arriving at once still resolves promptly.
    const enterDelay = isNew
      ? Math.min(index - firstNew, ENTER_STAGGER_MAX) * ENTER_STAGGER_MS
      : 0;

    return {
      ...message,
      isNew,
      enterDelay
    };
  });
});

/** Where each sitting starts: the first message, and any message that comes
 *  after a long enough quiet spell (see utils/sessionBreaks). */
const sessionStarts = computed(() => sessionStartIndexes(props.messages))

/** What the app reported, without the framing written for the coordinator:
 *  the fenced error lines. */
function appErrorText(content: string): string {
  const fenced = content.match(/"""\n([\s\S]*?)\n"""/g)
  if (!fenced) return content
  return fenced.map(block => block.slice(4, -4)).join('\n')
}

/** The reply currently streaming in is the last message while a run is active. */
function isStreamingMessage(index: number): boolean {
  return !!props.isProcessing && index === props.messages.length - 1
}

// --- Autoscroll ---------------------------------------------------------
// Only follow the conversation while the user is pinned near the bottom;
// scrolling up to read pauses following until they return.
const PIN_THRESHOLD_PX = 80
const isPinnedToBottom = ref(true)

function handleScroll() {
  const el = messagesContainer.value
  if (!el) return
  isPinnedToBottom.value = el.scrollHeight - el.scrollTop - el.clientHeight <= PIN_THRESHOLD_PX
}

// rAF-throttled: at most one scroll per frame, measured after Vue has
// patched the DOM (render flush happens in a microtask, before the frame).
let scrollFrame: number | null = null
function scheduleScrollToBottom(behavior: ScrollBehavior) {
  if (scrollFrame !== null) return
  scrollFrame = requestAnimationFrame(() => {
    scrollFrame = null
    const el = messagesContainer.value
    if (!el) return
    if (typeof el.scrollTo === 'function') {
      el.scrollTo({ top: el.scrollHeight, behavior })
    } else {
      // jsdom (tests) has no Element#scrollTo
      el.scrollTop = el.scrollHeight
    }
  })
}

function followConversation() {
  if (isPinnedToBottom.value) {
    // Instant jumps while streaming; smooth for one-off additions
    scheduleScrollToBottom(props.isProcessing ? 'auto' : 'smooth')
  }
}

// New messages: track the count for entry animations, then follow
watch(() => props.messages.length, (newLength) => {
  // Only update the animation state after rendering is complete
  nextTick(() => {
    previousMessageCount.value = newLength
    followConversation()
  })
}, { immediate: true })

// Streaming deltas: watch the last message's size instead of deep-watching
// (and re-serializing) the whole conversation on every SSE event. Activity
// steps count too so the feed growing keeps the view pinned.
watch(() => {
  const last = props.messages[props.messages.length - 1]
  return `${last?.content?.length ?? 0}:${last?.activity?.length ?? 0}`
}, () => {
  followConversation()
})

// The viewport itself shrinks when something docks under it (the threads
// queue appearing above the composer, a taller draft). No scroll event fires,
// so without this the newest message (often a question waiting on the user)
// ends up hidden under whatever docked.
let viewportObserver: ResizeObserver | null = null

// Initial scroll when component is mounted
onMounted(() => {
  messagesContainer.value?.addEventListener('scroll', handleScroll, { passive: true })
  if (typeof ResizeObserver !== 'undefined' && messagesContainer.value) {
    viewportObserver = new ResizeObserver(() => {
      if (isPinnedToBottom.value) scheduleScrollToBottom('auto')
    })
    viewportObserver.observe(messagesContainer.value)
  }
  nextTick(() => {
    // Initialize previous message count
    previousMessageCount.value = props.messages.length
    scheduleScrollToBottom('auto')
  })
})

onBeforeUnmount(() => {
  messagesContainer.value?.removeEventListener('scroll', handleScroll)
  viewportObserver?.disconnect()
  viewportObserver = null
  if (scrollFrame !== null) {
    cancelAnimationFrame(scrollFrame)
    scrollFrame = null
  }
})

// Rendered-HTML cache: markdown parsing + sanitization run once per
// (message, size), so a streaming delta only re-renders the growing message
// instead of the whole conversation. Never evicted — conversations are
// bounded, and stale keys are just unused strings. The source content is
// stored alongside the HTML and verified on hit: end-of-run reconciliation
// rewrites a message wholesale, and the corrected text can collide with a
// previously rendered prefix of the same length.
const renderedHtmlCache = new Map<string, { content: string; html: string }>()

const formatMessage = (message: AIMessage, index: number): string => {
  const content = message.content || ''
  if (!content) {
    return ''
  }

  // Same identity fallback as the template's v-for key
  const cacheKey = `${message.id || index}:${content.length}`
  const cached = renderedHtmlCache.get(cacheKey)
  if (cached !== undefined && cached.content === content) {
    return cached.html
  }

  let html: string
  try {
    // Parse markdown (fenced code included) and sanitize to prevent XSS
    html = DOMPurify.sanitize(marked.parse(content).toString())
  } catch (e) {
    console.error('Error parsing markdown:', e)
    html = DOMPurify.sanitize(content)
  }
  renderedHtmlCache.set(cacheKey, { content, html })
  return html
}
</script>

<style scoped>
/* Markdown arrives via v-html and never gets the scope attribute, so styling
   it needs :deep. Fenced code renders as a quiet navy-ink chip that scrolls
   within its own box. */
.prose :deep(pre) {
  background: rgba(239, 246, 255, 0.6);
  border: 1px solid theme('colors.blue.100');
  border-radius: var(--iw-r-md);
  padding: 0.75rem 0.875rem;
  margin: 0.75rem 0;
  overflow-x: auto;
  font-size: 0.75rem;
  line-height: 1.6;
  color: theme('colors.blue.950');
}

.dark .prose :deep(pre) {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.85);
}

.prose :deep(code) {
  color: theme('colors.orange.700');
  background: theme('colors.orange.50');
  padding: 0.125rem 0.375rem;
  border-radius: 0.375rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  border: 1px solid rgba(254, 215, 170, 0.7);
}

.dark .prose :deep(code) {
  color: theme('colors.orange.300');
  background: rgba(251, 146, 60, 0.1);
  border-color: rgba(251, 146, 60, 0.2);
}

/* The typography plugin wraps inline code in backticks — the chip already
   says "code" */
.prose :deep(code::before),
.prose :deep(code::after) {
  content: none;
}

/* Inside a fenced block the inline-code pill styling resets away */
.prose :deep(pre code),
.dark .prose :deep(pre code) {
  display: block;
  background: transparent;
  border: none;
  padding: 0;
  color: inherit;
  font-size: inherit;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}

/* Wide tables scroll within their own box; the container clips overflow, so
   without this their far columns would be cut off with no way to reach them. */
.prose :deep(table) {
  display: block;
  max-width: 100%;
  overflow-x: auto;
}

/* Message animations. A message settles up into place with a trace of
   overshoot — closer to something being set down than to a fade. These stay
   CSS: a scoped @keyframes name is hashed, so no utility can reference it. */
@keyframes message-in {
  from {
    opacity: 0;
    transform: translateY(10px) scale(0.99);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.animate-message-in {
  animation: message-in var(--iw-dur-3) var(--iw-ease-spring) both;
}

.animate-fade-in {
  animation: fade-in var(--iw-dur-3) var(--iw-ease-out) both;
}

@media (prefers-reduced-motion: reduce) {
  .animate-message-in,
  .animate-fade-in {
    animation: none;
  }
}
</style>
