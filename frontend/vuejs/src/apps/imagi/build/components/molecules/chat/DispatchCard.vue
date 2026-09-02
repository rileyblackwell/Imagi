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

  The fold says what it holds ("See summary", "See what it's doing") rather
  than leaving a bare caret to be guessed at, and the way into the subagent's
  own step-by-step waits inside it, named. Both were once unlabelled marks in
  the corner, which is the same mistake twice: an icon can say that there is
  more, but never what, so the only way to find out is to press it and see.

  There is no separate title. A name and a description of the same job are the
  same sentence written twice, and the name was the one being clipped to an
  ellipsis on a phone. Everything here wraps and is read in full: a card that
  hides the end of its own sentence is worse than a taller card.

  Nothing on it is technical either — no file paths, no component names, no
  step-by-step. The person reading is running a business, not reviewing a
  diff. This card is the gist; the thread is the record.

  A stopped card has one more thing on it: the way back. A subagent whose run
  died is never retried on its own — a failure that quietly restarts itself
  is a loop, and a card that never gets to say "stopped" — so the card says
  so, and puts "Try again" under it for the person reading to decide.

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
      </span>

      <!-- Which job, in the user's language. Under the state and in the brand
           serif, because it is the reading matter: present in every state,
           since a result means nothing without the job it answers. -->
      <span v-if="state.job" class="dispatch-card__job">{{ state.job }}</span>

      <!-- What the fold holds, said in words. A bare caret is a puzzle: it
           marks that something is hidden without ever saying what, so the
           only way to find out is to press it. Naming the thing is the
           difference between an invitation and a guess. -->
      <span v-if="expandable" class="dispatch-card__reveal">
        <span>{{ revealLabel }}</span>
        <i class="fas fa-chevron-down dispatch-card__caret" aria-hidden="true"></i>
      </span>
    </button>

    <!-- The paragraph under the job. While the subagent runs it is the lead's
         overview of what it is doing; once it lands it is the subagent's own
         summary of the changes now in the app, or the question it stopped on
         — so the flip to "complete" changes the words here, not only the
         label above. -->
    <Transition name="dispatch-reveal">
      <div v-if="expandable && expanded" :id="bodyId">
        <p class="dispatch-card__result">{{ state.result }}</p>

        <!-- The way through to the subagent's own thread, for the reader who
             has just finished the summary and wants the working. Named rather
             than drawn: an unlabelled corner icon was a trip nobody could see
             the point of taking. -->
        <button type="button" class="dispatch-card__more" @click="emit('open')">
          See step by step
          <i class="fas fa-arrow-right" aria-hidden="true"></i>
        </button>
      </div>
    </Transition>

    <!-- The way back for a run that died. One press and the same subagent
         picks the job up again — the card flips straight to "starting", so
         the press is seen to have landed. Outside the fold, because a card
         that stopped before saying anything has no fold, and the retry is
         the one thing on it the reader most needs to reach. -->
    <div v-if="retryable" class="dispatch-card__actions">
      <button type="button" class="dispatch-card__retry" @click="emit('retry')">
        <i class="fas fa-rotate-right" aria-hidden="true"></i>
        Try again
      </button>
    </div>
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

const emit = defineEmits<{
  (e: 'open'): void
  /** Run this failed subagent again — the user's call, never the card's */
  (e: 'retry'): void
}>()

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

/** What a stopped card says when the run died before it said anything. The
 *  reason it stopped is in the main thread's queue; this is what it means
 *  for the app, which is the part the owner needs to hear from the card. */
const NO_LAST_WORDS =
  'It stopped before it could say anything. Nothing it started has been added to the app.'

/* What the fold is called in each state — the noun in "See ___". Named for
   what is actually inside it, so the invitation is never a surprise: a
   running subagent has its plan for the job, a finished one has its account
   of the changes, and a stuck one has the question or the bad news. */
const WHAT_ITS_DOING = "what it's doing"
const THE_SUMMARY = 'summary'

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
    return {
      tone: 'starting',
      icon: 'fas fa-hourglass-start',
      label: 'Subagent starting',
      result: '',
      reveal: WHAT_ITS_DOING,
    }
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
      reveal: WHAT_ITS_DOING,
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
        reveal: 'the question',
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
        reveal: THE_SUMMARY,
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
        result: saidBy(instance) || NO_LAST_WORDS,
        reveal: 'what happened',
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
        reveal: THE_SUMMARY,
      }
    case 'dismissed':
      return {
        tone: 'settled',
        icon: 'fas fa-xmark',
        label: 'Discarded',
        result: '',
        reveal: THE_SUMMARY,
      }
    default:
      // Dispatched, run not yet fired. The overview is already known, so the
      // card reads the same as it will a moment later when the run starts.
      return {
        tone: 'starting',
        icon: 'fas fa-hourglass-start',
        label: 'Subagent starting',
        result: instance.overview,
        reveal: WHAT_ITS_DOING,
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

/** A run that died, and is not already running again. */
const retryable = computed(
  () => !!props.instance && !props.instance.isProcessing && props.instance.reviewStatus === 'failed'
)

/** The fold, in words: what opening it gets you, or what closing it puts
 *  away. Always names the thing — never a bare "more". */
const revealLabel = computed(
  () => `${expanded.value ? 'Hide' : 'See'} ${state.value.reveal}`
)
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
/* Takes its ink from the label it sits beside — the two are one control, and
   the caret's only job here is to say which way this is about to go. */
.dispatch-card__caret {
  flex-shrink: 0;
  font-size: 0.5rem;
  transition: transform var(--iw-dur-3) var(--iw-ease-out);
}

.dispatch-card__toggle[aria-expanded='true'] .dispatch-card__caret {
  transform: rotate(180deg);
}

/* The fold, named. Small and quiet — it is an offer, not the news — but it
   is words, because a caret alone never says what it is hiding. */
.dispatch-card__reveal {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  gap: 0.3125rem;
  margin-top: 0.0625rem;
  font-size: 0.625rem;
  font-weight: 550;
  letter-spacing: 0.005em;
  color: rgba(23, 37, 84, 0.5);
  transition: color var(--iw-dur-2) var(--iw-ease-out);
}

.dark .dispatch-card__reveal {
  color: rgba(255, 255, 255, 0.45);
}

.dispatch-card:hover .dispatch-card__reveal {
  color: rgba(23, 37, 84, 0.8);
}

.dark .dispatch-card:hover .dispatch-card__reveal {
  color: rgba(255, 255, 255, 0.8);
}

/* The trip to the subagent's own thread, at the end of what it had to say —
   where someone who has just read the summary and wants the working is
   already looking. */
.dispatch-card__more {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  margin-top: 0.5rem;
  padding: 0.1875rem 0.5rem 0.1875rem 0.5rem;
  margin-left: -0.5rem;
  border-radius: var(--iw-r-sm);
  font-size: 0.625rem;
  font-weight: 550;
  color: rgba(23, 37, 84, 0.55);
  transition:
    background-color var(--iw-dur-2) var(--iw-ease-out),
    color var(--iw-dur-2) var(--iw-ease-out);
}

.dark .dispatch-card__more {
  color: rgba(255, 255, 255, 0.5);
}

.dispatch-card__more i {
  font-size: 0.5625rem;
  transition: transform var(--iw-dur-2) var(--iw-ease-out);
}

.dispatch-card__more:hover {
  background: rgba(23, 37, 84, 0.06);
  color: rgba(23, 37, 84, 0.85);
}

.dark .dispatch-card__more:hover {
  background: rgba(255, 255, 255, 0.07);
  color: rgba(255, 255, 255, 0.9);
}

.dispatch-card__more:hover i {
  transform: translateX(2px);
}

.dispatch-card__more:focus-visible {
  outline: none;
  box-shadow: var(--iw-focus-ring);
}

/* The retry, on a stopped card. A hairline pill in the card's own amber, the
   workspace's compact-control shape: outlined rather than filled, because it
   is an offer on a notice, not the notice itself — but the one control on the
   card that is a control, so it gets a real border and a real press. */
.dispatch-card__actions {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.125rem;
}

.dispatch-card__retry {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.3125rem 0.75rem;
  border-radius: 9999px;
  border: 1px solid rgba(217, 119, 6, 0.4);
  background: rgba(255, 255, 255, 0.55);
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.005em;
  color: theme('colors.amber.800');
  cursor: pointer;
  transition:
    background-color var(--iw-dur-2) var(--iw-ease-out),
    border-color var(--iw-dur-2) var(--iw-ease-out),
    color var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-1) var(--iw-ease-out);
}

.dispatch-card__retry i {
  font-size: 0.625rem;
  transition: transform var(--iw-dur-3) var(--iw-ease-out);
}

.dispatch-card__retry:hover {
  background: rgba(245, 158, 11, 0.16);
  border-color: rgba(217, 119, 6, 0.6);
  color: theme('colors.amber.900');
}

.dispatch-card__retry:hover i {
  transform: rotate(90deg);
}

.dispatch-card__retry:active {
  transform: scale(0.97);
}

.dispatch-card__retry:focus-visible {
  outline: none;
  box-shadow: var(--iw-focus-ring);
}

.dark .dispatch-card__retry {
  border-color: rgba(252, 211, 77, 0.35);
  background: rgba(252, 211, 77, 0.06);
  color: theme('colors.amber.200');
}

.dark .dispatch-card__retry:hover {
  background: rgba(252, 211, 77, 0.16);
  border-color: rgba(252, 211, 77, 0.55);
  color: theme('colors.amber.100');
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

  .dispatch-card__retry,
  .dispatch-card__retry i,
  .dispatch-card__retry:active {
    transition: none;
    transform: none;
  }

  .dispatch-reveal-enter-active,
  .dispatch-reveal-leave-active {
    transition: none;
  }
}
</style>
