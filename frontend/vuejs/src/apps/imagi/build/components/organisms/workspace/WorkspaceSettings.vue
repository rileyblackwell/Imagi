<!--
  WorkspaceSettings.vue — the workspace's settings panel.

  Opened from the gear in either pane's header. Thread defaults for now: the
  model and effort new threads start on, and one tap to move every thread onto
  them. The coordinator picks its own in its text box. Each setting is its own
  section, so the panel grows by adding sections.
-->
<template>
  <Teleport to="body">
    <!-- The overlay fades and the panel scales up from 96%. -->
    <Transition
      enter-active-class="[transition:opacity_var(--iw-dur-2,0.2s)_ease] [&_.settings-panel]:[transition:transform_var(--iw-dur-2,0.2s)_ease,opacity_var(--iw-dur-2,0.2s)_ease] motion-reduce:[transition:none] motion-reduce:[&_.settings-panel]:[transition:none]"
      leave-active-class="[transition:opacity_var(--iw-dur-2,0.2s)_ease] [&_.settings-panel]:[transition:transform_var(--iw-dur-2,0.2s)_ease,opacity_var(--iw-dur-2,0.2s)_ease] motion-reduce:[transition:none] motion-reduce:[&_.settings-panel]:[transition:none]"
      enter-from-class="opacity-0 [&_.settings-panel]:[transform:scale(0.96)] [&_.settings-panel]:opacity-0"
      leave-to-class="opacity-0 [&_.settings-panel]:[transform:scale(0.96)] [&_.settings-panel]:opacity-0"
    >
      <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center p-4" @keydown.escape="closeSettings">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="closeSettings" />

        <div
          ref="panel"
          role="dialog"
          aria-modal="true"
          aria-labelledby="workspace-settings-title"
          tabindex="-1"
          class="settings-panel relative w-full max-w-md rounded-2xl border border-ink/[0.08] dark:border-white/[0.1] bg-white dark:bg-[#101014] shadow-2xl overflow-hidden focus:[outline:none]"
        >
          <div class="flex items-center justify-between gap-3 px-5 py-4 border-b border-ink/[0.08] dark:border-white/[0.08]">
            <h2 id="workspace-settings-title" class="text-base font-semibold text-ink dark:text-white">
              Workspace settings
            </h2>
            <button
              type="button"
              class="iw-press w-8 h-8 inline-flex items-center justify-center rounded-full text-ink/45 hover:text-ink/80 hover:bg-ink/[0.05] dark:text-white/50 dark:hover:text-white dark:hover:bg-white/[0.08] focus-visible:[outline:none] focus-visible:[box-shadow:var(--iw-focus-ring)]"
              aria-label="Close settings"
              @click="closeSettings"
            >
              <i class="fas fa-times text-sm"></i>
            </button>
          </div>

          <div class="iw-scroll max-h-[min(36rem,calc(100vh-8rem))] overflow-y-auto px-5 py-4">
            <section aria-labelledby="settings-threads">
              <h3 id="settings-threads" class="text-[11px] font-semibold tracking-[0.06em] uppercase text-ink/50 dark:text-white/50">Threads</h3>
              <p class="mt-0.5 text-[11px] leading-[1.45] text-ink/60 dark:text-white/[0.55]">
                New threads start on these. You can still change one thread from its own text box.
              </p>

              <div class="py-3.5">
                <p class="text-[13px] font-semibold text-ink/[0.92] dark:text-white/[0.92]">Model</p>
                <ModelChoice
                  class="mt-2"
                  label="Thread model"
                  :model-value="store.threadModelId"
                  @update:model-value="store.setThreadModel"
                />
              </div>

              <div class="py-3.5 border-t border-t-iw-hairline">
                <p class="text-[13px] font-semibold text-ink/[0.92] dark:text-white/[0.92]">Effort</p>
                <p class="mt-0.5 text-[11px] leading-[1.45] text-ink/60 dark:text-white/[0.55]">How hard a thread thinks before it acts. Higher is slower and costs more.</p>
                <EffortChoice
                  class="mt-2"
                  label="Thread effort"
                  :model-value="store.threadEffort"
                  @update:model-value="store.setThreadEffort"
                />
                <!-- Navy ink primary, the composer's send recipe -->
                <button
                  v-if="offCount > 0"
                  type="button"
                  class="settings-switch iw-press mt-3 w-full rounded-full px-3 py-2 text-xs font-semibold text-paper dark:text-ink
                    bg-blue-950 hover:bg-blue-900 dark:bg-[#f3ede2] dark:hover:bg-white
                    [box-shadow:var(--iw-shadow-2),inset_0_1px_0_rgba(255,255,255,0.12)]
                    focus-visible:[outline:none] focus-visible:[box-shadow:var(--iw-focus-ring)]"
                  @click="store.switchAllThreadsToThreadModel()"
                >
                  Switch {{ offCount }} {{ offCount === 1 ? 'thread' : 'threads' }} to {{ defaultsName }}
                </button>
                <p v-else-if="hasThreads" class="mt-0.5 text-[11px] leading-[1.45] text-ink/60 dark:text-white/[0.55]">
                  Every thread is on {{ defaultsName }}.
                </p>
              </div>
            </section>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { useAgentStore } from '../../../stores/agentStore'
import { useWorkspaceSettings } from '../../../composables/useWorkspaceSettings'
import { AI_MODELS, REASONING_EFFORTS } from '../../../types/services'
import EffortChoice from '../../molecules/sidebar/EffortChoice.vue'
import ModelChoice from '../../molecules/sidebar/ModelChoice.vue'

const store = useAgentStore()
const { open, closeSettings } = useWorkspaceSettings()
const panel = ref<HTMLElement | null>(null)

const offCount = computed(() => store.threadsOffThreadModel.length)
const hasThreads = computed(() =>
  store.instances.some(i => i.kind === 'task' && !i.archivedAt && i.reviewStatus !== 'dismissed')
)

/** "Opus 5.5 · Medium": the thread defaults, as the switch button names them. */
const defaultsName = computed(() => {
  const model = (AI_MODELS.find(m => m.id === store.threadModelId)?.name ?? 'Claude Opus 5.5')
    .replace(/^(?:GPT\s*\d+(?:\.\d+)?|Claude)\s*/i, '').trim()
  const effort = REASONING_EFFORTS.find(e => e.id === store.threadEffort)?.name ?? 'Medium'
  return `${model} · ${effort}`
})

// Focus moves into the dialog so Escape and Tab work from the first key.
watch(open, isOpen => {
  if (isOpen) void nextTick(() => panel.value?.focus())
})
</script>

