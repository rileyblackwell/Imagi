<!--
  ThreadModelSetting.vue — which model the threads run on.

  The foot of the Threads pane. New threads start on this model, whatever the
  coordinator runs on (Opus 5.5 until the user picks another), and one tap
  moves every thread that can still run onto it. A single thread can still be
  changed from its own composer; this is the default and the bulk switch.
-->
<template>
  <div ref="root" class="thread-model relative shrink-0 px-3 py-2">
    <Transition name="popover">
      <div
        v-if="open"
        id="thread-model-panel"
        role="group"
        aria-label="Model for threads"
        class="popover absolute bottom-full left-2 right-2 mb-1 z-50 overflow-hidden"
        @keydown.escape.stop.prevent="close"
      >
        <div class="popover__head px-3 py-2">
          <span id="thread-model-heading" class="text-[11px] font-semibold uppercase tracking-wider text-ink/50 dark:text-white/50">
            Model for threads
          </span>
        </div>
        <div role="radiogroup" aria-labelledby="thread-model-heading" class="p-1">
          <button
            v-for="m in models"
            :key="m.id"
            type="button"
            role="radio"
            :aria-checked="m.id === store.threadModelId"
            class="model-row"
            :class="{ 'model-row--on': m.id === store.threadModelId }"
            @click="pick(m.id)"
          >
            <span class="min-w-0 flex-1">
              <span class="model-row__name">
                {{ m.short }}
                <span class="model-row__tier">{{ m.tier }}</span>
              </span>
            </span>
            <i
              class="fas fa-check model-row__check"
              :class="{ 'opacity-0': m.id !== store.threadModelId }"
              aria-hidden="true"
            ></i>
          </button>
        </div>
        <div class="popover__foot px-3 pt-2 pb-3">
          <p class="thread-model__note">
            New threads start on this model. You can still change one thread from its own box.
          </p>
          <button
            v-if="offCount > 0"
            type="button"
            class="thread-model__switch iw-press mt-2 w-full rounded-full px-3 py-1.5 text-[11px] font-semibold text-paper dark:text-ink"
            @click="switchAll"
          >
            Switch {{ offCount }} {{ offCount === 1 ? 'thread' : 'threads' }} to {{ currentShort }}
          </button>
          <p v-else-if="hasThreads" class="thread-model__note mt-1.5">
            Every thread is on {{ currentShort }}.
          </p>
        </div>
      </div>
    </Transition>

    <div class="flex items-center justify-between gap-2">
      <span class="text-[11px] text-ink/50 dark:text-white/45">Threads run on</span>
      <button
        type="button"
        class="control-chip iw-press"
        :class="{ 'control-chip--active': open }"
        aria-controls="thread-model-panel"
        :aria-expanded="open"
        :title="`Model for threads: ${currentShort}`"
        @click="open = !open"
      >
        <i class="fas fa-microchip control-chip-icon"></i>
        <span class="control-chip-label">{{ currentShort }}</span>
        <i class="fas fa-chevron-down control-chip-caret" :class="{ 'rotate-180': open }"></i>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useAgentStore } from '../../../stores/agentStore'
import { AI_MODELS } from '../../../types/services'

const store = useAgentStore()
const open = ref(false)
const root = ref<HTMLElement | null>(null)

// Faster → smarter, the order the composer's model menu uses.
const RANK: Record<string, number> = { 'gpt-6-luna': 0, 'claude-opus-5-5': 1, 'gpt-6-astra': 2 }
const TIERS: Record<string, string> = {
  'gpt-6-luna': 'Fast',
  'claude-opus-5-5': 'Balanced',
  'gpt-6-astra': 'Frontier',
}

/** "Luna", "Opus 5.5", "Astra": the name without its family prefix. */
function shortName(name: string): string {
  return name.replace(/^(?:GPT\s*\d+(?:\.\d+)?|Claude)\s*/i, '').trim() || name
}

const models = computed(() => {
  const lineup = store.availableModels.length > 0 ? store.availableModels : AI_MODELS
  return [...lineup]
    .filter(m => m.id in RANK)
    .sort((a, b) => RANK[a.id]! - RANK[b.id]!)
    .map(m => ({ id: m.id, short: shortName(m.name), tier: TIERS[m.id] ?? '' }))
})

const currentShort = computed(
  () => models.value.find(m => m.id === store.threadModelId)?.short ?? 'Opus 5.5'
)

const offCount = computed(() => store.threadsOffThreadModel.length)
const hasThreads = computed(() =>
  store.instances.some(i => i.kind === 'task' && !i.archivedAt && i.reviewStatus !== 'dismissed')
)

function pick(id: string) {
  store.setThreadModel(id)
}

function switchAll() {
  store.switchAllThreadsToThreadModel()
}

function close() {
  open.value = false
  root.value?.querySelector<HTMLButtonElement>('.control-chip')?.focus()
}

function onDocMousedown(e: MouseEvent) {
  if (open.value && !root.value?.contains(e.target as Node)) open.value = false
}
onMounted(() => document.addEventListener('mousedown', onDocMousedown))
onBeforeUnmount(() => document.removeEventListener('mousedown', onDocMousedown))
</script>

<style scoped>
.thread-model {
  border-top: 1px solid var(--iw-hairline);
}

/* The composer's popover material and chip, so the setting reads as the
   same control family as the model chip in every text box. */
.popover {
  border-radius: var(--iw-r-lg);
  border: 1px solid var(--iw-material-border);
  background: var(--iw-material-bg);
  -webkit-backdrop-filter: var(--iw-material-filter);
  backdrop-filter: var(--iw-material-filter);
  box-shadow: var(--iw-shadow-3);
}

@supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
  .popover {
    background: #ffffff;
  }

  .dark .popover {
    background: #0f0f0f;
  }
}

.popover__head {
  border-bottom: 1px solid var(--iw-hairline);
}

.popover__foot {
  border-top: 1px solid var(--iw-hairline);
}

.popover-enter-active {
  transition:
    opacity var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-3) var(--iw-ease-spring);
  transform-origin: bottom center;
}

.popover-leave-active {
  transition:
    opacity var(--iw-dur-1) var(--iw-ease-out),
    transform var(--iw-dur-1) var(--iw-ease-out);
  transform-origin: bottom center;
}

.popover-enter-from {
  opacity: 0;
  transform: translateY(8px) scale(0.96);
}

.popover-leave-to {
  opacity: 0;
  transform: translateY(4px) scale(0.98);
}

.control-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  min-width: 0;
  height: 1.75rem;
  padding: 0 0.625rem;
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 500;
  color: rgba(19, 26, 44, 0.65);
  transition:
    background-color var(--iw-dur-2) var(--iw-ease-out),
    color var(--iw-dur-2) var(--iw-ease-out);
}

.control-chip:hover,
.control-chip--active {
  background: rgba(19, 26, 44, 0.06);
  color: rgba(19, 26, 44, 0.9);
}

.control-chip:focus-visible,
.model-row:focus-visible,
.thread-model__switch:focus-visible {
  outline: none;
  box-shadow: var(--iw-focus-ring);
}

.dark .control-chip {
  color: rgba(255, 255, 255, 0.6);
}

.dark .control-chip:hover,
.dark .control-chip--active {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.9);
}

.control-chip-icon {
  font-size: 10px;
  opacity: 0.7;
}

.control-chip-caret {
  font-size: 8px;
  opacity: 0.6;
  transition: transform var(--iw-dur-2) var(--iw-ease-out);
}

.model-row {
  display: flex;
  width: 100%;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.625rem;
  border-radius: var(--iw-r-md, 0.75rem);
  text-align: left;
  transition: background-color var(--iw-dur-2) var(--iw-ease-out);
}

.model-row:hover,
.model-row--on {
  background: rgba(19, 26, 44, 0.05);
}

.dark .model-row:hover,
.dark .model-row--on {
  background: rgba(255, 255, 255, 0.06);
}

.model-row__name {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: rgba(19, 26, 44, 0.9);
}

.dark .model-row__name {
  color: rgba(255, 255, 255, 0.9);
}

.model-row__tier {
  margin-left: 0.25rem;
  font-size: 10px;
  font-weight: 500;
  color: rgba(19, 26, 44, 0.5);
}

.dark .model-row__tier {
  color: rgba(255, 255, 255, 0.5);
}

.model-row__check {
  font-size: 10px;
  color: rgba(19, 26, 44, 0.7);
}

.dark .model-row__check {
  color: rgba(255, 255, 255, 0.75);
}

.thread-model__note {
  font-size: 10px;
  line-height: 1.4;
  color: rgba(19, 26, 44, 0.6);
}

.dark .thread-model__note {
  color: rgba(255, 255, 255, 0.55);
}

/* Navy ink primary, the composer's send recipe */
.thread-model__switch {
  background: theme('colors.blue.950');
  box-shadow: var(--iw-shadow-2), inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

.thread-model__switch:hover {
  background: theme('colors.blue.900');
}

.dark .thread-model__switch {
  background: #f3ede2;
}

.dark .thread-model__switch:hover {
  background: #ffffff;
}
</style>
