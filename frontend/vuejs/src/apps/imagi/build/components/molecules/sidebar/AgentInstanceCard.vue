<!--
  AgentInstanceCard.vue — one subagent, as a line in the crew ledger.

  Each card is spined by a status rail on its left edge: the rail is the only
  thing that differs at a glance, so a column of these reads as a single
  instrument — live work travels down the rail, work waiting on you sits as
  solid ink, settled work fades to a hairline. The agent's name is set in the
  brand serif, which makes the list read as a cast of characters rather than
  another stack of chat rows.
-->
<template>
  <article
    :class="[
      'iw-surface group relative flex items-start gap-1.5 pt-[0.4375rem] pr-2 pb-[0.4375rem] pl-3 rounded-iw-md border cursor-pointer overflow-hidden',
      'hover:[transform:translateY(-1px)] active:[transform:translateY(0)_scale(0.985)] active:[transition-duration:var(--iw-dur-1)]',
      'motion-reduce:hover:[transform:none] motion-reduce:active:[transform:none]',
      'focus-visible:![outline:none]',
      isArchived
        ? 'opacity-[0.72] hover:opacity-100 [transition:opacity_var(--iw-dur-2)_var(--iw-ease-out)]'
        : '[transition:background-color_var(--iw-dur-2)_var(--iw-ease-out),border-color_var(--iw-dur-2)_var(--iw-ease-out),box-shadow_var(--iw-dur-2)_var(--iw-ease-out),transform_var(--iw-dur-2)_var(--iw-ease-out)]',
      isActive ? CARD_SELECTED : CARD,
      RAIL_TONE[status.state],
      status.state === 'working' && WORKING_GLOW
    ]"
    :style="{ '--stagger': `${Math.min(index, 8) * 45}ms` }"
    role="button"
    tabindex="0"
    :aria-current="isActive ? 'true' : undefined"
    @click="emit('select')"
    @keydown.enter.prevent="emit('select')"
    @keydown.space.prevent="emit('select')"
  >
    <!-- Hover lifts the card off the column rather than nudging it sideways: a
         sideways shift re-lays the text out by a pixel, which reads as a wobble
         in a list this dense. Rising is silent. The press puts it back down,
         slightly compressed — the whole row behaves like one physical control.
         Selected wears the soft baby-blue wash the workspace uses for "you are
         here". -->
    <!-- The spine: state as a vertical rail, animated while a run is live —
         ink travels down it (::after, see the styles). -->
    <span
      :class="[
        'agent-card__rail absolute left-0 top-0 bottom-0 w-[0.1875rem] [background:var(--rail)] [transition:background-color_var(--iw-dur-3)_var(--iw-ease-out)]',
        status.state === 'working' && RAIL_LIVE
      ]"
      aria-hidden="true"
    ></span>

    <!-- Above the working card's edge glow, which is absolutely positioned
         and would otherwise paint over this static content. -->
    <div class="relative z-[1] flex-1 min-w-0">
      <!-- Name + the two markers that can sit beside it. The name carries the
           display face, the same face as the pane masthead — a subagent gets a
           byline, not a filename. -->
      <div class="flex items-start gap-1.5">
        <h3
          :class="[
            TITLE,
            isActive
              ? 'font-[650] text-blue-950 dark:text-white'
              : 'font-[550] text-ink/[0.86] group-hover:text-blue-950 dark:text-white/[0.82] dark:group-hover:text-white'
          ]"
        >{{ instance.title || 'Untitled thread' }}</h3>

        <!-- One of several parallel takes on the same brief -->
        <span
          v-if="variantCount && variantCount> 1"
          class="shrink-0 mt-px px-1 rounded bg-ink/[0.07] text-ink/55 text-[0.5625rem] font-semibold leading-[1.05rem] tabular-nums dark:bg-white/[0.08] dark:text-blue-100/60"
          :title="`Take ${variantIndex} of ${variantCount} on the same brief`"
        >{{ variantIndex }}/{{ variantCount }}</span>

        <!-- A run finished while this instance was off-screen. It arrives
             with a small pop, so a card that gains one while you are looking
             at the list actually announces itself. -->
        <span
          v-if="instance.hasUnread"
          class="agent-card__unread shrink-0 w-1.5 h-1.5 mt-[0.3125rem] rounded-full bg-blue-950 [box-shadow:0_0_0_2px_rgba(219,238,255,0.9)] dark:bg-[#f3ede2] dark:[box-shadow:0_0_0_2px_rgba(10,10,10,0.9)]"
          title="Agent finished while you were away"
        ></span>
      </div>

      <!-- Where this agent stands. While a run is live this carries the
           agent's own words for what it is doing right now. -->
      <div class="flex items-center gap-[0.3125rem] mt-[0.1875rem] text-[0.625rem] leading-[1.35] text-[color:var(--status)] [transition:color_var(--iw-dur-3)_var(--iw-ease-out)]">
        <i :class="[status.icon, 'shrink-0 text-[0.5625rem]']"></i>
        <span class="truncate">{{ status.label }}</span>
      </div>

      <!-- Ledger line: where it came from on the schedule, what is lined up
           behind it, and when it last moved -->
      <div class="flex items-center gap-[0.3125rem] min-w-0 mt-0.5 text-[0.625rem] tracking-[0.004em] tabular-nums text-ink/[0.38] dark:text-blue-100/35">
        <template v-if="forkedFrom">
          <span class="inline-flex items-center gap-1 min-w-0" :title="`Started from the conversation of ${forkedFrom}`">
            <i class="fas fa-code-branch shrink-0 text-[0.5rem]" aria-hidden="true"></i>
            <span class="truncate">{{ forkedFrom }}</span>
          </span>
          <span aria-hidden="true">·</span>
        </template>
        <template v-if="queuedAfter > 0">
          <span>{{ queuedAfter }} more lined up</span>
          <span aria-hidden="true">·</span>
        </template>
        <span class="shrink-0">{{ relativeTime(instance.updatedAt) }}</span>
      </div>
    </div>

    <!-- Open affordance: no per-card actions, because an agent's work ends by
         being added to the app or discarded from the main thread's queue —
         this only says the thread is readable. Quiet until hover: the row is
         clickable, but it does not advertise it. -->
    <i
      :class="[
        'fas fa-chevron-right relative z-[1] shrink-0 self-center text-[0.5rem] text-ink/30 dark:text-white/35 [transition:opacity_var(--iw-dur-2)_var(--iw-ease-out),transform_var(--iw-dur-2)_var(--iw-ease-out)]',
        isActive
          ? 'opacity-100 [transform:translateX(0)]'
          : 'opacity-0 [transform:translateX(-4px)] group-hover:opacity-100 group-hover:[transform:translateX(0)] group-focus-visible:opacity-100 group-focus-visible:[transform:translateX(0)]'
      ]"
      aria-hidden="true"
    ></i>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AgentInstance } from '../../../types/services'
import { isHeldThread } from '../../../stores/agentStore'
import { heldStatus } from '../../../utils/threadSchedule'

const props = withDefaults(
  defineProps<{
    instance: AgentInstance
    isActive: boolean
    isArchived?: boolean
    /** Position in its list — drives the staggered entrance only */
    index?: number
    /** This take's place among parallel takes on one brief */
    variantIndex?: number
    variantCount?: number
  }>(),
  { index: 0 }
)

/**
 * One line describing where this agent stands, plus the state token the rail
 * and tones key off. Running beats everything (a re-prompted agent is working
 * again whatever its last outcome was), then the states that want the user,
 * then the settled ones.
 */
const status = computed(() => {
  const instance = props.instance
  if (instance.isProcessing) {
    return {
      state: 'working' as const,
      // The agent's own account of the current step, when it has one.
      label: instance.statusText || 'Working…',
      icon: 'fas fa-circle-notch fa-spin',
    }
  }
  if (instance.archivedAt) {
    return { state: 'settled' as const, label: 'Archived', icon: 'fas fa-box-archive' }
  }
  // Placed by the coordinator to start after other threads' work lands. On
  // hold (one of those stopped) wants the user, so it wears waiting's ink.
  if (isHeldThread(instance)) {
    const blocked = instance.schedule?.status === 'blocked'
    return {
      state: blocked ? 'waiting' as const : 'scheduled' as const,
      label: heldStatus(instance.schedule),
      icon: blocked ? 'fas fa-pause' : 'fas fa-link',
    }
  }
  switch (instance.reviewStatus) {
    case 'input':
      return { state: 'waiting' as const, label: 'Asked you a question', icon: 'fas fa-circle-question' }
    case 'ready':
      // One of several takes the user asked to compare — the only state left
      // where finished work waits on them. A solo subagent applies its own.
      return { state: 'waiting' as const, label: 'Thread complete — one of your options', icon: 'fas fa-check' }
    case 'failed':
      // Its run died. It wants a decision (dismiss, or ask again), so it
      // reads as waiting rather than settled.
      return { state: 'stopped' as const, label: 'Stopped before finishing', icon: 'fas fa-triangle-exclamation' }
    case 'accepted':
      return { state: 'settled' as const, label: 'Thread complete', icon: 'fas fa-check-double' }
    case 'dismissed':
      return { state: 'settled' as const, label: 'Discarded', icon: 'fas fa-xmark' }
    case 'active':
      // A dispatched agent between creation and its run starting.
      return { state: 'starting' as const, label: 'Starting…', icon: 'fas fa-hourglass-start' }
    default:
      return { state: 'settled' as const, label: 'Idle', icon: 'fas fa-comments' }
  }
})

/* The card's surface, at rest / hovered / focused. */
const CARD = [
  'border-ink/[0.07] bg-blue-50/40 hover:bg-blue-50/95 hover:border-ink/[0.13] hover:[box-shadow:var(--iw-shadow-2)]',
  'active:[box-shadow:var(--iw-shadow-1)] focus-visible:[box-shadow:var(--iw-focus-ring)]',
  'dark:border-white/[0.09] dark:bg-white/[0.02] dark:hover:bg-white/5 dark:hover:border-white/[0.17]',
]
/* Selected: the soft baby-blue wash for "you are here". Its own hover keeps
   the wash (and outranks the focus ring), and dark mode holds one look. */
const CARD_SELECTED = [
  'border-blue-300/85 [background:linear-gradient(155deg,rgba(219,238,255,0.9)_0%,rgba(183,221,247,0.45)_100%)]',
  '[box-shadow:0_1px_2px_rgba(30,58,138,0.08),0_4px_12px_-5px_rgba(30,58,138,0.16),inset_0_1px_0_rgba(255,255,255,0.6)]',
  'hover:border-blue-300 hover:[background:linear-gradient(155deg,rgba(219,238,255,1)_0%,rgba(183,221,247,0.55)_100%)]',
  'hover:[box-shadow:0_2px_4px_rgba(30,58,138,0.1),0_10px_24px_-10px_rgba(30,58,138,0.28),inset_0_1px_0_rgba(255,255,255,0.6)]',
  'focus-visible:[box-shadow:var(--iw-focus-ring)]',
  'focus-visible:hover:[box-shadow:0_2px_4px_rgba(30,58,138,0.1),0_10px_24px_-10px_rgba(30,58,138,0.28),inset_0_1px_0_rgba(255,255,255,0.6)]',
  'dark:border-blue-400/[0.42] dark:[background:linear-gradient(155deg,rgba(96,165,250,0.14)_0%,rgba(96,165,250,0.05)_100%)]',
  'dark:[box-shadow:0_1px_2px_rgba(0,0,0,0.3),inset_0_1px_0_rgba(255,255,255,0.05)]',
  'dark:hover:[box-shadow:0_1px_2px_rgba(0,0,0,0.3),inset_0_1px_0_rgba(255,255,255,0.05)]',
]

/*
  The rail and the status line read their colour from --rail / --status, one
  pair per state. Live work is the working blue; waiting on you is solid navy
  ink — a full-height mark you can spot from the top of the list without
  reading a word; a run that died is warm ink, the one non-navy note in the
  pane (the work never reached the app, so it is something to clear rather
  than an alarm); dispatched-but-not-running and scheduled work get a rail
  that is drawn but not yet filled (it has a place in the line, not a run);
  settled work recedes to a hairline. In dark, a working card keeps the
  default rail.
*/
const RAIL_TONE = {
  working:
    '[--rail:color-mix(in_srgb,var(--sl-work)_32%,transparent)] [--status:var(--sl-work)] dark:[--rail:rgba(255,255,255,0.16)] dark:[--status:rgba(219,234,254,0.6)]',
  waiting: '[--rail:#172554] [--status:rgba(19,26,44,0.78)] dark:[--rail:#f3ede2] dark:[--status:rgba(243,237,226,0.85)]',
  stopped: '[--rail:#f59e0b] [--status:#b45309] dark:[--rail:#fcd34d] dark:[--status:#fde68a]',
  scheduled:
    '[--rail:repeating-linear-gradient(180deg,rgba(19,26,44,0.3)_0_3px,transparent_3px_7px)] [--status:rgba(19,26,44,0.5)] dark:[--rail:repeating-linear-gradient(180deg,rgba(255,255,255,0.3)_0_3px,transparent_3px_7px)] dark:[--status:rgba(219,234,254,0.5)]',
  starting:
    '[--rail:repeating-linear-gradient(180deg,rgba(19,26,44,0.3)_0_3px,transparent_3px_7px)] [--status:rgba(19,26,44,0.5)] dark:[--rail:repeating-linear-gradient(180deg,rgba(255,255,255,0.3)_0_3px,transparent_3px_7px)] dark:[--status:rgba(219,234,254,0.5)]',
  settled: '[--rail:rgba(19,26,44,0.1)] [--status:rgba(19,26,44,0.42)] dark:[--rail:rgba(255,255,255,0.1)] dark:[--status:rgba(219,234,254,0.4)]',
} as const

/* Ink travelling down a working card's rail (animated in the styles) */
const RAIL_LIVE =
  "after:content-[''] after:absolute after:inset-0 " +
  'after:bg-[linear-gradient(180deg,transparent_0%,var(--sl-work)_40%,color-mix(in_srgb,var(--sl-work)_70%,transparent)_60%,transparent_100%)]'

const TITLE =
  "flex-1 min-w-0 truncate font-sl-display [font-variation-settings:'opsz'_11,'SOFT'_30,'WONK'_1] " +
  'text-[0.8125rem] leading-[1.25] tracking-[-0.006em] [transition:color_var(--iw-dur-2)_var(--iw-ease-out)]'

/* The glow the rail casts into a working card — light bleeding off a lit
   edge, so a working agent is legible from the corner of the eye without the
   row having to shout. It breathes (see the styles). */
const WORKING_GLOW =
  "agent-card--working before:content-[''] before:absolute before:left-0 before:top-0 before:bottom-0 before:w-[40%] before:pointer-events-none " +
  'before:bg-[linear-gradient(90deg,color-mix(in_srgb,var(--sl-work)_10%,transparent)_0%,transparent_100%)]'

/** The thread this one was forked from, by its job. */
const forkedFrom = computed(() => props.instance.schedule?.forked_from?.title || '')

/** Jobs the coordinator lined up on this thread behind the current one. */
const queuedAfter = computed(() => props.instance.schedule?.queued_after || 0)

const emit = defineEmits<{ (e: 'select'): void }>()

function relativeTime(iso: string): string {
  if (!iso) return ''
  const date = new Date(iso)
  const diff = Date.now() - date.getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  const days = Math.floor(hrs / 24)
  if (days < 7) return `${days}d ago`
  return date.toLocaleDateString()
}
</script>

<style scoped>
/* Live run: ink travels down the rail and the card breathes with the faintest
   left-edge glow — the one moving thing in the list. Keyframed, so CSS. */
.agent-card--working::before {
  animation: rail-breathe 3.2s var(--iw-ease-ambient) infinite;
}

.agent-card--working .agent-card__rail::after {
  animation: rail-travel 2.6s var(--iw-ease-ambient) infinite;
}

.agent-card__unread {
  animation: unread-in var(--iw-dur-3) var(--iw-ease-spring) both;
}

@keyframes rail-travel {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100%); }
}

@keyframes rail-breathe {
  0%, 100% { opacity: 0.55; }
  50% { opacity: 1; }
}

@keyframes unread-in {
  from { opacity: 0; transform: scale(0.2); }
  to { opacity: 1; transform: none; }
}

@media (prefers-reduced-motion: reduce) {
  .agent-card--working::before {
    animation: none;
    opacity: 0.8;
  }

  .agent-card--working .agent-card__rail::after {
    animation: none;
    background: var(--sl-work);
  }
}
</style>
