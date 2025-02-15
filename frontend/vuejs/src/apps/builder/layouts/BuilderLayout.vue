<template>
  <DashboardLayout :storage-key="storageKey" :navigation-items="navigationItems">
    <template #sidebar-content="{ isSidebarCollapsed }">
      <slot name="sidebar-content" :collapsed="isSidebarCollapsed"></slot>
    </template>

    <template #default="{ isSidebarCollapsed }">
      <slot :collapsed="isSidebarCollapsed"></slot>
    </template>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { DashboardLayout } from '@/shared/layouts'

const navigationItems = [
  {
    name: 'Projects',
    to: '/builder/projects',
    icon: 'fas fa-folder',
  },
  {
    name: 'Chat',
    to: '/builder/chat',
    icon: 'fas fa-comments',
  },
  {
    name: 'Build',
    to: '/builder/build',
    icon: 'fas fa-hammer',
  },
  {
    name: 'Settings',
    to: '/builder/settings',
    icon: 'fas fa-cog',
  }
]

defineProps<{
  storageKey?: string
}>()
</script>
