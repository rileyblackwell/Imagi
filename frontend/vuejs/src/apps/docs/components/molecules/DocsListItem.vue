<template>
  <li class="flex items-start">
    <DocsIconBadge 
      v-if="icon" 
      :icon="icon" 
      :color="color" 
      size="sm" 
    />
    <span>
      <slot></slot>
    </span>
  </li>
</template>

<script setup lang="ts">
import DocsIconBadge from '../atoms/DocsIconBadge.vue';

withDefaults(defineProps<{
  icon?: string;
  color?: string;
}>(), {
  color: 'primary'
});
</script>

<style scoped>
/* Override Tailwind prose styling for lists */
:deep(.prose li) {
  padding-left: 0;
  margin: 0;
}

:deep(.prose li::before) {
  display: none !important;
}
</style> 