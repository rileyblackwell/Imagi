<!--
  ThreadComposer.vue — talking to one thread directly.

  Threads are dispatched by the coordinator, but the user can step into one and
  steer it: what they type here is the thread's next turn, the same as a
  follow-up the coordinator would forward. Mid-run it waits behind the current
  run (shown as a queued row, cancellable); otherwise it starts the thread
  again on its own copy of the project, and the thread's ending reports back
  to the coordinator as usual.

  It wears the coordinator's own composer (AgentComposer), so the two look
  and work the same. The thread's model and reasoning are its own: changing
  them here changes this thread only.
-->
<template>
  <!-- A discarded or archived thread has no copy of the project left to
       work in, so there is nothing to steer. -->
  <div v-if="!canSteer" class="px-2 pt-1 pb-3">
    <div class="rounded-2xl border border-ink/[0.08] dark:border-white/[0.14] bg-ink/[0.03] dark:bg-white/[0.03] px-3 py-2.5">
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
  </div>

  <!-- The coordinator's composer, as is: microphone, send arrow, model and
       reasoning, usage. Keyed by thread, so a draft belongs to the thread it
       was typed in. -->
  <AgentComposer
    v-else
    :key="instance.id"
    :instance="instance"
    :submit="send"
    :placeholder="placeholder"
    queued-note="Queued — the thread reads it when this step finishes"
    @stop="store.abortInstanceRun(instance.id)"
  >
    <!-- A run that died: the one-tap way to pick the job back up, from where
         it stopped. Typing instead also works, and says how to carry on. -->
    <div
      v-if="instance.reviewStatus === 'failed' && !instance.isProcessing"
      class="retry-row flex items-center gap-2 rounded-xl px-2.5 py-1.5 mb-1.5"
    >
      <span class="retry-row__mark shrink-0" aria-hidden="true"><i class="fas fa-xmark"></i></span>
      <p class="flex-1 min-w-0 text-[11px] font-medium text-ink/75 dark:text-white/70">
        This thread stopped before finishing.
      </p>
      <button
        type="button"
        class="retry-btn thread-btn iw-press shrink-0 inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[11px] font-semibold"
        @click="retry"
      >
        <i class="fas fa-rotate-right text-[9px]" aria-hidden="true"></i>
        Try again
      </button>
    </div>
  </AgentComposer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAgentStore } from '../../../stores/agentStore'
import AgentComposer from '../chat/AgentComposer.vue'
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

const canSteer = computed(
  () => !props.instance.archivedAt && props.instance.reviewStatus !== 'dismissed'
)

const lockedNote = computed(() =>
  props.instance.archivedAt
    ? 'This thread is archived. Ask the coordinator for anything new and it will start a fresh thread.'
    : 'This thread’s work was discarded, so it has nothing left to work on. Ask the coordinator and it will start a fresh thread.'
)

/** The box says the one thing that is new here: you can steer this thread. */
const placeholder = computed(() => {
  if (props.instance.isProcessing) return 'Steer this thread — it reads this when the current step finishes…'
  switch (props.instance.reviewStatus) {
    case 'input': return 'Answer this thread, or steer it somewhere else…'
    case 'failed': return 'Steer this thread — tell it how to carry on…'
    default: return 'Steer this thread…'
  }
})

function retry() {
  if (props.instance.conversationId != null) store.retryTask(props.instance.conversationId)
}

/** The thread's next turn. Mid-run it waits behind the run. */
function send(text: string) {
  store.steerThread(props.instance.id, text)
}
</script>

<style scoped>
.thread-btn:focus-visible {
  outline: none;
  box-shadow: var(--iw-focus-ring);
}

/* Navy ink primary, the composer's send recipe */
.thread-btn {
  background: theme('colors.blue.950');
  box-shadow: var(--iw-shadow-2), inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

.thread-btn:hover {
  background: theme('colors.blue.900');
}

.dark .thread-btn {
  background: #f3ede2;
}

.dark .thread-btn:hover {
  background: #ffffff;
}

/* A stopped thread: the chat rail's red, with the workspace's lit pill as
   the way back. */
.retry-row {
  border: 1px solid color-mix(in srgb, var(--sl-bad) 24%, transparent);
  background: color-mix(in srgb, var(--sl-bad) 7%, transparent);
}

.retry-row__mark {
  display: grid;
  place-items: center;
  width: 1rem;
  height: 1rem;
  border-radius: 50%;
  background: var(--sl-bad);
  color: rgb(var(--app-canvas, 255 255 255));
  font-size: 0.5rem;
  box-shadow: 0 0 12px -2px var(--sl-bad);
}

.retry-btn,
.dark .retry-btn {
  background: var(--sl-grad);
  color: var(--sl-on-accent, #1a0e08);
  box-shadow: var(--sl-btn-shadow);
}

.retry-btn:hover,
.dark .retry-btn:hover {
  background: var(--sl-grad);
  box-shadow: var(--sl-btn-shadow-hover);
}
</style>
