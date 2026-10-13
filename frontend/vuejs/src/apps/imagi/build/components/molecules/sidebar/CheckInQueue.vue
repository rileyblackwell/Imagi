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
    <!-- Queue depth: only worth showing once something is waiting behind -->
    <div v-if="queue.length> 1" class="queue-head">
      <span class="queue-head__label">Waiting on you</span>
      <span class="queue-head__count">{{ queue.length }}</span>
      <span class="queue-head__rule"></span>
    </div>

    <!-- The pile: layers behind the card stand for the check-ins queued after
         this one, so the depth is a thing you see rather than a number. -->
    <div
      :class="[
        'queue-stack',
        queue.length> 1 ? 'is-stacked' : '',
        queue.length > 2 ? 'is-deep' : ''
      ]"
    >
      <article :key="current.id" class="check-in iw-surface">
        <span class="check-in__rail" aria-hidden="true"></span>

        <div class="check-in__body">
          <!-- What came back, and from which task -->
          <div class="flex items-start gap-1.5">
            <h3 class="check-in__title">{{ jobName }}</h3>
            <!-- One of several parallel takes on the same brief: say so, or
                 accepting the first one looks like the only option. -->
            <span
              v-if="siblingCount> 1"
              class="check-in__take"
              :title="`Take ${siblingIndex} of ${siblingCount} on the same brief`"
            >{{ siblingIndex }}/{{ siblingCount }}</span>
            <button
              type="button"
              title="Open this thread"
              aria-label="Open this thread"
              class="check-in__open iw-press"
              @click="emit('view', current)"
            >
              <i class="fas fa-arrow-up-right-from-square text-[9px]"></i>
            </button>
          </div>

          <div class="check-in__status">
            <i :class="[kindIcon, 'check-in__status-icon']"></i>
            <span>{{ kindLabel }}</span>
          </div>

          <!-- Body: the question, or the take's sign-off. Shown whole —
               a question with its end clipped off cannot be answered, and a
               four-to-six-sentence account of what changed in someone's app is
               the part of this card worth reading. The server caps bodies at
               2000 chars, so a runaway card cannot happen. -->
          <p v-if="current.body" class="check-in__text">
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
            <textarea
              ref="answerInput"
              v-model="answer"
              rows="2"
              :placeholder="current.options?.length ? 'Or type your own answer…' : 'Answer to send back…'"
              class="answer-textarea w-full rounded-lg bg-white/70 dark:bg-white/[0.04] border border-ink/[0.1] dark:border-white/[0.12] text-ink dark:text-white/90 placeholder-ink/35 dark:placeholder-white/30 text-[11px] px-2 py-1.5 resize-none leading-relaxed"
              @keydown.enter.exact.prevent="sendAnswer"
            ></textarea>
            <div class="flex items-center gap-1.5 mt-1.5">
              <button
                type="button"
                :disabled="!answer.trim()"
                class="btn-primary iw-press flex-1 rounded-full px-2.5 py-1 text-[11px] font-semibold"
                :class="answer.trim()
                  ? 'btn-primary--active text-paper dark:text-ink'
                  : 'bg-blue-100/60 dark:bg-white/[0.05] text-ink/40 dark:text-white/40 cursor-not-allowed border border-ink/10 dark:border-white/[0.12]'"
                @click="sendAnswer"
              >
                Send answer
              </button>
              <!-- Only worth offering when there is a card to move behind -->
              <button
                v-if="queue.length > 1"
                type="button"
                title="Move this to the back of the queue"
                class="btn-ghost iw-press rounded-full px-2.5 py-1 text-[11px] font-medium"
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
              class="btn-primary btn-primary--active iw-press flex-1 rounded-full px-2.5 py-1 text-[11px] font-semibold text-paper dark:text-ink disabled:opacity-50"
              @click="emit('accept', current)"
            >
              <i v-if="busy" class="fas fa-circle-notch fa-spin text-[10px]"></i>
              <span v-else>Use this one</span>
            </button>
            <button
              type="button"
              :disabled="busy"
              class="btn-ghost iw-press flex-1 rounded-full px-2.5 py-1 text-[11px] font-medium disabled:opacity-50"
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
/* ── Queue depth ────────────────────────────────────────────────────────── */

/* The Subagents pane's section head, reused: label, count, hairline to the
   edge. Two lists of agent work should be labelled the same way. */
.queue-head {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0 0.25rem 0.375rem;
}

.queue-head__label {
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.09em;
  color: rgba(19, 26, 44, 0.45);
}

.dark .queue-head__label {
  color: rgba(255, 255, 255, 0.42);
}

.queue-head__count {
  padding: 0 0.25rem;
  border-radius: 0.25rem;
  background: rgba(19, 26, 44, 0.06);
  color: rgba(19, 26, 44, 0.5);
  font-size: 0.5625rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  line-height: 0.9375rem;
}

.dark .queue-head__count {
  background: rgba(255, 255, 255, 0.07);
  color: rgba(219, 234, 254, 0.55);
}

.queue-head__rule {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, rgba(19, 26, 44, 0.12) 0%, rgba(19, 26, 44, 0) 100%);
}

.dark .queue-head__rule {
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.14) 0%, rgba(255, 255, 255, 0) 100%);
}

/* ── The pile ───────────────────────────────────────────────────────────── */

/* Two hairline layers peeking out below the card: the queue has depth, and
   the depth is worth seeing without opening anything.

   Both layers are always drawn and revealed by opacity rather than being
   created by the class — a pseudo-element that springs into existence cannot
   be transitioned, and the pile gaining a layer should look like something
   sliding under the card, not like a line appearing from nowhere. */
.queue-stack {
  position: relative;
  padding-bottom: 0;
  transition: padding-bottom var(--iw-dur-3) var(--iw-ease-out);
}

.queue-stack.is-stacked {
  padding-bottom: 0.3125rem;
}

.queue-stack::before,
.queue-stack::after {
  content: '';
  position: absolute;
  left: 0.375rem;
  right: 0.375rem;
  height: 0.625rem;
  border: 1px solid rgba(19, 26, 44, 0.09);
  border-top: none;
  border-radius: 0 0 var(--iw-r-md) var(--iw-r-md);
  background: rgba(239, 246, 255, 0.7);
  opacity: 0;
  transform: translateY(-0.25rem);
  transition:
    opacity var(--iw-dur-3) var(--iw-ease-out),
    transform var(--iw-dur-3) var(--iw-ease-out);
}

.dark .queue-stack::before,
.dark .queue-stack::after {
  border-color: rgba(255, 255, 255, 0.09);
  background: rgba(255, 255, 255, 0.03);
}

.queue-stack::before {
  bottom: 0.0625rem;
  z-index: 1;
}

.queue-stack.is-stacked::before {
  opacity: 1;
  transform: none;
}

/* The second layer only appears once three or more are queued — it would be a
   lie about the pile's depth otherwise. */
.queue-stack::after {
  bottom: -0.125rem;
  left: 0.6875rem;
  right: 0.6875rem;
  z-index: 0;
}

.queue-stack.is-deep::after {
  opacity: 1;
  transform: none;
}

/* ── The card ───────────────────────────────────────────────────────────── */

/* Every colour comes from --st: amber, the chat rail's "waiting on you". */
.check-in {
  --st: var(--sl-wait);
  --rail: var(--st);
  --status: var(--st);

  position: relative;
  z-index: 2;
  display: flex;
  border-radius: 0.875rem;
  border: 1px solid color-mix(in srgb, var(--st) 24%, transparent);
  background:
    linear-gradient(color-mix(in srgb, var(--st) 7%, transparent), color-mix(in srgb, var(--st) 7%, transparent)),
    rgb(var(--app-canvas, 255 255 255));
  box-shadow: var(--iw-shadow-1);
  overflow: hidden;
  animation: check-in-arrive var(--iw-dur-4) var(--iw-ease-spring) both;
  transition:
    border-color var(--iw-dur-3) var(--iw-ease-out),
    background-color var(--iw-dur-3) var(--iw-ease-out);
}

.check-in__rail {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 0.1875rem;
  background: var(--rail);
}

.check-in__body {
  flex: 1;
  min-width: 0;
  padding: 0.5rem 0.625rem 0.5625rem 0.75rem;
}

/* The job keeps the byline it has on its card in the thread. It wraps rather
   than clipping: these are short names, and a name cut off mid-word in a
   sidebar is how two subagents end up looking like the same one. */
.check-in__title {
  flex: 1;
  min-width: 0;
  font-family: var(--sl-font-display, theme('fontFamily.display'));
  font-variation-settings: 'opsz' 11, 'SOFT' 30, 'WONK' 1;
  font-size: 0.8125rem;
  font-weight: 600;
  line-height: 1.25;
  letter-spacing: -0.006em;
  color: theme('colors.blue.950');
  overflow-wrap: anywhere;
}

.dark .check-in__title {
  color: rgba(255, 255, 255, 0.92);
}

.check-in__take {
  flex-shrink: 0;
  margin-top: 0.0625rem;
  padding: 0 0.25rem;
  border-radius: 0.25rem;
  background: rgba(19, 26, 44, 0.07);
  color: rgba(19, 26, 44, 0.55);
  font-size: 0.5625rem;
  font-weight: 600;
  line-height: 1.05rem;
  font-variant-numeric: tabular-nums;
}

.dark .check-in__take {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(219, 234, 254, 0.6);
}

.check-in__open {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.25rem;
  height: 1.25rem;
  margin: -0.0625rem -0.125rem 0 0;
  border-radius: var(--iw-r-xs);
  color: rgba(19, 26, 44, 0.35);
  transition:
    background-color var(--iw-dur-2) var(--iw-ease-out),
    color var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-1) var(--iw-ease-out);
}

.check-in__open:focus-visible {
  outline: none;
  box-shadow: var(--iw-focus-ring);
}

.check-in__open:hover {
  background: rgba(19, 26, 44, 0.07);
  color: rgba(19, 26, 44, 0.75);
}

.dark .check-in__open {
  color: rgba(255, 255, 255, 0.35);
}

.dark .check-in__open:hover {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.8);
}

.check-in__status {
  display: flex;
  align-items: baseline;
  gap: 0.3125rem;
  margin-top: 0.1875rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 0.625rem;
  line-height: 1.35;
  color: var(--status);
}

.check-in__status-icon {
  flex-shrink: 0;
  font-size: 0.5625rem;
}

.check-in__text {
  margin-top: 0.375rem;
  font-size: 0.6875rem;
  line-height: 1.45;
  color: rgba(19, 26, 44, 0.7);
  overflow-wrap: break-word;
}

.dark .check-in__text {
  color: rgba(255, 255, 255, 0.65);
}

/* A check-in lands rather than blinks — the card is keyed on the check-in id,
   so each new one plays this as it takes the front of the queue. It rises
   slightly out of the pile it was waiting in, which is where the next one
   genuinely comes from. */
@keyframes check-in-arrive {
  from { opacity: 0; transform: translateY(6px) scale(0.97); }
  to { opacity: 1; transform: none; }
}

@media (prefers-reduced-motion: reduce) {
  .check-in { animation: none; }
}

/* ── Buttons (the workspace's navy-ink pairing, unchanged) ──────────────── */

/* Both buttons share one transition contract, so the pair reacts as a pair —
   .iw-press supplies the scale under the pointer on top of this. */
.btn-primary,
.btn-ghost {
  transition:
    background-color var(--iw-dur-2) var(--iw-ease-out),
    border-color var(--iw-dur-2) var(--iw-ease-out),
    color var(--iw-dur-2) var(--iw-ease-out),
    box-shadow var(--iw-dur-2) var(--iw-ease-out),
    opacity var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-1) var(--iw-ease-out);
}

.btn-primary:focus-visible,
.btn-ghost:focus-visible {
  outline: none;
  box-shadow: var(--iw-focus-ring);
}

/* Navy ink primary - matching the composer's send button */
.btn-primary--active {
  background: theme('colors.blue.950');
  box-shadow: var(--iw-shadow-2), inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

.btn-primary--active:hover:not(:disabled) {
  background: theme('colors.blue.900');
  box-shadow: var(--iw-shadow-3), inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

.dark .btn-primary--active {
  background: #f3ede2;
}

.dark .btn-primary--active:hover:not(:disabled) {
  background: #ffffff;
}

/* Ghost secondary - quiet outline that only tints on hover */
.btn-ghost {
  border: 1px solid rgba(191, 219, 254, 0.7);
  color: rgba(19, 26, 44, 0.7);
  background: transparent;
}

.btn-ghost:hover:not(:disabled) {
  background: rgba(239, 246, 255, 0.9);
  border-color: rgba(147, 197, 253, 0.9);
  color: rgb(19, 26, 44);
}

.dark .btn-ghost {
  border-color: rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.7);
}

.dark .btn-ghost:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.95);
}

/* Focus is a ring rather than a border swap: the field's edge stays where it
   was and gains a halo, so nothing shifts by a pixel as you click into it. */
.answer-textarea {
  transition:
    border-color var(--iw-dur-2) var(--iw-ease-out),
    box-shadow var(--iw-dur-2) var(--iw-ease-out);
  outline: none;
}

.answer-textarea:focus {
  border-color: rgba(19, 26, 44, 0.45);
  box-shadow: 0 0 0 3px rgba(var(--iw-accent), 0.14);
}

.dark .answer-textarea:focus {
  border-color: rgba(255, 255, 255, 0.45);
}
</style>
