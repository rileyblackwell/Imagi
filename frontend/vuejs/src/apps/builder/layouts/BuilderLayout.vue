<template>
  <DashboardLayout :storage-key="storageKey" :navigation-items="[]">
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

defineProps<{
  storageKey?: string
}>()
</script>
