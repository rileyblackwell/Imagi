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
             agent's story, the bubbles are the user's. -->
        <div class="rail-feed max-w-3xl mx-auto">
          <template v-for="(message, index) in processedMessages" :key="`msg-${message.id || index}`">
            <!-- A thread opens on the coordinator's hand-off, not on something
                 the user typed, so it hangs on the rail as the brief rather
                 than sitting in a user bubble. -->
            <div v-if="isBrief(message, index)"
              class="msg-row rail-entry brief-row"
              :class="{ 'animate-message-in': message.isNew }">
              <span class="rail-node rail-node--brief" aria-hidden="true"><i class="fas fa-share"></i></span>
              <p class="rail-who"><span class="rail-name">From the coordinator</span></p>
              <p class="brief-text whitespace-pre-wrap break-words">{{ message.content }}</p>
            </div>

            <!-- User Message: a single compact bubble that opens the turn -->
            <div v-else-if="message.role === 'user'"
              class="msg-row user-row group flex flex-col items-end"
              :class="{ 'animate-message-in': message.isNew }"
              :style="message.isNew ? { 'animation-delay': `${message.enterDelay}ms` } : {}">
              <div class="user-bubble">
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
                class="restore-chip mt-1 inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-[10px] font-medium text-ink/40 dark:text-white/35 hover:text-ink/75 dark:hover:text-white/75 hover:bg-ink/[0.03] dark:hover:bg-white/[0.06] opacity-0 group-hover:opacity-100 focus-visible:opacity-100"
                title="Restore your app and this conversation to the moment before this message"
                @click="emit('restore-checkpoint', message)"
              >
                <i class="fas fa-clock-rotate-left text-[9px]"></i>
                Restore checkpoint
              </button>
            </div>

            <!-- Assistant Message: the agent's work flows plainly below the bubble -->
            <div v-else-if="message.role === 'assistant'"
              class="msg-row rail-entry assistant-response"
              :class="{ 'animate-message-in': message.isNew, 'rail-entry--asking': message.question && isAnswerable(index) }"
              :style="message.isNew ? { 'animation-delay': `${message.enterDelay}ms` } : {}">
              <!-- Who is speaking, as the node on the rail: the coordinator's
                   lit mark, or a thread's blue ring. A question still waiting
                   on the user lights its node amber instead. -->
              <span v-if="message.question && isAnswerable(index)" class="rail-node rail-node--wait" aria-hidden="true">
                <i class="fas fa-question"></i>
              </span>
              <span v-else :class="['rail-node', `rail-node--${agentKind}`]" aria-hidden="true">{{ agentKind === 'coordinator' ? 'i' : '' }}</span>
              <p class="rail-who">
                <span class="rail-name">{{ speakerName }}</span>
                <span v-if="message.question && isAnswerable(index)" class="rail-tag">Needs your answer</span>
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
              <div
                class="prose prose-gray dark:prose-invert max-w-none prose-p:my-2 prose-headings:mb-3 prose-headings:mt-4 leading-relaxed text-sm"
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
              <Transition name="handback">
                <p v-if="index === handbackIndex" class="handback">
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

            <!-- System Message -->
            <!-- System notes hang on the rail as a small quiet node: part of
                 the log, but nobody speaking. -->
            <div v-else
              class="msg-row rail-entry system-row"
              :class="{ 'animate-fade-in': message.isNew }"
              :style="message.isNew ? { 'animation-delay': `${message.enterDelay}ms` } : {}">
              <span class="rail-node rail-node--note" aria-hidden="true"></span>
              <p class="system-text">{{ message.content }}</p>
            </div>
          </template>

          <!-- Agent activity indicator. Hidden while the reply itself is
               streaming in — the growing message already shows progress.
               It fades both ways: when the reply starts arriving this hands
               over to the text rather than vanishing out from under it. -->
          <Transition name="status">
            <div v-if="showActivityIndicator" class="msg-row rail-entry status-row">
              <span class="rail-node rail-node--live" aria-hidden="true"><span class="status-orb"></span></span>
              <div class="agent-status flex items-center gap-2.5">
                <!-- Keyed on the reading so each new step cross-fades in
                     place, the same way the pane masthead's status does. -->
                <Transition name="status-text" mode="out-in">
                  <span :key="statusLabel" class="status-shimmer text-sm font-medium">{{ statusLabel }}</span>
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

// Initial scroll when component is mounted
onMounted(() => {
  messagesContainer.value?.addEventListener('scroll', handleScroll, { passive: true })
  nextTick(() => {
    // Initialize previous message count
    previousMessageCount.value = props.messages.length
    scheduleScrollToBottom('auto')
  })
})

onBeforeUnmount(() => {
  messagesContainer.value?.removeEventListener('scroll', handleScroll)
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
/* Vertical rhythm: messages within a turn sit close together, and each new
   user bubble opens a turn with extra breathing room above it. */
.msg-row + .msg-row {
  margin-top: 1rem;
}

.msg-row + .user-row {
  margin-top: 2rem;
}

/* Quiet until the turn is hovered, then it fades up in place. */
.restore-chip {
  transition:
    opacity var(--iw-dur-2) var(--iw-ease-out),
    background-color var(--iw-dur-2) var(--iw-ease-out),
    color var(--iw-dur-2) var(--iw-ease-out);
}

.restore-chip:focus-visible {
  outline: none;
  box-shadow: var(--iw-focus-ring);
}

/* Touch screens have no hover: keep the restore chip faintly visible so the
   affordance is discoverable without a pointer. */
@media (hover: none) {
  .restore-chip {
    opacity: 0.55;
  }
}

/* The user's prompt is the one element that gets a bubble: solid, off the
   rail on the right, so it reads as the user's side of the conversation.
   Ink on the daylight floor, a raised surface on the dark one. */
.user-bubble {
  max-width: 85%;
  padding: 0.625rem 0.875rem;
  border-radius: 1rem 1rem 0.25rem 1rem;
  background-color: #1c1d26;
  border: 1px solid transparent;
  box-shadow: var(--sl-card-shadow, var(--iw-shadow-1));
  color: #f2f2f6;
  /* Long unbroken strings (paths, URLs) wrap instead of widening the chat
     and dragging in a horizontal scrollbar. */
  overflow-wrap: anywhere;
  min-width: 0;
}

.dark .user-bubble {
  background-color: var(--sl-surface-2, #1a1d28);
  border-color: var(--sl-line-strong, rgba(255, 255, 255, 0.14));
  color: var(--sl-text, #eef0f6);
}

/* ── The rail ───────────────────────────────────────────────────────────
   One line down the left edge, and a node on it for every step the agent
   takes. Nodes are punched out of the line by a ring of the floor colour,
   so the line reads as running between them rather than through them. */
.rail-feed {
  position: relative;
  --rail-x: 0.5625rem;
  --node: 1.25rem;
  --node-ring: 0 0 0 4px rgb(var(--app-canvas));
}

.rail-feed::before {
  content: '';
  position: absolute;
  left: var(--rail-x);
  top: 0.625rem;
  bottom: 0.625rem;
  width: 2px;
  border-radius: 2px;
  background: linear-gradient(
    180deg,
    var(--sl-line-strong, rgba(19, 26, 44, 0.15)),
    var(--sl-line, rgba(19, 26, 44, 0.09)) 85%,
    transparent
  );
  pointer-events: none;
}

.rail-entry {
  position: relative;
  padding-left: 2rem;
}

.rail-node {
  position: absolute;
  left: 0;
  top: 0;
  width: var(--node);
  height: var(--node);
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 0.5625rem;
  background: rgb(var(--app-canvas));
  box-shadow: var(--node-ring);
}

/* The coordinator's mark: the Spotlight light, lit. */
.rail-node--coordinator {
  background: var(--sl-grad);
  color: var(--sl-on-accent, #1a0e08);
  font-family: var(--sl-font-display, inherit);
  font-size: 0.6875rem;
  font-weight: 700;
  box-shadow: var(--node-ring), 0 0 14px -2px var(--sl-glow, rgba(255, 120, 80, 0.3));
}

/* A thread: a blue ring, the colour of work in progress. */
.rail-node--thread {
  border: 1.5px solid var(--sl-work);
}

/* Waiting on the user: amber and glowing, the one node asking for a hand. */
.rail-node--wait {
  background: var(--sl-wait);
  color: rgb(var(--app-canvas));
  box-shadow: var(--node-ring), 0 0 16px -2px var(--sl-wait);
}

.rail-node--brief {
  border: 1.5px solid var(--sl-line-strong);
  color: var(--sl-muted);
  font-size: 0.5rem;
}

.rail-node--note {
  left: calc(var(--rail-x) - 3px);
  top: 0.4375rem;
  width: 0.5rem;
  height: 0.5rem;
  background: var(--sl-faint);
}

.rail-node--live .status-orb {
  margin: 0;
}

/* The speaker, on the node's line. */
.rail-who {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-height: var(--node);
  margin-bottom: 0.1875rem;
  font-size: 0.75rem;
  line-height: 1.3;
}

.rail-name {
  font-weight: 600;
  color: var(--sl-text);
  overflow-wrap: anywhere;
}

/* A small mono label in the state's colour, the rail's way of saying how a
   step went (dispatch cards wear the same). */
.rail-tag {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.625rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--sl-wait);
  white-space: nowrap;
}

/* A question still waiting on the user steps off the rail into an amber
   tinted box, so it is the one thing in the log that asks to be read. */
.rail-entry--asking {
  margin-left: -0.75rem;
  padding: 0.75rem 0.75rem 0.75rem 2.75rem;
  border-radius: 0.875rem;
  background: color-mix(in srgb, var(--sl-wait) 7%, transparent);
  border: 1px solid color-mix(in srgb, var(--sl-wait) 22%, transparent);
}

.rail-entry--asking > .rail-node {
  left: 0.75rem;
  top: 0.75rem;
  box-shadow: 0 0 16px -2px var(--sl-wait);
}

/* The brief a thread opens on: the coordinator's words, quietly boxed. */
.brief-text {
  padding: 0.5rem 0.75rem;
  border-radius: 0.625rem;
  background: var(--sl-chip-bg, rgba(19, 26, 44, 0.035));
  font-size: 0.8125rem;
  line-height: 1.55;
  color: var(--sl-muted);
}

.brief-row .rail-name {
  font-weight: 500;
  color: var(--sl-faint);
}

.system-text {
  min-height: var(--node);
  display: flex;
  align-items: center;
  font-size: 0.75rem;
  line-height: 1.45;
  color: var(--sl-muted);
}

.status-row .agent-status {
  min-height: var(--node);
}

/* The agent's work flows directly on the panel background — no box, no label */
.assistant-response {
  font-size: 0.875rem;
  line-height: 1.6;
  /* Code blocks keep their own overflow-x so they scroll within their box,
     not the page. */
  overflow-wrap: anywhere;
  min-width: 0;
}

/* The hand-back line under a live dispatch. Deliberately the quietest thing
   in the turn: it is read once, the first time someone wonders whether they
   have to sit and wait, and it must never compete with the card above it or
   pass for the agent speaking — hence caption-sized muted text rather than
   the 14px ink the reply is set in. */
.handback {
  margin-top: 0.4375rem;
  padding-left: 0.0625rem;
  font-size: 0.6875rem;
  line-height: 1.5;
  color: rgba(19, 26, 44, 0.45);
}

.dark .handback {
  color: rgba(255, 255, 255, 0.4);
}

/* It leaves when the work lands, which is a small piece of news of its own —
   so it fades rather than blinking out from under the card that just turned
   green. */
.handback-enter-active,
.handback-leave-active {
  transition:
    opacity var(--iw-dur-3) var(--iw-ease-out),
    transform var(--iw-dur-3) var(--iw-ease-out);
}

.handback-enter-from,
.handback-leave-to {
  opacity: 0;
  transform: translateY(-2px);
}

@media (prefers-reduced-motion: reduce) {
  .handback-enter-active,
  .handback-leave-active {
    transition: none;
  }
}

/* Prose styling */
.prose {
  font-size: 0.875rem;
  line-height: 1.6;
  color: var(--sl-text);
  --tw-prose-body: var(--sl-text);
  --tw-prose-invert-body: var(--sl-text);
  --tw-prose-bold: var(--sl-text);
  --tw-prose-invert-bold: var(--sl-text);
  --tw-prose-headings: var(--sl-text);
  --tw-prose-invert-headings: var(--sl-text);
}

/* Markdown children arrive via v-html and never get the scope attribute,
   so anything targeting them needs :deep. Fenced code renders as a quiet
   navy-ink chip that scrolls within its own box. */
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

.prose p {
  margin-bottom: 0.75rem;
}

.prose p:last-child {
  margin-bottom: 0;
}

.prose h1, .prose h2, .prose h3, .prose h4 {
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  font-weight: 600;
  color: theme('colors.blue.950');
}

.dark .prose h1, .dark .prose h2, .dark .prose h3, .dark .prose h4 {
  color: theme('colors.white');
}

.prose ul, .prose ol {
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

/* Ink-tinted links instead of the typography plugin's gray */
.prose a {
  color: theme('colors.blue.700');
}

.dark .prose a {
  color: theme('colors.blue.300');
}

/* Ink-tinted list markers instead of the typography plugin's gray */
.prose ::marker {
  color: rgba(19, 26, 44, 0.4);
}

.dark .prose ::marker {
  color: rgba(219, 234, 254, 0.4);
}

.prose li {
  margin-bottom: 0.5rem;
}

/* Message animations. A message settles up into place with a trace of
   overshoot — closer to something being set down than to a fade. */
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

/* The indicator hands over to the streaming reply rather than blinking out */
.status-enter-active,
.status-leave-active {
  transition:
    opacity var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-2) var(--iw-ease-out);
}

.status-enter-from,
.status-leave-to {
  opacity: 0;
  transform: translateY(4px);
}

/* And each reading of it cross-fades in place */
.status-text-enter-active,
.status-text-leave-active {
  transition:
    opacity var(--iw-dur-1) var(--iw-ease-out),
    transform var(--iw-dur-1) var(--iw-ease-out);
}

.status-text-enter-from {
  opacity: 0;
  transform: translateY(3px);
}

.status-text-leave-to {
  opacity: 0;
  transform: translateY(-3px);
}

/* Agent activity indicator: a lit orb radiating a halo, next to status text
   with a shimmer sweeping across it. Same construction as the pane
   masthead's live dot — the orb holds steady while the halo travels — so
   "something is running" looks identical wherever it is reported. */
.status-orb {
  position: relative;
  flex-shrink: 0;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #93c5fd, #3b82f6);
  animation: orb-breathe 2.4s var(--iw-ease-ambient) infinite;
}

.status-orb::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: theme('colors.blue.500');
  animation: orb-halo 2.4s var(--iw-ease-ambient) infinite;
}

.dark .status-orb {
  background: radial-gradient(circle at 30% 30%, #bfdbfe, #60a5fa);
}

.dark .status-orb::after {
  background: theme('colors.blue.300');
}

@keyframes orb-breathe {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}

@keyframes orb-halo {
  0% { opacity: 0.4; transform: scale(1); }
  70%, 100% { opacity: 0; transform: scale(2.6); }
}

.status-shimmer {
  background-image: linear-gradient(
    100deg,
    rgba(19, 26, 44, 0.4) 20%,
    rgba(59, 130, 246, 0.95) 50%,
    rgba(19, 26, 44, 0.4) 80%
  );
  background-size: 200% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  animation: shimmer-sweep 2.2s linear infinite;
}

.dark .status-shimmer {
  background-image: linear-gradient(
    100deg,
    rgba(255, 255, 255, 0.35) 20%,
    rgba(255, 255, 255, 0.95) 50%,
    rgba(255, 255, 255, 0.35) 80%
  );
  background-size: 200% 100%;
}

@keyframes shimmer-sweep {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .status-orb,
  .status-orb::after,
  .status-shimmer,
  .animate-message-in,
  .animate-fade-in {
    animation: none;
  }

  .status-orb::after {
    opacity: 0;
  }

  .status-shimmer {
    background-clip: unset;
    -webkit-background-clip: unset;
    background-image: none;
    color: rgba(19, 26, 44, 0.55);
  }

  .dark .status-shimmer {
    color: rgba(219, 234, 254, 0.65);
  }
}

/* Prose styling for dark mode */
.prose-invert h1,
.prose-invert h2,
.prose-invert h3,
.prose-invert h4,
.prose-invert h5,
.prose-invert h6 {
  color: theme('colors.white');
  font-weight: 600;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}

.prose-invert p {
  color: rgba(219, 234, 254, 0.8);
  line-height: 1.6;
  margin-bottom: 0.75rem;
}

.prose-invert p:last-child {
  margin-bottom: 0;
}

.prose-invert strong {
  color: theme('colors.white');
  font-weight: 600;
}

.prose-invert code {
  color: theme('colors.orange.300');
  background-color: rgba(251, 146, 60, 0.1);
  padding: 0.2rem 0.4rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  border: 1px solid rgba(251, 146, 60, 0.2);
}

.prose-invert blockquote {
  color: rgba(191, 219, 254, 0.7);
  border-left-color: rgba(59, 130, 246, 0.5);
  border-left-width: 4px;
  padding-left: 1rem;
  font-style: italic;
  margin: 1rem 0;
}

.prose-invert ul,
.prose-invert ol {
  color: rgba(219, 234, 254, 0.8);
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

.prose-invert li {
  margin: 0.375rem 0;
  line-height: 1.5;
}

.prose-invert a {
  color: theme('colors.blue.300');
  text-decoration: underline;
  text-decoration-color: rgba(147, 197, 253, 0.4);
}

.prose-invert a:hover {
  color: theme('colors.blue.200');
  text-decoration-color: rgba(191, 219, 254, 0.6);
}
</style> 