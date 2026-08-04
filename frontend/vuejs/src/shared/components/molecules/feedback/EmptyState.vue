<!--
  EmptyState.vue — "there is nothing here yet", once.

  Eight views wrote out the same block: a card, a 14×14 accent icon tile, an
  18px heading, a muted paragraph on a narrow measure, and usually a primary
  button offering the thing that would fill it. The prose is different every
  time and the shape never was.

  The icon tile carries the workspace's accent, so the caller passes the accent
  it is standing in rather than a colour.
-->
<template>
  <div class="py-16 text-center" :class="ui.card">
    <div class="w-14 h-14 mx-auto mb-4 text-xl" :class="accentUi(accent).iconTile">
      <i :class="icon"></i>
    </div>

    <h3 class="mb-2" :class="ui.headingText">{{ title }}</h3>

    <p v-if="description" class="max-w-md mx-auto" :class="[ui.bodyText, $slots.action ? 'mb-6' : '']">
      {{ description }}
    </p>

    <!-- The action that would make this state go away — "Add your first
         product", "Create a campaign". Optional: a list that is empty because
         of a filter has nothing to offer. -->
    <slot name="action"></slot>
  </div>
</template>

<script setup lang="ts">
import { ui, accentUi, type ToolAccent } from '@/shared/styles'

defineProps<{
  /** Font Awesome classes, e.g. `fas fa-box-open`. */
  icon: string
  title: string
  description?: string
  /** The workspace's identity colour, for the icon tile. */
  accent: ToolAccent
}>()
</script>
