<template>
  <div class="max-w-4xl mx-auto">
    <DocsPageHeader 
      :title="title" 
      :description="description" 
      :badge-text="badgeText" 
    />
    
    <DocsDivider v-if="useDivider" />
    
    <div class="prose prose-invert prose-lg max-w-none">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import DocsPageHeader from '../molecules/DocsPageHeader.vue';
import DocsDivider from '../atoms/DocsDivider.vue';

withDefaults(defineProps<{
  title: string;
  description: string;
  badgeText?: string;
  useDivider?: boolean;
}>(), {
  badgeText: 'DOCUMENTATION',
  useDivider: true
});
</script>

<style scoped>
/* Override Tailwind prose styling for lists */
:deep(.prose ul) {
  list-style-type: none;
  padding-left: 0;
}

:deep(.prose ol) {
  padding-left: 1.75rem;
}
</style> 