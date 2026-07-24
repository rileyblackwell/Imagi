<template>
  <div class="flex flex-col h-full bg-white dark:bg-[#0a0a0a] transition-colors duration-300">
    <!-- Reading one subagent's thread. It happens here rather than in the chat
         pane on purpose: a subagent is something you look in on, so opening one
         must not displace the thread you are actually talking in. -->
    <template v-if="opened">
      <WorkspacePaneHeader
        icon="fas fa-robot"
        tone="muted"
        :title="opened.title || 'Background agent'"
        :status="openedStatus"
        :live="!!opened.isProcessing"
        switch-icon="fas fa-layer-group"
        switch-label="Subagents"
        switch-direction="back"
        @switch="closeOpened"
      />

      <div class="flex-1 min-h-0 overflow-hidden flex flex-col">
        <!-- Keyed by instance: scroll position belongs to one transcript. -->
        <ChatConversation
          :key="opened.id"
          :messages="opened.conversation"
          :is-processing="!!opened.isProcessing"
          :status-text="opened.statusText || ''"
          :can-restore="false"
          @open-task="openByConversation"
          class="flex-1"
        />
      </div>

      <!-- No composer: this thread is driven from the main thread (dispatch,
           and answers relayed from the check-in queue). -->
      <div class="shrink-0 px-2 pt-1 pb-3">
        <div class="rounded-2xl border border-blue-950/[0.08] dark:border-white/[0.14] bg-blue-50/40 dark:bg-white/[0.03] px-3 py-2.5">
          <p class="text-[11px] leading-snug text-blue-950/60 dark:text-white/55">
            {{ opened.isProcessing
              ? 'This agent is working in the background. You direct it from your main thread — its results and questions arrive there.'
              : 'A record of what this agent did. You direct subagents from your main thread.' }}
          </p>
          <button
            type="button"
            class="btn-back mt-2 w-full rounded-full px-3 py-1.5 text-[11px] font-semibold text-[#fdf9f2] dark:text-blue-950 transition-all duration-200"
            @click="closeOpened"
          >
            Back to subagents
          </button>
        </div>
      </div>
    </template>

    <template v-else>
    <!-- Header: the same plate the chat pane wears, switching back the other
         way. The status line reports the fleet, which is what the removed
         "view only" badge was gesturing at — except it carries real news. -->
    <WorkspacePaneHeader
      icon="fas fa-layer-group"
      tone="muted"
      title="Subagents"
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
            :is-active="instance.id === store.openedSubagentId"
            @select="handleSelect(instance)"
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
              :is-active="instance.id === store.openedSubagentId || instance.id === store.activeInstanceId"
              :is-archived="!!instance.archivedAt"
              @select="handleSelect(instance)"
            />
          </template>
        </template>
      </template>
    </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAgentStore } from '../../../stores/agentStore'
import InstanceCard from '../../molecules/sidebar/AgentInstanceCard.vue'
import WorkspacePaneHeader from '../../molecules/sidebar/WorkspacePaneHeader.vue'
import { ChatConversation } from '../../organisms/chat'
import type { AgentInstance } from '../../../types/services'

const emit = defineEmits<{
  (e: 'collapse'): void
  /** A thread the user can actually talk in was clicked (a legacy chat, a
   *  stray lead) — the workspace flips the sidebar to chat for it. Subagents
   *  never emit this: they open in place, right here. */
  (e: 'select', instanceId: string): void
}>()

const store = useAgentStore()
const showHistory = ref(false)
const opened = computed(() => store.openedSubagent)

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

/** The open subagent's own header line — the same wording its card uses. */
const openedStatus = computed(() => {
  const instance = opened.value
  if (!instance) return ''
  if (instance.isProcessing) return instance.statusText || 'Working…'
  switch (instance.reviewStatus) {
    case 'input': return 'Asked you a question'
    case 'ready': return 'Finished — waiting on you'
    case 'accepted': return 'Added to your app'
    case 'dismissed': return 'Discarded'
    default: return 'Read only'
  }
})

/**
 * A card was clicked. A subagent opens in place, so the user stays in this
 * pane and the main thread keeps its place. History also holds threads the
 * user can still talk in (legacy chats, a stray second lead) — those have a
 * composer, so they still belong in the chat pane.
 */
async function handleSelect(instance: AgentInstance) {
  if (instance.kind === 'task') {
    await store.openSubagent(instance.id)
    return
  }
  emit('select', instance.id)
  await store.switchInstance(instance.id)
}

function closeOpened() {
  void store.openSubagent(null)
}

/** A dispatch card inside a subagent's transcript: follow it in place. */
async function openByConversation(conversationId: number) {
  const instance = store.instances.find(i => i.conversationId === conversationId)
  if (instance) await store.openSubagent(instance.id)
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

/* Navy ink primary — the same recipe the chat pane's back button wears */
.btn-back {
  background: theme('colors.blue.950');
  box-shadow:
    0 1px 2px rgba(23, 37, 84, 0.2),
    0 3px 8px -2px rgba(23, 37, 84, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

.btn-back:hover {
  background: theme('colors.blue.900');
}

.dark .btn-back {
  background: #f3ede2;
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.4),
    0 3px 8px -2px rgba(0, 0, 0, 0.45);
}

.dark .btn-back:hover {
  background: #ffffff;
}
</style>
