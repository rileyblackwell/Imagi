<template>
  <DashboardLayout
    :storage-key="storageKey"
    :navigation-items="navigationItems"
    aside-width-class="w-[22rem] max-md:w-full"
    content-offset-class="md:ml-[22rem]"
    nav-offset-class="md:left-[22rem]"
    compact-top
    app-shell
    hide-toggle-on-mobile
  >
    <template #sidebar-content="{ isSidebarCollapsed, toggleSidebar }">
      <slot name="sidebar-content" :collapsed="isSidebarCollapsed" :toggle-sidebar="toggleSidebar"></slot>
    </template>

    <!-- Pass through any navbar content from parent, forwarding sidebar controls -->
    <template #navbar-left="slotProps">
      <slot name="navbar-left" v-bind="slotProps"></slot>
    </template>
    <template #navbar-center="slotProps">
      <slot name="navbar-center" v-bind="slotProps"></slot>
    </template>
    <template #navbar-right="slotProps">
      <slot name="navbar-right" v-bind="slotProps"></slot>
    </template>

    <template #default="{ isSidebarCollapsed }">
      <div class="flex flex-col h-full w-full">
        <slot :isSidebarCollapsed="isSidebarCollapsed"></slot>
      </div>
    </template>
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
