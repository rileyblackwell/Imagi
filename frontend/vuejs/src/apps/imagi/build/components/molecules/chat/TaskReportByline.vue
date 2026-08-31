<!--
  TaskReportByline.vue — a subagent speaking in the main thread.

  Subagents run in parallel and finish in their own time. When one does, it
  posts what it did straight into the main thread, so the message underneath
  this line is not the main agent talking — it is the subagent's own sign-off,
  arriving at the bottom of the thread the moment it lands, whatever order the
  work was dispatched in.

  So the whole job of this line is attribution: whose words these are, where
  the work stands, and what it was asked for. The reading matter is the message
  below; this is a byline, not a card — a second bordered box around a summary
  the transcript is already showing would be a heavier way of saying less.

  It keeps the dispatch card's state vocabulary (the same four tones, the same
  words for the same states) because it is the same subagent the user watched
  start, and clicking it opens the same thread.
-->
<template>
  <button
    type="button"
    :class="['report-byline', `report-byline--${tone}`]"
    title="Open this subagent's thread"
    @click="emit('open')"
  >
    <span class="report-byline__head">
      <span class="report-byline__chip">
        <i :class="icon"></i>
      </span>
      <span class="report-byline__state">{{ label }}</span>
      <i class="fas fa-chevron-right report-byline__chevron" aria-hidden="true"></i>
    </span>
    <!-- What it was asked for, in the user's language. The summary below only
         means something next to the job it is a summary of — so it wraps and
         is read whole. On its own line, because the main thread is a sidebar:
         beside the state there is room for three words and an ellipsis, which
         is worse than not saying it at all. -->
    <span v-if="job" class="report-byline__job">{{ job }}</span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { TaskReport } from '../../../types/services'

const props = defineProps<{ report: TaskReport }>()

const emit = defineEmits<{ (e: 'open'): void }>()

/**
 * Where the work stood when the subagent said this. Read off the report the
 * message carries rather than the live subagent: this is a line in a
 * transcript, so it has to keep saying what was true when it was written, in a
 * thread reloaded a week later as much as one second after it landed.
 */
const state = computed(() => {
  switch (props.report.kind) {
    case 'question':
      return {
        tone: 'asking',
        icon: 'fas fa-circle-question',
        label: 'Subagent needs an answer',
      }
    case 'ready':
      return {
        tone: 'asking',
        icon: 'fas fa-check',
        label: 'Subagent complete — waiting on you',
      }
    case 'error':
      return {
        tone: 'stopped',
        icon: 'fas fa-triangle-exclamation',
        label: 'Subagent stopped before finishing',
      }
    default:
      return {
        tone: 'done',
        icon: 'fas fa-check',
        // The whole point of a solo subagent: it applied its own work, so
        // there is nothing here for the user to approve.
        label: 'Subagent complete — added to your app',
      }
  }
})

const tone = computed(() => state.value.tone)
const icon = computed(() => state.value.icon)
const label = computed(() => state.value.label)
const job = computed(() => props.report.goal || props.report.title || '')
</script>

<style scoped>
/* Two lines: where it stands, then what it was for. Every colour comes from
   the three variables, so a state is one block of overrides. */
.report-byline {
  --ink: rgba(23, 37, 84, 0.62);
  --chip-bg: rgba(23, 37, 84, 0.08);
  --chip-fg: rgba(23, 37, 84, 0.8);

  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0.125rem;
  width: 100%;
  margin-bottom: 0.375rem;
  padding: 0.125rem 0.25rem 0.3125rem 0;
  border: 0;
  background: none;
  text-align: left;
  cursor: pointer;
}

.dark .report-byline {
  --ink: rgba(219, 234, 254, 0.6);
  --chip-bg: rgba(243, 237, 226, 0.12);
  --chip-fg: rgba(243, 237, 226, 0.9);
}

.report-byline__head {
  display: flex;
  align-items: center;
  gap: 0.4375rem;
}

.report-byline:focus-visible {
  outline: none;
  border-radius: var(--iw-r-sm);
  box-shadow: var(--iw-focus-ring);
}

/* Landed in the app: the transcript's one affirmative note, same green the
   dispatch card settles into. */
.report-byline--done {
  --ink: theme('colors.green.700');
  --chip-bg: theme('colors.green.100');
  --chip-fg: theme('colors.green.700');
}

.dark .report-byline--done {
  --ink: theme('colors.green.300');
  --chip-bg: rgba(74, 222, 128, 0.16);
  --chip-fg: theme('colors.green.300');
}

/* Wants the user — a question to answer, or finished work to merge. Solid
   navy ink, the workspace's "this one is on you" mark. */
.report-byline--asking {
  --ink: rgba(23, 37, 84, 0.78);
  --chip-bg: rgba(23, 37, 84, 0.1);
  --chip-fg: theme('colors.blue.950');
}

.dark .report-byline--asking {
  --ink: rgba(243, 237, 226, 0.85);
  --chip-bg: rgba(243, 237, 226, 0.16);
  --chip-fg: #f3ede2;
}

/* A run that died. Warm rather than alarming: nothing was lost from the app,
   because the work never touched it. */
.report-byline--stopped {
  --ink: theme('colors.amber.700');
  --chip-bg: rgba(245, 158, 11, 0.14);
  --chip-fg: theme('colors.amber.600');
}

.dark .report-byline--stopped {
  --ink: theme('colors.amber.200');
  --chip-bg: rgba(252, 211, 77, 0.16);
  --chip-fg: theme('colors.amber.200');
}

.report-byline__chip {
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
}

/* Takes the row so the chevron sits at the far edge, and wraps rather than
   overflowing: the main thread is a sidebar, and these labels are sentences. */
.report-byline__state {
  flex: 1;
  min-width: 0;
  font-size: 0.625rem;
  font-weight: 650;
  line-height: 1.3;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  color: var(--ink);
}

/* The job it was given, quieter than the state — the summary below is where
   the detail belongs, and this is the reminder of what it answers. Indented to
   start under the state's first letter, and wrapping in full: a job description
   with its end cut off is not a reminder of anything. */
.report-byline__job {
  padding-left: 1.6875rem;
  font-size: 0.6875rem;
  line-height: 1.4;
  color: rgba(23, 37, 84, 0.45);
  overflow-wrap: anywhere;
}

.dark .report-byline__job {
  color: rgba(255, 255, 255, 0.4);
}

.report-byline__chevron {
  flex-shrink: 0;
  font-size: 0.5625rem;
  color: rgba(23, 37, 84, 0.28);
  transition:
    color var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-2) var(--iw-ease-out);
}

.dark .report-byline__chevron {
  color: rgba(255, 255, 255, 0.28);
}

.report-byline:hover .report-byline__chevron {
  color: rgba(23, 37, 84, 0.6);
  transform: translateX(2px);
}

.dark .report-byline:hover .report-byline__chevron {
  color: rgba(255, 255, 255, 0.6);
}

@media (prefers-reduced-motion: reduce) {
  .report-byline:hover .report-byline__chevron {
    transform: none;
  }
}
</style>
