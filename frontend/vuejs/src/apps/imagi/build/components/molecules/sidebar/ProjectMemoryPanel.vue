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
  <div class="flex flex-col gap-2.5 pt-3 px-2.5 pb-4">
    <div class="flex items-start gap-3">
      <p class="flex-1 px-0.5 text-[0.75rem] leading-[1.5] text-sl-muted">
        What the coordinator and every thread know about your app. It saves
        what matters from your chats and finished threads on its own, and you
        can change anything here.
      </p>
      <button
        v-if="!editing && memory"
        type="button"
        :class="QUIET_BTN"
        @click="startEdit"
      >
        <i class="fas fa-pen text-[0.5625rem]" aria-hidden="true"></i>
        Edit
      </button>
    </div>

    <p v-if="!memory" class="py-2 px-1 text-[0.6875rem] text-sl-muted">Loading memory…</p>

    <!-- Editing: the whole document as plain markdown. One border that
         deepens on hover and focus, never a ring — a text field takes no
         focus ring, whatever the page's :focus-visible says. -->
    <form v-else-if="editing" class="flex flex-col gap-1.5" @submit.prevent="save">
      <textarea
        ref="editor"
        v-model="draft"
        class="w-full min-h-[22rem] py-2.5 px-3 border border-sl-line rounded-[0.625rem] bg-transparent bg-sl-card-bg text-sl-text text-[0.8125rem] leading-[1.55] resize-y
          ![outline:none] [transition:border-color_var(--iw-dur-2)_var(--iw-ease-out)] motion-reduce:[transition:none]
          hover:border-sl-line-strong focus:border-[color:color-mix(in_srgb,var(--sl-text)_45%,transparent)]"
        aria-label="Project memory"
        spellcheck="true"
        @keydown.meta.enter.prevent="save"
        @keydown.ctrl.enter.prevent="save"
      ></textarea>
      <p class="flex flex-wrap justify-between gap-y-1 gap-x-3 px-0.5 text-[0.6875rem] text-sl-muted">
        <span>One fact per line, under its <code class="text-[0.625rem] px-[0.1875rem] rounded bg-sl-chip-bg">##</code> section.</span>
        <span :class="draft.length > memory.max_chars && 'text-sl-wait'">
          {{ draft.length.toLocaleString() }} / {{ memory.max_chars.toLocaleString() }} characters
        </span>
      </p>
      <div class="flex items-center justify-end gap-2">
        <p v-if="error" class="flex-1 text-[0.6875rem] text-sl-bad" role="alert">{{ error }}</p>
        <button type="button" :class="QUIET_BTN" @click="cancelEdit">Cancel</button>
        <!-- The view's one lit button. -->
        <button
          type="submit"
          :class="['iw-press py-[0.3125rem] px-3.5 rounded-full bg-sl-grad text-sl-on-accent text-[0.75rem] font-semibold [box-shadow:var(--sl-btn-shadow)] disabled:opacity-50 disabled:cursor-not-allowed', FOCUS]"
          :disabled="saving"
        >Save</button>
      </div>
    </form>

    <!-- Reading: the document by section -->
    <template v-else>
      <p
        v-for="(line, i) in doc.preamble"
        :key="`p${i}`"
        :class="[LINE, 'pl-1.5 text-sl-muted before:bg-sl-line-strong before:hidden']"
        v-html="inline(line)"
      ></p>

      <section v-for="section in doc.sections" :key="section.title" class="flex flex-col gap-1">
        <div :class="[HEAD, 'pt-2']">
          <span :class="HEAD_LABEL">{{ section.title }}</span>
          <span
            v-if="section.lines.length"
            class="text-[0.5625rem] font-semibold tabular-nums px-1 rounded bg-sl-chip-bg text-sl-muted leading-[0.9375rem]"
          >{{ section.lines.length }}</span>
          <span :class="HEAD_RULE"></span>
        </div>
        <ul v-if="section.lines.length" class="flex flex-col">
          <!-- A fact: a diamond tick, then the line. Saved since the user
               last looked: the info tone, quietly. -->
          <li
            v-for="(line, i) in section.lines"
            :key="i"
            :class="[
              LINE, 'pl-[1.125rem] text-sl-text',
              isNew(line) ? 'bg-[color:color-mix(in_srgb,var(--sl-cool)_9%,transparent)] before:bg-sl-cool' : 'before:bg-sl-line-strong'
            ]"
            v-html="inline(line)"
          ></li>
        </ul>
        <p v-else class="pt-0.5 px-1.5 pb-1 text-[0.6875rem] text-sl-faint">Nothing yet</p>
      </section>

      <div
        v-if="lineCount === 0"
        class="mt-1 pt-4 px-3.5 pb-[1.125rem] border border-dashed border-sl-line-strong rounded-[0.875rem] text-center"
      >
        <p class="font-sl-display text-[0.8125rem] font-semibold text-sl-text">Nothing saved yet</p>
        <p class="mt-1 text-[0.6875rem] leading-[1.45] text-sl-muted">
          As you chat with the coordinator and threads finish, what later work
          should know is saved here, so every new thread starts knowing it.
        </p>
      </div>
    </template>

    <!-- Threads' notes: saved when each thread's work lands. Not saved yet:
         drawn but not filled, like a thread that has not started. -->
    <template v-if="memory && memory.pending.length">
      <div :class="[HEAD, 'pt-2']">
        <span :class="HEAD_LABEL">Saves when its thread lands</span>
        <span :class="HEAD_RULE"></span>
      </div>
      <ul class="flex flex-col gap-1">
        <li v-for="item in memory.pending" :key="item.thread.id" :class="[CHANGE, 'border-dashed bg-sl-chip-bg']">
          <p :class="BYLINE">{{ item.thread.title || 'A thread' }}</p>
          <p v-for="(note, i) in item.notes" :key="i" :class="[DIFF, 'text-sl-text']">
            <span :class="[DIFF_MARK, 'text-sl-ok']" aria-hidden="true">+</span><span>{{ note.text }}</span>
          </p>
        </li>
      </ul>
    </template>

    <!-- Where each line came from, newest first, each one undoable -->
    <template v-if="memory && memory.changes.length && !editing">
      <div :class="[HEAD, 'pt-4']">
        <span :class="HEAD_LABEL">Recent changes</span>
        <span :class="HEAD_RULE"></span>
      </div>
      <ul class="flex flex-col gap-1">
        <li
          v-for="change in memory.changes"
          :key="change.id"
          :class="[CHANGE, 'bg-sl-card-bg', change.undone && 'opacity-60']"
        >
          <div class="flex items-center gap-2">
            <p :class="BYLINE">
              {{ changeByline(change) }}
              <span class="font-normal text-sl-muted">· {{ timeAgo(change.created_at) }}</span>
            </p>
            <span v-if="change.undone" class="shrink-0 text-[0.625rem] text-sl-faint">Undone</span>
            <button
              v-else
              type="button"
              :class="[
                'iw-press shrink-0 text-[0.6875rem] font-semibold text-sl-muted rounded-full hover:text-sl-text disabled:opacity-50 disabled:cursor-not-allowed',
                '[transition:color_var(--iw-dur-2)_var(--iw-ease-out)] motion-reduce:[transition:none]',
                FOCUS
              ]"
              :disabled="undoing === change.id"
              @click="undo(change.id)"
            >
              Undo
            </button>
          </div>
          <p
            v-for="(line, i) in change.lines"
            :key="i"
            :class="[DIFF, line.op === 'remove' ? 'text-sl-muted' : 'text-sl-text']"
          >
            <span :class="[DIFF_MARK, line.op === 'add' ? 'text-sl-ok' : 'text-sl-muted']" aria-hidden="true">{{ line.op === 'add' ? '+' : '−' }}</span>
            <span
              :class="line.op === 'remove'
                ? 'line-through decoration-[color:color-mix(in_srgb,var(--sl-muted)_60%,transparent)]'
                : change.undone && 'line-through'"
            >{{ line.text }}</span>
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

/* Spotlight's own ring, stated at the call site. */
const FOCUS = 'focus-visible:[outline:2px_solid_var(--sl-focus)] focus-visible:[outline-offset:3px]'

const QUIET_BTN = [
  'iw-press inline-flex items-center gap-1.5 shrink-0 py-[0.3125rem] px-3 rounded-full border border-sl-line',
  'text-sl-muted text-[0.75rem] font-semibold hover:border-sl-line-strong hover:text-sl-text',
  '[transition:border-color_var(--iw-dur-2)_var(--iw-ease-out),color_var(--iw-dur-2)_var(--iw-ease-out)] motion-reduce:[transition:none]',
  FOCUS,
]

/* Section heads: the workspace's label convention — label, count, then a
   hairline running to the edge. */
const HEAD = 'flex items-center gap-1.5 px-1 pb-0'
const HEAD_LABEL = 'text-[0.625rem] font-semibold uppercase tracking-[0.09em] text-sl-muted'
const HEAD_RULE = 'flex-1 h-px bg-[linear-gradient(90deg,var(--sl-line-strong)_0%,transparent_100%)]'

/* One line of the document, with its diamond tick (::before) and the inline
   markdown it may carry (v-html). */
const LINE = [
  'relative py-1 pr-1.5 rounded-lg text-[0.78125rem] leading-[1.5] [overflow-wrap:anywhere]',
  '[transition:background-color_var(--iw-dur-3)_var(--iw-ease-out)] motion-reduce:[transition:none]',
  "before:content-[''] before:absolute before:left-[0.4375rem] before:top-[0.6875rem] before:w-[0.3125rem] before:h-[0.3125rem] before:[transform:rotate(45deg)]",
  '[&_code]:text-[0.6875rem] [&_code]:px-[0.1875rem] [&_code]:rounded [&_code]:bg-sl-chip-bg [&_a]:underline [&_a]:underline-offset-2',
]

/* Pending notes and recent changes */
const CHANGE = 'pt-[0.4375rem] px-2.5 pb-2 border border-sl-line rounded-xl'
const BYLINE = 'flex-1 min-w-0 truncate text-[0.6875rem] font-semibold text-sl-text'
const DIFF = 'flex gap-1.5 mt-[0.1875rem] text-[0.71875rem] leading-[1.45] [overflow-wrap:anywhere]'
const DIFF_MARK = 'shrink-0 w-2 font-semibold'

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
