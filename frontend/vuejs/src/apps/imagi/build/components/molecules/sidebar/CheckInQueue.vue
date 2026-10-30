<!--
  CheckInQueue.vue — what the coordinator needs the user to answer.

  Threads never interrupt the user. When one needs something only the user
  can give, it lands here, above the coordinator's composer, and the user
  works through the pile one card at a time (FIFO) so they stay
  single-threaded.

  Only asks queue: a thread's question, or a pick between takes on a brief
  the user asked to compare. A thread that finished or stopped is reported on
  its own card in the coordinator chat, which turns complete (or stopped,
  with Try again) in place and stays there as history, so nothing about it
  waits here to be cleared.

  Same language as the Threads pane: a status rail spines the card, the job
  keeps its byline, and parallel takes carry the n/m marker.
-->
<template>
  <div v-if="queue.length> 0" class="mb-1.5">
    <!-- Queue depth: only worth showing once something is waiting behind.
         The Threads pane's section head, reused: label, count, hairline to
         the edge. Two lists of agent work should be labelled the same way. -->
    <div v-if="queue.length> 1" class="queue-head flex items-center gap-1.5 px-1 pb-1.5">
      <span class="text-[0.625rem] font-semibold uppercase tracking-[0.09em] text-ink/45 dark:text-white/[0.42]">Waiting on you</span>
      <span
        class="queue-head__count px-1 rounded bg-ink/[0.06] text-ink/50 text-[0.5625rem] font-semibold tabular-nums leading-[0.9375rem] dark:bg-white/[0.07] dark:text-blue-100/55"
      >{{ queue.length }}</span>
      <span
        class="flex-1 h-px bg-[linear-gradient(90deg,rgba(19,26,44,0.12)_0%,rgba(19,26,44,0)_100%)] dark:bg-[linear-gradient(90deg,rgba(255,255,255,0.14)_0%,rgba(255,255,255,0)_100%)]"
      ></span>
    </div>

    <!-- The pile: layers behind the card stand for the check-ins queued after
         this one, so the depth is a thing you see rather than a number.

         Two hairline layers (::before, ::after) peek out below the card. Both
         are always drawn and revealed by opacity rather than created by the
         state — a pseudo-element that springs into existence cannot be
         transitioned, and the pile gaining a layer should look like
         something sliding under the card. The second layer only shows once
         three or more are queued: it would be a lie about the depth
         otherwise. -->
    <div
      :class="[
        'relative [transition:padding-bottom_var(--iw-dur-3)_var(--iw-ease-out)]',
        LAYER_BEFORE,
        LAYER_AFTER,
        queue.length > 1 ? 'pb-[0.3125rem] before:opacity-100 before:[transform:none]' : 'pb-0 before:opacity-0 before:[transform:translateY(-0.25rem)]',
        queue.length > 2 ? 'after:opacity-100 after:[transform:none]' : 'after:opacity-0 after:[transform:translateY(-0.25rem)]'
      ]"
    >
      <!-- Every colour comes from --sl-wait: amber, the chat rail's
           "waiting on you". -->
      <article
        :key="current.id"
        class="check-in iw-surface relative z-[2] flex rounded-[0.875rem] overflow-hidden shadow-iw-1
          border border-[color:color-mix(in_srgb,var(--sl-wait)_24%,transparent)]
          [background:linear-gradient(color-mix(in_srgb,var(--sl-wait)_7%,transparent),color-mix(in_srgb,var(--sl-wait)_7%,transparent)),rgb(var(--app-canvas,255_255_255))]
          [transition:border-color_var(--iw-dur-3)_var(--iw-ease-out),background-color_var(--iw-dur-3)_var(--iw-ease-out)]"
      >
        <span class="absolute left-0 top-0 bottom-0 w-[0.1875rem] bg-sl-wait" aria-hidden="true"></span>

        <div class="flex-1 min-w-0 pt-2 pr-2.5 pb-[0.5625rem] pl-3">
          <!-- What came back, and from which task -->
          <div class="flex items-start gap-1.5">
            <!-- The job keeps the byline it has on its card in the thread. It
                 wraps rather than clipping: a name cut off mid-word in a
                 sidebar is how two subagents end up looking like the same one. -->
            <h3
              class="check-in__title flex-1 min-w-0 font-sl-display [font-variation-settings:'opsz'_11,'SOFT'_30,'WONK'_1] text-[0.8125rem] font-semibold leading-[1.25] tracking-[-0.006em] text-blue-950 dark:text-white/[0.92] [overflow-wrap:anywhere]"
            >{{ jobName }}</h3>
            <!-- One of several parallel takes on the same brief: say so, or
                 accepting the first one looks like the only option. -->
            <span
              v-if="siblingCount> 1"
              class="shrink-0 mt-px px-1 rounded bg-ink/[0.07] text-ink/55 text-[0.5625rem] font-semibold leading-[1.05rem] tabular-nums dark:bg-white/[0.08] dark:text-blue-100/60"
              :title="`Take ${siblingIndex} of ${siblingCount} on the same brief`"
            >{{ siblingIndex }}/{{ siblingCount }}</span>
            <button
              type="button"
              title="Open this thread"
              aria-label="Open this thread"
              class="check-in__open iw-press shrink-0 inline-flex items-center justify-center w-5 h-5 -mt-px -mr-0.5 rounded-iw-xs
                text-ink/35 hover:bg-ink/[0.07] hover:text-ink/75 dark:text-white/35 dark:hover:bg-white/[0.08] dark:hover:text-white/80
                [transition:background-color_var(--iw-dur-2)_var(--iw-ease-out),color_var(--iw-dur-2)_var(--iw-ease-out),transform_var(--iw-dur-1)_var(--iw-ease-out)]
                focus-visible:![outline:none] focus-visible:shadow-iw-focus"
              @click="emit('view', current)"
            >
              <i class="fas fa-arrow-up-right-from-square text-[9px]"></i>
            </button>
          </div>

          <div
            class="flex items-baseline gap-[0.3125rem] mt-[0.1875rem] [font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace] tracking-[0.08em] uppercase text-[0.625rem] leading-[1.35] text-sl-wait"
          >
            <i :class="[kindIcon, 'shrink-0 text-[0.5625rem]']"></i>
            <span>{{ kindLabel }}</span>
          </div>

          <!-- Body: the question, or the take's sign-off. Shown whole —
               a question with its end clipped off cannot be answered, and a
               four-to-six-sentence account of what changed in someone's app is
               the part of this card worth reading. The server caps bodies at
               2000 chars, so a runaway card cannot happen. -->
          <p v-if="current.body" class="check-in__text mt-1.5 text-[0.6875rem] leading-[1.45] text-ink/70 dark:text-white/65 break-words">
            {{ current.body }}
          </p>

          <!-- A question is answered in place: the answer restarts the thread
               in the background, so the user never leaves this thread. -->
          <div v-if="current.kind === 'question'" class="mt-2">
            <!-- One-tap answers and a sketch, when the thread offered them -->
            <QuestionChoices
              v-if="current.options?.length || current.visual"
              :options="current.options || []"
              :visual="current.visual || ''"
              class="mb-2"
              @pick="emit('answer', current, $event)"
            />
            <!-- Focus is a ring rather than a border swap: the field's edge
                 stays where it was and gains a halo, so nothing shifts by a
                 pixel as you click into it. -->
            <textarea
              ref="answerInput"
              v-model="answer"
              rows="2"
              :placeholder="current.options?.length ? 'Or type your own answer…' : 'Answer to send back…'"
              class="w-full rounded-lg bg-white/70 dark:bg-white/[0.04] border border-ink/[0.1] dark:border-white/[0.12] text-ink dark:text-white/90 placeholder-ink/35 dark:placeholder-white/30 text-[11px] px-2 py-1.5 resize-none leading-relaxed
                [outline:none] [transition:border-color_var(--iw-dur-2)_var(--iw-ease-out),box-shadow_var(--iw-dur-2)_var(--iw-ease-out)]
                focus:border-ink/45 dark:focus:border-white/45 focus:[box-shadow:0_0_0_3px_rgba(var(--iw-accent),0.14)]"
              @keydown.enter.exact.prevent="sendAnswer"
            ></textarea>
            <div class="flex items-center gap-1.5 mt-1.5">
              <button
                type="button"
                :disabled="!answer.trim()"
                :class="[
                  BTN_PRIMARY,
                  'flex-1 rounded-full px-2.5 py-1 text-[11px] font-semibold',
                  answer.trim()
                    ? [BTN_PRIMARY_ACTIVE, 'text-paper dark:text-ink']
                    : 'bg-blue-100/60 dark:bg-white/[0.05] text-ink/40 dark:text-white/40 cursor-not-allowed border border-ink/10 dark:border-white/[0.12]'
                ]"
                @click="sendAnswer"
              >
                Send answer
              </button>
              <!-- Only worth offering when there is a card to move behind -->
              <button
                v-if="queue.length > 1"
                type="button"
                title="Move this to the back of the queue"
                :class="[BTN_GHOST, 'rounded-full px-2.5 py-1 text-[11px] font-medium']"
                @click="emit('later', current)"
              >
                Later
              </button>
            </div>
          </div>

          <!-- One of several takes on a brief the user asked to compare: the
               only place finished work waits on a choice. A solo thread
               applies its own work and never gets here. -->
          <div v-else class="flex items-center gap-1.5 mt-2">
            <button
              type="button"
              :disabled="busy"
              :class="[BTN_PRIMARY, BTN_PRIMARY_ACTIVE, 'flex-1 rounded-full px-2.5 py-1 text-[11px] font-semibold text-paper dark:text-ink disabled:opacity-50']"
              @click="emit('accept', current)"
            >
              <i v-if="busy" class="fas fa-circle-notch fa-spin text-[10px]"></i>
              <span v-else>Use this one</span>
            </button>
            <button
              type="button"
              :disabled="busy"
              :class="[BTN_GHOST, 'flex-1 rounded-full px-2.5 py-1 text-[11px] font-medium disabled:opacity-50']"
              @click="emit('dismiss', current)"
            >
              Discard
            </button>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import QuestionChoices from '../chat/QuestionChoices.vue'
import type { CheckInDto } from '../../../types/services'

const props = defineProps<{
  queue: CheckInDto[]
  /** An accept/dismiss is in flight for the current card */
  busy?: boolean
}>()

const emit = defineEmits<{
  (e: 'accept', checkIn: CheckInDto): void
  (e: 'dismiss', checkIn: CheckInDto): void
  /** Answer a subagent's question — restarts it in the background */
  (e: 'answer', checkIn: CheckInDto, answer: string): void
  /** Put this card off: it moves to the back of the queue */
  (e: 'later', checkIn: CheckInDto): void
  /** Open the thread */
  (e: 'view', checkIn: CheckInDto): void
}>()

/* The pile's two layers, drawn as the stack's ::before and ::after. */
const LAYER_BEFORE =
  "before:content-[''] before:absolute before:left-1.5 before:right-1.5 before:bottom-[0.0625rem] before:z-[1] before:h-2.5 " +
  'before:border before:border-ink/[0.09] before:[border-top:none] before:rounded-b-iw-md before:bg-blue-50/70 ' +
  'dark:before:border-white/[0.09] dark:before:bg-white/[0.03] ' +
  'before:[transition:opacity_var(--iw-dur-3)_var(--iw-ease-out),transform_var(--iw-dur-3)_var(--iw-ease-out)]'
const LAYER_AFTER =
  "after:content-[''] after:absolute after:left-[0.6875rem] after:right-[0.6875rem] after:-bottom-0.5 after:z-0 after:h-2.5 " +
  'after:border after:border-ink/[0.09] after:[border-top:none] after:rounded-b-iw-md after:bg-blue-50/70 ' +
  'dark:after:border-white/[0.09] dark:after:bg-white/[0.03] ' +
  'after:[transition:opacity_var(--iw-dur-3)_var(--iw-ease-out),transform_var(--iw-dur-3)_var(--iw-ease-out)]'

/*
  The workspace's navy-ink pairing. .iw-press supplies the scale under the
  pointer on both.

  The primary keeps .btn-primary, and Spotlight's lit pill (spotlight.css,
  which loads after every component style) dresses it: the gradient, border,
  ink, weight, shadow, transition and hover lift are all that rule's. Only a
  hover, a keyboard focus and the dark fill outrank it, so those are stated
  here, with `!` (the focus drops the outline but, as before, keeps the
  pill's outline colour).
*/
const BTN_PRIMARY =
  'btn-primary iw-press focus-visible:![outline-style:none] focus-visible:![outline-width:medium] focus-visible:![box-shadow:var(--iw-focus-ring)]'
/* Navy ink under the pointer, matching the composer's send button; in dark
   the fill is bone at rest too (a disabled one under the pointer is the
   pill again). */
const BTN_PRIMARY_ACTIVE =
  'enabled:hover:![background:#1e3a8a] enabled:hover:![box-shadow:var(--iw-shadow-3),inset_0_1px_0_rgba(255,255,255,0.12)] ' +
  'dark:![background:#f3ede2] dark:enabled:hover:![background:#ffffff] dark:disabled:hover:![background:var(--sl-grad)]'
/* Ghost secondary: a quiet outline that only tints on hover */
const BTN_GHOST =
  'iw-press focus-visible:![outline:none] focus-visible:shadow-iw-focus border border-blue-200/70 bg-transparent text-ink/70 ' +
  '[transition:background-color_var(--iw-dur-2)_var(--iw-ease-out),border-color_var(--iw-dur-2)_var(--iw-ease-out),color_var(--iw-dur-2)_var(--iw-ease-out),box-shadow_var(--iw-dur-2)_var(--iw-ease-out),opacity_var(--iw-dur-2)_var(--iw-ease-out),transform_var(--iw-dur-1)_var(--iw-ease-out)] ' +
  'enabled:hover:bg-blue-50/90 enabled:hover:border-blue-300/90 enabled:hover:text-ink ' +
  'dark:border-white/[0.12] dark:text-white/70 dark:enabled:hover:bg-white/[0.06] dark:enabled:hover:text-white/95'

const answer = ref('')
const answerInput = ref<HTMLTextAreaElement | null>(null)

// The queue is FIFO — the user works one item at a time.
const current = computed(() => props.queue[0]!)

// Moving to the next card must not carry the previous card's draft answer
// with it.
watch(() => current.value?.id, async (id) => {
  answer.value = ''
  if (current.value?.kind === 'question' && id) {
    await nextTick()
    answerInput.value?.focus()
  }
})

// Sibling takes on the same brief (drafts=2/3) queue as separate cards, so
// the card names its place among them rather than looking like the only one.
const siblings = computed(() => {
  const group = current.value?.task.variant_group
  if (!group) return []
  return props.queue.filter(c => c.task.variant_group === group)
})
const siblingCount = computed(() => siblings.value.length)
const siblingIndex = computed(
  () => siblings.value.findIndex(c => c.id === current.value?.id) + 1
)

/** The job this subagent was given, named as the main thread's card names it
 *  — the same subagent, so the same words. Falls back to the workspace title
 *  for a task dispatched before goals were carried on the queue. */
const jobName = computed(
  () => current.value?.task.goal || current.value?.task.title || 'Thread'
)

const kindIcon = computed(() =>
  current.value?.kind === 'question' ? 'fas fa-circle-question' : 'fas fa-check'
)

const kindLabel = computed(() =>
  current.value?.kind === 'question' ? 'Needs your answer' : 'Pick one of your options'
)

function sendAnswer() {
  const text = answer.value.trim()
  if (!text) return
  answer.value = ''
  emit('answer', current.value, text)
}
</script>

<style scoped>
/* A check-in lands rather than blinks — the card is keyed on the check-in id,
   so each new one plays this as it takes the front of the queue. It rises
   slightly out of the pile it was waiting in, which is where the next one
   genuinely comes from. (Keyframes: scoped names can't be reached from a
   utility.) */
.check-in {
  animation: check-in-arrive var(--iw-dur-4) var(--iw-ease-spring) both;
}

@keyframes check-in-arrive {
  from { opacity: 0; transform: translateY(6px) scale(0.97); }
  to { opacity: 1; transform: none; }
}

@media (prefers-reduced-motion: reduce) {
  .check-in { animation: none; }
}
</style>
