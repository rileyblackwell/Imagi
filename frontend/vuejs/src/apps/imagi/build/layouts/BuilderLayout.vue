<template>
  <DashboardLayout
    :storage-key="storageKey"
    aside-width-class="w-[22rem] max-md:w-full"
    content-offset-class="md:ml-[22rem]"
    app-shell
    hide-toggle-on-mobile
  >
    <template #sidebar-content="{ isSidebarCollapsed, toggleSidebar, setSidebarCollapsed }">
      <slot
        name="sidebar-content"
        :collapsed="isSidebarCollapsed"
        :toggle-sidebar="toggleSidebar"
        :set-sidebar-collapsed="setSidebarCollapsed"
      ></slot>
    </template>

    <template #default="{ isSidebarCollapsed, setSidebarCollapsed }">
      <div class="flex flex-col h-full w-full">
        <slot
          :isSidebarCollapsed="isSidebarCollapsed"
          :setSidebarCollapsed="setSidebarCollapsed"
        ></slot>
      </div>
    </template>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { DashboardLayout } from '@/shared/layouts'

defineProps({
  storageKey: {
    type: String,
    default: undefined
  }
})
</script>
