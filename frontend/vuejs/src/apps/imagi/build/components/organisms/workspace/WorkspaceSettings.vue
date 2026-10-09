<!--
  WorkspaceSettings.vue — the workspace's settings panel.

  Opened from the gear in either pane's header. Thread defaults for now: the
  model and effort new threads start on, and one tap to move every thread onto
  them. The coordinator picks its own in its text box. Each setting is its own
  section, so the panel grows by adding sections.
-->
<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center p-4" @keydown.escape="closeSettings">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="closeSettings" />

        <div
          ref="panel"
          role="dialog"
          aria-modal="true"
          aria-labelledby="workspace-settings-title"
          tabindex="-1"
          class="settings-panel relative w-full max-w-md rounded-2xl border border-ink/[0.08] dark:border-white/[0.1] bg-white dark:bg-[#101014] shadow-2xl overflow-hidden"
        >
          <div class="flex items-center justify-between gap-3 px-5 py-4 border-b border-ink/[0.08] dark:border-white/[0.08]">
            <h2 id="workspace-settings-title" class="text-base font-semibold text-ink dark:text-white">
              Workspace settings
            </h2>
            <button
              type="button"
              class="settings-close iw-press w-8 h-8 inline-flex items-center justify-center rounded-full text-ink/45 hover:text-ink/80 hover:bg-ink/[0.05] dark:text-white/50 dark:hover:text-white dark:hover:bg-white/[0.08]"
              aria-label="Close settings"
              @click="closeSettings"
            >
              <i class="fas fa-times text-sm"></i>
            </button>
          </div>

          <div class="iw-scroll max-h-[min(36rem,calc(100vh-8rem))] overflow-y-auto px-5 py-4">
            <section aria-labelledby="settings-threads">
              <h3 id="settings-threads" class="settings-section-title">Threads</h3>
              <p class="settings-row__hint mt-1">
                New threads start on these. You can still change one thread from its own text box.
              </p>

              <div class="settings-row">
                <p class="settings-row__name">Model</p>
                <ModelChoice
                  class="mt-2"
                  label="Thread model"
                  :model-value="store.threadModelId"
                  @update:model-value="store.setThreadModel"
                />
              </div>

              <div class="settings-row">
                <p class="settings-row__name">Effort</p>
                <p class="settings-row__hint">How hard a thread thinks before it acts. Higher is slower and costs more.</p>
                <EffortChoice
                  class="mt-2"
                  label="Thread effort"
                  :model-value="store.threadEffort"
                  @update:model-value="store.setThreadEffort"
                />
                <button
                  v-if="offCount > 0"
                  type="button"
                  class="settings-switch iw-press mt-3 w-full rounded-full px-3 py-2 text-xs font-semibold text-paper dark:text-ink"
                  @click="store.switchAllThreadsToThreadModel()"
                >
                  Switch {{ offCount }} {{ offCount === 1 ? 'thread' : 'threads' }} to {{ defaultsName }}
                </button>
                <p v-else-if="hasThreads" class="settings-row__hint mt-2">
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

<style scoped>
.settings-section-title {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: rgba(19, 26, 44, 0.5);
}

.dark .settings-section-title {
  color: rgba(255, 255, 255, 0.5);
}

.settings-row {
  padding: 0.875rem 0;
}

.settings-row + .settings-row {
  border-top: 1px solid var(--iw-hairline);
}

.settings-row__name {
  font-size: 13px;
  font-weight: 600;
  color: rgba(19, 26, 44, 0.92);
}

.dark .settings-row__name {
  color: rgba(255, 255, 255, 0.92);
}

.settings-row__hint {
  margin-top: 0.125rem;
  font-size: 11px;
  line-height: 1.45;
  color: rgba(19, 26, 44, 0.6);
}

.dark .settings-row__hint {
  color: rgba(255, 255, 255, 0.55);
}

.settings-panel:focus {
  outline: none;
}

.settings-close:focus-visible,
.settings-switch:focus-visible {
  outline: none;
  box-shadow: var(--iw-focus-ring);
}

/* Navy ink primary, the composer's send recipe */
.settings-switch {
  background: theme('colors.blue.950');
  box-shadow: var(--iw-shadow-2), inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

.settings-switch:hover {
  background: theme('colors.blue.900');
}

.dark .settings-switch {
  background: #f3ede2;
}

.dark .settings-switch:hover {
  background: #ffffff;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity var(--iw-dur-2, 0.2s) ease;
}

.modal-enter-active .settings-panel,
.modal-leave-active .settings-panel {
  transition: transform var(--iw-dur-2, 0.2s) ease, opacity var(--iw-dur-2, 0.2s) ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .settings-panel,
.modal-leave-to .settings-panel {
  transform: scale(0.96);
  opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
  .modal-enter-active,
  .modal-leave-active,
  .modal-enter-active .settings-panel,
  .modal-leave-active .settings-panel {
    transition: none;
  }
}
</style>
