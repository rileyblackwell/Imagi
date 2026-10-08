<!--
  DispatchCard.vue — a thread, as the coordinator's chat shows it.

  One card per thread, and it is the WHOLE of what the coordinator says about
  that thread, from kickoff to sign-off. When the coordinator hands a job
  over, this card is the message: where the work stands, which job, a
  paragraph on what it is doing, and the way into the thread. When the work
  lands, the same card turns "complete" and the thread's own summary of what
  changed takes the place of that paragraph. Nothing arrives below as a
  second telling.

  It wears the Spotlight card ("Lit"): a plain lit surface, the state in the
  site's marquee eyebrow (a diamond, the words, a hairline running off to the
  edge) in the state's colour, the job in the display face, and "Go to
  thread" ending on the coral-to-amber arrow — the one warm accent on the
  card, so the way in is never something to hunt for.

  The paragraph is folded away until asked for ("Details"). Two lines answer
  "is it done yet?", which is the question nearly every glance at this card
  is asking. Open one and it stays open, including through the flip to
  complete.

  A thread waiting on an answer is a different card, because it is asking
  for something rather than reporting. Its question is shown whole and is
  answered right here — one-tap choices when the thread offered them, or a
  typed answer — and the answer goes straight back to the thread, which picks
  the job up again. There is no "Go to thread" on it: nothing in the thread
  is needed to answer, and a way off the card only competes with the answer.

  A stopped card carries the way back ("Try again"). A run that died is never
  retried on its own — a failure that quietly restarts itself is a loop — so
  the reader decides.

  It hangs on the chat's rail (see ChatConversation): the node is the card's
  mark on the rail, filled in the state's colour — the workspace's live dot
  while it works, green when it lands, amber when it needs the user, red when
  it stopped — so a run of these can be scanned by colour alone.
-->
<template>
  <article :class="['dispatch-card', `dispatch-card--${state.tone}`, { 'dispatch-card--question': isQuestion }]">
    <!-- The card's node on the rail. Working wears the workspace's live dot,
         the same one as the status row under the chat. -->
    <span v-if="state.tone === 'working'" class="dispatch-card__chip dispatch-card__chip--live iw-live-node" aria-hidden="true">
      <span class="iw-live"></span>
    </span>
    <span v-else class="dispatch-card__chip" aria-hidden="true">
      <i :class="state.icon"></i>
    </span>

    <!-- Where it stands, as the marquee eyebrow -->
    <p class="dispatch-card__eyebrow">
      <span class="dispatch-card__status">{{ state.label }}</span>
      <span class="dispatch-card__rule" aria-hidden="true"></span>
    </p>

    <!-- Which job, in the user's language. Present in every state, since a
         result means nothing without the job it answers. -->
    <p class="dispatch-card__job">{{ state.job }}</p>

    <!-- A question is answered on the card: the question in full, then the
         answers. The answer goes back to the thread as its next message. -->
    <div v-if="isQuestion" class="dispatch-card__ask">
      <p class="dispatch-card__question">{{ state.result }}</p>
      <QuestionChoices
        v-if="questionOptions.length || questionVisual"
        :options="questionOptions"
        :visual="questionVisual"
        @pick="sendAnswer"
      />
      <form class="dispatch-card__answer" @submit.prevent="sendAnswer(answer)">
        <textarea
          v-model="answer"
          rows="1"
          class="dispatch-card__input"
          :placeholder="questionOptions.length ? 'Or type your own answer…' : 'Type your answer…'"
          aria-label="Your answer"
          @keydown.enter.exact.prevent="sendAnswer(answer)"
        ></textarea>
        <button
          type="submit"
          class="dispatch-card__send"
          :disabled="!answer.trim()"
          aria-label="Send answer"
        >
          <i class="fas fa-arrow-up" aria-hidden="true"></i>
        </button>
      </form>
    </div>

    <template v-else>
      <!-- The paragraph under the job: what it is doing while it runs, what
           came of it once it has. A stopped card shows it unfolded — it is
           short, and it is the part that says what did and did not land. -->
      <Transition name="dispatch-reveal">
        <p v-if="showResult" :id="bodyId" class="dispatch-card__result">{{ state.result }}</p>
      </Transition>

      <div class="dispatch-card__foot">
        <button
          v-if="retryable"
          type="button"
          class="dispatch-card__retry"
          @click="emit('retry')"
        >
          <i class="fas fa-rotate-right" aria-hidden="true"></i>
          Try again
        </button>
        <button
          v-else-if="expandable"
          type="button"
          class="dispatch-card__toggle"
          :aria-expanded="expanded"
          :aria-controls="bodyId"
          @click="expanded = !expanded"
        >
          {{ expanded ? 'Hide details' : 'Details' }}
          <i class="fas fa-chevron-down dispatch-card__caret" aria-hidden="true"></i>
        </button>

        <button type="button" class="dispatch-card__go" @click="emit('open')">
          Go to thread
          <span class="dispatch-card__orb" aria-hidden="true"><i class="fas fa-arrow-right"></i></span>
        </button>
      </div>
    </template>
  </article>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import QuestionChoices from './QuestionChoices.vue'
import type { AgentInstance } from '../../../types/services'

/** Ties each card's toggle to the paragraph it opens (aria-controls needs a
 *  document-unique id, and a chat holds many of these). */
let nextBodyId = 0

const props = withDefaults(defineProps<{
  /** The task's title from the transcript. The card names its job from the
   *  live instance; this is what it falls back to in the window before the
   *  store has loaded one, so a reloaded chat is never a blank card. */
  title: string
  /** The live thread behind this card, when the store knows about it. */
  instance?: AgentInstance | null
  /** The one-tap answers the thread offered with its question, if any */
  questionOptions?: string[]
  /** The sketch the thread offered with its question, if any */
  questionVisual?: string
}>(), { instance: null, questionOptions: () => [], questionVisual: '' })

const emit = defineEmits<{
  /** Go to this thread */
  (e: 'open'): void
  /** Run this failed thread again — the user's call, never the card's */
  (e: 'retry'): void
  /** The user answered the thread's question, here on the card */
  (e: 'answer', text: string): void
}>()

/**
 * The thread's own closing words, whole — its summary of the changes or the
 * question it stopped on. Never the clipped list-row preview: a question
 * missing its last clause cannot be answered, and a summary missing its last
 * sentence has failed at its one job. The preview is only the standby for a
 * DTO from before the summary field existed.
 */
function saidBy(instance: AgentInstance): string {
  return instance.lastAssistantSummary || instance.lastMessagePreview || ''
}

/** What a finished card says when the run signed off with nothing at all.
 *  "Thread complete" over an empty space tells the owner nothing about
 *  their own app, so the card always says something and points at the one
 *  place the answer is. */
const NO_SIGN_OFF = 'It finished without saying what it changed — open it to see the work.'

/** What a stopped card says when the run died before it said anything. The
 *  reason it stopped is in the coordinator's queue; this is what it means
 *  for the app, which is the part the owner needs to hear from the card. */
const NO_LAST_WORDS =
  'It stopped before it could say anything. Nothing it started has been added to the app.'

/** A question the thread asked without leaving its words behind (a DTO from
 *  before summaries were stored). The card still has to be answerable. */
const NO_QUESTION_TEXT = 'This thread needs an answer from you before it can carry on.'

/**
 * Where this thread stands, as the things the card renders: a tone (which
 * drives every colour on it), an icon for the rail node, the state in words,
 * and the paragraph under the job — what it is doing while live, what came
 * of it once done.
 *
 * A live run beats every stored status — a thread re-prompted after
 * finishing is working again whatever its last outcome was.
 */
const status = computed(() => {
  const instance = props.instance
  if (!instance) {
    return { tone: 'starting', icon: 'fas fa-hourglass-start', label: 'Thread starting', result: '' }
  }
  if (instance.isProcessing) {
    return {
      tone: 'working',
      icon: '',
      label: 'Thread working',
      // What it is doing: the coordinator's overview of the job, three to
      // five plain sentences written for the owner at dispatch. Not the
      // agent's live status ("Editing project files…") — that says how it
      // is working, which is exactly the kind of detail this card keeps out.
      result: instance.overview,
    }
  }
  switch (instance.reviewStatus) {
    case 'input':
      return {
        tone: 'asking',
        icon: 'fas fa-question',
        label: 'Needs an answer from you',
        // The thread stopped on ask_user, so its closing line is the
        // question itself.
        result: saidBy(instance) || NO_QUESTION_TEXT,
      }
    case 'ready':
      // One of several takes on a brief the user asked to compare. The only
      // state left where finished work waits on a decision.
      return {
        tone: 'asking',
        icon: 'fas fa-check',
        label: 'Thread complete — one of your options',
        result: saidBy(instance) || NO_SIGN_OFF,
      }
    case 'failed':
      return {
        tone: 'stopped',
        icon: 'fas fa-exclamation',
        label: 'Stopped before finishing',
        // Whatever it managed to say before it died, shown whole: a
        // half-sentence is where the user finds out what did and did not
        // land.
        result: saidBy(instance) || NO_LAST_WORDS,
      }
    case 'accepted':
      return {
        tone: 'done',
        icon: 'fas fa-check',
        // Applied, not offered: the changes are in the app already.
        label: 'Thread complete',
        result: saidBy(instance) || NO_SIGN_OFF,
      }
    case 'dismissed':
      return { tone: 'settled', icon: 'fas fa-xmark', label: 'Discarded', result: '' }
    default:
      // Dispatched, run not yet fired. The overview is already known, so the
      // card reads the same as it will a moment later when the run starts.
      return { tone: 'starting', icon: 'fas fa-hourglass-start', label: 'Thread starting', result: instance.overview }
  }
})

const bodyId = `dispatch-card-body-${nextBodyId++}`

/**
 * Whether the paragraph is open. Closed to begin with, the finished card
 * included: "Thread complete" over the job's name is the whole of what most
 * people need from a card they have scrolled back to. Once opened it stays
 * open, including through the flip from working to complete.
 */
const expanded = ref(false)

const state = computed(() => ({
  ...status.value,
  // What this thread is for, named the way the user would name it. The
  // title is the standby for the moment before the instance loads.
  job: props.instance?.brief || props.title || 'Thread',
}))

/** Waiting on the user's answer: the card that asks rather than reports. */
const isQuestion = computed(
  () => !!props.instance && !props.instance.isProcessing && props.instance.reviewStatus === 'input'
)

/** A run that died, and is not already running again. */
const retryable = computed(
  () => !!props.instance && !props.instance.isProcessing && props.instance.reviewStatus === 'failed'
)

/** Nothing to open when the run has said nothing yet: a discarded card, or
 *  a thread still starting on a dispatch that carried no overview. */
const expandable = computed(() => !!state.value.result)

/** A stopped card shows what happened without a fold — the Try again button
 *  takes the fold's place, and the reader needs both. */
const showResult = computed(() => !!state.value.result && (retryable.value || expanded.value))

const answer = ref('')

function sendAnswer(text: string) {
  const reply = text.trim()
  if (!reply) return
  answer.value = ''
  emit('answer', reply)
}
</script>

<style scoped>
/* ── The card ───────────────────────────────────────────────────────────── */

/* Every state colour on the card comes from --st, so a state change is one
   line rather than a rule per element. The surface itself stays neutral —
   the Spotlight card — and the state lives in the node and the eyebrow. */
.dispatch-card {
  --st: var(--sl-faint, rgba(19, 26, 44, 0.5));

  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0.3125rem;
  width: 100%;
  padding: 0.6875rem 0.8125rem 0.625rem;
  border-radius: 0.875rem;
  border: 1px solid var(--sl-line-strong, rgba(19, 26, 44, 0.15));
  background: var(--sl-card-bg, #ffffff);
  box-shadow: var(--sl-card-shadow, none);
  text-align: left;
  transition:
    border-color var(--iw-dur-3) var(--iw-ease-out),
    box-shadow var(--iw-dur-2) var(--iw-ease-out);
}

/* A short branch from the rail to the card, so the card reads as a step
   hanging off the line like everything else in the log. */
.dispatch-card::before {
  content: '';
  position: absolute;
  left: -0.75rem;
  top: 1.25rem;
  width: 0.75rem;
  height: 1px;
  background: color-mix(in srgb, var(--st) 45%, transparent);
  pointer-events: none;
}

/* ── States ─────────────────────────────────────────────────────────────── */

/* Dispatched, run not yet fired: drawn but not lit. */
.dispatch-card--starting {
  border-style: dashed;
  background: var(--sl-chip-bg, rgba(19, 26, 44, 0.035));
  box-shadow: none;
}

/* Working: a faint blue light falling on the top edge, the stage lit for
   the work in progress. */
.dispatch-card--working {
  --st: var(--sl-work);
  background:
    radial-gradient(90% 3.75rem at 30% 0, color-mix(in srgb, var(--sl-work) 13%, transparent), transparent 80%),
    var(--sl-card-bg, #ffffff);
}

.dispatch-card--asking {
  --st: var(--sl-wait);
}

/* A question waiting on the user: the card that asks rather than reports,
   so its edge warms to amber to be found in a scroll of quiet cards. */
.dispatch-card--question {
  border-color: color-mix(in srgb, var(--sl-wait) 45%, transparent);
  background:
    radial-gradient(90% 3.75rem at 30% 0, color-mix(in srgb, var(--sl-wait) 12%, transparent), transparent 80%),
    var(--sl-card-bg, #ffffff);
}

/* Done. The flip from "working" to "complete" is the single moment this card
   exists to report, so it plays a one-shot settle rather than simply being
   repainted. */
.dispatch-card--done {
  --st: var(--sl-ok);
  animation: done-settle var(--iw-dur-4) var(--iw-ease-spring) both;
}

.dispatch-card--stopped {
  --st: var(--sl-bad);
}

/* Discarded work recedes — it is a record, not news. */
.dispatch-card--settled {
  opacity: 0.7;
}

.dispatch-card--settled:hover {
  opacity: 1;
}

/* ── The rail node ──────────────────────────────────────────────────────── */

/* A filled circle in the state's colour, punched out of the rail by a ring
   of the floor. Placed back across the rail's gutter (the 2rem every rail
   entry is indented). */
.dispatch-card__chip {
  position: absolute;
  left: -2rem;
  top: 0.625rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.25rem;
  height: 1.25rem;
  border-radius: 50%;
  background: var(--st);
  color: rgb(var(--app-canvas, 255 255 255));
  font-size: 0.5625rem;
  box-shadow:
    0 0 0 4px rgb(var(--app-canvas, 255 255 255)),
    0 0 14px -3px var(--st);
  transition: background-color var(--iw-dur-3) var(--iw-ease-out);
}

/* Working: the workspace's live dot in its node (styles/workspace.css). */
.dispatch-card__chip--live {
  display: grid;
  border: 1.5px solid color-mix(in srgb, var(--sl-work) 55%, transparent);
  background: color-mix(in srgb, var(--sl-work) 10%, rgb(var(--app-canvas, 255 255 255)));
  box-shadow: 0 0 0 4px rgb(var(--app-canvas, 255 255 255));
}

.dispatch-card--starting .dispatch-card__chip,
.dispatch-card--settled .dispatch-card__chip {
  background: rgb(var(--app-canvas, 255 255 255));
  border: 1.5px dashed var(--sl-line-strong, rgba(19, 26, 44, 0.15));
  color: var(--sl-faint);
  box-shadow: 0 0 0 4px rgb(var(--app-canvas, 255 255 255));
}

/* ── Parts ──────────────────────────────────────────────────────────────── */

/* The marquee eyebrow: a diamond, the state, a hairline fading to the edge —
   the site's page eyebrow, in the state's colour. */
.dispatch-card__eyebrow {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 1rem;
}

.dispatch-card__eyebrow::before {
  content: '';
  flex-shrink: 0;
  width: 0.3125rem;
  height: 0.3125rem;
  transform: rotate(45deg);
  background: var(--st);
}

.dispatch-card__status {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.625rem;
  font-weight: 500;
  line-height: 1.3;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--st);
}

.dispatch-card__rule {
  flex: 1;
  min-width: 1rem;
  height: 1px;
  background: linear-gradient(90deg, color-mix(in srgb, var(--st) 55%, transparent), transparent);
}

/* The job, in the display face: what is being done to the app is the
   subject of the card. It wraps: no clamp, no ellipsis. */
.dispatch-card__job {
  font-family: var(--sl-font-display, theme('fontFamily.display'));
  font-size: 0.9375rem;
  font-weight: 600;
  line-height: 1.35;
  letter-spacing: -0.012em;
  color: var(--sl-text);
  overflow-wrap: anywhere;
}

/* The paragraph under the job, sized as prose: it is the part of the card
   the owner actually reads. */
.dispatch-card__result,
.dispatch-card__question {
  font-size: 0.8125rem;
  line-height: 1.55;
  color: var(--sl-muted);
  overflow-wrap: anywhere;
  white-space: pre-wrap;
}

/* The question is the point of its card, so it reads in full ink. */
.dispatch-card__question {
  color: var(--sl-text);
}

.dispatch-card__foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-top: 0.1875rem;
}

/* The fold, named. Small and quiet — it is an offer, not the news. */
.dispatch-card__toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.3125rem;
  padding: 0.25rem 0;
  border: none;
  background: none;
  font: inherit;
  font-size: 0.6875rem;
  font-weight: 550;
  color: var(--sl-faint);
  cursor: pointer;
  border-radius: var(--iw-r-sm);
  transition: color var(--iw-dur-2) var(--iw-ease-out);
}

.dispatch-card__toggle:hover {
  color: var(--sl-text);
}

.dispatch-card__caret {
  font-size: 0.5rem;
  transition: transform var(--iw-dur-3) var(--iw-ease-out);
}

.dispatch-card__toggle[aria-expanded='true'] .dispatch-card__caret {
  transform: rotate(180deg);
}

/* The way into the thread: a quiet pill ending on the lit arrow. Always at
   the right of the foot, so it is in the same place on every card. */
.dispatch-card__go {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-left: auto;
  padding: 0.125rem 0.125rem 0.125rem 0.625rem;
  border-radius: 9999px;
  border: 1px solid var(--sl-line-strong, rgba(19, 26, 44, 0.15));
  background: none;
  font: inherit;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--sl-text);
  cursor: pointer;
  transition:
    border-color var(--iw-dur-2) var(--iw-ease-out),
    box-shadow var(--iw-dur-2) var(--iw-ease-out);
}

.dispatch-card__orb {
  display: grid;
  place-items: center;
  width: 1.375rem;
  height: 1.375rem;
  border-radius: 9999px;
  background: var(--sl-grad);
  color: var(--sl-on-accent, #1a0e08);
  font-size: 0.625rem;
  box-shadow: 0 4px 12px -4px rgba(236, 90, 50, 0.6);
}

.dispatch-card__orb i {
  transition: transform var(--iw-dur-2) var(--iw-ease-out);
}

.dispatch-card__go:hover {
  border-color: color-mix(in srgb, var(--sl-amber, #ee8c10) 50%, transparent);
  box-shadow: 0 0 18px -6px var(--sl-glow, rgba(255, 120, 80, 0.3));
}

.dispatch-card__go:hover .dispatch-card__orb i {
  transform: translateX(1px);
}

/* The retry, on a stopped card: the workspace's lit pill, because it is the
   one thing on the card the reader most needs to reach. */
.dispatch-card__retry {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  border: none;
  background: var(--sl-grad);
  box-shadow: var(--sl-btn-shadow);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--sl-on-accent, #1a0e08);
  cursor: pointer;
  transition:
    box-shadow var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-1) var(--iw-ease-out);
}

.dispatch-card__retry i {
  font-size: 0.625rem;
  transition: transform var(--iw-dur-3) var(--iw-ease-out);
}

.dispatch-card__retry:hover {
  box-shadow: var(--sl-btn-shadow-hover);
}

.dispatch-card__retry:hover i {
  transform: rotate(90deg);
}

.dispatch-card__retry:active {
  transform: scale(0.97);
}

/* ── The answer ─────────────────────────────────────────────────────────── */

.dispatch-card__ask {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.dispatch-card__answer {
  display: flex;
  align-items: flex-end;
  gap: 0.375rem;
  margin-top: 0.5rem;
  padding: 0.25rem 0.25rem 0.25rem 0.625rem;
  border-radius: 0.75rem;
  border: 1px solid var(--sl-line-strong, rgba(19, 26, 44, 0.15));
  background: var(--sl-surface, #ffffff);
  transition: border-color var(--iw-dur-2) var(--iw-ease-out);
}

.dispatch-card__answer:focus-within {
  border-color: color-mix(in srgb, var(--sl-wait) 55%, transparent);
}

.dispatch-card__input {
  flex: 1;
  min-width: 0;
  min-height: 1.75rem;
  max-height: 8rem;
  padding: 0.3125rem 0;
  border: none;
  background: none;
  resize: none;
  field-sizing: content;
  font: inherit;
  font-size: 0.8125rem;
  line-height: 1.45;
  color: var(--sl-text);
  outline: none;
}

.dispatch-card__input::placeholder {
  color: var(--sl-faint);
}

.dispatch-card__send {
  flex-shrink: 0;
  display: grid;
  place-items: center;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 9999px;
  border: none;
  background: var(--sl-grad);
  color: var(--sl-on-accent, #1a0e08);
  font-size: 0.6875rem;
  cursor: pointer;
  box-shadow: 0 4px 12px -4px rgba(236, 90, 50, 0.6);
  transition: opacity var(--iw-dur-2) var(--iw-ease-out);
}

.dispatch-card__send:disabled {
  cursor: default;
  background: var(--sl-chip-bg-hover, rgba(19, 26, 44, 0.065));
  color: var(--sl-faint);
  box-shadow: none;
}

.dispatch-card__toggle:focus-visible,
.dispatch-card__go:focus-visible,
.dispatch-card__retry:focus-visible,
.dispatch-card__send:focus-visible {
  outline: none;
  box-shadow: var(--iw-focus-ring);
}

/* ── Motion ─────────────────────────────────────────────────────────────── */

@keyframes done-settle {
  0% { transform: scale(0.985); }
  45% { transform: scale(1.012); }
  100% { transform: none; }
}

.dispatch-reveal-enter-active,
.dispatch-reveal-leave-active {
  transition:
    opacity var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-2) var(--iw-ease-out);
}

.dispatch-reveal-enter-from,
.dispatch-reveal-leave-to {
  opacity: 0;
  transform: translateY(-3px);
}

@media (prefers-reduced-motion: reduce) {
  .dispatch-card--done {
    animation: none;
  }

  .dispatch-card__caret,
  .dispatch-card__orb i,
  .dispatch-card__retry,
  .dispatch-card__retry i,
  .dispatch-reveal-enter-active,
  .dispatch-reveal-leave-active {
    transition: none;
    transform: none;
  }
}
</style>
