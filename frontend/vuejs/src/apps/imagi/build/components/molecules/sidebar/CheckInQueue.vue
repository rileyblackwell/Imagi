<!--
  CheckInQueue.vue — the main thread's processing queue.

  Background subagents never interrupt the user: when one finishes, needs an
  answer, or fails, it files a check-in that surfaces here, above the lead
  thread's composer. One card is shown at a time (FIFO) so the user stays
  single-threaded; the rest wait behind a count.
-->
<template>
  <div v-if="queue.length > 0" class="mb-1.5">
    <!-- Queue depth: only worth showing once something is waiting behind -->
    <div
      v-if="queue.length > 1"
      class="flex items-center gap-1.5 px-1 pb-1 text-[10px] font-semibold uppercase tracking-wider text-blue-950/40 dark:text-white/40"
    >
      <i class="fas fa-inbox text-[9px]"></i>
      <span>{{ queue.length }} agents waiting on you</span>
    </div>

    <div class="check-in-card rounded-xl border px-2.5 py-2" :class="cardTone">
      <!-- Header: what came back, and from which task -->
      <div class="flex items-start gap-2">
        <div class="check-in-chip flex items-center justify-center w-5 h-5 rounded-md shrink-0 mt-0.5">
          <i :class="[kindIcon, 'text-[9px]']"></i>
        </div>
        <div class="flex-1 min-w-0">
          <div class="text-[11px] font-semibold text-blue-950/90 dark:text-white/90 truncate">
            {{ current.task.title || 'Background task' }}
          </div>
          <div class="text-[10px] text-blue-950/45 dark:text-white/40">
            {{ kindLabel }}
            <!-- One of several parallel takes on the same brief: say so, or
                 accepting the first one looks like the only option. -->
            <span v-if="siblingCount > 1"> · take {{ siblingIndex }} of {{ siblingCount }}</span>
          </div>
        </div>
        <button
          type="button"
          title="Open this task"
          aria-label="Open this task"
          class="shrink-0 inline-flex items-center justify-center w-6 h-6 rounded-md text-blue-950/40 dark:text-white/40 hover:bg-blue-100/70 dark:hover:bg-white/[0.08] hover:text-blue-950/70 dark:hover:text-white/70 transition-colors"
          @click="emit('view', current)"
        >
          <i class="fas fa-arrow-up-right-from-square text-[10px]"></i>
        </button>
      </div>

      <!-- Body: the question, the summary, or the error -->
      <p
        v-if="current.body"
        class="mt-1.5 text-[11px] leading-snug text-blue-950/70 dark:text-white/65 break-words"
        :class="expanded ? '' : 'line-clamp-3'"
      >
        {{ current.body }}
      </p>
      <button
        v-if="current.body && current.body.length > 180"
        type="button"
        class="mt-0.5 text-[10px] font-medium text-blue-950/45 dark:text-white/40 hover:text-blue-950/75 dark:hover:text-white/70 transition-colors"
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

      <!-- A finished task is merged or discarded from right here -->
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

const kindIcon = computed(() => {
  switch (current.value?.kind) {
    case 'question': return 'fas fa-circle-question'
    case 'error': return 'fas fa-triangle-exclamation'
    default: return 'fas fa-check'
  }
})

const kindLabel = computed(() => {
  switch (current.value?.kind) {
    case 'question': return 'Needs your answer'
    case 'error': return 'Stopped early'
    default: return 'Finished — ready to review'
  }
})

// Errors carry a warm tone; questions and completions stay in the workspace's
// quiet blue so the queue never reads as alarming.
const cardTone = computed(() =>
  current.value?.kind === 'error'
    ? 'border-amber-200/80 dark:border-amber-400/20 bg-amber-50/60 dark:bg-amber-500/[0.06]'
    : 'border-blue-950/[0.1] dark:border-white/[0.12] bg-blue-50/60 dark:bg-white/[0.04]'
)

function sendAnswer() {
  const text = answer.value.trim()
  if (!text) return
  answer.value = ''
  emit('answer', current.value, text)
}
</script>

<style scoped>
/* Chip tint follows the workspace's navy-ink / cream pairing */
.check-in-chip {
  background: rgba(23, 37, 84, 0.08);
  box-shadow: inset 0 0 0 1px rgba(23, 37, 84, 0.06);
  color: rgba(23, 37, 84, 0.8);
}

.dark .check-in-chip {
  background: rgba(243, 237, 226, 0.12);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
  color: rgba(243, 237, 226, 0.9);
}

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

.answer-textarea {
  transition: border-color 0.18s ease, box-shadow 0.18s ease;
  outline: none;
}

.answer-textarea:focus {
  border-color: rgba(59, 130, 246, 0.55);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.dark .answer-textarea:focus {
  border-color: rgba(147, 197, 253, 0.5);
  box-shadow: 0 0 0 3px rgba(147, 197, 253, 0.18);
}
</style>
