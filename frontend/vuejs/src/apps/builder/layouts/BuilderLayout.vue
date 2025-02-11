<template>
  <DashboardLayout :navigation-items="navigationItems" :storage-key="storageKey">
    <!-- Pass through all slots -->
    <template v-for="(_, name) in $slots" v-slot:[name]="slotData">
      <slot :name="name" v-bind="slotData"></slot>
    </template>
  </DashboardLayout>
</template>

<script setup>
import { DashboardLayout } from '@/shared/layouts';

// Props
defineProps({
  storageKey: {
    type: String,
    default: 'builderSidebarCollapsed'
  },
  navigationItems: {
    type: Array,
    default: () => []
  }
});
</script>
