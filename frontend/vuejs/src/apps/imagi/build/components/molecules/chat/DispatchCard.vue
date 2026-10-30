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

  A thread waiting on an answer shows its question whole, in the needs-you
  colour, but is not answered here: every question waits in one queue above
  the coordinator's composer, so the user works through them in one place.
  The card is the history; once answered it flips back to working.

  A stopped card carries the way back ("Try again") and the way out
  ("Discard", which frees what the run was holding). A run that died is never
  retried on its own — a failure that quietly restarts itself is a loop — so
  the reader decides.

  It hangs on the chat's rail (see ChatConversation): the node is the card's
  mark on the rail, filled in the state's colour — the workspace's live dot
  while it works, green when it lands, amber when it needs the user, red when
  it stopped — so a run of these can be scanned by colour alone.
-->
<template>
  <article
    class="relative flex w-full flex-col gap-[0.3125rem] rounded-[0.875rem] border px-[0.8125rem] pb-[0.625rem] pt-[0.6875rem] text-left
      [transition:border-color_var(--iw-dur-3)_var(--iw-ease-out),box-shadow_var(--iw-dur-2)_var(--iw-ease-out)]
      before:pointer-events-none before:absolute before:-left-3 before:top-5 before:h-px before:w-3
      before:bg-[color:color-mix(in_srgb,var(--st)_45%,transparent)] before:content-['']"
    :class="[
      'dispatch-card', `dispatch-card--${state.tone}`, { 'dispatch-card--question': isQuestion },
      isQuestion ? QUESTION_CARD : CARD_TONE[state.tone],
    ]"
  >
    <!-- Every state colour on the card comes from --st, so a state change is
         one class rather than a rule per element. The surface itself stays
         neutral — the Spotlight card — and the state lives in the node and the
         eyebrow. The ::before is a short branch from the rail to the card, so
         it reads as a step hanging off the line like everything else in the
         log. -->
    <!-- The card's node on the rail: a filled circle in the state's colour,
         punched out of the rail by a ring of the floor, placed back across
         the rail's 2rem gutter. Working wears the workspace's live dot, the
         same one as the status row under the chat (its disc, ring and grid
         come from .iw-live-node). -->
    <span
      v-if="state.tone === 'working'"
      class="iw-live-node !absolute -left-8 top-[0.625rem] h-5 w-5 items-center justify-center !rounded-[50%] text-[0.5625rem] text-[color:rgb(var(--app-canvas,255_255_255))]
        [box-shadow:0_0_0_4px_rgb(var(--app-canvas,255_255_255))] [transition:background-color_var(--iw-dur-3)_var(--iw-ease-out)]"
      aria-hidden="true"
    >
      <span class="iw-live"></span>
    </span>
    <span
      v-else
      :class="[
        'absolute -left-8 top-[0.625rem] flex h-5 w-5 items-center justify-center rounded-[50%] text-[0.5625rem]',
        '[transition:background-color_var(--iw-dur-3)_var(--iw-ease-out)]',
        DRAWN_TONES.has(state.tone)
          ? 'border-[1.5px] border-dashed border-sl-line-strong bg-[color:rgb(var(--app-canvas,255_255_255))] text-sl-faint [box-shadow:0_0_0_4px_rgb(var(--app-canvas,255_255_255))]'
          : 'bg-[color:var(--st)] text-[color:rgb(var(--app-canvas,255_255_255))] [box-shadow:0_0_0_4px_rgb(var(--app-canvas,255_255_255)),0_0_14px_-3px_var(--st)]',
      ]"
      aria-hidden="true"
    >
      <i :class="state.icon"></i>
    </span>

    <!-- Where it stands, as the marquee eyebrow: a diamond, the state, a
         hairline fading to the edge — the site's page eyebrow, in the
         state's colour. -->
    <p
      class="flex min-h-[1rem] items-center gap-2
        before:h-[0.3125rem] before:w-[0.3125rem] before:shrink-0 before:rotate-45 before:bg-[color:var(--st)] before:content-['']"
    >
      <span
        class="dispatch-card__status text-[0.625rem] font-medium uppercase leading-[1.3] tracking-[0.08em] text-[color:var(--st)]
          [font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace]"
      >{{ state.label }}</span>
      <span
        class="h-px min-w-[1rem] flex-1 bg-[image:linear-gradient(90deg,color-mix(in_srgb,var(--st)_55%,transparent),transparent)]"
        aria-hidden="true"
      ></span>
    </p>

    <!-- Which job, in the user's language, in the display face: what is being
         done to the app is the subject of the card. Present in every state,
         since a result means nothing without the job it answers. It wraps:
         no clamp, no ellipsis. -->
    <p
      class="dispatch-card__job font-sl-display text-[0.9375rem] font-semibold leading-[1.35] tracking-[-0.012em] text-sl-text [overflow-wrap:anywhere]"
    >{{ state.job }}</p>

    <!-- How the coordinator placed it, when that is more than "alongside
         everything else": what it starts after, what it is on hold for, or
         the thread it was forked from — with the coordinator's reason. Small
         and muted; on hold takes the card's state colour, since that is what
         the user has to act on. -->
    <p
      v-if="plan"
      :class="[
        'dispatch-card__plan -mt-px flex items-baseline gap-1.5 text-[0.75rem] leading-[1.45] [overflow-wrap:anywhere]',
        plan.kind === 'blocked' ? 'text-[color:var(--st)]' : 'text-sl-muted',
      ]"
    >
      <i
        :class="[plan.icon, 'shrink-0 text-[0.625rem]', plan.kind === 'blocked' ? 'text-[color:var(--st)]' : 'text-sl-faint']"
        aria-hidden="true"
      ></i>
      <span>
        {{ plan.text }}<span v-if="planReason"> · {{ planReason }}</span>
      </span>
    </p>

    <!-- A question in full. It is answered in the queue above the
         composer, which is where every open question waits. -->
    <div v-if="isQuestion" class="flex flex-col gap-1">
      <!-- The question is the point of its card, so it reads in full ink. -->
      <p
        class="dispatch-card__question whitespace-pre-wrap text-[0.8125rem] leading-[1.55] text-sl-text [overflow-wrap:anywhere]"
      >{{ state.result }}</p>
      <!-- Where to answer it, quietly, in the needs-you colour. -->
      <p class="dispatch-card__hint text-[0.75rem] leading-[1.4] text-sl-wait">Answer it in the queue below.</p>
    </div>

    <template v-else>
      <!-- The paragraph under the job: what it is doing while it runs, what
           came of it once it has. A stopped card shows it unfolded — it is
           short, and it is the part that says what did and did not land.
           Sized as prose: it is the part of the card the owner reads. -->
      <Transition
        enter-active-class="[transition:opacity_var(--iw-dur-2)_var(--iw-ease-out),transform_var(--iw-dur-2)_var(--iw-ease-out)] motion-reduce:[transition:none] motion-reduce:[transform:none]"
        enter-from-class="-translate-y-[3px] opacity-0"
        leave-active-class="[transition:opacity_var(--iw-dur-2)_var(--iw-ease-out),transform_var(--iw-dur-2)_var(--iw-ease-out)] motion-reduce:[transition:none] motion-reduce:[transform:none]"
        leave-to-class="-translate-y-[3px] opacity-0"
      >
        <p
          v-if="showResult"
          :id="bodyId"
          class="dispatch-card__result whitespace-pre-wrap text-[0.8125rem] leading-[1.55] text-sl-muted [overflow-wrap:anywhere]"
        >{{ state.result }}</p>
      </Transition>
    </template>

    <div class="mt-[0.1875rem] flex items-center justify-between gap-2">
      <!-- The retry, on a stopped card: the workspace's lit pill, because it
           is the one thing on the card the reader most needs to reach. -->
      <button
        v-if="retryable"
        type="button"
        class="dispatch-card__retry group/retry inline-flex cursor-pointer items-center gap-1.5 rounded-full bg-sl-grad px-3 py-1 text-[0.75rem] font-semibold text-sl-on-accent shadow-sl-btn [border:none]
          [transition:box-shadow_var(--iw-dur-2)_var(--iw-ease-out),transform_var(--iw-dur-1)_var(--iw-ease-out)]
          hover:shadow-sl-btn-hover focus-visible:shadow-iw-focus focus-visible:![outline:none] active:scale-[0.97] motion-reduce:[transition:none]"
        @click="emit('retry')"
      >
        <i
          class="fas fa-rotate-right text-[0.625rem] [transition:transform_var(--iw-dur-3)_var(--iw-ease-out)] group-hover/retry:rotate-90 motion-reduce:[transition:none]"
          aria-hidden="true"
        ></i>
        Try again
      </button>
      <!-- The fold, named (and Discard beside a retry). Small and quiet — it
           is an offer, not the news. -->
      <button
        v-if="retryable"
        type="button"
        :class="['dispatch-card__discard', FOLD_BUTTON]"
        @click="emit('dismiss')"
      >
        Discard
      </button>
      <button
        v-else-if="expandable"
        type="button"
        :class="['dispatch-card__toggle', FOLD_BUTTON]"
        :aria-expanded="expanded"
        :aria-controls="bodyId"
        @click="expanded = !expanded"
      >
        {{ expanded ? 'Hide details' : 'Details' }}
        <i
          class="fas fa-chevron-down dispatch-card__caret text-[0.5rem] [transition:transform_var(--iw-dur-3)_var(--iw-ease-out)] motion-reduce:[transition:none]"
          :class="{ 'rotate-180': expanded }"
          aria-hidden="true"
        ></i>
      </button>

      <!-- The way into the thread: a quiet pill ending on the lit arrow.
           Always at the right of the foot, so it is in the same place on
           every card. -->
      <button
        type="button"
        class="dispatch-card__go group/go ml-auto inline-flex cursor-pointer items-center gap-2 rounded-full border border-sl-line-strong py-0.5 pl-2.5 pr-0.5 text-[0.75rem] font-semibold text-sl-text
          [transition:border-color_var(--iw-dur-2)_var(--iw-ease-out),box-shadow_var(--iw-dur-2)_var(--iw-ease-out)]
          hover:border-[color:color-mix(in_srgb,var(--sl-amber,#ee8c10)_50%,transparent)] hover:[box-shadow:0_0_18px_-6px_var(--sl-glow,rgba(255,120,80,0.3))]
          focus-visible:shadow-iw-focus focus-visible:![outline:none]"
        @click="emit('open')"
      >
        Go to thread
        <span
          class="grid h-[1.375rem] w-[1.375rem] place-items-center rounded-full bg-sl-grad text-[0.625rem] text-sl-on-accent [box-shadow:0_4px_12px_-4px_rgba(236,90,50,0.6)]"
          aria-hidden="true"
        ><i
          class="fas fa-arrow-right [transition:transform_var(--iw-dur-2)_var(--iw-ease-out)] group-hover/go:translate-x-px motion-reduce:[transition:none]"
        ></i></span>
      </button>
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { AgentInstance } from '../../../types/services'
import { isHeldThread } from '../../../stores/agentStore'
import { scheduleLine } from '../../../utils/threadSchedule'

/** The card per tone: its --st colour and its surface. Starting and
 *  scheduled work is drawn but not lit (dashed, on the chip ground); working
 *  has a faint blue light falling on its top edge, the stage lit for the work
 *  in progress; discarded work recedes — it is a record, not news. */
const LIT = 'border-sl-line-strong bg-sl-card-bg shadow-sl-card'
const DRAWN = '[--st:var(--sl-faint)] border-dashed border-sl-line-strong bg-sl-chip-bg'
const CARD_TONE: Record<string, string> = {
  starting: DRAWN,
  scheduled: DRAWN,
  working:
    '[--st:var(--sl-work)] border-sl-line-strong shadow-sl-card bg-[image:radial-gradient(90%_3.75rem_at_30%_0,color-mix(in_srgb,var(--sl-work)_13%,transparent),transparent_80%),var(--sl-card-bg)]',
  asking: `[--st:var(--sl-wait)] ${LIT}`,
  done: `[--st:var(--sl-ok)] ${LIT}`,
  stopped: `[--st:var(--sl-bad)] ${LIT}`,
  settled: `[--st:var(--sl-faint)] ${LIT} opacity-70 hover:opacity-100`,
}

/** A question waiting on the user: the card that asks rather than reports,
 *  so its edge warms to amber to be found in a scroll of quiet cards. */
const QUESTION_CARD =
  '[--st:var(--sl-wait)] border-[color:color-mix(in_srgb,var(--sl-wait)_45%,transparent)] shadow-sl-card bg-[image:radial-gradient(90%_3.75rem_at_30%_0,color-mix(in_srgb,var(--sl-wait)_12%,transparent),transparent_80%),var(--sl-card-bg)]'

/** Tones whose rail node is drawn rather than filled. */
const DRAWN_TONES = new Set(['starting', 'scheduled', 'settled'])

/** The fold toggle and Discard: small, quiet text buttons. */
const FOLD_BUTTON =
  'inline-flex cursor-pointer items-center gap-[0.3125rem] rounded-iw-sm py-1 text-[0.6875rem] font-[550] text-sl-faint [border:none] [transition:color_var(--iw-dur-2)_var(--iw-ease-out)] hover:text-sl-text focus-visible:shadow-iw-focus focus-visible:![outline:none]'

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
}>(), { instance: null })

const emit = defineEmits<{
  /** Go to this thread */
  (e: 'open'): void
  /** Run this failed thread again — the user's call, never the card's */
  (e: 'retry'): void
  /** Discard this stopped thread, freeing what its run was holding */
  (e: 'dismiss'): void
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
  // Scheduled by the coordinator to start once other threads' work lands.
  // On hold (one of those stopped) is the user's to sort out, so it wears
  // the needs-you tone; plain waiting is drawn but not lit, like starting.
  if (isHeldThread(instance)) {
    return instance.schedule?.status === 'blocked'
      ? { tone: 'asking', icon: 'fas fa-pause', label: 'On hold', result: instance.overview }
      : { tone: 'scheduled', icon: 'fas fa-link', label: 'Thread scheduled', result: instance.overview }
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

/** The schedule line, and the coordinator's reason beside it while the
 *  thread is held (once it runs, how it was placed is history). */
const plan = computed(() => scheduleLine(props.instance?.schedule))
const planReason = computed(() =>
  plan.value && plan.value.kind !== 'forked' ? props.instance?.schedule?.reason || '' : ''
)

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
const expandable = computed(() => !!state.value.result && !isQuestion.value)

/** A stopped card shows what happened without a fold — the Try again button
 *  takes the fold's place, and the reader needs both. */
const showResult = computed(() => !!state.value.result && (retryable.value || expanded.value))

</script>

<style scoped>
/* Done. The flip from "working" to "complete" is the single moment this card
   exists to report, so it plays a one-shot settle rather than simply being
   repainted. Stays CSS: a scoped @keyframes name is hashed, so no utility can
   reference it. */
.dispatch-card--done {
  animation: done-settle var(--iw-dur-4) var(--iw-ease-spring) both;
}

@keyframes done-settle {
  0% { transform: scale(0.985); }
  45% { transform: scale(1.012); }
  100% { transform: none; }
}

@media (prefers-reduced-motion: reduce) {
  .dispatch-card--done {
    animation: none;
  }
}
</style>
