<template>
  <div class="mb-5">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white/90 m-0 transition-colors duration-300">{{ title }}</h3>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  title: string;
  icon?: string;
  color?: string;
  useIconBadge?: boolean;
}>(), {
  color: 'primary',
  useIconBadge: true
});

const getIconContainerClass = (color: string) => {
  const classes = {
    primary: 'bg-gray-100 dark:bg-emerald-500/10 border-gray-200 dark:border-emerald-500/20 group-hover:bg-gray-200 dark:group-hover:bg-emerald-500/15 group-hover:border-gray-300 dark:group-hover:border-emerald-500/30',
    violet: 'bg-gray-100 dark:bg-emerald-500/10 border-gray-200 dark:border-emerald-500/20 group-hover:bg-gray-200 dark:group-hover:bg-emerald-500/15 group-hover:border-gray-300 dark:group-hover:border-emerald-500/30',
    fuchsia: 'bg-gray-100 dark:bg-blue-500/10 border-gray-200 dark:border-blue-500/20 group-hover:bg-gray-200 dark:group-hover:bg-blue-500/15 group-hover:border-gray-300 dark:group-hover:border-blue-500/30',
    blue: 'bg-gray-100 dark:bg-blue-500/10 border-gray-200 dark:border-blue-500/20 group-hover:bg-gray-200 dark:group-hover:bg-blue-500/15 group-hover:border-gray-300 dark:group-hover:border-blue-500/30',
    cyan: 'bg-gray-100 dark:bg-blue-500/10 border-gray-200 dark:border-blue-500/20 group-hover:bg-gray-200 dark:group-hover:bg-blue-500/15 group-hover:border-gray-300 dark:group-hover:border-blue-500/30',
    emerald: 'bg-gray-100 dark:bg-emerald-500/10 border-gray-200 dark:border-emerald-500/20 group-hover:bg-gray-200 dark:group-hover:bg-emerald-500/15 group-hover:border-gray-300 dark:group-hover:border-emerald-500/30',
    green: 'bg-gray-100 dark:bg-emerald-500/10 border-gray-200 dark:border-emerald-500/20 group-hover:bg-gray-200 dark:group-hover:bg-emerald-500/15 group-hover:border-gray-300 dark:group-hover:border-emerald-500/30',
    amber: 'bg-gray-100 dark:bg-amber-500/10 border-gray-200 dark:border-amber-500/20 group-hover:bg-gray-200 dark:group-hover:bg-amber-500/15 group-hover:border-gray-300 dark:group-hover:border-amber-500/30',
    purple: 'bg-gray-100 dark:bg-purple-500/10 border-gray-200 dark:border-purple-500/20 group-hover:bg-gray-200 dark:group-hover:bg-purple-500/15 group-hover:border-gray-300 dark:group-hover:border-purple-500/30',
  } as Record<string, string>
  return classes[color] || classes.primary
}

const getIconClass = (color: string) => {
  const classes = {
    primary: 'text-gray-700 dark:text-emerald-400',
    violet: 'text-gray-700 dark:text-emerald-400',
    fuchsia: 'text-gray-700 dark:text-blue-400',
    blue: 'text-gray-700 dark:text-blue-400',
    cyan: 'text-gray-700 dark:text-blue-400',
    emerald: 'text-gray-700 dark:text-emerald-400',
    green: 'text-gray-700 dark:text-emerald-400',
    amber: 'text-gray-700 dark:text-amber-400',
    purple: 'text-gray-700 dark:text-purple-400',
  } as Record<string, string>
  return classes[color] || classes.primary
}
</script>
