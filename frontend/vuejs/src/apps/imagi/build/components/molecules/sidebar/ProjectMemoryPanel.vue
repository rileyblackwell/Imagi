<!--
  ProjectMemoryPanel.vue — the project's shared memory, as the user sees it.

  What the coordinator and every thread know about this app: decisions,
  conventions and facts that later work should follow. Threads add to it as
  their work lands (a thread's entry waits, under "Saves when its thread
  lands", until then), the coordinator saves what the user decides, and the
  user can add, change or remove anything here. Every thread reads the
  current entries before each step, so a change here reaches work already
  running.

  It lives in the threads pane, opened from its header, because it belongs
  to the threads: it is the one thing they all share.
-->
<template>
  <div class="memory">
    <p class="memory__lede">
      What the coordinator and every thread know about your app. Threads add
      to it as their work lands, and you can change anything here.
    </p>

    <!-- Add an entry: a topic and what every thread should know about it -->
    <form class="memory__add" @submit.prevent="add">
      <input
        v-model="draftKey"
        class="memory__field"
        placeholder="Topic, e.g. Brand colors"
        aria-label="Topic"
        maxlength="80"
      />
      <textarea
        v-model="draftValue"
        class="memory__field memory__field--value"
        rows="2"
        placeholder="What every thread should know"
        aria-label="What every thread should know"
        maxlength="1000"
        @keydown.enter.exact.prevent="add"
      ></textarea>
      <div class="memory__add-foot">
        <p v-if="error" class="memory__error" role="alert">{{ error }}</p>
        <button type="submit" class="memory__save iw-press" :disabled="!canAdd || saving">
          Save
        </button>
      </div>
    </form>

    <p v-if="!store.memoryLoaded" class="memory__loading">Loading memory…</p>

    <template v-else>
      <template v-for="group in groups" :key="group.key">
        <div v-if="group.items.length" class="memory__head">
          <span class="memory__head-label">{{ group.label }}</span>
          <span class="memory__head-count">{{ group.items.length }}</span>
          <span class="memory__head-rule"></span>
        </div>
        <ul v-if="group.items.length" class="memory__list">
          <li
            v-for="entry in group.items"
            :key="entry.id"
            :class="['memory__entry', entry.status === 'proposed' && 'memory__entry--proposed']"
          >
            <!-- Editing in place: the same two fields as the add form -->
            <form v-if="editingId === entry.id" class="memory__edit" @submit.prevent="saveEdit(entry.id)">
              <input v-model="editKey" class="memory__field" aria-label="Topic" maxlength="80" />
              <textarea
                v-model="editValue"
                class="memory__field memory__field--value"
                rows="3"
                aria-label="What every thread should know"
                maxlength="1000"
              ></textarea>
              <div class="memory__add-foot">
                <button type="button" class="memory__quiet iw-press" @click="editingId = null">Cancel</button>
                <button type="submit" class="memory__save iw-press" :disabled="!editKey.trim() || !editValue.trim() || saving">
                  Save
                </button>
              </div>
            </form>
            <template v-else>
              <div class="memory__entry-top">
                <p class="memory__key">{{ entry.key }}</p>
                <div class="memory__actions">
                  <button type="button" class="memory__icon iw-press" :aria-label="`Edit ${entry.key}`" title="Edit" @click="startEdit(entry)">
                    <i class="fas fa-pen" aria-hidden="true"></i>
                  </button>
                  <button type="button" class="memory__icon iw-press" :aria-label="`Remove ${entry.key}`" title="Remove" @click="remove(entry.id)">
                    <i class="fas fa-xmark" aria-hidden="true"></i>
                  </button>
                </div>
              </div>
              <p class="memory__value">{{ entry.value }}</p>
              <p class="memory__by">{{ byline(entry) }}</p>
            </template>
          </li>
        </ul>
      </template>

      <div v-if="store.memoryEntries.length === 0" class="memory__empty">
        <p class="memory__empty-title">Nothing saved yet</p>
        <p class="memory__empty-body">
          As threads finish, the decisions later work should follow are kept
          here, so every new thread starts knowing them.
        </p>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useAgentStore } from '../../../stores/agentStore'
import type { ProjectMemoryEntry } from '../../../types/services'

const store = useAgentStore()

const draftKey = ref('')
const draftValue = ref('')
const saving = ref(false)
const error = ref('')
const editingId = ref<number | null>(null)
const editKey = ref('')
const editValue = ref('')

onMounted(() => { void store.loadMemory() })

const canAdd = computed(() => !!draftKey.value.trim() && !!draftValue.value.trim())

const groups = computed(() => [
  {
    key: 'active',
    label: 'Saved',
    items: store.memoryEntries.filter(e => e.status === 'active'),
  },
  {
    key: 'proposed',
    label: 'Saves when its thread lands',
    items: store.memoryEntries.filter(e => e.status === 'proposed'),
  },
])

/** Who put it here, in a few words. */
function byline(entry: ProjectMemoryEntry): string {
  const thread = entry.source?.title
  if (entry.status === 'proposed') return thread ? `From ${thread}` : 'From a thread'
  if (entry.author === 'user') return 'Saved by you'
  if (entry.author === 'thread') return thread ? `From ${thread}` : 'From a thread'
  return 'Saved by the coordinator'
}

function failed(e: unknown) {
  const detail = (e as any)?.response?.data?.error
  error.value = typeof detail === 'string' ? detail : 'That did not save. Try again.'
}

async function add() {
  if (!canAdd.value || saving.value) return
  saving.value = true
  error.value = ''
  try {
    await store.addMemory(draftKey.value.trim(), draftValue.value.trim())
    draftKey.value = ''
    draftValue.value = ''
  } catch (e) {
    failed(e)
  } finally {
    saving.value = false
  }
}

function startEdit(entry: ProjectMemoryEntry) {
  editingId.value = entry.id
  editKey.value = entry.key
  editValue.value = entry.value
}

async function saveEdit(entryId: number) {
  saving.value = true
  error.value = ''
  try {
    await store.editMemory(entryId, editKey.value.trim(), editValue.value.trim())
    editingId.value = null
  } catch (e) {
    failed(e)
  } finally {
    saving.value = false
  }
}

async function remove(entryId: number) {
  error.value = ''
  try {
    await store.removeMemory(entryId)
  } catch (e) {
    failed(e)
  }
}
</script>

<style scoped>
.memory {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
  padding: 0.75rem 0.625rem 1rem;
}

.memory__lede {
  padding: 0 0.125rem;
  font-size: 0.75rem;
  line-height: 1.5;
  color: var(--sl-muted);
}

/* ── Fields: one border that deepens on hover and focus, never a ring ──── */

.memory__add,
.memory__edit {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.memory__field {
  width: 100%;
  padding: 0.4375rem 0.625rem;
  border: 1px solid var(--sl-line);
  border-radius: 0.625rem;
  background: var(--sl-card-bg);
  color: var(--sl-text);
  font-size: 0.8125rem;
  line-height: 1.45;
  outline: none;
  transition: border-color var(--iw-dur-2) var(--iw-ease-out);
}

.memory__field::placeholder {
  color: var(--sl-placeholder, var(--sl-muted));
}

.memory__field:hover {
  border-color: var(--sl-line-strong);
}

.memory__field:focus {
  border-color: color-mix(in srgb, var(--sl-text) 45%, transparent);
}

.memory__field--value {
  resize: vertical;
  min-height: 2.75rem;
}

.memory__add-foot {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
}

.memory__error {
  flex: 1;
  font-size: 0.6875rem;
  color: var(--sl-bad);
}

/* The view's one lit button. */
.memory__save {
  padding: 0.3125rem 0.875rem;
  border-radius: 9999px;
  background: var(--sl-grad);
  color: var(--sl-on-accent);
  font-size: 0.75rem;
  font-weight: 600;
  box-shadow: var(--sl-btn-shadow);
}

.memory__save:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.memory__quiet {
  padding: 0.3125rem 0.75rem;
  border-radius: 9999px;
  border: 1px solid var(--sl-line);
  color: var(--sl-muted);
  font-size: 0.75rem;
  font-weight: 600;
}

.memory__save:focus-visible,
.memory__quiet:focus-visible,
.memory__icon:focus-visible {
  outline: 2px solid var(--sl-focus);
  outline-offset: 3px;
}

/* ── Groups ───────────────────────────────────────────────────────────── */

.memory__head {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.25rem 0;
}

.memory__head-label {
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.09em;
  color: var(--sl-muted);
}

.memory__head-count {
  font-size: 0.5625rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  padding: 0 0.25rem;
  border-radius: 0.25rem;
  background: var(--sl-chip-bg);
  color: var(--sl-muted);
  line-height: 0.9375rem;
}

.memory__head-rule {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, var(--sl-line-strong) 0%, transparent 100%);
}

.memory__list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

/* ── An entry ─────────────────────────────────────────────────────────── */

.memory__entry {
  padding: 0.5rem 0.625rem 0.5625rem;
  border: 1px solid var(--sl-line);
  border-radius: 0.75rem;
  background: var(--sl-card-bg);
  transition: border-color var(--iw-dur-2) var(--iw-ease-out);
}

.memory__entry:hover {
  border-color: var(--sl-line-strong);
}

/* Not saved yet: drawn but not filled, like a thread that has not started. */
.memory__entry--proposed {
  border-style: dashed;
  background: var(--sl-chip-bg);
}

.memory__entry-top {
  display: flex;
  align-items: flex-start;
  gap: 0.375rem;
}

.memory__key {
  flex: 1;
  min-width: 0;
  font-family: var(--sl-font-display, theme('fontFamily.display'));
  font-size: 0.8125rem;
  font-weight: 600;
  line-height: 1.35;
  color: var(--sl-text);
  overflow-wrap: anywhere;
}

.memory__value {
  margin-top: 0.125rem;
  font-size: 0.75rem;
  line-height: 1.5;
  color: var(--sl-muted);
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.memory__by {
  margin-top: 0.3125rem;
  font-size: 0.625rem;
  color: var(--sl-muted);
}

/* Quiet until the row is hovered or focused within. */
.memory__actions {
  display: flex;
  gap: 0.125rem;
  opacity: 0;
  transition: opacity var(--iw-dur-2) var(--iw-ease-out);
}

.memory__entry:hover .memory__actions,
.memory__entry:focus-within .memory__actions {
  opacity: 1;
}

@media (hover: none) {
  .memory__actions {
    opacity: 1;
  }
}

.memory__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.375rem;
  height: 1.375rem;
  border-radius: 9999px;
  font-size: 0.5625rem;
  color: var(--sl-muted);
  transition: background-color var(--iw-dur-2) var(--iw-ease-out), color var(--iw-dur-2) var(--iw-ease-out);
}

.memory__icon:hover {
  background: var(--sl-chip-bg-hover, var(--sl-chip-bg));
  color: var(--sl-text);
}

.memory__loading {
  padding: 0.5rem 0.25rem;
  font-size: 0.6875rem;
  color: var(--sl-muted);
}

.memory__empty {
  margin-top: 0.25rem;
  padding: 1rem 0.875rem 1.125rem;
  border: 1px dashed var(--sl-line-strong);
  border-radius: 0.875rem;
  text-align: center;
}

.memory__empty-title {
  font-family: var(--sl-font-display, theme('fontFamily.display'));
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--sl-text);
}

.memory__empty-body {
  margin-top: 0.25rem;
  font-size: 0.6875rem;
  line-height: 1.45;
  color: var(--sl-muted);
}
</style>
