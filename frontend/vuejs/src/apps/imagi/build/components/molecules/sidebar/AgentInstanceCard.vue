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
      'agent-card group',
      `agent-card--${status.state}`,
      isActive ? 'agent-card--active' : '',
      isArchived ? 'agent-card--archived' : ''
    ]"
    :style="{ '--stagger': `${Math.min(index, 8) * 45}ms` }"
    role="button"
    tabindex="0"
    :aria-current="isActive ? 'true' : undefined"
    @click="emit('select')"
    @keydown.enter.prevent="emit('select')"
    @keydown.space.prevent="emit('select')"
  >
    <!-- The spine: state as a vertical rail, animated while a run is live -->
    <span class="agent-card__rail" aria-hidden="true"></span>

    <div class="agent-card__body">
      <!-- Name + the two markers that can sit beside it -->
      <div class="flex items-start gap-1.5">
        <h3 class="agent-card__title">{{ instance.title || 'Untitled agent' }}</h3>

        <!-- One of several parallel takes on the same brief -->
        <span
          v-if="variantCount && variantCount > 1"
          class="agent-card__take"
          :title="`Take ${variantIndex} of ${variantCount} on the same brief`"
        >{{ variantIndex }}/{{ variantCount }}</span>

        <!-- A run finished while this instance was off-screen -->
        <span
          v-if="instance.hasUnread"
          class="agent-card__unread"
          title="Agent finished while you were away"
        ></span>
      </div>

      <!-- Where this agent stands. While a run is live this carries the
           agent's own words for what it is doing right now. -->
      <div class="agent-card__status">
        <i :class="[status.icon, 'agent-card__status-icon']"></i>
        <span class="truncate">{{ status.label }}</span>
      </div>

      <!-- Ledger line: when it last moved, and what it has spent -->
      <div class="agent-card__meta">
        <span>{{ relativeTime(instance.updatedAt) }}</span>
        <!-- Conversation-wide token total; null means never captured, so
             nothing renders (unknown, not "0 tokens") -->
        <template v-if="typeof instance.totalTokens === 'number' && instance.totalTokens > 0">
          <span class="agent-card__dot" aria-hidden="true"></span>
          <span :title="`${instance.totalTokens.toLocaleString()} tokens used`">
            {{ formatTokens(instance.totalTokens) }} tokens
          </span>
        </template>
      </div>
    </div>

    <!-- Open affordance: no per-card actions, because an agent's work ends by
         being added to the app or discarded from the main thread's queue —
         this only says the thread is readable. -->
    <i class="fas fa-chevron-right agent-card__chevron" aria-hidden="true"></i>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AgentInstance } from '../../../types/services'

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
  switch (instance.reviewStatus) {
    case 'input':
      return { state: 'waiting' as const, label: 'Asked you a question', icon: 'fas fa-circle-question' }
    case 'ready':
      return { state: 'waiting' as const, label: 'Finished — waiting on you', icon: 'fas fa-check' }
    case 'accepted':
      return { state: 'settled' as const, label: 'Added to your app', icon: 'fas fa-check-double' }
    case 'dismissed':
      return { state: 'settled' as const, label: 'Discarded', icon: 'fas fa-xmark' }
    case 'active':
      // A dispatched agent between creation and its run starting.
      return { state: 'starting' as const, label: 'Starting…', icon: 'fas fa-hourglass-start' }
    default:
      return { state: 'settled' as const, label: 'Idle', icon: 'fas fa-comments' }
  }
})

const emit = defineEmits<{ (e: 'select'): void }>()

/** Compact token count for the meta row: 850, 12.3k, 2M. */
function formatTokens(total: number): string {
  if (total >= 1_000_000) {
    const millions = total / 1_000_000
    return `${millions >= 10 ? Math.round(millions) : Math.round(millions * 10) / 10}M`
  }
  if (total >= 1_000) {
    const thousands = total / 1_000
    return `${thousands >= 100 ? Math.round(thousands) : Math.round(thousands * 10) / 10}k`
  }
  return String(total)
}

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
/* ── The card ───────────────────────────────────────────────────────────── */

.agent-card {
  --rail: rgba(23, 37, 84, 0.14);
  --status: rgba(23, 37, 84, 0.55);

  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 0.375rem;
  padding: 0.4375rem 0.5rem 0.4375rem 0.75rem;
  border-radius: 0.625rem;
  border: 1px solid rgba(23, 37, 84, 0.07);
  background: rgba(239, 246, 255, 0.4);
  cursor: pointer;
  overflow: hidden;
  transition:
    background-color 0.2s ease,
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s cubic-bezier(0.22, 1, 0.36, 1);
  animation: agent-card-in 0.45s cubic-bezier(0.22, 1, 0.36, 1) both;
  animation-delay: var(--stagger, 0ms);
}

.dark .agent-card {
  --rail: rgba(255, 255, 255, 0.16);
  --status: rgba(219, 234, 254, 0.6);
  border-color: rgba(255, 255, 255, 0.09);
  background: rgba(255, 255, 255, 0.02);
}

.agent-card:hover {
  background: rgba(239, 246, 255, 0.95);
  border-color: rgba(23, 37, 84, 0.14);
  transform: translateX(1px);
}

.dark .agent-card:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.17);
}

.agent-card:focus-visible {
  outline: none;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.45);
}

.dark .agent-card:focus-visible {
  box-shadow: 0 0 0 2px rgba(147, 197, 253, 0.5);
}

/* Selected — the soft baby-blue wash the workspace uses for "you are here" */
.agent-card--active {
  border-color: rgba(147, 197, 253, 0.85);
  background: linear-gradient(155deg, rgba(219, 238, 255, 0.9) 0%, rgba(183, 221, 247, 0.45) 100%);
  box-shadow:
    0 1px 2px rgba(30, 58, 138, 0.08),
    0 3px 8px -3px rgba(30, 58, 138, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
}

.agent-card--active:hover {
  background: linear-gradient(155deg, rgba(219, 238, 255, 1) 0%, rgba(183, 221, 247, 0.55) 100%);
  border-color: rgba(147, 197, 253, 1);
}

.dark .agent-card--active,
.dark .agent-card--active:hover {
  border-color: rgba(96, 165, 250, 0.42);
  background: linear-gradient(155deg, rgba(96, 165, 250, 0.14) 0%, rgba(96, 165, 250, 0.05) 100%);
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.agent-card--archived {
  opacity: 0.72;
}

.agent-card--archived:hover {
  opacity: 1;
}

/* ── The spine ──────────────────────────────────────────────────────────── */

.agent-card__rail {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 0.1875rem;
  background: var(--rail);
}

/* Live run: ink travels down the rail, and the card breathes with the faintest
   left-edge glow. This is the one moving thing in the list. */
.agent-card--working {
  --rail: rgba(37, 99, 235, 0.32);
  --status: theme('colors.blue.600');
}

.dark .agent-card--working {
  --rail: rgba(147, 197, 253, 0.3);
  --status: theme('colors.blue.300');
}

.agent-card--working .agent-card__rail::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    180deg,
    transparent 0%,
    theme('colors.blue.500') 40%,
    theme('colors.blue.400') 60%,
    transparent 100%
  );
  animation: rail-travel 2.1s cubic-bezier(0.45, 0, 0.55, 1) infinite;
}

.dark .agent-card--working .agent-card__rail::after {
  background: linear-gradient(
    180deg,
    transparent 0%,
    theme('colors.blue.300') 40%,
    theme('colors.blue.200') 60%,
    transparent 100%
  );
}

/* Waiting on you: solid navy ink — a full-height mark you can spot from the
   top of the list without reading a word. */
.agent-card--waiting {
  --rail: theme('colors.blue.950');
  --status: rgba(23, 37, 84, 0.78);
}

.dark .agent-card--waiting {
  --rail: #f3ede2;
  --status: rgba(243, 237, 226, 0.85);
}

/* Dispatched but not yet running — the rail is drawn but not yet filled */
.agent-card--starting {
  --rail: repeating-linear-gradient(
    180deg,
    rgba(23, 37, 84, 0.3) 0 3px,
    transparent 3px 7px
  );
  --status: rgba(23, 37, 84, 0.5);
}

.dark .agent-card--starting {
  --rail: repeating-linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.3) 0 3px,
    transparent 3px 7px
  );
  --status: rgba(219, 234, 254, 0.5);
}

/* Settled work recedes to a hairline */
.agent-card--settled {
  --rail: rgba(23, 37, 84, 0.1);
  --status: rgba(23, 37, 84, 0.42);
}

.dark .agent-card--settled {
  --rail: rgba(255, 255, 255, 0.1);
  --status: rgba(219, 234, 254, 0.4);
}

/* ── Contents ───────────────────────────────────────────────────────────── */

.agent-card__body {
  flex: 1;
  min-width: 0;
}

/* The name carries the brand serif (Fraunces), the same face as the pane
   masthead — a subagent gets a byline, not a filename. */
.agent-card__title {
  flex: 1;
  min-width: 0;
  font-family: theme('fontFamily.display');
  font-variation-settings: 'opsz' 11, 'SOFT' 30, 'WONK' 1;
  font-size: 0.8125rem;
  font-weight: 550;
  line-height: 1.25;
  letter-spacing: -0.006em;
  color: rgba(23, 37, 84, 0.86);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: color 0.2s ease;
}

.dark .agent-card__title {
  color: rgba(255, 255, 255, 0.82);
}

.agent-card:hover .agent-card__title,
.agent-card--active .agent-card__title {
  color: theme('colors.blue.950');
}

.dark .agent-card:hover .agent-card__title,
.dark .agent-card--active .agent-card__title {
  color: #ffffff;
}

.agent-card--active .agent-card__title {
  font-weight: 650;
}

/* Take marker for parallel attempts at one brief */
.agent-card__take {
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

.dark .agent-card__take {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(219, 234, 254, 0.6);
}

.agent-card__unread {
  flex-shrink: 0;
  width: 0.375rem;
  height: 0.375rem;
  margin-top: 0.3125rem;
  border-radius: 9999px;
  background: theme('colors.blue.950');
  box-shadow: 0 0 0 2px rgba(219, 238, 255, 0.9);
}

.dark .agent-card__unread {
  background: #f3ede2;
  box-shadow: 0 0 0 2px rgba(10, 10, 10, 0.9);
}

.agent-card__status {
  display: flex;
  align-items: center;
  gap: 0.3125rem;
  margin-top: 0.1875rem;
  font-size: 0.625rem;
  line-height: 1.35;
  color: var(--status);
  transition: color 0.2s ease;
}

.agent-card__status-icon {
  flex-shrink: 0;
  font-size: 0.5625rem;
}

.agent-card__meta {
  display: flex;
  align-items: center;
  gap: 0.3125rem;
  margin-top: 0.125rem;
  font-size: 0.625rem;
  letter-spacing: 0.004em;
  font-variant-numeric: tabular-nums;
  color: rgba(23, 37, 84, 0.38);
}

.dark .agent-card__meta {
  color: rgba(219, 234, 254, 0.35);
}

.agent-card__dot {
  width: 0.125rem;
  height: 0.125rem;
  border-radius: 9999px;
  background: currentColor;
  opacity: 0.7;
}

/* Quiet until hover — the row is clickable, but it does not advertise it */
.agent-card__chevron {
  flex-shrink: 0;
  align-self: center;
  font-size: 0.5rem;
  color: rgba(23, 37, 84, 0.3);
  opacity: 0;
  transform: translateX(-3px);
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.dark .agent-card__chevron {
  color: rgba(255, 255, 255, 0.35);
}

.agent-card:hover .agent-card__chevron,
.agent-card:focus-visible .agent-card__chevron,
.agent-card--active .agent-card__chevron {
  opacity: 1;
  transform: translateX(0);
}

/* ── Motion ─────────────────────────────────────────────────────────────── */

@keyframes rail-travel {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100%); }
}

@keyframes agent-card-in {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: none; }
}

@media (prefers-reduced-motion: reduce) {
  .agent-card {
    animation: none;
  }

  .agent-card--working .agent-card__rail::after {
    animation: none;
    background: theme('colors.blue.500');
  }

  .agent-card:hover {
    transform: none;
  }
}
</style>
