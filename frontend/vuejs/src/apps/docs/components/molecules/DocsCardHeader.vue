<template>
  <h3 :class="[`text-${color}-400 mt-0 flex items-center`]">
    <template v-if="useIconBadge">
      <div :class="[`w-8 h-8 bg-${color}-500/20 rounded-full flex items-center justify-center mr-3`]">
        <i :class="[icon, `text-${color}-400`]"></i>
      </div>
    </template>
    <template v-else-if="icon">
      <i :class="[icon, 'mr-2']"></i>
    </template>
    {{ title }}
  </h3>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  title: string;
  icon?: string;
  color?: string;
  useIconBadge?: boolean;
}>(), {
  color: 'primary',
  useIconBadge: false
});
</script> 