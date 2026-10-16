<!--
  ProjectMemoryPanel.vue — the project's shared memory, as the user sees it.

  One short document that the coordinator and every thread read before they
  work: what the app is, what the user decided, how it's built and how they
  like to work. It keeps itself current (after each coordinator turn, and as
  each thread's work lands, a small model saves what later work should know),
  so this view is for reading it, correcting it and seeing where a line came
  from: the document by section, an Edit mode that is the plain markdown,
  threads' notes still waiting for their work to land, and recent changes,
  each with Undo.

  It lives in the threads pane, opened from its header, because it belongs
  to the threads: it is the one thing they all share.
-->
<template>
  <div class="memory">
    <div class="memory__top">
      <p class="memory__lede">
        What the coordinator and every thread know about your app. It saves
        what matters from your chats and finished threads on its own, and you
        can change anything here.
      </p>
      <button
        v-if="!editing && memory"
        type="button"
        class="memory__quiet iw-press"
        @click="startEdit"
      >
        <i class="fas fa-pen" aria-hidden="true"></i>
        Edit
      </button>
    </div>

    <p v-if="!memory" class="memory__loading">Loading memory…</p>

    <!-- Editing: the whole document as plain markdown -->
    <form v-else-if="editing" class="memory__edit" @submit.prevent="save">
      <textarea
        ref="editor"
        v-model="draft"
        class="memory__field"
        aria-label="Project memory"
        spellcheck="true"
        @keydown.meta.enter.prevent="save"
        @keydown.ctrl.enter.prevent="save"
      ></textarea>
      <p class="memory__hint">
        <span>One fact per line, under its <code>##</code> section.</span>
        <span :class="draft.length > memory.max_chars && 'memory__hint--over'">
          {{ draft.length.toLocaleString() }} / {{ memory.max_chars.toLocaleString() }} characters
        </span>
      </p>
      <div class="memory__foot">
        <p v-if="error" class="memory__error" role="alert">{{ error }}</p>
        <button type="button" class="memory__quiet iw-press" @click="cancelEdit">Cancel</button>
        <button type="submit" class="memory__save iw-press" :disabled="saving">Save</button>
      </div>
    </form>

    <!-- Reading: the document by section -->
    <template v-else>
      <p v-for="(line, i) in doc.preamble" :key="`p${i}`" class="memory__line memory__line--plain" v-html="inline(line)"></p>

      <section v-for="section in doc.sections" :key="section.title" class="memory__section">
        <div class="memory__head">
          <span class="memory__head-label">{{ section.title }}</span>
          <span v-if="section.lines.length" class="memory__head-count">{{ section.lines.length }}</span>
          <span class="memory__head-rule"></span>
        </div>
        <ul v-if="section.lines.length" class="memory__lines">
          <li
            v-for="(line, i) in section.lines"
            :key="i"
            :class="['memory__line', isNew(line) && 'memory__line--new']"
            v-html="inline(line)"
          ></li>
        </ul>
        <p v-else class="memory__none">Nothing yet</p>
      </section>

      <div v-if="lineCount === 0" class="memory__empty">
        <p class="memory__empty-title">Nothing saved yet</p>
        <p class="memory__empty-body">
          As you chat with the coordinator and threads finish, what later work
          should know is saved here, so every new thread starts knowing it.
        </p>
      </div>
    </template>

    <!-- Threads' notes: saved when each thread's work lands -->
    <template v-if="memory && memory.pending.length">
      <div class="memory__head">
        <span class="memory__head-label">Saves when its thread lands</span>
        <span class="memory__head-rule"></span>
      </div>
      <ul class="memory__changes">
        <li v-for="item in memory.pending" :key="item.thread.id" class="memory__change memory__change--pending">
          <p class="memory__by">{{ item.thread.title || 'A thread' }}</p>
          <p v-for="(note, i) in item.notes" :key="i" class="memory__diff memory__diff--add">
            <span class="memory__diff-mark" aria-hidden="true">+</span><span>{{ note.text }}</span>
          </p>
        </li>
      </ul>
    </template>

    <!-- Where each line came from, newest first, each one undoable -->
    <template v-if="memory && memory.changes.length && !editing">
      <div class="memory__head memory__head--changes">
        <span class="memory__head-label">Recent changes</span>
        <span class="memory__head-rule"></span>
      </div>
      <ul class="memory__changes">
        <li
          v-for="change in memory.changes"
          :key="change.id"
          :class="['memory__change', change.undone && 'memory__change--undone']"
        >
          <div class="memory__change-top">
            <p class="memory__by">
              {{ changeByline(change) }}
              <span class="memory__when">· {{ timeAgo(change.created_at) }}</span>
            </p>
            <span v-if="change.undone" class="memory__undone">Undone</span>
            <button
              v-else
              type="button"
              class="memory__undo iw-press"
              :disabled="undoing === change.id"
              @click="undo(change.id)"
            >
              Undo
            </button>
          </div>
          <p
            v-for="(line, i) in change.lines"
            :key="i"
            :class="['memory__diff', `memory__diff--${line.op}`]"
          >
            <span class="memory__diff-mark" aria-hidden="true">{{ line.op === 'add' ? '+' : '−' }}</span>
            <span class="memory__diff-text">{{ line.text }}</span>
          </p>
        </li>
      </ul>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'isomorphic-dompurify'
import { useAgentStore } from '../../../stores/agentStore'
import { changeByline, memoryLineCount, parseMemory, timeAgo } from '../../../utils/projectMemory'

const store = useAgentStore()

const editing = ref(false)
const draft = ref('')
const base = ref<{ version: number; content: string } | null>(null)
const saving = ref(false)
const undoing = ref<number | null>(null)
const error = ref('')
const editor = ref<HTMLTextAreaElement | null>(null)

// What the user had seen before opening: lines saved since then are marked.
const seenAtOpen = store.memorySeenVersion

onMounted(() => store.setMemoryViewing(true))
onBeforeUnmount(() => store.setMemoryViewing(false))

const memory = computed(() => store.memory)
const doc = computed(() => parseMemory(memory.value?.content ?? ''))
const lineCount = computed(() => memoryLineCount(memory.value?.content ?? ''))

/** Lines added by changes the user had not seen when they opened the view. */
const newLines = computed(() => {
  const m = memory.value
  // A first look marks nothing: all of it is new.
  if (!m || !seenAtOpen || seenAtOpen >= m.version) return new Set<string>()
  // Each write bumps the version once, so the newest (version - seen)
  // changes are the ones saved since.
  const lines = m.changes
    .slice(0, m.version - seenAtOpen)
    .filter(c => !c.undone && c.author !== 'user')
    .flatMap(c => c.lines.filter(l => l.op === 'add').map(l => norm(l.text)))
  return new Set(lines)
})

function norm(text: string): string {
  return text.split(/\s+/).join(' ').trim().toLowerCase().replace(/\.$/, '')
}

function isNew(line: string): boolean {
  return newLines.value.has(norm(line))
}

/** A line's own emphasis and links, nothing else. */
function inline(text: string): string {
  return DOMPurify.sanitize(marked.parseInline(text) as string, {
    ALLOWED_TAGS: ['strong', 'em', 'code', 'a', 'del'],
    ALLOWED_ATTR: ['href'],
  })
}

function failed(e: unknown, fallback: string) {
  const detail = (e as any)?.response?.data?.error
  error.value = typeof detail === 'string' && detail !== 'changed' ? detail : fallback
}

async function startEdit() {
  if (!memory.value) return
  base.value = { version: memory.value.version, content: memory.value.content }
  draft.value = memory.value.content
  error.value = ''
  editing.value = true
  await nextTick()
  // From the top, not wherever focusing would scroll it.
  editor.value?.focus({ preventScroll: true })
  editor.value?.setSelectionRange(0, 0)
  if (editor.value) editor.value.scrollTop = 0
}

function cancelEdit() {
  editing.value = false
  error.value = ''
}

async function save() {
  if (!base.value || saving.value) return
  saving.value = true
  error.value = ''
  try {
    await store.saveMemory(draft.value, base.value)
    editing.value = false
  } catch (e) {
    failed(e, 'That did not save. Try again.')
  } finally {
    saving.value = false
  }
}

async function undo(changeId: number) {
  undoing.value = changeId
  error.value = ''
  try {
    await store.undoMemoryChange(changeId)
  } catch (e) {
    failed(e, 'That did not undo. Try again.')
  } finally {
    undoing.value = null
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

.memory__top {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.memory__lede {
  flex: 1;
  padding: 0 0.125rem;
  font-size: 0.75rem;
  line-height: 1.5;
  color: var(--sl-muted);
}

/* ── Editing: one border that deepens on hover and focus, never a ring ── */

.memory__edit {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.memory__field {
  width: 100%;
  min-height: 22rem;
  padding: 0.625rem 0.75rem;
  border: 1px solid var(--sl-line);
  border-radius: 0.625rem;
  background: var(--sl-card-bg);
  color: var(--sl-text);
  font-size: 0.8125rem;
  line-height: 1.55;
  outline: none;
  resize: vertical;
  transition: border-color var(--iw-dur-2) var(--iw-ease-out);
}

.memory__field:hover {
  border-color: var(--sl-line-strong);
}

.memory__field:focus {
  border-color: color-mix(in srgb, var(--sl-text) 45%, transparent);
}

/* A text field takes no focus ring, whatever the page's :focus-visible says. */
.memory__field:focus-visible {
  outline: none;
}

.memory__hint {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.25rem 0.75rem;
  padding: 0 0.125rem;
  font-size: 0.6875rem;
  color: var(--sl-muted);
}

.memory__hint code {
  font-size: 0.625rem;
  padding: 0 0.1875rem;
  border-radius: 0.25rem;
  background: var(--sl-chip-bg);
}

.memory__hint--over {
  color: var(--sl-wait);
}

.memory__foot {
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

.memory__save:disabled,
.memory__undo:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.memory__quiet {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  flex-shrink: 0;
  padding: 0.3125rem 0.75rem;
  border-radius: 9999px;
  border: 1px solid var(--sl-line);
  color: var(--sl-muted);
  font-size: 0.75rem;
  font-weight: 600;
  transition: border-color var(--iw-dur-2) var(--iw-ease-out), color var(--iw-dur-2) var(--iw-ease-out);
}

.memory__quiet i {
  font-size: 0.5625rem;
}

.memory__quiet:hover {
  border-color: var(--sl-line-strong);
  color: var(--sl-text);
}

.memory__save:focus-visible,
.memory__quiet:focus-visible,
.memory__undo:focus-visible {
  outline: 2px solid var(--sl-focus);
  outline-offset: 3px;
}

/* ── Sections ─────────────────────────────────────────────────────────── */

.memory__section {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.memory__head {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.25rem 0;
}

.memory__head--changes {
  padding-top: 1rem;
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

.memory__lines {
  display: flex;
  flex-direction: column;
}

/* A fact: a diamond tick, then the line. */
.memory__line {
  position: relative;
  padding: 0.25rem 0.375rem 0.25rem 1.125rem;
  border-radius: 0.5rem;
  font-size: 0.78125rem;
  line-height: 1.5;
  color: var(--sl-text);
  overflow-wrap: anywhere;
  transition: background-color var(--iw-dur-3) var(--iw-ease-out);
}

.memory__line::before {
  content: '';
  position: absolute;
  left: 0.4375rem;
  top: 0.6875rem;
  width: 0.3125rem;
  height: 0.3125rem;
  background: var(--sl-line-strong);
  transform: rotate(45deg);
}

.memory__line--plain::before {
  display: none;
}

.memory__line--plain {
  padding-left: 0.375rem;
  color: var(--sl-muted);
}

/* Saved since the user last looked: the info tone, quietly. */
.memory__line--new {
  background: color-mix(in srgb, var(--sl-cool) 9%, transparent);
}

.memory__line--new::before {
  background: var(--sl-cool);
}

.memory__line :deep(code) {
  font-size: 0.6875rem;
  padding: 0 0.1875rem;
  border-radius: 0.25rem;
  background: var(--sl-chip-bg);
}

.memory__line :deep(a) {
  text-decoration: underline;
  text-underline-offset: 2px;
}

.memory__none {
  padding: 0.125rem 0.375rem 0.25rem;
  font-size: 0.6875rem;
  color: var(--sl-faint);
}

/* ── Pending notes and recent changes ─────────────────────────────────── */

.memory__changes {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.memory__change {
  padding: 0.4375rem 0.625rem 0.5rem;
  border: 1px solid var(--sl-line);
  border-radius: 0.75rem;
  background: var(--sl-card-bg);
}

/* Not saved yet: drawn but not filled, like a thread that has not started. */
.memory__change--pending {
  border-style: dashed;
  background: var(--sl-chip-bg);
}

.memory__change--undone {
  opacity: 0.6;
}

.memory__change--undone .memory__diff-text {
  text-decoration: line-through;
}

.memory__change-top {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.memory__by {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--sl-text);
}

.memory__when {
  font-weight: 400;
  color: var(--sl-muted);
}

.memory__undo {
  flex-shrink: 0;
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--sl-muted);
  border-radius: 9999px;
  transition: color var(--iw-dur-2) var(--iw-ease-out);
}

.memory__undo:hover {
  color: var(--sl-text);
}

.memory__undone {
  flex-shrink: 0;
  font-size: 0.625rem;
  color: var(--sl-faint);
}

.memory__diff {
  display: flex;
  gap: 0.375rem;
  margin-top: 0.1875rem;
  font-size: 0.71875rem;
  line-height: 1.45;
  color: var(--sl-text);
  overflow-wrap: anywhere;
}

.memory__diff--remove {
  color: var(--sl-muted);
}

.memory__diff--remove .memory__diff-text {
  text-decoration: line-through;
  text-decoration-color: color-mix(in srgb, var(--sl-muted) 60%, transparent);
}

.memory__diff-mark {
  flex-shrink: 0;
  width: 0.5rem;
  font-weight: 600;
}

.memory__diff--add .memory__diff-mark {
  color: var(--sl-ok);
}

.memory__diff--remove .memory__diff-mark {
  color: var(--sl-muted);
}

/* ── Loading and empty ───────────────────────────────────────────────── */

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

@media (prefers-reduced-motion: reduce) {
  .memory__line,
  .memory__field,
  .memory__quiet,
  .memory__undo {
    transition: none;
  }
}
</style>
