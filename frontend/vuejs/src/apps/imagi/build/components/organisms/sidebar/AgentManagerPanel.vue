<template>
  <div class="flex flex-col h-full bg-white dark:bg-[#0a0a0a] transition-colors duration-300">
    <!-- Header: the same plate the chat pane wears, switching back the other
         way. The status line reports the fleet, which is what the removed
         "view only" badge was gesturing at — except it carries real news. -->
    <WorkspacePaneHeader
      icon="fas fa-layer-group"
      tone="muted"
      title="Agent Manager"
      :status="fleetStatus"
      :live="activeAgents.some(a => a.isProcessing)"
      switch-icon="fas fa-comments"
      switch-label="Main agent"
      :switch-count="store.checkIns.length"
      switch-direction="back"
      @switch="emit('collapse')"
    />

    <!-- Team view -->
    <div class="flex-1 min-h-0 overflow-y-auto px-2 py-2 space-y-1">
      <!-- Loading state -->
      <div
        v-if="store.instancesLoading && store.instances.length === 0"
        class="flex items-center justify-center gap-2 px-2 py-8 text-xs text-blue-950/40 dark:text-blue-100/45"
      >
        <i class="fas fa-circle-notch fa-spin text-[11px]"></i>
        <span>Loading agents…</span>
      </div>

      <template v-else>
        <!-- Active: every subagent still on the hook — running, waiting on an
             answer, or finished but not yet accepted. One list, because to the
             user they are one thing; the status line says which is which.
             Read-only: decisions happen in the main agent's queue. -->
        <div class="section-label px-2 pt-1 pb-1.5">Active</div>
        <template v-if="activeAgents.length > 0">
          <InstanceCard
            v-for="instance in activeAgents"
            :key="instance.id"
            :instance="instance"
            :is-active="instance.id === store.activeInstanceId"
            @select="handleSelect(instance.id)"
          />
        </template>
        <div v-else class="px-2 pb-1 text-[11px] text-blue-950/35 dark:text-white/30">
          No agents working right now. Ask for what you want in your chat — your
          agent hands off anything worth building in parallel.
        </div>

        <!-- History: archived threads, legacy chats, resolved tasks -->
        <template v-if="history.length > 0">
          <button
            class="w-full flex items-center justify-between rounded-md px-2 py-2 mt-3 text-[10px] font-semibold uppercase tracking-wider text-blue-950/40 dark:text-white/40 hover:text-blue-950/70 dark:hover:text-white/70 hover:bg-blue-50/60 dark:hover:bg-white/[0.04] transition-colors"
            @click="showHistory = !showHistory"
          >
            <span>History ({{ history.length }})</span>
            <i :class="['fas text-[9px]', showHistory ? 'fa-chevron-down' : 'fa-chevron-right']"></i>
          </button>
          <template v-if="showHistory">
            <InstanceCard
              v-for="instance in history"
              :key="instance.id"
              :instance="instance"
              :is-active="instance.id === store.activeInstanceId"
              :is-archived="!!instance.archivedAt"
              @select="handleSelect(instance.id)"
            />
          </template>
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

/** The fleet at a glance, leading with whoever is actually working. */
const fleetStatus = computed(() => {
  const total = activeAgents.value.length
  if (total === 0) return 'No agents working'
  const working = activeAgents.value.filter(a => a.isProcessing).length
  if (working === total) return `${total} ${total === 1 ? 'agent' : 'agents'} working`
  if (working > 0) return `${working} working · ${total - working} waiting on you`
  return `${total} ${total === 1 ? 'agent' : 'agents'} waiting on you`
})

async function handleSelect(id: string) {
  emit('select', id)
  await store.switchInstance(id)
}
</script>

<style scoped>
/* Section labels share the workspace's uppercase micro-label convention */
.section-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: rgba(23, 37, 84, 0.4);
}

.dark .section-label {
  color: rgba(255, 255, 255, 0.4);
}
</style>
