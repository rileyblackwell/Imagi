<template>
  <DashboardLayout :storage-key="storageKey" :navigation-items="navigationItems">
    <template #sidebar-content="{ isSidebarCollapsed }">
      <slot name="sidebar-content" :collapsed="isSidebarCollapsed"></slot>
    </template>

    <div class="flex flex-col h-full w-full">
      <slot></slot>
    </div>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { DashboardLayout } from '@/shared/layouts'

defineProps<{
  storageKey?: string,
  navigationItems?: any[]
}>()
</script>
