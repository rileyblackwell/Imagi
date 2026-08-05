<!--
  ProjectCard.vue — one project in the list.

  A ruled row rather than a floating card: on the editorial surface the library
  reads as a single list of businesses, and a stack of bordered slabs would sit
  on the paper instead of in it.

  The row is a wrapper rather than one big link, because it holds two actions.
  The link stretches over the whole row with a pseudo-element, and the delete
  button sits above it — which keeps the whole row clickable without nesting a
  <button> inside an <a>.
-->
<template>
  <div v-if="project" class="row group">
    <router-link
      :to="{ name: 'project-hub', params: { projectName: projectSlug(project) }}"
      class="row__link"
      :title="`Open ${project.name}`"
    >
      <span class="row__name">{{ project.name }}</span>
      <span v-if="project.description" class="row__desc">{{ project.description }}</span>
    </router-link>

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
import type { Project } from '@/apps/imagi/build/types/components'
import { projectSlug } from '@/apps/imagi/build/utils/slug'

const props = defineProps<{
  project?: Project;
}>();

const emit = defineEmits<{
  (e: 'delete', project: Project): void;
}>();

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
  gap: 0.75rem;
  padding: 1.05rem 0.25rem 1.05rem 0;
  border-bottom: 1px solid var(--rule);
  transition: border-color 0.18s ease;
}

.row:hover {
  border-bottom-color: var(--rule-strong);
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
  font-size: 1rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.row__desc {
  display: block;
  margin-top: 0.2rem;
  font-size: 0.8125rem;
  line-height: 1.5;
  color: var(--ink-40);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  border-radius: 0.375rem;
  color: var(--ink-40);
  opacity: 0;
  transition: opacity 0.18s ease, color 0.18s ease;
}

.row:hover .row__delete,
.row__delete:focus-visible {
  opacity: 1;
}

.row__delete:hover {
  color: var(--accent);
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
  color: var(--ink);
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
