<!--
  DispatchCard.vue — a subagent, as it appears in the main thread.

  One card per task the lead handed off, and it answers exactly the questions
  the user has about it, in order: what is being done to my app, and is it
  done yet? So the card is a state line and a description of the job, and
  while the run is live that is the whole card. When it lands, one more thing
  arrives — what the subagent actually did — and the job it was given stays
  above it, because "complete" is only meaningful next to what was asked.

  There is no separate title. A name and a description of the same task are
  the same sentence written twice, and the name was the one being clipped to
  an ellipsis on a phone. Everything here wraps and is read in full: a card
  that hides the end of its own sentence is worse than a taller card.

  Nothing on it is technical either — no file paths, no component names, no
  step-by-step. The person reading is running a business, not reviewing a
  diff, and the full account (files, tool calls, the lot) is one click away in
  the subagent's own thread. This card is the gist; the thread is the record.

  It borrows the crew ledger's state vocabulary (AgentInstanceCard): a rail
  down the left edge, ink travelling while live, so a card here and a card
  there report the same state the same way. The one place it departs is
  "done" — settled work recedes to a hairline in the ledger, but in the
  transcript a finished task is news, so it lands in an affirmative green.
-->
<template>
  <button
    type="button"
    :class="['dispatch-card', `dispatch-card--${state.tone}`]"
    :title="`Open this subagent's thread`"
    @click="emit('open')"
  >
    <span class="dispatch-card__rail" aria-hidden="true"></span>

    <span class="dispatch-card__head">
      <span class="dispatch-card__chip">
        <i :class="state.icon"></i>
      </span>

      <!-- Where it stands -->
      <span class="dispatch-card__status">{{ state.label }}</span>

      <i class="fas fa-chevron-right dispatch-card__chevron" aria-hidden="true"></i>
    </span>

    <!-- The job, in the user's language. Present in every state, because it
         is what the card is about — while the work runs it is the only thing
         to say, and once the work lands it is what the result is a result
         OF. -->
    <span v-if="state.task" class="dispatch-card__task">{{ state.task }}</span>

    <!-- What came back: the summary of the changes when it finished, or the
         question when it stopped to ask. Only a finished (or stuck) subagent
         has one, which is exactly why its arrival reads as news. -->
    <span v-if="state.result" class="dispatch-card__result">{{ state.result }}</span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AgentInstance } from '../../../types/services'

const props = defineProps<{
  /** The task's title from the transcript. The card describes its work from
   *  the live instance; this is what it falls back to in the window before
   *  the store has loaded one, so a reloaded thread is never a blank card. */
  title: string
  /** The live subagent behind this card, when the store knows about it. */
  instance?: AgentInstance | null
}>()

const emit = defineEmits<{ (e: 'open'): void }>()

/**
 * Where this subagent stands, as the four things the card renders: a tone
 * (which drives every colour on it), an icon, the state in words, and — once
 * there is one — what came back.
 *
 * `task` is deliberately not part of the switch: the job is the same job in
 * every state, so it is read once, below, rather than repeated per branch.
 *
 * A live run beats every stored status — a task re-prompted after finishing is
 * working again whatever its last outcome was.
 */
const status = computed(() => {
  const instance = props.instance
  if (!instance) {
    return { tone: 'starting', icon: 'fas fa-hourglass-start', label: 'Starting…', result: '' }
  }
  if (instance.isProcessing) {
    return {
      tone: 'working',
      icon: 'fas fa-circle-notch fa-spin',
      label: 'Working on this now…',
      // Nothing has come back yet, and the agent's live status ("Editing
      // project files…") is not a result — it says how it is working, which
      // is exactly the kind of detail this card keeps out.
      result: '',
    }
  }
  switch (instance.reviewStatus) {
    case 'input':
      return {
        tone: 'asking',
        icon: 'fas fa-circle-question',
        label: 'Needs an answer from you',
        // The subagent stopped on ask_user, so its closing line is the
        // question itself. Whole, never the clipped list-row preview: a
        // question missing its last clause cannot be answered, and a summary
        // missing its last sentence has failed at its one job — the preview
        // is only the standby for a DTO from before the summary field.
        result: instance.lastAssistantSummary || instance.lastMessagePreview || '',
      }
    case 'ready':
      return {
        tone: 'asking',
        icon: 'fas fa-check',
        label: 'Subagent complete — waiting on you',
        result: instance.lastAssistantSummary || instance.lastMessagePreview || '',
      }
    case 'failed':
      return {
        tone: 'stopped',
        icon: 'fas fa-triangle-exclamation',
        // Said as what happened to the app, not as an error code: the run
        // stopped and nothing it started was added, which is the whole of
        // what a business owner needs from this card.
        label: 'Stopped before finishing',
        // Whatever it managed to say before it died — often a partial reply.
        // The reason it stopped is in the main thread's queue card.
        result: instance.lastMessagePreview || '',
      }
    case 'accepted':
      return {
        tone: 'done',
        icon: 'fas fa-check',
        label: 'Subagent complete',
        // What it did, in its own words: the run is over, so the last message
        // is its sign-off, written as a plain summary of the changes for
        // exactly this spot (see TASK_AGENT_INSTRUCTIONS).
        result: instance.lastAssistantSummary || instance.lastMessagePreview || '',
      }
    case 'dismissed':
      return { tone: 'settled', icon: 'fas fa-xmark', label: 'Discarded', result: '' }
    default:
      // Dispatched, run not yet fired.
      return { tone: 'starting', icon: 'fas fa-hourglass-start', label: 'Starting…', result: '' }
  }
})

const state = computed(() => ({
  ...status.value,
  // What this subagent was asked to do. The title is the standby for the
  // moment before the instance loads — shorter, but never nothing.
  task: props.instance?.brief || props.title || 'Background subagent',
}))
</script>

<style scoped>
/* ── The card ───────────────────────────────────────────────────────────── */

/* Every colour on the card comes from these four, so a state change is one
   block of overrides rather than a rule per element. */
.dispatch-card {
  --rail: rgba(23, 37, 84, 0.14);
  --status: rgba(23, 37, 84, 0.5);
  --chip-bg: rgba(23, 37, 84, 0.08);
  --chip-fg: rgba(23, 37, 84, 0.8);

  position: relative;
  /* Stacked, not two columns: the description is the card, and giving it the
     full width is what lets it be read whole on a phone rather than clipped
     into a column beside an icon. */
  display: flex;
  flex-direction: column;
  gap: 0.3125rem;
  width: 100%;
  padding: 0.5rem 0.625rem 0.5625rem 0.875rem;
  border-radius: var(--iw-r-lg);
  border: 1px solid rgba(23, 37, 84, 0.08);
  background: rgba(239, 246, 255, 0.5);
  text-align: left;
  overflow: hidden;
  cursor: pointer;
  transition:
    background-color var(--iw-dur-3) var(--iw-ease-out),
    border-color var(--iw-dur-3) var(--iw-ease-out),
    box-shadow var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-2) var(--iw-ease-out);
}

.dark .dispatch-card {
  --rail: rgba(255, 255, 255, 0.16);
  --status: rgba(219, 234, 254, 0.55);
  --chip-bg: rgba(243, 237, 226, 0.12);
  --chip-fg: rgba(243, 237, 226, 0.9);
  border-color: rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.04);
}

.dispatch-card:hover {
  border-color: rgba(23, 37, 84, 0.14);
  box-shadow: var(--iw-shadow-2);
  transform: translateY(-1px);
}

.dark .dispatch-card:hover {
  border-color: rgba(255, 255, 255, 0.2);
}

.dispatch-card:active {
  transform: translateY(0) scale(0.99);
  box-shadow: var(--iw-shadow-1);
  transition-duration: var(--iw-dur-1);
}

.dispatch-card:focus-visible {
  outline: none;
  box-shadow: var(--iw-focus-ring);
}

/* ── States ─────────────────────────────────────────────────────────────── */

/* Dispatched, run not yet fired: the rail is drawn but not filled. */
.dispatch-card--starting {
  --rail: repeating-linear-gradient(
    180deg,
    rgba(23, 37, 84, 0.3) 0 3px,
    transparent 3px 7px
  );
}

.dark .dispatch-card--starting {
  --rail: repeating-linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.3) 0 3px,
    transparent 3px 7px
  );
}

/* Live: ink travels down the rail and the left edge breathes — the same
   treatment a working agent gets in the crew ledger. */
.dispatch-card--working {
  --rail: rgba(37, 99, 235, 0.32);
  --status: theme('colors.blue.600');
  --chip-bg: rgba(59, 130, 246, 0.13);
  --chip-fg: theme('colors.blue.600');
}

.dark .dispatch-card--working {
  --rail: rgba(147, 197, 253, 0.3);
  --status: theme('colors.blue.300');
  --chip-bg: rgba(147, 197, 253, 0.16);
  --chip-fg: theme('colors.blue.300');
}

.dispatch-card--working::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 40%;
  pointer-events: none;
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.09) 0%, rgba(59, 130, 246, 0) 100%);
  animation: rail-breathe 3.2s var(--iw-ease-ambient) infinite;
}

.dark .dispatch-card--working::before {
  background: linear-gradient(90deg, rgba(147, 197, 253, 0.1) 0%, rgba(147, 197, 253, 0) 100%);
}

.dispatch-card--working .dispatch-card__rail::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    180deg,
    transparent 0%,
    theme('colors.blue.500') 40%,
    theme('colors.blue.400') 60%,
    transparent 100%
  );
  animation: rail-travel 2.6s var(--iw-ease-ambient) infinite;
}

.dark .dispatch-card--working .dispatch-card__rail::after {
  background: linear-gradient(
    180deg,
    transparent 0%,
    theme('colors.blue.300') 40%,
    theme('colors.blue.200') 60%,
    transparent 100%
  );
}

/* Wants the user — a question to answer or a draft to pick. Solid navy ink,
   the workspace's "this one is on you" mark. */
.dispatch-card--asking {
  --rail: theme('colors.blue.950');
  --status: rgba(23, 37, 84, 0.78);
  --chip-bg: rgba(23, 37, 84, 0.1);
  --chip-fg: theme('colors.blue.950');
  border-color: rgba(23, 37, 84, 0.16);
}

.dark .dispatch-card--asking {
  --rail: #f3ede2;
  --status: rgba(243, 237, 226, 0.85);
  --chip-bg: rgba(243, 237, 226, 0.16);
  --chip-fg: #f3ede2;
  border-color: rgba(255, 255, 255, 0.2);
}

/* Done. The ledger lets settled work recede, but here the flip from "working"
   to "complete, and here is what it did" is the single moment this card exists
   to report, so it arrives in green and says so — and plays a one-shot settle
   rather than simply being repainted. */
.dispatch-card--done {
  --rail: theme('colors.green.600');
  --status: theme('colors.green.700');
  --chip-bg: theme('colors.green.100');
  --chip-fg: theme('colors.green.700');
  border-color: rgba(22, 163, 74, 0.28);
  background: rgba(240, 253, 244, 0.85);
  animation: done-settle var(--iw-dur-4) var(--iw-ease-spring) both;
}

.dark .dispatch-card--done {
  --rail: theme('colors.green.400');
  --status: theme('colors.green.300');
  --chip-bg: rgba(74, 222, 128, 0.16);
  --chip-fg: theme('colors.green.300');
  border-color: rgba(74, 222, 128, 0.28);
  background: rgba(74, 222, 128, 0.07);
}

.dispatch-card--done:hover {
  border-color: rgba(22, 163, 74, 0.45);
}

.dark .dispatch-card--done:hover {
  border-color: rgba(74, 222, 128, 0.45);
}

/* A run that died. Warm rather than alarming: nothing was lost from the app
   (the work never touched it), so this is news to act on, not a fault to
   panic about. Same reading as the queue card's error rail. */
.dispatch-card--stopped {
  --rail: theme('colors.amber.500');
  --status: theme('colors.amber.700');
  --chip-bg: rgba(245, 158, 11, 0.14);
  --chip-fg: theme('colors.amber.600');
  border-color: rgba(245, 158, 11, 0.28);
  background: rgba(255, 251, 235, 0.75);
}

.dark .dispatch-card--stopped {
  --rail: theme('colors.amber.300');
  --status: theme('colors.amber.200');
  --chip-bg: rgba(252, 211, 77, 0.16);
  --chip-fg: theme('colors.amber.200');
  border-color: rgba(252, 211, 77, 0.26);
  background: rgba(252, 211, 77, 0.06);
}

.dispatch-card--stopped:hover {
  border-color: rgba(245, 158, 11, 0.45);
}

.dark .dispatch-card--stopped:hover {
  border-color: rgba(252, 211, 77, 0.42);
}

/* Discarded work recedes — it is a record, not news. */
.dispatch-card--settled {
  opacity: 0.7;
}

.dispatch-card--settled:hover {
  opacity: 1;
}

/* ── Parts ──────────────────────────────────────────────────────────────── */

.dispatch-card__rail {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 0.1875rem;
  background: var(--rail);
  transition: background-color var(--iw-dur-3) var(--iw-ease-out);
}

.dispatch-card__chip {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 1.5rem;
  height: 1.5rem;
  margin-top: 0.0625rem;
  border-radius: var(--iw-r-sm);
  background: var(--chip-bg);
  color: var(--chip-fg);
  font-size: 0.625rem;
  transition:
    background-color var(--iw-dur-3) var(--iw-ease-out),
    color var(--iw-dur-3) var(--iw-ease-out);
}

/* The state line: chip, words, and the affordance that says there is more
   through here. One row, above the working state's edge glow, which would
   otherwise wash over it. */
.dispatch-card__head {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 0.4375rem;
}

.dispatch-card__chip {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 1.25rem;
  height: 1.25rem;
  border-radius: var(--iw-r-sm);
  background: var(--chip-bg);
  color: var(--chip-fg);
  font-size: 0.5625rem;
  transition:
    background-color var(--iw-dur-3) var(--iw-ease-out),
    color var(--iw-dur-3) var(--iw-ease-out);
}

/* Where it stands, in the state's own ink. Small caps: this is a label on the
   card, and the description below it is the reading matter. */
.dispatch-card__status {
  flex: 1;
  min-width: 0;
  font-size: 0.625rem;
  font-weight: 650;
  line-height: 1.3;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  color: var(--status);
  transition: color var(--iw-dur-3) var(--iw-ease-out);
}

/* The job. Set in the brand serif like the crew ledger's byline, so what is
   being done to the app reads as the subject of the card. It wraps: no clamp,
   no ellipsis — the whole sentence, at any width. */
.dispatch-card__task {
  position: relative;
  z-index: 1;
  font-family: theme('fontFamily.display');
  font-variation-settings: 'opsz' 11, 'SOFT' 30, 'WONK' 1;
  font-size: 0.8125rem;
  font-weight: 550;
  line-height: 1.4;
  letter-spacing: -0.006em;
  color: rgba(23, 37, 84, 0.88);
  overflow-wrap: anywhere;
}

.dark .dispatch-card__task {
  color: rgba(255, 255, 255, 0.86);
}

/* What came back. Set apart from the job by a hairline rather than a label —
   a rule reads as "and then this happened" without spending a line on saying
   so. Also wraps in full. */
.dispatch-card__result {
  position: relative;
  z-index: 1;
  margin-top: 0.0625rem;
  padding-top: 0.375rem;
  border-top: 1px solid rgba(23, 37, 84, 0.08);
  font-size: 0.6875rem;
  line-height: 1.5;
  color: rgba(23, 37, 84, 0.7);
  overflow-wrap: anywhere;
}

.dark .dispatch-card__result {
  border-top-color: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.62);
}

/* On a finished card the result is the news, so it takes the state's ink
   rather than the muted grey a pending question sits in. */
.dispatch-card--stopped .dispatch-card__result {
  border-top-color: rgba(245, 158, 11, 0.22);
  color: rgba(180, 83, 9, 0.9);
}

.dark .dispatch-card--stopped .dispatch-card__result {
  border-top-color: rgba(252, 211, 77, 0.22);
  color: rgba(253, 230, 138, 0.8);
}

.dispatch-card--done .dispatch-card__result {
  border-top-color: rgba(22, 163, 74, 0.18);
  color: rgba(21, 128, 61, 0.9);
}

.dark .dispatch-card--done .dispatch-card__result {
  border-top-color: rgba(74, 222, 128, 0.2);
  color: rgba(134, 239, 172, 0.82);
}

.dispatch-card__chevron {
  flex-shrink: 0;
  font-size: 0.625rem;
  color: rgba(23, 37, 84, 0.3);
  transition:
    color var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-2) var(--iw-ease-out);
}

.dark .dispatch-card__chevron {
  color: rgba(255, 255, 255, 0.3);
}

.dispatch-card:hover .dispatch-card__chevron {
  color: rgba(23, 37, 84, 0.6);
  transform: translateX(2px);
}

.dark .dispatch-card:hover .dispatch-card__chevron {
  color: rgba(255, 255, 255, 0.6);
}

/* ── Motion ─────────────────────────────────────────────────────────────── */

@keyframes rail-travel {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100%); }
}

@keyframes rail-breathe {
  0%, 100% { opacity: 0.55; }
  50% { opacity: 1; }
}

/* The arrival. Work landing in the app should register even out of the corner
   of the eye, so the card takes a beat of extra height and settles back. */
@keyframes done-settle {
  0% { transform: scale(0.985); }
  45% { transform: scale(1.012); }
  100% { transform: none; }
}

@media (prefers-reduced-motion: reduce) {
  .dispatch-card--working::before {
    animation: none;
    opacity: 0.8;
  }

  .dispatch-card--working .dispatch-card__rail::after {
    animation: none;
    background: theme('colors.blue.500');
  }

  .dispatch-card--done {
    animation: none;
  }

  .dispatch-card:hover,
  .dispatch-card:active {
    transform: none;
  }
}
</style>
