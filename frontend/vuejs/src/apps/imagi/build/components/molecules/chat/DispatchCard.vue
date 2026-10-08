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

  It hangs on the chat's rail (see ChatConversation): the state chip is the
  card's node on the rail, and the card is tinted in the state's colour — blue
  while it works, green when it lands, amber when it needs the user, red when
  it stopped — with the state named in a small mono label, so a thread of
  these can be scanned by colour alone.
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
 *  "Thread complete" over an empty space tells the owner nothing about
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
      label: 'Thread starting',
      result: '',
      reveal: WHAT_ITS_DOING,
    }
  }
  if (instance.isProcessing) {
    return {
      tone: 'working',
      icon: 'fas fa-circle-notch fa-spin',
      label: 'Thread working',
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
        label: 'Thread complete — one of your options',
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
        label: 'Thread complete',
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
        label: 'Thread starting',
        result: instance.overview,
        reveal: WHAT_ITS_DOING,
      }
  }
})

const bodyId = `dispatch-card-body-${nextBodyId++}`

/**
 * Whether the card is open. Closed to begin with in every state, the
 * finished one included: "Thread complete" over the job's name is the
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
  job: props.instance?.brief || props.title || 'Thread',
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

/* Every colour on the card comes from --st, the state's colour, so a state
   change is one line rather than a rule per element. */
.dispatch-card {
  --st: var(--sl-faint, rgba(19, 26, 44, 0.5));

  position: relative;
  /* Stacked, not two columns: the job is the card, and giving it the full
     width is what lets it be read whole on a phone rather than clipped into a
     column beside an icon. */
  display: flex;
  flex-direction: column;
  gap: 0.3125rem;
  width: 100%;
  padding: 0.5625rem 0.75rem 0.625rem;
  border-radius: 0.875rem;
  border: 1px solid color-mix(in srgb, var(--st) 22%, transparent);
  background: color-mix(in srgb, var(--st) 6%, transparent);
  text-align: left;
  transition:
    background-color var(--iw-dur-3) var(--iw-ease-out),
    border-color var(--iw-dur-3) var(--iw-ease-out),
    box-shadow var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-2) var(--iw-ease-out);
}

.dispatch-card:hover {
  border-color: color-mix(in srgb, var(--st) 40%, transparent);
  transform: translateY(-1px);
}

/* A short branch from the rail to the card, so the card reads as a step
   hanging off the line like everything else in the log. */
.dispatch-card::before {
  content: '';
  position: absolute;
  left: -0.75rem;
  top: 1.1875rem;
  width: 0.75rem;
  height: 1px;
  background: color-mix(in srgb, var(--st) 45%, transparent);
  pointer-events: none;
}

/* The disclosure: the state line and the job, as one target. Stripped of the
   button element's own styling so the card reads as a card — everything
   visible here is the card's. */
.dispatch-card__toggle {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
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

/* Nothing to open — a discarded card, or a thread that has not said
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

/* Dispatched, run not yet fired: drawn but not filled. */
.dispatch-card--starting {
  border-style: dashed;
  background: var(--sl-chip-bg, rgba(19, 26, 44, 0.035));
}

.dispatch-card--working {
  --st: var(--sl-work);
}

.dispatch-card--asking {
  --st: var(--sl-wait);
}

/* Done. The flip from "working" to "complete, and here is what it did" is the
   single moment this card exists to report, so it arrives in green and plays
   a one-shot settle rather than simply being repainted. */
.dispatch-card--done {
  --st: var(--sl-ok);
  animation: done-settle var(--iw-dur-4) var(--iw-ease-spring) both;
}

/* A run that died: red, the workspace's colour for "this didn't work", with
   the way back right under it. */
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

/* ── Parts ──────────────────────────────────────────────────────────────── */

/* The ledger's left-edge rail gave way to the chat's own rail. */
.dispatch-card__rail {
  display: none;
}

.dispatch-card__head {
  display: flex;
  align-items: center;
  gap: 0.4375rem;
  min-height: 1.25rem;
  transition: transform var(--iw-dur-2) var(--iw-ease-out);
}

/* The chip is the card's node on the chat rail: a filled circle in the
   state's colour, punched out of the line by a ring of the floor. Placed
   back across the rail's gutter (the 2rem every rail entry is indented). */
.dispatch-card__chip {
  position: absolute;
  left: -2rem;
  top: 0.5625rem;
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
    0 0 16px -2px var(--st);
  transition:
    background-color var(--iw-dur-3) var(--iw-ease-out),
    color var(--iw-dur-3) var(--iw-ease-out);
}

.dispatch-card--starting .dispatch-card__chip,
.dispatch-card--settled .dispatch-card__chip {
  background: rgb(var(--app-canvas, 255 255 255));
  border: 1.5px dashed var(--sl-line-strong, rgba(19, 26, 44, 0.15));
  color: var(--sl-faint);
  box-shadow: 0 0 0 4px rgb(var(--app-canvas, 255 255 255));
}

/* Where it stands, as the rail's small mono label in the state's colour. */
.dispatch-card__status {
  flex: 1;
  min-width: 0;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.625rem;
  font-weight: 500;
  line-height: 1.3;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--st);
  transition: color var(--iw-dur-3) var(--iw-ease-out);
}

/* The job, in the display face, so what is being done to the app reads as
   the subject of the card. It wraps: no clamp, no ellipsis. */
.dispatch-card__job {
  font-family: var(--sl-font-display, theme('fontFamily.display'));
  font-size: 0.875rem;
  font-weight: 600;
  line-height: 1.35;
  letter-spacing: -0.006em;
  color: var(--sl-text);
  overflow-wrap: anywhere;
}

/* The paragraph under the job — what it is doing, then what came back. Set
   apart by a hairline in the state's colour, and sized as prose: it is the
   part of the card the owner actually reads. */
.dispatch-card__result {
  margin-top: 0.125rem;
  padding-top: 0.4375rem;
  border-top: 1px solid color-mix(in srgb, var(--st) 18%, transparent);
  font-size: 0.8125rem;
  line-height: 1.55;
  color: var(--sl-muted);
  overflow-wrap: anywhere;
}

.dispatch-card__caret {
  flex-shrink: 0;
  font-size: 0.5rem;
  transition: transform var(--iw-dur-3) var(--iw-ease-out);
}

.dispatch-card__toggle[aria-expanded='true'] .dispatch-card__caret {
  transform: rotate(180deg);
}

/* The fold, named. Small and quiet — it is an offer, not the news. */
.dispatch-card__reveal {
  display: inline-flex;
  align-items: center;
  gap: 0.3125rem;
  margin-top: 0.0625rem;
  font-size: 0.6875rem;
  font-weight: 550;
  color: var(--sl-faint);
  transition: color var(--iw-dur-2) var(--iw-ease-out);
}

.dispatch-card:hover .dispatch-card__reveal {
  color: var(--sl-text);
}

/* The trip to the thread's own transcript, at the end of what it had to
   say. */
.dispatch-card__more {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  margin-top: 0.5rem;
  padding: 0.25rem 0.625rem;
  border-radius: 9999px;
  border: 1px solid var(--sl-line-strong, rgba(19, 26, 44, 0.15));
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--sl-text);
  transition:
    background-color var(--iw-dur-2) var(--iw-ease-out),
    border-color var(--iw-dur-2) var(--iw-ease-out);
}

.dispatch-card__more i {
  font-size: 0.5625rem;
  transition: transform var(--iw-dur-2) var(--iw-ease-out);
}

.dispatch-card__more:hover {
  background: var(--sl-chip-bg-hover, rgba(19, 26, 44, 0.065));
}

.dispatch-card__more:hover i {
  transform: translateX(2px);
}

.dispatch-card__more:focus-visible {
  outline: none;
  box-shadow: var(--iw-focus-ring);
}

/* The retry, on a stopped card: the workspace's lit pill, because it is the
   one thing on the card the reader most needs to reach. */
.dispatch-card__actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.dispatch-card__retry {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.3125rem 0.8125rem;
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

.dispatch-card__retry:focus-visible {
  outline: none;
  box-shadow: var(--iw-focus-ring);
}

/* ── Motion ─────────────────────────────────────────────────────────────── */

/* The arrival. Work landing in the app should register even out of the corner
   of the eye, so the card takes a beat of extra height and settles back. */
@keyframes done-settle {
  0% { transform: scale(0.985); }
  45% { transform: scale(1.012); }
  100% { transform: none; }
}

/* Opening the card: the layout settles at once and the text fades up. */
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
