<!--
  DispatchCard.vue — a subagent, as the main thread shows it.

  One card per subagent, and it is the WHOLE of what the main thread says
  about that subagent, from kickoff to sign-off. When the lead hands a job
  over, this card is the message: the job's name, the news that a subagent is
  on it, a few plain sentences on what it is doing, and a way through to
  watch it happen. When the work lands, the same card turns into "Subagent
  complete" and the subagent's own summary of what changed takes the place of
  those sentences. Nothing arrives below as a second telling — a kickoff line
  and a completion message for one piece of work is the same news printed
  twice, and the second copy is always somewhere else in the thread by the
  time it matters.

  So the card is read top-down as: where it stands (the state line, which is
  what anyone glancing at it wants), which job (the serif line under it), and
  a paragraph that is what it is doing while it runs and what came of it once
  it has. The job stays put through every state, because "complete" only
  means something next to what was asked for.

  That paragraph is folded away until asked for. Two lines answer "is it done
  yet?", which is the question nearly every glance at this card is asking,
  and several sentences per subagent stacked down a thread is a wall to
  scroll rather than a record to read. Open one and it stays open — including
  through the flip to complete, so watching a job through to its sign-off
  costs one click, not one per state.

  There is no separate title. A name and a description of the same job are the
  same sentence written twice, and the name was the one being clipped to an
  ellipsis on a phone. Everything here wraps and is read in full: a card that
  hides the end of its own sentence is worse than a taller card.

  Nothing on it is technical either — no file paths, no component names, no
  step-by-step. The person reading is running a business, not reviewing a
  diff. This card is the gist; the thread is the record.

  It borrows the crew ledger's state vocabulary (AgentInstanceCard): a rail
  down the left edge, ink travelling while live, so a card here and a card
  there report the same state the same way. The one place it departs is
  "done" — settled work recedes to a hairline in the ledger, but in the
  transcript a finished subagent is news, so it lands in an affirmative green.
-->
<template>
  <article :class="['dispatch-card', `dispatch-card--${state.tone}`]">
    <span class="dispatch-card__rail" aria-hidden="true"></span>

    <!-- The card at rest: where it stands, and which job. Everything here is
         one button, because at a glance these two lines ARE the card and a
         click anywhere on them opens the rest.

         The paragraph underneath is the long half — several sentences of it —
         and a thread of these at full height is a wall to scroll past when
         all most people want is "is it done yet?". So it starts closed, and
         opens on demand. -->
    <button
      type="button"
      class="dispatch-card__toggle"
      :disabled="!expandable"
      :aria-expanded="expandable ? expanded : undefined"
      :aria-controls="expandable ? bodyId : undefined"
      @click="expanded = !expanded"
    >
      <span class="dispatch-card__head">
        <span class="dispatch-card__chip">
          <i :class="state.icon"></i>
        </span>
        <span class="dispatch-card__status">{{ state.label }}</span>
        <i
          v-if="expandable"
          class="fas fa-chevron-down dispatch-card__caret"
          aria-hidden="true"
        ></i>
      </span>

      <!-- Which job, in the user's language. Under the state and in the brand
           serif, because it is the reading matter: present in every state,
           since a result means nothing without the job it answers. -->
      <span v-if="state.job" class="dispatch-card__job">{{ state.job }}</span>
    </button>

    <!-- The way through to the subagent's own thread. Its own control now
         that the card body toggles: one button cannot both open a panel and
         navigate away, and of the two, the summary is what people want far
         more often. Same mark the check-in queue uses for the same trip. -->
    <button
      type="button"
      class="dispatch-card__open"
      title="Open this subagent's thread"
      aria-label="Open this subagent's thread"
      @click="emit('open')"
    >
      <i class="fas fa-arrow-up-right-from-square" aria-hidden="true"></i>
    </button>

    <!-- The paragraph under the job. While the subagent runs it is the lead's
         overview of what it is doing; once it lands it is the subagent's own
         summary of the changes now in the app, or the question it stopped on
         — so the flip to "complete" changes the words here, not only the
         label above. -->
    <Transition name="dispatch-reveal">
      <p v-if="expandable && expanded" :id="bodyId" class="dispatch-card__result">
        {{ state.result }}
      </p>
    </Transition>
  </article>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { AgentInstance } from '../../../types/services'

/** Ties each card's toggle to the paragraph it opens (aria-controls needs a
 *  document-unique id, and a thread holds many of these). */
let nextBodyId = 0

const props = defineProps<{
  /** The task's title from the transcript. The card names its job from the
   *  live instance; this is what it falls back to in the window before the
   *  store has loaded one, so a reloaded thread is never a blank card. */
  title: string
  /** The live subagent behind this card, when the store knows about it. */
  instance?: AgentInstance | null
}>()

const emit = defineEmits<{ (e: 'open'): void }>()

/**
 * The subagent's own closing words, whole — its summary of the changes or the
 * question it stopped on. Never the clipped list-row preview: a question
 * missing its last clause cannot be answered, and a summary missing its last
 * sentence has failed at its one job. The preview is only the standby for a
 * DTO from before the summary field existed.
 */
function saidBy(instance: AgentInstance): string {
  return instance.lastAssistantSummary || instance.lastMessagePreview || ''
}

/** What a finished card says when the run signed off with nothing at all.
 *  "Subagent complete" over an empty space tells the owner nothing about
 *  their own app, so the card always says something and points at the one
 *  place the answer is. */
const NO_SIGN_OFF = 'It finished without saying what it changed — open it to see the work.'

/**
 * Where this subagent stands, as the things the card renders: a tone (which
 * drives every colour on it), an icon, the state in words, and the paragraph
 * under the job — what it is doing while live, what came of it once done.
 *
 * The job is deliberately not part of the switch: it is the same job in every
 * state, so it is read once, below, rather than repeated per branch.
 *
 * A live run beats every stored status — a subagent re-prompted after
 * finishing is working again whatever its last outcome was.
 */
const status = computed(() => {
  const instance = props.instance
  if (!instance) {
    return { tone: 'starting', icon: 'fas fa-hourglass-start', label: 'Subagent starting', result: '' }
  }
  if (instance.isProcessing) {
    return {
      tone: 'working',
      icon: 'fas fa-circle-notch fa-spin',
      label: 'Subagent working',
      // What it is doing: the lead's overview of the job, three to five plain
      // sentences written for the owner at dispatch. Not the agent's live
      // status ("Editing project files…") — that says how it is working,
      // which is exactly the kind of detail this card keeps out.
      result: instance.overview,
    }
  }
  switch (instance.reviewStatus) {
    case 'input':
      return {
        tone: 'asking',
        icon: 'fas fa-circle-question',
        label: 'Needs an answer from you',
        // The subagent stopped on ask_user, so its closing line is the
        // question itself — the same words the queue card above the composer
        // is waiting for an answer to.
        result: saidBy(instance),
      }
    case 'ready':
      // One of several takes on a brief the user asked to compare. The only
      // state left where finished work waits on a decision — a solo subagent
      // applies its own and never lands here.
      return {
        tone: 'asking',
        icon: 'fas fa-check',
        label: 'Subagent complete — one of your options',
        result: saidBy(instance) || NO_SIGN_OFF,
      }
    case 'failed':
      return {
        tone: 'stopped',
        icon: 'fas fa-triangle-exclamation',
        // Said as what happened to the app, not as an error code: the run
        // stopped and nothing it started was added, which is the whole of
        // what a business owner needs from this card.
        label: 'Stopped before finishing',
        // Whatever it managed to say before it died — often a partial reply,
        // and shown whole for the same reason a finished summary is: a
        // half-sentence is where the user finds out what did and did not
        // land. The reason it stopped is in the main thread's queue card.
        result: saidBy(instance),
      }
    case 'accepted':
      return {
        tone: 'done',
        icon: 'fas fa-check',
        // Applied, not offered: the changes are in the app already, which is
        // the whole point of handing the job over.
        label: 'Subagent complete',
        // What it did, in its own words: the run is over, so the last message
        // is its sign-off — four to six plain sentences about the changes,
        // written for exactly this spot (see TASK_AGENT_INSTRUCTIONS). This
        // is the whole of what most owners ever read about the run, so the
        // card always shows one, even when the run left none.
        result: saidBy(instance) || NO_SIGN_OFF,
      }
    case 'dismissed':
      return { tone: 'settled', icon: 'fas fa-xmark', label: 'Discarded', result: '' }
    default:
      // Dispatched, run not yet fired. The overview is already known, so the
      // card reads the same as it will a moment later when the run starts.
      return {
        tone: 'starting',
        icon: 'fas fa-hourglass-start',
        label: 'Subagent starting',
        result: instance.overview,
      }
  }
})

const bodyId = `dispatch-card-body-${nextBodyId++}`

/**
 * Whether the card is open. Closed to begin with in every state, the
 * finished one included: "Subagent complete" over the job's name is the
 * whole of what most people need from a card they have scrolled back to,
 * and the account of what changed is there for the asking.
 *
 * Once opened it stays open, including through the flip from working to
 * complete — someone who asked to watch this job is not asking to be shut
 * again the moment it lands.
 */
const expanded = ref(false)

const state = computed(() => ({
  ...status.value,
  // What this subagent is for, named the way the user would name it. The
  // title is the standby for the moment before the instance loads — shorter,
  // but never nothing.
  job: props.instance?.brief || props.title || 'Background subagent',
}))

/** Nothing to open when the run has said nothing yet: a discarded card, or
 *  a subagent still starting on a dispatch that carried no overview. */
const expandable = computed(() => !!state.value.result)
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
  /* Stacked, not two columns: the job is the card, and giving it the full
     width is what lets it be read whole on a phone rather than clipped into a
     column beside an icon. */
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

/* The disclosure: the state line and the job, as one target. Stripped of the
   button element's own styling so the card reads as a card — everything
   visible here is the card's. */
.dispatch-card__toggle {
  display: flex;
  flex-direction: column;
  gap: 0.3125rem;
  width: 100%;
  padding: 0;
  border: none;
  background: none;
  font: inherit;
  color: inherit;
  text-align: left;
  cursor: pointer;
  border-radius: var(--iw-r-sm);
}

/* Nothing to open — a discarded card, or a subagent that has not said
   anything yet. It still holds the state and the job; it just does not
   pretend there is more behind it. */
.dispatch-card__toggle:disabled {
  cursor: default;
}

.dispatch-card__toggle:focus-visible {
  outline: none;
  box-shadow: var(--iw-focus-ring);
}

.dispatch-card__toggle:active:not(:disabled) .dispatch-card__head {
  transform: scale(0.995);
  transition-duration: var(--iw-dur-1);
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

/* The state line: chip, where it stands, and the affordance that says there
   is more through here. One row, above the working state's edge glow, which
   would otherwise wash over it. */
.dispatch-card__head {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 0.4375rem;
  /* Room at the end of the row for the open-thread button, which floats over
     the card rather than sitting in this flow — nested buttons are not a
     thing, and the toggle owns the whole row. */
  padding-right: 1.375rem;
  transition: transform var(--iw-dur-2) var(--iw-ease-out);
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

/* Where it stands, in the state's own ink. Small caps: this is the label on
   the card, and the job below it is the reading matter. */
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
   no ellipsis — the whole thing, at any width. */
.dispatch-card__job {
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

.dark .dispatch-card__job {
  color: rgba(255, 255, 255, 0.86);
}

/* The paragraph under the job — what it is doing, then what came back. Set
   apart from the job by a hairline rather than a label: a rule reads as "and
   here is the substance" without spending a line on saying so. Also wraps in
   full.

   Sized as prose, not as a caption: an overview is three to five sentences
   and a sign-off four to six, and it is the part of the card the owner
   actually reads, so it gets a readable size and open leading. It still sits
   a step below the job line, which stays the card's heading. */
.dispatch-card__result {
  position: relative;
  z-index: 1;
  margin-top: 0.0625rem;
  padding-top: 0.375rem;
  border-top: 1px solid rgba(23, 37, 84, 0.08);
  font-size: 0.75rem;
  line-height: 1.55;
  color: rgba(23, 37, 84, 0.72);
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

/* The green stays in the rail, the chip and the status line, which is where
   the card announces itself. The sign-off underneath is a paragraph now, and
   several lines of saturated green read as a highlight to skim rather than
   text to read — so it takes a near-neutral ink, warmed just enough to belong
   to the green card it sits on. */
.dispatch-card--done .dispatch-card__result {
  border-top-color: rgba(22, 163, 74, 0.18);
  color: rgba(20, 65, 45, 0.82);
}

.dark .dispatch-card--done .dispatch-card__result {
  border-top-color: rgba(74, 222, 128, 0.2);
  color: rgba(219, 245, 230, 0.78);
}

/* The disclosure mark. Points down at a closed card and turns over as it
   opens, so the card says which way it is going without a word of label. */
.dispatch-card__caret {
  flex-shrink: 0;
  font-size: 0.5625rem;
  color: rgba(23, 37, 84, 0.3);
  transition:
    color var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-3) var(--iw-ease-out);
}

.dark .dispatch-card__caret {
  color: rgba(255, 255, 255, 0.3);
}

.dispatch-card:hover .dispatch-card__caret {
  color: rgba(23, 37, 84, 0.6);
}

.dark .dispatch-card:hover .dispatch-card__caret {
  color: rgba(255, 255, 255, 0.6);
}

.dispatch-card__toggle[aria-expanded='true'] .dispatch-card__caret {
  transform: rotate(180deg);
}

/* The trip to the subagent's own thread. Quiet by design: the summary below
   answers most of what anyone wants, and this is for the times it does not.
   Same mark, size and manners as the check-in queue's. */
.dispatch-card__open {
  position: absolute;
  top: 0.4375rem;
  right: 0.4375rem;
  z-index: 2;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.25rem;
  height: 1.25rem;
  border-radius: var(--iw-r-xs);
  font-size: 0.5625rem;
  color: rgba(23, 37, 84, 0.3);
  transition:
    background-color var(--iw-dur-2) var(--iw-ease-out),
    color var(--iw-dur-2) var(--iw-ease-out);
}

.dark .dispatch-card__open {
  color: rgba(255, 255, 255, 0.3);
}

.dispatch-card:hover .dispatch-card__open {
  color: rgba(23, 37, 84, 0.55);
}

.dark .dispatch-card:hover .dispatch-card__open {
  color: rgba(255, 255, 255, 0.55);
}

.dispatch-card__open:hover {
  background: rgba(23, 37, 84, 0.07);
  color: rgba(23, 37, 84, 0.8);
}

.dark .dispatch-card__open:hover {
  background: rgba(255, 255, 255, 0.09);
  color: rgba(255, 255, 255, 0.85);
}

.dispatch-card__open:focus-visible {
  outline: none;
  box-shadow: var(--iw-focus-ring);
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

/* Opening the card. The paragraph arrives rather than appearing: the layout
   settles at once (a card growing in slow motion under the pointer is worse
   than one that simply grew) and the text fades up into the space. */
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
  .dispatch-card__toggle:active:not(:disabled) .dispatch-card__head {
    transform: none;
  }

  .dispatch-card__caret {
    transition: none;
  }

  .dispatch-reveal-enter-active,
  .dispatch-reveal-leave-active {
    transition: none;
  }
}
</style>
