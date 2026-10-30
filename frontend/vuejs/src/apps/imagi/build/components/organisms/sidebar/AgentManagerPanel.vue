<!--
  AgentManagerPanel.vue — the threads pane.

  Every thread the coordinator has dispatched, grouped by what it wants from
  the user: waiting on you, working, finished. The pane wears the same
  masthead as the chat pane, then states the fleet twice: once as a meter and
  once as the cards. Opening a thread shows its transcript with a composer, so
  the user can steer it directly; its results and questions still report back
  to the coordinator.
-->
<template>
  <div class="iw-surface relative overflow-hidden h-full bg-canvas transition-colors duration-300">
    <!-- Opening a thread is a navigation, so it moves like one: the list
         slides out to the left as the thread comes in from the right, and
         back the other way on the return (push: the deeper view comes
         forward; pop: the same movement, reversed). The leaving pane is taken
         out of flow so the two cross in place rather than one waiting for the
         other to finish — otherwise the incoming view would stack below the
         outgoing one and the pane would grow to twice its height mid-way. -->
    <Transition
      enter-active-class="[transition:opacity_var(--iw-dur-3)_var(--iw-ease-out),transform_var(--iw-dur-3)_var(--iw-ease-out)]"
      leave-active-class="absolute inset-0 [transition:opacity_var(--iw-dur-3)_var(--iw-ease-out),transform_var(--iw-dur-3)_var(--iw-ease-out)]"
      :enter-from-class="opened || memoryOpen ? 'opacity-0 [transform:translateX(14px)]' : 'opacity-0 [transform:translateX(-14px)]'"
      :leave-to-class="opened || memoryOpen ? 'opacity-0 [transform:translateX(-10px)]' : 'opacity-0 [transform:translateX(10px)]'"
    >
    <!-- Reading (and steering) one thread. It happens here rather than in the
         chat pane on purpose: opening a thread must not displace the
         coordinator chat and its draft. -->
    <div v-if="opened" key="opened" class="w-full flex flex-col h-full">
      <WorkspacePaneHeader
        :title="opened.title || 'Thread'"
        :status="openedStatus"
        :state="openedState"
        :switches="[{ id: 'back', icon: 'fas fa-layer-group', label: 'Threads', direction: 'back' }]"
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
          agent-kind="thread"
          :agent-name="opened.title || 'Thread'"
          @open-task="openByConversation"
          @answer="store.steerThread(opened.id, $event)"
          class="flex-1"
        />
      </div>

      <!-- The user can steer a thread from inside it: what they type is its
           next turn, the same as a follow-up the coordinator forwards. -->
      <ThreadComposer :instance="opened" @back="closeOpened" />
    </div>

    <!-- The project's shared memory: what every thread reads. Opened from
         this pane's header, because it is the one thing the threads share. -->
    <div v-else-if="memoryOpen" key="memory" class="w-full flex flex-col h-full">
      <WorkspacePaneHeader
        title="Project memory"
        :status="memoryStatus"
        state="idle"
        :switches="[{ id: 'back', icon: 'fas fa-layer-group', label: 'Threads', direction: 'back' }]"
        @switch="memoryOpen = false"
      />
      <div class="iw-scroll flex-1 min-h-0 overflow-y-auto">
        <ProjectMemoryPanel />
      </div>
    </div>

    <div v-else key="list" class="w-full flex flex-col h-full">
    <!-- Header: the same plate the chat pane wears, switching back the other
         way. The status line reports the fleet, which is what the removed
         "view only" badge was gesturing at — except it carries real news.

         One destination, at every width, and deliberately so: this pane is
         looking under the hood of the main thread, and the main thread is
         where everything is driven from. The preview is a hop further out —
         you get there through the main agent, the same as everything else. -->
    <WorkspacePaneHeader
      title="Threads"
      :status="fleetStatus"
      :state="fleetState"
      :switches="[{
        id: 'chat',
        icon: 'fas fa-comments',
        label: 'Coordinator',
        count: store.waitingCheckIns.length,
        direction: 'back',
      }, {
        id: 'memory',
        icon: 'fas fa-book-open',
        label: 'Project memory',
        iconOnly: true,
        fresh: store.memoryFresh,
      }, {
        id: 'settings',
        icon: 'fas fa-gear',
        label: 'Workspace settings',
        iconOnly: true,
      }]"
      @switch="onListSwitch"
    />

    <!-- Fleet meter: the same numbers as the status line, drawn. Segments are
         proportional, so a glance says whether the crew is busy or the pile of
         work waiting on you is the bigger half. -->
    <div v-if="fleetSegments.length > 0" class="flex gap-0.5 h-0.5 mx-3.5 pt-2 box-content" :title="fleetStatus">
      <!-- Re-proportioning is the slowest thing in the pane on purpose: the
           bar is reporting a change in the crew's shape, and a bar that snaps
           to a new division reads as a glitch rather than as news. Same three
           tones the card rails use, so the bar reads as a key to the list. -->
      <span
        v-for="seg in fleetSegments"
        :key="seg.key"
        :class="['basis-0 rounded-full [transition:flex-grow_var(--iw-dur-4)_var(--iw-ease-out)]', SEGMENT[seg.key]]"
        :style="{ flexGrow: seg.count }"
      ></span>
    </div>

    <!-- Team view -->
    <div class="iw-scroll flex-1 min-h-0 overflow-y-auto px-2 py-2">
      <!-- Loading: the shape of the list, before the list -->
      <div v-if="store.instancesLoading && store.instances.length === 0" class="space-y-1.5 pt-1">
        <!-- The list's own silhouette — rail on the left, two lines of text —
             so the pane does not jump when the real cards land. -->
        <div
          v-for="n in 3"
          :key="n"
          class="skeleton-card relative flex gap-2.5 py-2 pr-2 pl-3 border border-ink/[0.06] rounded-iw-md overflow-hidden opacity-0 dark:border-white/[0.07]"
          :style="{ '--stagger': `${n * 90}ms` }"
        >
          <span class="absolute left-0 top-0 bottom-0 w-[0.1875rem] bg-ink/[0.13] dark:bg-white/[0.13]"></span>
          <div class="flex-1 space-y-1.5">
            <div :class="[SKELETON_LINE, 'h-2']" :style="{ width: n === 2 ? '58%' : '72%' }"></div>
            <div :class="[SKELETON_LINE, 'h-1.5 opacity-[0.65]']" :style="{ width: n === 3 ? '34%' : '46%' }"></div>
          </div>
        </div>
        <p class="pt-1 text-center text-[10px] text-ink/35 dark:text-white/30">Loading agents…</p>
      </div>

      <template v-else>
        <!-- Three groups, in the order they want the user: threads waiting
             on you (a question, takes to pick from, a run that stopped), the
             ones working right now, and the ones that are finished. -->
        <template v-for="section in sections" :key="section.key">
          <!-- Uppercase micro-label, its count, then a hairline running to the
               edge — the workspace's label convention, given a rule so
               sections separate without another box. -->
          <div v-if="section.items.length > 0" :class="HEAD">
            <span :class="HEAD_LABEL">{{ section.label }}</span>
            <span :class="HEAD_COUNT">{{ section.items.length }}</span>
            <span :class="HEAD_RULE"></span>
          </div>

          <!-- Threads reorder as they finish and new ones are dispatched.
               TransitionGroup makes that a movement rather than a re-render;
               the per-card --stagger spaces a batch of parallel takes so they
               arrive as a sequence. A card joining drops into place; leaving
               is quicker and quieter than arriving (a settled agent should not
               take the eye with it); and the rest of the column closing the
               gap is the move that makes the list feel like objects rather
               than rows. Gap rather than margins: leaving cards are taken out
               of flow, and a margin-based rhythm would collapse around them. -->
          <TransitionGroup
            v-if="section.items.length > 0"
            tag="div"
            :class="['flex flex-col gap-1', section.key === 'finished' ? '' : 'mb-2']"
            appear
            v-bind="LIST_MOTION"
          >
            <InstanceCard
              v-for="(instance, i) in section.items"
              :key="instance.id"
              :instance="instance"
              :index="i"
              :is-active="instance.id === store.openedThreadId"
              :variant-index="variantPlace(instance).index"
              :variant-count="variantPlace(instance).count"
              @select="handleSelect(instance)"
            />
          </TransitionGroup>

          <button
            v-if="section.key === 'finished' && finishedHidden > 0"
            type="button"
            class="iw-press block mx-auto mt-1.5 mb-0 py-1 px-2.5 rounded-full text-[0.625rem] font-semibold text-ink/50
              [transition:background-color_var(--iw-dur-2)_var(--iw-ease-out),color_var(--iw-dur-2)_var(--iw-ease-out)]
              hover:bg-blue-50/80 hover:text-ink/80 dark:text-white/45 dark:hover:bg-white/5 dark:hover:text-white/80
              focus-visible:![outline:none] focus-visible:shadow-iw-focus"
            @click="showAllFinished = true"
          >
            Show {{ finishedHidden }} more
          </button>
        </template>

        <!-- Nothing at all yet: say what would put something here -->
        <!-- A drawn-but-unfilled plate: the same dashed language the "not
             started yet" card rail uses, so an empty crew reads as capacity
             rather than an error. -->
        <div
          v-if="!hasThreads"
          class="empty-plate mt-0.5 mx-0.5 mb-0 pt-[1.125rem] px-3.5 pb-5 border border-dashed border-ink/[0.14] rounded-iw-md text-center
            bg-[linear-gradient(180deg,rgba(239,246,255,0.55)_0%,rgba(239,246,255,0)_100%)]
            dark:border-white/[0.11] dark:bg-[linear-gradient(180deg,rgba(255,255,255,0.03)_0%,rgba(255,255,255,0)_100%)]"
        >
          <span
            class="inline-flex items-center justify-center w-[1.625rem] h-[1.625rem] mb-2 rounded-lg bg-ink/[0.06] text-ink/40 [box-shadow:inset_0_0_0_1px_rgba(19,26,44,0.05)]
              dark:bg-white/[0.06] dark:text-white/40 dark:[box-shadow:inset_0_1px_0_rgba(255,255,255,0.06)]"
          ><i class="fas fa-layer-group text-[10px]"></i></span>
          <p :class="EMPTY_TITLE">No threads yet</p>
          <p class="mt-1 text-[0.6875rem] leading-[1.45] text-ink/[0.42] dark:text-blue-100/[0.38]">
            Tell the coordinator what you want, one thing after another — it
            starts a thread for each job and they work in parallel.
          </p>
        </div>

        <!-- History: archived threads, legacy chats, resolved tasks -->
        <template v-if="history.length> 0">
          <button
            type="button"
            :class="[
              HEAD,
              'group/head mt-3 rounded-iw-xs cursor-pointer [transition:background-color_var(--iw-dur-2)_var(--iw-ease-out)]',
              'hover:bg-blue-50/70 dark:hover:bg-white/[0.035] focus-visible:![outline:none] focus-visible:shadow-iw-focus'
            ]"
            :aria-expanded="showHistory"
            @click="showHistory = !showHistory"
          >
            <i
              :class="[
                'fas fa-chevron-right text-[0.5rem] text-ink/35 dark:text-white/35 [transition:transform_var(--iw-dur-3)_var(--iw-ease-inout)]',
                showHistory && '[transform:rotate(90deg)]'
              ]"
            ></i>
            <span :class="[HEAD_LABEL, 'group-hover/head:text-ink/[0.72] dark:group-hover/head:text-white/[0.72]']">History</span>
            <span :class="HEAD_COUNT">{{ history.length }}</span>
            <span :class="HEAD_RULE"></span>
          </button>
          <!-- Unfolds to its own height instead of appearing. Still behind
               v-if, so a collapsed History costs nothing until it is opened. -->
          <FoldTransition>
            <div v-if="showHistory" class="flex flex-col gap-1">
              <InstanceCard
                v-for="(instance, i) in history"
                :key="instance.id"
                :instance="instance"
                :index="i"
                :is-active="instance.id === store.openedThreadId || instance.id === store.activeInstanceId"
                :is-archived="!!instance.archivedAt"
                @select="handleSelect(instance)"
              />
            </div>
          </FoldTransition>
        </template>
      </template>
    </div>
    </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAgentStore } from '../../../stores/agentStore'
// This pane's half of the workspace's shared motion + material vocabulary
// (see BuilderSidebarChat for why each pane imports it directly).
import '../../../styles/workspace.css'
import InstanceCard from '../../molecules/sidebar/AgentInstanceCard.vue'
import WorkspacePaneHeader from '../../molecules/sidebar/WorkspacePaneHeader.vue'
import FoldTransition from '../../molecules/common/FoldTransition.vue'
import ThreadComposer from '../../molecules/sidebar/ThreadComposer.vue'
import ProjectMemoryPanel from '../../molecules/sidebar/ProjectMemoryPanel.vue'
import { timeAgo } from '../../../utils/projectMemory'
import { heldStatus } from '../../../utils/threadSchedule'
import { isHeldThread } from '../../../stores/agentStore'
import { useWorkspaceSettings } from '../../../composables/useWorkspaceSettings'
import { ChatConversation } from '../../organisms/chat'
import type { AgentInstance } from '../../../types/services'

const emit = defineEmits<{
  (e: 'collapse'): void
  /** A thread the user can actually talk in was clicked (a legacy chat, a
   *  stray lead) — the workspace flips the sidebar to chat for it. Threads
   *  never emit this: they open in place, right here. */
  (e: 'select', instanceId: string): void
}>()

const store = useAgentStore()

/* The fleet meter's three tones: live work drifting, what wants the user in
   navy ink, what has not started faint. */
const SEGMENT: Record<string, string> = {
  working:
    'fleet-meter__seg--working bg-[length:200%_100%] ' +
    'bg-[linear-gradient(90deg,color-mix(in_srgb,var(--sl-work)_65%,transparent)_0%,var(--sl-work)_50%,color-mix(in_srgb,var(--sl-work)_65%,transparent)_100%)]',
  waiting: 'bg-blue-950 dark:bg-[#f3ede2]',
  starting: 'bg-ink/20 dark:bg-white/[0.22]',
}

/* The cards carry their own transition (and position), so the list's
   motion classes outrank them with `!`. */
const LIST_MOTION = {
  // The delay is its own declaration (one value, the card's --stagger); the
  // [&] variant only places it after the shorthand.
  enterActiveClass:
    '![transition:opacity_var(--iw-dur-3)_var(--iw-ease-out),transform_var(--iw-dur-3)_var(--iw-ease-spring)] [&]:![transition-delay:var(--stagger,0ms)]',
  enterFromClass: 'opacity-0 [transform:translateY(-6px)_scale(0.97)]',
  leaveActiveClass:
    '!absolute left-2 right-2 ![transition:opacity_var(--iw-dur-2)_var(--iw-ease-out),transform_var(--iw-dur-2)_var(--iw-ease-out)]',
  leaveToClass: 'opacity-0 [transform:scale(0.96)]',
  moveClass: '![transition:transform_var(--iw-dur-4)_var(--iw-ease-out)]',
}

const HEAD = 'flex items-center gap-1.5 w-full pt-1.5 px-2 pb-2 text-left'
const HEAD_LABEL =
  'text-[0.625rem] font-semibold uppercase tracking-[0.09em] text-ink/45 dark:text-white/[0.42] [transition:color_var(--iw-dur-2)_var(--iw-ease-out)]'
const HEAD_COUNT =
  'text-[0.5625rem] font-semibold tabular-nums px-1 rounded bg-ink/[0.06] text-ink/50 leading-[0.9375rem] dark:bg-white/[0.07] dark:text-blue-100/55 ' +
  '[transition:background-color_var(--iw-dur-2)_var(--iw-ease-out),color_var(--iw-dur-2)_var(--iw-ease-out)]'
const HEAD_RULE =
  'flex-1 h-px bg-[linear-gradient(90deg,rgba(19,26,44,0.12)_0%,rgba(19,26,44,0)_100%)] dark:bg-[linear-gradient(90deg,rgba(255,255,255,0.14)_0%,rgba(255,255,255,0)_100%)]'

const EMPTY_TITLE =
  "font-sl-display [font-variation-settings:'opsz'_12,'SOFT'_30,'WONK'_1] text-[0.8125rem] font-[550] text-ink/70 dark:text-white/[0.72]"

const SKELETON_LINE =
  'skeleton-line rounded-full bg-[length:200%_100%] ' +
  'bg-[linear-gradient(90deg,rgba(19,26,44,0.07)_0%,rgba(19,26,44,0.13)_50%,rgba(19,26,44,0.07)_100%)] ' +
  'dark:bg-[linear-gradient(90deg,rgba(255,255,255,0.05)_0%,rgba(255,255,255,0.11)_50%,rgba(255,255,255,0.05)_100%)]'
const { openSettings } = useWorkspaceSettings()
const showHistory = ref(false)
const opened = computed(() => store.openedThread)
const memoryOpen = ref(false)

function onListSwitch(id: string) {
  if (id === 'settings') openSettings()
  else if (id === 'memory') memoryOpen.value = true
  else emit('collapse')
}

const memoryStatus = computed(() => {
  if (!store.memory) return ''
  const updated = timeAgo(store.memory.updated_at)
  return updated ? `Shared by every thread · updated ${updated}` : 'Shared by every thread'
})

// Already newest-first. The coordinator's own chat is the chat pane, so it is
// deliberately absent here — this panel is only about the threads.
const activeAgents = computed(() => store.activeAgentInstances)
const history = computed(() => store.historyInstances)

/** Finished threads pile up; the newest few are shown until asked for more. */
const FINISHED_PREVIEW = 5
const showAllFinished = ref(false)
const finishedHidden = computed(() =>
  showAllFinished.value ? 0 : Math.max(0, store.finishedThreads.length - FINISHED_PREVIEW)
)

const sections = computed(() => [
  { key: 'waiting', label: 'Waiting on you', items: store.waitingThreads },
  { key: 'working', label: 'Working', items: store.workingThreads },
  // Placed by the coordinator to start once other threads' work lands.
  { key: 'scheduled', label: 'Scheduled', items: store.scheduledThreads },
  {
    key: 'finished',
    label: 'Finished',
    items: showAllFinished.value
      ? store.finishedThreads
      : store.finishedThreads.slice(0, FINISHED_PREVIEW),
  },
])

const hasThreads = computed(() => sections.value.some(s => s.items.length > 0))

const workingCount = computed(() => store.workingThreads.length)

/** The fleet at a glance, leading with whoever is actually working. */
const fleetStatus = computed(() => {
  const working = workingCount.value
  const waiting = store.waitingThreads.length
  const scheduled = store.scheduledThreads.length
  if (working === 0 && waiting === 0) {
    if (scheduled > 0) return `${scheduled} scheduled`
    return store.finishedThreads.length > 0 ? 'All threads finished' : 'No threads yet'
  }
  const parts = []
  if (working > 0) parts.push(waiting === 0 ? `${working} ${working === 1 ? 'thread' : 'threads'} working` : `${working} working`)
  if (waiting > 0) parts.push(`${waiting} waiting on you`)
  if (scheduled > 0) parts.push(`${scheduled} scheduled`)
  return parts.join(' · ')
})

/** The dot beside that line. Live work outranks the rest — the same precedence
 *  a card applies to its own rail. */
const fleetState = computed<'working' | 'waiting' | 'idle'>(() => {
  if (workingCount.value > 0) return 'working'
  return store.waitingThreads.length > 0 ? 'waiting' : 'idle'
})

/**
 * The meter's segments, in the order the eye should read them: live work
 * first, then what wants the user, then what has not started. Empty segments
 * are dropped so the bar never carries a zero-width sliver.
 */
const fleetSegments = computed(() => {
  const working = store.workingThreads.filter(a => a.isProcessing).length
  const starting = store.workingThreads.length - working
  const waiting = store.waitingThreads.length
  return [
    { key: 'working', count: working },
    { key: 'waiting', count: waiting },
    { key: 'starting', count: starting + store.scheduledThreads.length },
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

/** The open thread's own header line — the same wording its card uses, and
 *  only while it is resting. What a running thread is doing is narrated at
 *  the foot of its transcript instead, where the work itself is. */
const openedStatus = computed(() => {
  const instance = opened.value
  if (!instance) return ''
  if (instance.isProcessing) return ''
  if (isHeldThread(instance)) return heldStatus(instance.schedule)
  switch (instance.reviewStatus) {
    case 'input': return 'Asked you a question'
    case 'ready': return 'Thread complete — one of your options'
    case 'failed': return 'Stopped before finishing'
    case 'accepted': return 'Thread complete'
    case 'dismissed': return 'Discarded'
    default: return ''
  }
})

/** …and the dot that leads it, keyed the same way its card is. Never
 *  'working': there is no line here while a run is live. */
const openedState = computed<'waiting' | 'idle'>(() => {
  if (opened.value && isHeldThread(opened.value)) {
    return opened.value.schedule?.status === 'blocked' ? 'waiting' : 'idle'
  }
  const status = opened.value?.reviewStatus
  // A failed run wants the user too — it is holding a worktree until they
  // dismiss it — so it leads with the same mark.
  return status === 'input' || status === 'ready' || status === 'failed'
    ? 'waiting'
    : 'idle'
})

/**
 * A card was clicked. A thread opens in place, so the user stays in this
 * pane and the main thread keeps its place. History also holds threads the
 * user can still talk in (legacy chats, a stray second lead) — those have a
 * composer, so they still belong in the chat pane.
 */
async function handleSelect(instance: AgentInstance) {
  if (instance.kind === 'task') {
    await store.openThread(instance.id)
    return
  }
  emit('select', instance.id)
  await store.switchInstance(instance.id)
}

function closeOpened() {
  void store.openThread(null)
}

/** A dispatch card inside a thread's transcript: follow it in place. */
async function openByConversation(conversationId: number) {
  const instance = store.instances.find(i => i.conversationId === conversationId)
  if (instance) await store.openThread(instance.id)
}
</script>

<style scoped>
/* Keyframed motion only: scoped keyframe names can't be reached from a
   utility. */

.fleet-meter__seg--working {
  animation: fleet-drift 2.8s linear infinite;
}

@keyframes fleet-drift {
  from { background-position: 200% 0; }
  to { background-position: 0 0; }
}

/* The pane settling into "nothing running" should feel like the list coming
   to rest, not like an error state flashing up. */
.empty-plate {
  animation: plate-in var(--iw-dur-4) var(--iw-ease-out) both;
}

@keyframes plate-in {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: none; }
}

.skeleton-card {
  animation: skeleton-in var(--iw-dur-3) var(--iw-ease-out) both;
  animation-delay: var(--stagger, 0ms);
}

.skeleton-line {
  animation: skeleton-sweep 1.6s ease-in-out infinite;
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
  .skeleton-card,
  .empty-plate {
    animation: none;
  }

  .skeleton-card,
  .empty-plate {
    opacity: 1;
  }
}
</style>
