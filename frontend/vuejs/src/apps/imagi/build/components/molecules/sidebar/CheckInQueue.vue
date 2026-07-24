<!--
  CheckInQueue.vue — the main thread's processing queue.

  Background subagents never interrupt the user: when one finishes, needs an
  answer, or fails, it files a check-in that surfaces here, above the lead
  thread's composer. One card is shown at a time (FIFO) so the user stays
  single-threaded; the rest wait behind it as a visible pile.

  Same language as the Subagents pane: a status rail spines the card, the task
  keeps its serif byline, and parallel takes carry the n/m marker — a check-in
  is the same agent the user just saw over there, so it should look like it.
-->
<template>
  <div v-if="queue.length > 0" class="mb-1.5">
    <!-- Queue depth: only worth showing once something is waiting behind -->
    <div v-if="queue.length > 1" class="queue-head">
      <span class="queue-head__label">Waiting on you</span>
      <span class="queue-head__count">{{ queue.length }}</span>
      <span class="queue-head__rule"></span>
    </div>

    <!-- The pile: layers behind the card stand for the check-ins queued after
         this one, so the depth is a thing you see rather than a number. -->
    <div
      :class="[
        'queue-stack',
        queue.length > 1 ? 'is-stacked' : '',
        queue.length > 2 ? 'is-deep' : ''
      ]"
    >
      <article :key="current.id" :class="['check-in', `check-in--${tone}`]">
        <span class="check-in__rail" aria-hidden="true"></span>

        <div class="check-in__body">
          <!-- What came back, and from which task -->
          <div class="flex items-start gap-1.5">
            <h3 class="check-in__title">{{ current.task.title || 'Background task' }}</h3>
            <!-- One of several parallel takes on the same brief: say so, or
                 accepting the first one looks like the only option. -->
            <span
              v-if="siblingCount > 1"
              class="check-in__take"
              :title="`Take ${siblingIndex} of ${siblingCount} on the same brief`"
            >{{ siblingIndex }}/{{ siblingCount }}</span>
            <button
              type="button"
              title="Open this task"
              aria-label="Open this task"
              class="check-in__open"
              @click="emit('view', current)"
            >
              <i class="fas fa-arrow-up-right-from-square text-[9px]"></i>
            </button>
          </div>

          <div class="check-in__status">
            <i :class="[kindIcon, 'check-in__status-icon']"></i>
            <span class="truncate">{{ kindLabel }}</span>
          </div>

          <!-- Body: the question, the summary, or the error -->
          <p
            v-if="current.body"
            class="check-in__text"
            :class="expanded ? '' : 'line-clamp-3'"
          >
            {{ current.body }}
          </p>
          <button
            v-if="current.body && current.body.length > 180"
            type="button"
            class="check-in__more"
            @click="expanded = !expanded"
          >
            {{ expanded ? 'Show less' : 'Show more' }}
          </button>

          <!-- A question is answered in place: the answer restarts the subagent
               in the background, so the user never leaves this thread. -->
          <div v-if="current.kind === 'question'" class="mt-2">
            <textarea
              ref="answerInput"
              v-model="answer"
              rows="2"
              placeholder="Answer to send back…"
              class="answer-textarea w-full rounded-lg bg-white/70 dark:bg-white/[0.04] border border-blue-950/[0.1] dark:border-white/[0.12] text-blue-950 dark:text-white/90 placeholder-blue-950/35 dark:placeholder-white/30 text-[11px] px-2 py-1.5 resize-none leading-relaxed"
              @keydown.enter.exact.prevent="sendAnswer"
            ></textarea>
            <div class="flex items-center gap-1.5 mt-1.5">
              <button
                type="button"
                :disabled="!answer.trim()"
                class="btn-primary flex-1 rounded-full px-2.5 py-1 text-[11px] font-semibold transition-all duration-200"
                :class="answer.trim()
                  ? 'btn-primary--active text-[#fdf9f2] dark:text-blue-950'
                  : 'bg-blue-100/60 dark:bg-white/[0.05] text-blue-950/40 dark:text-white/40 cursor-not-allowed border border-blue-200/70 dark:border-white/[0.12]'"
                @click="sendAnswer"
              >
                Send answer
              </button>
              <button
                type="button"
                title="Deal with this later"
                class="btn-ghost rounded-full px-2.5 py-1 text-[11px] font-medium transition-colors"
                @click="emit('skip', current)"
              >
                Later
              </button>
            </div>
          </div>

          <!-- An auto-applied task is already part of the app: this is a
               notification, not a decision — just look or clear it away. -->
          <div v-else-if="applied" class="flex items-center gap-1.5 mt-2">
            <button
              type="button"
              class="btn-ghost flex-1 rounded-full px-2.5 py-1 text-[11px] font-medium transition-colors"
              @click="emit('view', current)"
            >
              View changes
            </button>
            <button
              type="button"
              class="btn-ghost flex-1 rounded-full px-2.5 py-1 text-[11px] font-medium transition-colors"
              @click="emit('skip', current)"
            >
              Dismiss
            </button>
          </div>

          <!-- A variant take (or a task whose auto-merge fell back) is merged or
               discarded from right here -->
          <div v-else-if="current.kind === 'ready'" class="flex items-center gap-1.5 mt-2">
            <button
              type="button"
              :disabled="busy"
              class="btn-primary btn-primary--active flex-1 rounded-full px-2.5 py-1 text-[11px] font-semibold text-[#fdf9f2] dark:text-blue-950 transition-all duration-200 disabled:opacity-50"
              @click="emit('accept', current)"
            >
              <i v-if="busy" class="fas fa-circle-notch fa-spin text-[10px]"></i>
              <span v-else>Add to my app</span>
            </button>
            <button
              type="button"
              :disabled="busy"
              class="btn-ghost flex-1 rounded-full px-2.5 py-1 text-[11px] font-medium transition-colors disabled:opacity-50"
              @click="emit('dismiss', current)"
            >
              Discard
            </button>
          </div>

          <!-- A failed task: nothing to merge, so it is just acknowledged -->
          <div v-else class="flex items-center gap-1.5 mt-2">
            <button
              type="button"
              class="btn-ghost flex-1 rounded-full px-2.5 py-1 text-[11px] font-medium transition-colors"
              @click="emit('view', current)"
            >
              See what happened
            </button>
            <button
              type="button"
              class="btn-ghost flex-1 rounded-full px-2.5 py-1 text-[11px] font-medium transition-colors"
              @click="emit('skip', current)"
            >
              Dismiss
            </button>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
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
  /** Clear this entry without acting on it */
  (e: 'skip', checkIn: CheckInDto): void
  /** Open the task's (read-only) thread */
  (e: 'view', checkIn: CheckInDto): void
}>()

const answer = ref('')
const expanded = ref(false)
const answerInput = ref<HTMLTextAreaElement | null>(null)

// The queue is FIFO — the user works one item at a time.
const current = computed(() => props.queue[0]!)

// Moving to the next card must not carry the previous card's draft answer or
// expanded state with it.
watch(() => current.value?.id, async (id) => {
  answer.value = ''
  expanded.value = false
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

// A finished solo task merges itself into the app; its check-in is a
// notification, not a review. Variant takes and merge-conflict fallbacks stay
// at 'ready' (still awaiting the user), so they keep the Add/Discard card.
const applied = computed(
  () => current.value?.kind === 'ready' && current.value?.task.review_status === 'accepted'
)

const kindIcon = computed(() => {
  switch (current.value?.kind) {
    case 'question': return 'fas fa-circle-question'
    case 'error': return 'fas fa-triangle-exclamation'
    default: return applied.value ? 'fas fa-check-double' : 'fas fa-check'
  }
})

const kindLabel = computed(() => {
  switch (current.value?.kind) {
    case 'question': return 'Needs your answer'
    case 'error': return 'Stopped early'
    default: return applied.value ? 'Done — added to your app' : 'Finished — ready to review'
  }
})

/**
 * The rail's reading, on the Subagents pane's terms: anything still wanting a
 * decision carries the navy-ink "waiting on you" rail, work already merged
 * recedes to a hairline, and a failed run is the one warm note in the pane.
 */
const tone = computed(() => {
  if (current.value?.kind === 'error') return 'error'
  if (applied.value) return 'settled'
  return 'waiting'
})

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
  color: rgba(23, 37, 84, 0.45);
}

.dark .queue-head__label {
  color: rgba(255, 255, 255, 0.42);
}

.queue-head__count {
  padding: 0 0.25rem;
  border-radius: 0.25rem;
  background: rgba(23, 37, 84, 0.06);
  color: rgba(23, 37, 84, 0.5);
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
  background: linear-gradient(90deg, rgba(23, 37, 84, 0.12) 0%, rgba(23, 37, 84, 0) 100%);
}

.dark .queue-head__rule {
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.14) 0%, rgba(255, 255, 255, 0) 100%);
}

/* ── The pile ───────────────────────────────────────────────────────────── */

/* Two hairline layers peeking out below the card: the queue has depth, and
   the depth is worth seeing without opening anything. */
.queue-stack {
  position: relative;
}

.queue-stack.is-stacked {
  padding-bottom: 0.3125rem;
}

.queue-stack.is-stacked::before,
.queue-stack.is-deep::after {
  content: '';
  position: absolute;
  left: 0.375rem;
  right: 0.375rem;
  height: 0.625rem;
  border: 1px solid rgba(23, 37, 84, 0.09);
  border-top: none;
  border-radius: 0 0 0.625rem 0.625rem;
  background: rgba(239, 246, 255, 0.7);
}

.dark .queue-stack.is-stacked::before,
.dark .queue-stack.is-deep::after {
  border-color: rgba(255, 255, 255, 0.09);
  background: rgba(255, 255, 255, 0.03);
}

.queue-stack.is-stacked::before {
  bottom: 0.0625rem;
  z-index: 1;
}

/* The second layer only appears once three or more are queued — it would be a
   lie about the pile's depth otherwise. */
.queue-stack.is-deep::after {
  bottom: -0.125rem;
  left: 0.6875rem;
  right: 0.6875rem;
  z-index: 0;
}

/* ── The card ───────────────────────────────────────────────────────────── */

.check-in {
  --rail: theme('colors.blue.950');
  --status: rgba(23, 37, 84, 0.75);

  position: relative;
  z-index: 2;
  display: flex;
  border-radius: 0.75rem;
  border: 1px solid rgba(23, 37, 84, 0.1);
  background: rgba(239, 246, 255, 0.75);
  overflow: hidden;
  animation: check-in-arrive 0.4s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.dark .check-in {
  --rail: #f3ede2;
  --status: rgba(243, 237, 226, 0.85);
  border-color: rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.04);
}

/* Already merged — this is a notification, so it recedes the way settled work
   does in the Subagents pane. */
.check-in--settled {
  --rail: rgba(23, 37, 84, 0.12);
  --status: rgba(23, 37, 84, 0.45);
}

.dark .check-in--settled {
  --rail: rgba(255, 255, 255, 0.12);
  --status: rgba(219, 234, 254, 0.42);
}

/* A run that stopped early: the one warm note in a pane that is otherwise
   all navy and cream. */
.check-in--error {
  --rail: theme('colors.amber.500');
  --status: theme('colors.amber.700');
  border-color: rgba(251, 191, 36, 0.45);
  background: rgba(255, 251, 235, 0.8);
}

.dark .check-in--error {
  --rail: theme('colors.amber.400');
  --status: theme('colors.amber.300');
  border-color: rgba(251, 191, 36, 0.22);
  background: rgba(245, 158, 11, 0.07);
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

/* The task keeps the byline it had in the Subagents pane */
.check-in__title {
  flex: 1;
  min-width: 0;
  font-family: theme('fontFamily.display');
  font-variation-settings: 'opsz' 11, 'SOFT' 30, 'WONK' 1;
  font-size: 0.8125rem;
  font-weight: 600;
  line-height: 1.25;
  letter-spacing: -0.006em;
  color: theme('colors.blue.950');
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dark .check-in__title {
  color: rgba(255, 255, 255, 0.92);
}

.check-in__take {
  flex-shrink: 0;
  margin-top: 0.0625rem;
  padding: 0 0.25rem;
  border-radius: 0.25rem;
  background: rgba(23, 37, 84, 0.07);
  color: rgba(23, 37, 84, 0.55);
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
  border-radius: 0.375rem;
  color: rgba(23, 37, 84, 0.35);
  transition: background-color 0.18s ease, color 0.18s ease;
}

.check-in__open:hover {
  background: rgba(23, 37, 84, 0.07);
  color: rgba(23, 37, 84, 0.75);
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
  align-items: center;
  gap: 0.3125rem;
  margin-top: 0.1875rem;
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
  color: rgba(23, 37, 84, 0.7);
  overflow-wrap: break-word;
}

.dark .check-in__text {
  color: rgba(255, 255, 255, 0.65);
}

.check-in__more {
  margin-top: 0.125rem;
  font-size: 0.625rem;
  font-weight: 500;
  color: rgba(23, 37, 84, 0.45);
  transition: color 0.18s ease;
}

.check-in__more:hover {
  color: rgba(23, 37, 84, 0.75);
}

.dark .check-in__more {
  color: rgba(255, 255, 255, 0.4);
}

.dark .check-in__more:hover {
  color: rgba(255, 255, 255, 0.7);
}

/* A check-in lands rather than blinks — the card is keyed on the check-in id,
   so each new one plays this as it takes the front of the queue. */
@keyframes check-in-arrive {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: none; }
}

@media (prefers-reduced-motion: reduce) {
  .check-in { animation: none; }
}

/* ── Buttons (the workspace's navy-ink pairing, unchanged) ──────────────── */

/* Navy ink primary - matching the composer's send button */
.btn-primary--active {
  background: theme('colors.blue.950');
  box-shadow:
    0 1px 2px rgba(23, 37, 84, 0.2),
    0 3px 8px -2px rgba(23, 37, 84, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

.btn-primary--active:hover:not(:disabled) {
  background: theme('colors.blue.900');
  box-shadow:
    0 2px 3px rgba(23, 37, 84, 0.22),
    0 5px 12px -2px rgba(23, 37, 84, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

.dark .btn-primary--active {
  background: #f3ede2;
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.4),
    0 3px 8px -2px rgba(0, 0, 0, 0.45);
}

.dark .btn-primary--active:hover:not(:disabled) {
  background: #ffffff;
  box-shadow:
    0 2px 3px rgba(0, 0, 0, 0.4),
    0 5px 12px -2px rgba(0, 0, 0, 0.5);
}

/* Ghost secondary - quiet outline that only tints on hover */
.btn-ghost {
  border: 1px solid rgba(191, 219, 254, 0.7);
  color: rgba(23, 37, 84, 0.7);
  background: transparent;
}

.btn-ghost:hover:not(:disabled) {
  background: rgba(239, 246, 255, 0.9);
  color: rgb(23, 37, 84);
}

.dark .btn-ghost {
  border-color: rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.7);
}

.dark .btn-ghost:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.95);
}

/* An error card sits on a warm wash, so the ghost outline warms with it */
.check-in--error .btn-ghost {
  border-color: rgba(251, 191, 36, 0.5);
}

.check-in--error .btn-ghost:hover:not(:disabled) {
  background: rgba(254, 243, 199, 0.6);
}

.dark .check-in--error .btn-ghost {
  border-color: rgba(251, 191, 36, 0.28);
}

.dark .check-in--error .btn-ghost:hover:not(:disabled) {
  background: rgba(245, 158, 11, 0.12);
}

.answer-textarea {
  transition: border-color 0.18s ease;
  outline: none;
}

.answer-textarea:focus {
  border-color: rgba(23, 37, 84, 0.45);
}

.dark .answer-textarea:focus {
  border-color: rgba(255, 255, 255, 0.45);
}
</style>
