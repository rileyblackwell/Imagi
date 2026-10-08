<!--
  ProjectCard.vue — one project in the list.

  A numbered ruled row rather than a floating card: the library reads as one
  list of businesses, most recently worked on first, and a stack of bordered
  slabs would sit on the page instead of in it.

  The row is a wrapper rather than one big link, because it holds two actions.
  The link stretches over the whole row with a pseudo-element, and the delete
  button sits above it — which keeps the whole row clickable without nesting a
  <button> inside an <a>.
-->
<template>
  <div v-if="project" class="row group">
    <span v-if="index" class="row__num" aria-hidden="true">{{ String(index).padStart(2, '0') }}</span>
    <router-link
      :to="{ name: 'project-hub', params: { projectName: projectSlug(project) }}"
      class="row__link"
      :title="`Open ${project.name}`"
    >
      <span class="row__name">{{ project.name }}</span>
      <span v-if="project.description" class="row__desc">{{ project.description }}</span>
    </router-link>
    <span v-if="updated" class="row__when">{{ updated }}</span>
    <button
      type="button"
      class="row__delete"
      :aria-label="`Delete ${project.name}`"
      @click="confirmDelete"
    >
      <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M3 6h18" />
        <path d="M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2" />
        <path d="M19 6v14a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V6" />
        <path d="M10 11v6M14 11v6" />
      </svg>
    </button>
    <svg class="row__arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <path d="M5 12h14M13 6l6 6-6 6" />
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Project } from '@/apps/imagi/build/types/components'
import { projectSlug } from '@/apps/imagi/build/utils/slug'
import { updatedLabel } from '../../../utils/updatedLabel'

const props = defineProps<{
  project?: Project;
  /** Position in the list, shown as 01, 02, … */
  index?: number;
}>();

const emit = defineEmits<{
  (e: 'delete', project: Project): void;
}>();

const updated = computed(() => updatedLabel(props.project?.updated_at))

function confirmDelete() {
  if (props.project) {
    emit('delete', props.project);
  }
}
</script>

<style scoped>
.row {
  position: relative;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 0.25rem 1.25rem 0;
  border-bottom: 1px solid var(--rule);
  transition: border-color 0.18s ease;
}

.row:hover {
  border-bottom-color: var(--rule-strong);
}

.row__num {
  flex: none;
  width: 2.5rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.8rem;
  color: var(--ink-40);
  transition: color 0.18s ease;
}

.row:hover .row__num {
  color: var(--sl-coral);
}

.row__link {
  min-width: 0;
  flex: 1;
  display: block;
}

/* Stretched over the whole row, so the name, the description and the space
   between them all open the project. */
.row__link::after {
  content: '';
  position: absolute;
  inset: 0;
}

.row__link:focus-visible {
  outline: none;
}

.row__link:focus-visible::after {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
  border-radius: 0.25rem;
}

.row__name {
  display: block;
  font-family: var(--sl-font-display);
  font-size: 1.3rem;
  font-weight: 650;
  letter-spacing: -0.015em;
  color: var(--ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* The name lights on hover, the same gradient as the page's accent words. */
.row:hover .row__name {
  background: var(--sl-grad);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.row__desc {
  display: block;
  margin-top: 0.2rem;
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--ink-55);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.row__when {
  flex: none;
  min-width: 7rem;
  text-align: right;
  font-size: 0.8rem;
  color: var(--ink-40);
  white-space: nowrap;
}

@media (max-width: 640px) {
  .row__num,
  .row__when {
    display: none;
  }
}

/* Quiet until the row is pointed at or tabbed to — deleting a business should
   never be the loudest thing in a list of them. */
.row__delete {
  position: relative;
  z-index: 1;
  flex: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 0.5rem;
  color: var(--ink-40);
  opacity: 0;
  transition: opacity 0.18s ease, color 0.18s ease, background 0.18s ease;
}

.row:hover .row__delete,
.row__delete:focus-visible {
  opacity: 1;
}

.row__delete:hover {
  color: var(--accent);
  background: var(--sl-chip-bg-hover);
}

.row__delete:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.row__arrow {
  flex: none;
  width: 1.1rem;
  height: 1.1rem;
  color: var(--ink-40);
  transition: transform 0.18s ease, color 0.18s ease;
}

.row:hover .row__arrow {
  color: var(--sl-amber);
  transform: translateX(3px);
}

/* Touch and keyboard users never hover, so the delete button has to be there
   without one. */
@media (hover: none) {
  .row__delete {
    opacity: 1;
  }
}

@media (prefers-reduced-motion: reduce) {
  .row:hover .row__arrow {
    transform: none;
  }
}
</style>
