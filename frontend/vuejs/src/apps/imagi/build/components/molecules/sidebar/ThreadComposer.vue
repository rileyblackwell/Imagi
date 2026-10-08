<!--
  ThreadComposer.vue — talking to one thread directly.

  Threads are dispatched by the coordinator, but the user can step into one and
  steer it: what they type here is the thread's next turn, the same as a
  follow-up the coordinator would forward. Mid-run it waits behind the current
  run (shown as a queued row, cancellable); otherwise it starts the thread
  again on its own copy of the project, and the thread's ending reports back
  to the coordinator as usual.

  Deliberately smaller than the coordinator's composer: no model menu, no
  usage meter, no dictation. A thread keeps the model it was dispatched on.
-->
<template>
  <div class="px-2 pt-1 pb-3">
    <!-- A discarded or archived thread has no copy of the project left to
         work in, so there is nothing to steer. -->
    <div
      v-if="!canSteer"
      class="rounded-2xl border border-ink/[0.08] dark:border-white/[0.14] bg-ink/[0.03] dark:bg-white/[0.03] px-3 py-2.5"
    >
      <p class="text-[11px] leading-snug text-ink/60 dark:text-white/55">
        {{ lockedNote }}
      </p>
      <button
        type="button"
        class="thread-btn iw-press mt-2 w-full rounded-full px-3 py-1.5 text-[11px] font-semibold text-paper dark:text-ink"
        @click="emit('back')"
      >
        {{ backLabel }}
      </button>
    </div>

    <template v-else>
      <Transition name="queued">
        <div
          v-if="instance.queuedPrompt"
          class="queued-row flex items-center gap-2 rounded-xl border border-blue-100 dark:border-white/[0.08] bg-ink/[0.03] dark:bg-white/[0.04] px-2.5 py-1.5 mb-1.5"
        >
          <i class="fas fa-hourglass-half text-[10px] text-ink/40 dark:text-white/40 shrink-0"></i>
          <div class="flex-1 min-w-0">
            <p class="text-[11px] font-medium text-ink/75 dark:text-white/70 truncate" :title="instance.queuedPrompt">
              {{ instance.queuedPrompt }}
            </p>
            <p class="text-[10px] text-ink/40 dark:text-white/35">Queued — the thread reads it when this step finishes</p>
          </div>
          <button
            type="button"
            title="Cancel queued message"
            aria-label="Cancel queued message"
            class="queued-cancel iw-press shrink-0 inline-flex items-center justify-center w-6 h-6 rounded-full text-ink/40 dark:text-white/40 hover:bg-blue-100/70 dark:hover:bg-white/[0.08] hover:text-ink/70 dark:hover:text-white/70"
            @click="store.clearQueuedPrompt(instance.id)"
          >
            <i class="fas fa-times text-[10px]"></i>
          </button>
        </div>
      </Transition>

      <div class="thread-input-shell rounded-2xl bg-ink/[0.03] dark:bg-white/[0.03] border border-ink/[0.08] dark:border-white/[0.14] shadow-sm">
        <textarea
          ref="textarea"
          v-model="draft"
          :placeholder="placeholder"
          rows="2"
          aria-label="Message this thread"
          class="thread-textarea w-full bg-transparent text-ink dark:text-white/90 placeholder-ink/40 dark:placeholder-bone/40 text-sm px-3 pt-2.5 pb-1 resize-none leading-relaxed"
          style="min-height: 56px; max-height: 180px;"
          @keydown.enter.exact.prevent="send"
          @input="autoResize"
        ></textarea>
        <div class="flex items-center justify-between gap-2 px-2 pb-2">
          <p class="thread-hint min-w-0 truncate text-[10px] text-ink/40 dark:text-white/35">
            {{ hint }}
          </p>
          <button
            type="button"
            :title="instance.isProcessing ? 'Queue for this thread (Enter)' : 'Send to this thread (Enter)'"
            :aria-label="instance.isProcessing ? 'Queue for this thread' : 'Send to this thread'"
            :disabled="!draft.trim()"
            class="thread-send iw-press flex shrink-0 items-center justify-center w-8 h-8 rounded-full"
            :class="draft.trim() ? 'thread-send--ready text-paper dark:text-ink' : 'thread-send--idle'"
            @click="send"
          >
            <i class="fas fa-arrow-up text-xs" aria-hidden="true"></i>
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { useAgentStore } from '../../../stores/agentStore'
import type { AgentInstance } from '../../../types/services'

const props = withDefaults(
  defineProps<{
    instance: AgentInstance
    /** What the way out says when the thread cannot be steered. */
    backLabel?: string
  }>(),
  { backLabel: 'Back to threads' }
)

const emit = defineEmits<{ (e: 'back'): void }>()

const store = useAgentStore()
const draft = ref('')
const textarea = ref<HTMLTextAreaElement | null>(null)

const canSteer = computed(
  () => !props.instance.archivedAt && props.instance.reviewStatus !== 'dismissed'
)

const lockedNote = computed(() =>
  props.instance.archivedAt
    ? 'This thread is archived. Ask the coordinator for anything new and it will start a fresh thread.'
    : 'This thread’s work was discarded, so it has nothing left to work on. Ask the coordinator and it will start a fresh thread.'
)

const placeholder = computed(() => {
  if (props.instance.isProcessing) return 'Steer this thread — it reads this when the current step finishes…'
  switch (props.instance.reviewStatus) {
    case 'input': return 'Answer this thread…'
    case 'failed': return 'Tell this thread how to carry on…'
    case 'accepted': return 'Ask this thread for a change to its work…'
    default: return 'Message this thread…'
  }
})

const hint = computed(() =>
  props.instance.isProcessing
    ? 'Working — your message waits for this step'
    : 'Replies here, and reports back to the coordinator'
)

function autoResize() {
  const el = textarea.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = `${Math.min(el.scrollHeight, 180)}px`
}

function send() {
  const text = draft.value.trim()
  if (!text) return
  if (store.steerThread(props.instance.id, text)) {
    draft.value = ''
    void nextTick(autoResize)
  }
}

// A draft belongs to the thread it was typed in.
watch(() => props.instance.id, () => {
  draft.value = ''
  void nextTick(autoResize)
})
</script>

<style scoped>
.thread-input-shell {
  transition:
    border-color var(--iw-dur-2) var(--iw-ease-out),
    box-shadow var(--iw-dur-2) var(--iw-ease-out);
}

.thread-input-shell:focus-within {
  border-color: rgba(19, 26, 44, 0.4);
  box-shadow: 0 0 0 3px rgba(var(--iw-accent), 0.13);
}

.dark .thread-input-shell:focus-within {
  border-color: rgba(255, 255, 255, 0.4);
}

.thread-textarea:focus {
  outline: none;
}

.thread-send {
  border: 1px solid transparent;
  transition:
    background-color var(--iw-dur-2) var(--iw-ease-out),
    color var(--iw-dur-2) var(--iw-ease-out),
    box-shadow var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-1) var(--iw-ease-out);
}

.thread-send:focus-visible,
.thread-btn:focus-visible,
.queued-cancel:focus-visible {
  outline: none;
  box-shadow: var(--iw-focus-ring);
}

.thread-send:disabled {
  cursor: not-allowed;
}

.thread-send--idle {
  background-color: rgba(219, 234, 254, 0.6);
  border-color: rgba(191, 219, 254, 0.7);
  color: rgba(19, 26, 44, 0.4);
}

.dark .thread-send--idle {
  background-color: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.4);
}

/* Navy ink primary, the coordinator composer's recipe */
.thread-send--ready,
.thread-btn {
  background: theme('colors.blue.950');
  box-shadow: var(--iw-shadow-2), inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

.thread-send--ready:hover,
.thread-btn:hover {
  background: theme('colors.blue.900');
}

.dark .thread-send--ready,
.dark .thread-btn {
  background: #f3ede2;
}

.dark .thread-send--ready:hover,
.dark .thread-btn:hover {
  background: #ffffff;
}

.queued-enter-active,
.queued-leave-active {
  transition:
    opacity var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-3) var(--iw-ease-out),
    margin-bottom var(--iw-dur-3) var(--iw-ease-out);
}

.queued-enter-from,
.queued-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.98);
  margin-bottom: -2.25rem;
}
</style>
