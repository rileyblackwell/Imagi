<template>
  <li class="flex items-start gap-3">
    <div class="flex-shrink-0 w-1.5 h-1.5 rounded-full bg-gray-400 dark:bg-white/40 mt-2"></div>
    <span class="text-gray-600 dark:text-white/60 text-sm transition-colors duration-300">
      <slot></slot>
    </span>
  </li>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  icon?: string;
  color?: string;
  size?: 'xs' | 'sm' | 'md';
}>(), {
  color: 'primary',
  size: 'sm'
});

const getSizeClass = (size: string) => {
  const sizes = {
    xs: 'w-4 h-4',
    sm: 'w-5 h-5',
    md: 'w-6 h-6',
  } as Record<string, string>
  return sizes[size] || sizes.sm
}

const getIconSizeClass = (size: string) => {
  const sizes = {
    xs: 'text-[8px]',
    sm: 'text-[10px]',
    md: 'text-xs',
  } as Record<string, string>
  return sizes[size] || sizes.sm
}

const getIconContainerClass = (color: string) => {
  const classes = {
    primary: 'bg-emerald-100 dark:bg-emerald-500/15',
    violet: 'bg-emerald-100 dark:bg-emerald-500/15',
    fuchsia: 'bg-blue-100 dark:bg-blue-500/15',
    blue: 'bg-blue-100 dark:bg-blue-500/15',
    cyan: 'bg-blue-100 dark:bg-blue-500/15',
    emerald: 'bg-emerald-100 dark:bg-emerald-500/15',
    green: 'bg-emerald-100 dark:bg-emerald-500/15',
    amber: 'bg-amber-100 dark:bg-amber-500/15',
    yellow: 'bg-amber-100 dark:bg-amber-500/15',
    purple: 'bg-purple-100 dark:bg-purple-500/15',
    rose: 'bg-rose-100 dark:bg-rose-500/15',
  } as Record<string, string>
  return classes[color] || classes.primary
}

const getIconClass = (color: string) => {
  const classes = {
    primary: 'text-emerald-600 dark:text-emerald-400',
    violet: 'text-emerald-600 dark:text-emerald-400',
    fuchsia: 'text-blue-600 dark:text-blue-400',
    blue: 'text-blue-600 dark:text-blue-400',
    cyan: 'text-blue-600 dark:text-blue-400',
    emerald: 'text-emerald-600 dark:text-emerald-400',
    green: 'text-emerald-600 dark:text-emerald-400',
    amber: 'text-amber-600 dark:text-amber-400',
    yellow: 'text-amber-600 dark:text-amber-400',
    purple: 'text-purple-600 dark:text-purple-400',
    rose: 'text-rose-600 dark:text-rose-400',
  } as Record<string, string>
  return classes[color] || classes.primary
}
</script>
