<template>
  <DashboardLayout :navigation-items="builderNavigationItems" :storage-key="storageKey">
    <!-- Pass through all slots -->
    <template v-for="(_, name) in $slots" v-slot:[name]="slotData">
      <slot :name="name" v-bind="slotData"></slot>
    </template>
  </DashboardLayout>
</template>

<script setup>
import { DashboardLayout } from '@/shared/layouts';

// Common builder navigation items
const builderNavigationItems = [
  { 
    name: 'Projects', 
    to: '/builder/dashboard', 
    icon: 'fas fa-folder',
    exact: true
  },
  { 
    name: 'Settings', 
    to: '/builder/settings', 
    icon: 'fas fa-cog'
  }
];

// Props
defineProps({
  storageKey: {
    type: String,
    default: 'builderSidebarCollapsed'
  }
});
</script>
