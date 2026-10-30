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
  <div
    v-if="project"
    class="row group relative flex items-center gap-4 border-b border-b-ed-rule py-5 pl-0 pr-1 [transition:border-color_0.18s_ease] hover:border-b-ed-rule-strong"
  >
    <span
      v-if="index"
      class="row__num w-10 flex-none font-[ui-monospace,SFMono-Regular,Menlo,monospace] text-[0.8rem] text-ed-ink-40 [transition:color_0.18s_ease] group-hover:text-sl-coral max-[640px]:hidden"
      aria-hidden="true"
    >{{ String(index).padStart(2, '0') }}</span>
    <!-- Stretched over the whole row (::after), so the name, the description
         and the space between them all open the project. -->
    <router-link
      :to="{ name: 'project-hub', params: { projectName: projectSlug(project) }}"
      class="row__link block min-w-0 flex-1 after:absolute after:inset-0 after:content-['']
        focus-visible:![outline:none] focus-visible:after:rounded-[0.25rem] focus-visible:after:outline-offset-2 focus-visible:after:[outline:2px_solid_var(--accent)]"
      :title="`Open ${project.name}`"
    >
      <!-- The name lights on hover, the same gradient as the page's accent words. -->
      <span
        class="row__name block overflow-hidden text-ellipsis whitespace-nowrap font-sl-display text-[1.3rem] font-[650] tracking-[-0.015em] text-ed-ink
          group-hover:bg-sl-grad group-hover:bg-clip-text group-hover:text-transparent"
      >{{ project.name }}</span>
      <span
        v-if="project.description"
        class="row__desc mt-[0.2rem] block overflow-hidden text-ellipsis whitespace-nowrap text-[0.875rem] leading-[1.5] text-ed-ink-55"
      >{{ project.description }}</span>
    </router-link>
    <span
      v-if="updated"
      class="row__when min-w-[7rem] flex-none whitespace-nowrap text-right text-[0.8rem] text-ed-ink-40 max-[640px]:hidden"
    >{{ updated }}</span>
    <!-- Quiet until the row is pointed at or tabbed to — deleting a business
         should never be the loudest thing in a list of them. Touch users never
         hover, so there it is always shown. -->
    <button
      type="button"
      class="row__delete relative z-[1] inline-flex h-8 w-8 flex-none items-center justify-center rounded-lg text-ed-ink-40 opacity-0
        [transition:opacity_0.18s_ease,color_0.18s_ease,background_0.18s_ease] hover:bg-sl-chip-bg-hover hover:text-ed-accent group-hover:opacity-100
        focus-visible:opacity-100 focus-visible:!outline-ed-accent focus-visible:!outline-offset-2 [@media(hover:none)]:opacity-100"
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
    <svg
      class="h-[1.1rem] w-[1.1rem] flex-none text-ed-ink-40 [transition:transform_0.18s_ease,color_0.18s_ease] group-hover:translate-x-[3px] group-hover:text-sl-amber motion-reduce:group-hover:transform-none"
      viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"
    >
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
