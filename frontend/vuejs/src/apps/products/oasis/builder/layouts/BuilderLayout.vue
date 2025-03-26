<template>
  <DashboardLayout :storage-key="storageKey" :navigation-items="navigationItems">
    <template #sidebar-content="{ isSidebarCollapsed }">
      <slot name="sidebar-content" :collapsed="isSidebarCollapsed"></slot>
    </template>
    
    <!-- Pass through any navbar-right content from parent -->
    <template #navbar-right>
      <slot name="navbar-right"></slot>
    </template>

    <div class="flex flex-col h-full w-full">
      <slot></slot>
    </div>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { DashboardLayout } from '@/shared/layouts'

// Define NavigationItem type inline since it's not exported
interface NavigationItem {
  name: string
  to: string
  icon?: string
  exact?: boolean
  children?: NavigationItem[]
}

defineProps({
  storageKey: {
    type: String,
    default: undefined
  },
  navigationItems: {
    type: Array as () => NavigationItem[],
    default: () => []
  }
})
</script>
