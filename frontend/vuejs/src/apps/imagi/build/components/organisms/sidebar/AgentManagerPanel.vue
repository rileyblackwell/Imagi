<!--
  AgentManagerPanel.vue — the crew ledger.

  Everything the project's subagents are doing, in one column. The pane wears
  the same masthead as the chat pane, then states the fleet twice: once as a
  meter (how the work splits between running and waiting on you) and once as
  the cards themselves. Read-only by design — decisions happen in the main
  agent's check-in queue, so this pane's whole job is legibility.
-->
<template>
  <div class="flex flex-col h-full bg-white dark:bg-[#0a0a0a] transition-colors duration-300">
    <!-- Header: the same plate the chat pane wears, switching back the other
         way. The status line reports the fleet, which is what the removed
         "view only" badge was gesturing at — except it carries real news. -->
    <WorkspacePaneHeader
      icon="fas fa-layer-group"
      tone="muted"
      title="Subagents"
      :status="fleetStatus"
      :live="workingCount > 0"
      switch-icon="fas fa-comments"
      switch-label="Main agent"
      :switch-count="store.checkIns.length"
      switch-direction="back"
      @switch="emit('collapse')"
    />

    <!-- Fleet meter: the same numbers as the status line, drawn. Segments are
         proportional, so a glance says whether the crew is busy or the pile of
         work waiting on you is the bigger half. -->
    <div v-if="activeAgents.length > 0" class="fleet-meter" :title="fleetStatus">
      <span
        v-for="seg in fleetSegments"
        :key="seg.key"
        :class="['fleet-meter__seg', `fleet-meter__seg--${seg.key}`]"
        :style="{ flexGrow: seg.count }"
      ></span>
    </div>

    <!-- Team view -->
    <div class="flex-1 min-h-0 overflow-y-auto px-2 py-2">
      <!-- Loading: the shape of the list, before the list -->
      <div v-if="store.instancesLoading && store.instances.length === 0" class="space-y-1.5 pt-1">
        <div v-for="n in 3" :key="n" class="skeleton-card" :style="{ '--stagger': `${n * 90}ms` }">
          <span class="skeleton-rail"></span>
          <div class="flex-1 space-y-1.5">
            <div class="skeleton-line" :style="{ width: n === 2 ? '58%' : '72%' }"></div>
            <div class="skeleton-line skeleton-line--faint" :style="{ width: n === 3 ? '34%' : '46%' }"></div>
          </div>
        </div>
        <p class="pt-1 text-center text-[10px] text-blue-950/35 dark:text-white/30">Loading agents…</p>
      </div>

      <template v-else>
        <!-- Active: every subagent still on the hook — running, waiting on an
             answer, or finished but not yet accepted. One list, because to the
             user they are one thing; the rail and status say which is which.
             Read-only: decisions happen in the main agent's queue. -->
        <div class="section-head">
          <span class="section-head__label">Active</span>
          <span v-if="activeAgents.length" class="section-head__count">{{ activeAgents.length }}</span>
          <span class="section-head__rule"></span>
        </div>

        <div v-if="activeAgents.length > 0" class="space-y-1">
          <InstanceCard
            v-for="(instance, i) in activeAgents"
            :key="instance.id"
            :instance="instance"
            :index="i"
            :is-active="instance.id === store.activeInstanceId"
            :variant-index="variantPlace(instance).index"
            :variant-count="variantPlace(instance).count"
            @select="handleSelect(instance.id)"
          />
        </div>

        <!-- Nothing running: say what would put something here -->
        <div v-else class="empty-plate">
          <span class="empty-plate__mark"><i class="fas fa-layer-group text-[10px]"></i></span>
          <p class="empty-plate__title">No agents working right now</p>
          <p class="empty-plate__body">
            Ask for what you want in your chat — your agent hands off anything
            worth building in parallel.
          </p>
        </div>

        <!-- History: archived threads, legacy chats, resolved tasks -->
        <template v-if="history.length > 0">
          <button
            type="button"
            class="section-head section-head--button"
            :aria-expanded="showHistory"
            @click="showHistory = !showHistory"
          >
            <i :class="['fas fa-chevron-right section-head__chevron', showHistory ? 'is-open' : '']"></i>
            <span class="section-head__label">History</span>
            <span class="section-head__count">{{ history.length }}</span>
            <span class="section-head__rule"></span>
          </button>
          <div v-if="showHistory" class="space-y-1">
            <InstanceCard
              v-for="(instance, i) in history"
              :key="instance.id"
              :instance="instance"
              :index="i"
              :is-active="instance.id === store.activeInstanceId"
              :is-archived="!!instance.archivedAt"
              @select="handleSelect(instance.id)"
            />
          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAgentStore } from '../../../stores/agentStore'
import InstanceCard from '../../molecules/sidebar/AgentInstanceCard.vue'
import WorkspacePaneHeader from '../../molecules/sidebar/WorkspacePaneHeader.vue'
import type { AgentInstance } from '../../../types/services'

const emit = defineEmits<{
  (e: 'collapse'): void
  /** An instance was clicked — the workspace flips the sidebar to chat. */
  (e: 'select', instanceId: string): void
}>()

const store = useAgentStore()
const showHistory = ref(false)

// Already newest-first. The main agent's own thread is the chat pane, so it
// is deliberately absent here — this panel is only about the subagents.
const activeAgents = computed(() => store.activeAgentInstances)
const history = computed(() => store.historyInstances)

const workingCount = computed(() => activeAgents.value.filter(a => a.isProcessing).length)

/** The fleet at a glance, leading with whoever is actually working. */
const fleetStatus = computed(() => {
  const total = activeAgents.value.length
  if (total === 0) return 'No agents working'
  const working = workingCount.value
  if (working === total) return `${total} ${total === 1 ? 'agent' : 'agents'} working`
  if (working > 0) return `${working} working · ${total - working} waiting on you`
  return `${total} ${total === 1 ? 'agent' : 'agents'} waiting on you`
})

/**
 * The meter's segments, in the order the eye should read them: live work
 * first, then what wants the user, then what has not started. Empty segments
 * are dropped so the bar never carries a zero-width sliver.
 */
const fleetSegments = computed(() => {
  const agents = activeAgents.value
  const working = agents.filter(a => a.isProcessing).length
  const starting = agents.filter(a => !a.isProcessing && a.reviewStatus === 'active').length
  const waiting = agents.length - working - starting
  return [
    { key: 'working', count: working },
    { key: 'waiting', count: waiting },
    { key: 'starting', count: starting },
  ].filter(s => s.count > 0)
})

/**
 * Parallel takes on one brief share a variant group. A card that is one of
 * several says so — otherwise accepting the first one looks like the only
 * option. Ungrouped tasks report a count of 1 and render no marker.
 */
const variantPlaces = computed(() => {
  const groups = new Map<string, string[]>()
  for (const instance of activeAgents.value) {
    if (!instance.variantGroup) continue
    const ids = groups.get(instance.variantGroup) ?? []
    ids.push(instance.id)
    groups.set(instance.variantGroup, ids)
  }
  return groups
})

function variantPlace(instance: AgentInstance): { index: number; count: number } {
  const siblings = instance.variantGroup ? variantPlaces.value.get(instance.variantGroup) : undefined
  if (!siblings || siblings.length < 2) return { index: 1, count: 1 }
  return { index: siblings.indexOf(instance.id) + 1, count: siblings.length }
}

async function handleSelect(id: string) {
  emit('select', id)
  await store.switchInstance(id)
}
</script>

<style scoped>
/* ── Fleet meter ────────────────────────────────────────────────────────── */

.fleet-meter {
  display: flex;
  gap: 0.125rem;
  height: 0.125rem;
  margin: 0 0.875rem;
  padding-top: 0.5rem;
  box-sizing: content-box;
}

.fleet-meter__seg {
  flex-basis: 0;
  border-radius: 9999px;
  transition: flex-grow 0.35s cubic-bezier(0.22, 1, 0.36, 1);
}

/* Same three tones the card rails use, so the bar reads as a key to the list */
.fleet-meter__seg--working {
  background: linear-gradient(
    90deg,
    theme('colors.blue.400') 0%,
    theme('colors.blue.600') 50%,
    theme('colors.blue.400') 100%
  );
  background-size: 200% 100%;
  animation: fleet-drift 2.8s linear infinite;
}

.fleet-meter__seg--waiting {
  background: theme('colors.blue.950');
}

.fleet-meter__seg--starting {
  background: rgba(23, 37, 84, 0.2);
}

.dark .fleet-meter__seg--working {
  background: linear-gradient(
    90deg,
    theme('colors.blue.300') 0%,
    theme('colors.blue.200') 50%,
    theme('colors.blue.300') 100%
  );
  background-size: 200% 100%;
}

.dark .fleet-meter__seg--waiting {
  background: #f3ede2;
}

.dark .fleet-meter__seg--starting {
  background: rgba(255, 255, 255, 0.22);
}

@keyframes fleet-drift {
  from { background-position: 200% 0; }
  to { background-position: 0 0; }
}

/* ── Section heads ──────────────────────────────────────────────────────── */

/* Uppercase micro-label, its count, then a hairline running to the edge —
   the workspace's label convention, given a rule so sections separate without
   another box. */
.section-head {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  width: 100%;
  padding: 0.375rem 0.5rem 0.5rem;
  text-align: left;
}

.section-head--button {
  margin-top: 0.75rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: background-color 0.18s ease;
}

.section-head--button:hover {
  background: rgba(239, 246, 255, 0.7);
}

.dark .section-head--button:hover {
  background: rgba(255, 255, 255, 0.035);
}

.section-head--button:focus-visible {
  outline: none;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.45);
}

.section-head__label {
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.09em;
  color: rgba(23, 37, 84, 0.45);
  transition: color 0.18s ease;
}

.dark .section-head__label {
  color: rgba(255, 255, 255, 0.42);
}

.section-head--button:hover .section-head__label {
  color: rgba(23, 37, 84, 0.72);
}

.dark .section-head--button:hover .section-head__label {
  color: rgba(255, 255, 255, 0.72);
}

.section-head__count {
  font-size: 0.5625rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  padding: 0 0.25rem;
  border-radius: 0.25rem;
  background: rgba(23, 37, 84, 0.06);
  color: rgba(23, 37, 84, 0.5);
  line-height: 0.9375rem;
}

.dark .section-head__count {
  background: rgba(255, 255, 255, 0.07);
  color: rgba(219, 234, 254, 0.55);
}

.section-head__rule {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, rgba(23, 37, 84, 0.12) 0%, rgba(23, 37, 84, 0) 100%);
}

.dark .section-head__rule {
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.14) 0%, rgba(255, 255, 255, 0) 100%);
}

.section-head__chevron {
  font-size: 0.5rem;
  color: rgba(23, 37, 84, 0.35);
  transition: transform 0.2s cubic-bezier(0.22, 1, 0.36, 1);
}

.dark .section-head__chevron {
  color: rgba(255, 255, 255, 0.35);
}

.section-head__chevron.is-open {
  transform: rotate(90deg);
}

/* ── Empty state ────────────────────────────────────────────────────────── */

/* A drawn-but-unfilled plate: the same dashed language the "not started yet"
   card rail uses, so an empty crew reads as capacity rather than an error. */
.empty-plate {
  margin: 0.125rem 0.125rem 0;
  padding: 1.125rem 0.875rem 1.25rem;
  border: 1px dashed rgba(23, 37, 84, 0.14);
  border-radius: 0.75rem;
  background: linear-gradient(180deg, rgba(239, 246, 255, 0.55) 0%, rgba(239, 246, 255, 0) 100%);
  text-align: center;
}

.dark .empty-plate {
  border-color: rgba(255, 255, 255, 0.11);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0) 100%);
}

.empty-plate__mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.625rem;
  height: 1.625rem;
  margin-bottom: 0.5rem;
  border-radius: 0.5rem;
  background: rgba(23, 37, 84, 0.06);
  color: rgba(23, 37, 84, 0.4);
  box-shadow: inset 0 0 0 1px rgba(23, 37, 84, 0.05);
}

.dark .empty-plate__mark {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.4);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
}

.empty-plate__title {
  font-family: theme('fontFamily.display');
  font-variation-settings: 'opsz' 12, 'SOFT' 30, 'WONK' 1;
  font-size: 0.8125rem;
  font-weight: 550;
  color: rgba(23, 37, 84, 0.7);
}

.dark .empty-plate__title {
  color: rgba(255, 255, 255, 0.72);
}

.empty-plate__body {
  margin-top: 0.25rem;
  font-size: 0.6875rem;
  line-height: 1.45;
  color: rgba(23, 37, 84, 0.42);
}

.dark .empty-plate__body {
  color: rgba(219, 234, 254, 0.38);
}

/* ── Loading ────────────────────────────────────────────────────────────── */

/* The list's own silhouette — rail on the left, two lines of text — so the
   pane does not jump when the real cards land. */
.skeleton-card {
  position: relative;
  display: flex;
  gap: 0.625rem;
  padding: 0.5rem 0.5rem 0.5rem 0.75rem;
  border: 1px solid rgba(23, 37, 84, 0.06);
  border-radius: 0.625rem;
  overflow: hidden;
  opacity: 0;
  animation: skeleton-in 0.4s ease both;
  animation-delay: var(--stagger, 0ms);
}

.dark .skeleton-card {
  border-color: rgba(255, 255, 255, 0.07);
}

.skeleton-rail {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 0.1875rem;
  background: rgba(23, 37, 84, 0.13);
}

.dark .skeleton-rail {
  background: rgba(255, 255, 255, 0.13);
}

.skeleton-line {
  height: 0.5rem;
  border-radius: 9999px;
  background: linear-gradient(
    90deg,
    rgba(23, 37, 84, 0.07) 0%,
    rgba(23, 37, 84, 0.13) 50%,
    rgba(23, 37, 84, 0.07) 100%
  );
  background-size: 200% 100%;
  animation: skeleton-sweep 1.6s ease-in-out infinite;
}

.skeleton-line--faint {
  height: 0.375rem;
  opacity: 0.65;
}

.dark .skeleton-line {
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.05) 0%,
    rgba(255, 255, 255, 0.11) 50%,
    rgba(255, 255, 255, 0.05) 100%
  );
  background-size: 200% 100%;
}

@keyframes skeleton-sweep {
  from { background-position: 200% 0; }
  to { background-position: -200% 0; }
}

@keyframes skeleton-in {
  from { opacity: 0; transform: translateY(3px); }
  to { opacity: 1; transform: none; }
}

@media (prefers-reduced-motion: reduce) {
  .fleet-meter__seg--working,
  .skeleton-line,
  .skeleton-card {
    animation: none;
  }

  .skeleton-card {
    opacity: 1;
  }
}
</style>
