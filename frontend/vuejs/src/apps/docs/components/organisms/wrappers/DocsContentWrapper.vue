<template>
  <div class="max-w-5xl mx-auto">
    <DocsPageHeader 
      :title="title" 
      :description="description" 
      :badge-text="badgeText" 
    />
    
    <div class="prose prose-invert prose-lg max-w-none">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import DocsPageHeader from '../../molecules/headers/DocsPageHeader.vue';

withDefaults(defineProps<{
  title: string;
  description: string;
  badgeText?: string;
}>(), {
  badgeText: 'DOCUMENTATION'
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

/* Enhanced prose styling for better hierarchy */
:deep(.prose h2) {
  margin-top: 3rem;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.prose h3) {
  margin-top: 2rem;
  margin-bottom: 1rem;
}

:deep(.prose p) {
  margin-bottom: 1.5rem;
  line-height: 1.75;
}

:deep(.prose li) {
  margin-bottom: 0.5rem;
}
</style> 