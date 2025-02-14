<template>
  <div class="p-4 border-b border-dark-700">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold text-white truncate">{{ projectName }}</h2>
      <IconButton
        icon-class="fa-times"
        :to="{ name: 'builder-dashboard' }"
        title="Back to projects"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { IconButton } from '@/apps/builder/components/atoms';

defineProps<{
  projectName?: string;
}>();
</script>
