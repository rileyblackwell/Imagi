<!--
  DispatchCard.vue — a subagent, as it appears in the main thread.

  One card per task the lead handed off. Whatever state it is in, it says the
  same three things: the task's name, what the work is in plain words, and
  where it stands. While the run is live the card is lit and moving and the
  plain words are the brief — what this subagent set out to do. When the run
  ends they become the subagent's own summary of what it did.

  Nothing on this card is technical: no file paths, no component names, no
  step-by-step. That is deliberate. The person reading it is running a
  business, not reviewing a diff, and the full account — files, tool calls,
  the lot — is one click away in the subagent's own thread. This card is the
  gist; the thread is the record.

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

    <span class="dispatch-card__chip">
      <i :class="state.icon"></i>
    </span>

    <span class="dispatch-card__body">
      <!-- The task's name -->
      <span class="dispatch-card__title">{{ title || 'Background subagent' }}</span>

      <!-- Where it stands -->
      <span class="dispatch-card__status">{{ state.label }}</span>

      <!-- The work in plain words: the brief while it runs, its summary once
           it is done, its question when it is stuck. A status line alone can
           be read without learning anything — this is the part that actually
           tells the user what is happening to their app. -->
      <span v-if="state.body" class="dispatch-card__detail">{{ state.body }}</span>
    </span>

    <i class="fas fa-chevron-right dispatch-card__chevron" aria-hidden="true"></i>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AgentInstance } from '../../../types/services'

const props = defineProps<{
  /** The task's title from the transcript — survives a reload even when the
   *  live instance has not loaded yet, so the card always names its work. */
  title: string
  /** The live subagent behind this card, when the store knows about it. */
  instance?: AgentInstance | null
}>()

const emit = defineEmits<{ (e: 'open'): void }>()

/**
 * Where this subagent stands, as the three things the card renders: a tone
 * (which drives every colour on the card), an icon, and a line of text.
 *
 * A live run beats every stored status — a task re-prompted after finishing is
 * working again whatever its last outcome was.
 */
const state = computed(() => {
  const instance = props.instance
  if (!instance) {
    return { tone: 'starting', icon: 'fas fa-hourglass-start', label: 'Starting…', body: '' }
  }
  if (instance.isProcessing) {
    return {
      tone: 'working',
      icon: 'fas fa-circle-notch fa-spin',
      label: 'Working on this now…',
      // What it set out to do. Deliberately the brief and not the agent's
      // live status ("Editing project files…") — that says how it is working,
      // which is exactly the kind of detail this card keeps out.
      body: instance.brief || '',
    }
  }
  switch (instance.reviewStatus) {
    case 'input':
      return {
        tone: 'asking',
        icon: 'fas fa-circle-question',
        // The subagent stopped on ask_user, so its closing line is the
        // question itself.
        label: 'Needs an answer from you',
        body: instance.lastMessagePreview || '',
      }
    case 'ready':
      return {
        tone: 'asking',
        icon: 'fas fa-check',
        label: 'Subagent complete — waiting on you',
        body: instance.lastMessagePreview || instance.brief || '',
      }
    case 'accepted':
      return {
        tone: 'done',
        icon: 'fas fa-check',
        label: 'Subagent complete',
        // What it did, in its own words. The run is over, so the last message
        // is its sign-off — written as a plain summary for exactly this spot
        // (see TASK_AGENT_INSTRUCTIONS). The brief is the standby for a task
        // whose sign-off never landed, so the card is never blank.
        body: instance.lastMessagePreview || instance.brief || '',
      }
    case 'dismissed':
      return { tone: 'settled', icon: 'fas fa-xmark', label: 'Discarded', body: '' }
    default:
      // Dispatched, run not yet fired: the brief is all there is to report.
      return {
        tone: 'starting',
        icon: 'fas fa-hourglass-start',
        label: 'Starting…',
        body: instance.brief || '',
      }
  }
})
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
  display: flex;
  align-items: flex-start;
  gap: 0.625rem;
  width: 100%;
  padding: 0.5rem 0.625rem 0.5rem 0.875rem;
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

/* Above the working state's edge glow, which would otherwise wash over it. */
.dispatch-card__body {
  position: relative;
  z-index: 1;
  flex: 1;
  min-width: 0;
}

/* The task itself. Set in the brand serif like the crew ledger's byline, so
   the thing being worked on reads as a name rather than a log line. */
.dispatch-card__title {
  display: block;
  font-family: theme('fontFamily.display');
  font-variation-settings: 'opsz' 11, 'SOFT' 30, 'WONK' 1;
  font-size: 0.8125rem;
  font-weight: 550;
  line-height: 1.3;
  letter-spacing: -0.006em;
  color: rgba(23, 37, 84, 0.88);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dark .dispatch-card__title {
  color: rgba(255, 255, 255, 0.86);
}

.dispatch-card__status {
  display: block;
  margin-top: 0.125rem;
  font-size: 0.6875rem;
  font-weight: 500;
  line-height: 1.35;
  color: var(--status);
  transition: color var(--iw-dur-3) var(--iw-ease-out);
}

/* Four lines holds the whole of a two-or-three-sentence summary at the widths
   this pane is usually dragged to; anything longer was never meant for the
   card and is why the thread is one click away. */
.dispatch-card__detail {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-top: 0.25rem;
  font-size: 0.6875rem;
  line-height: 1.45;
  color: rgba(23, 37, 84, 0.65);
}

.dark .dispatch-card__detail {
  color: rgba(255, 255, 255, 0.6);
}

/* On a finished card the detail line is the payload, so it takes the state's
   ink rather than the muted grey a pending question sits in. */
.dispatch-card--done .dispatch-card__detail {
  color: rgba(21, 128, 61, 0.85);
}

.dark .dispatch-card--done .dispatch-card__detail {
  color: rgba(134, 239, 172, 0.8);
}

/* While the run is live the same line carries the brief, which is context
   rather than news: two lines of it, a shade quieter, so the eye still goes
   to the status. It grows into the summary when the run lands. */
.dispatch-card--working .dispatch-card__detail,
.dispatch-card--starting .dispatch-card__detail {
  -webkit-line-clamp: 2;
  line-clamp: 2;
  opacity: 0.85;
}

.dispatch-card__chevron {
  position: relative;
  z-index: 1;
  flex-shrink: 0;
  align-self: center;
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
