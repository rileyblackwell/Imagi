<template>
  <li class="flex items-start gap-3">
    <div 
      v-if="icon" 
      class="flex-shrink-0 flex items-center justify-center rounded-full mt-0.5"
      :class="[getSizeClass(size), getIconContainerClass(color)]"
    >
      <i :class="[icon, getIconSizeClass(size), getIconClass(color)]"></i>
    </div>
    <span class="text-white/60 text-sm">
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
    primary: 'bg-violet-500/15',
    violet: 'bg-violet-500/15',
    fuchsia: 'bg-fuchsia-500/15',
    blue: 'bg-blue-500/15',
    cyan: 'bg-cyan-500/15',
    emerald: 'bg-emerald-500/15',
    green: 'bg-emerald-500/15',
    amber: 'bg-amber-500/15',
    yellow: 'bg-amber-500/15',
    purple: 'bg-purple-500/15',
    rose: 'bg-rose-500/15',
  } as Record<string, string>
  return classes[color] || classes.primary
}

const getIconClass = (color: string) => {
  const classes = {
    primary: 'text-violet-400',
    violet: 'text-violet-400',
    fuchsia: 'text-fuchsia-400',
    blue: 'text-blue-400',
    cyan: 'text-cyan-400',
    emerald: 'text-emerald-400',
    green: 'text-emerald-400',
    amber: 'text-amber-400',
    yellow: 'text-amber-400',
    purple: 'text-purple-400',
    rose: 'text-rose-400',
  } as Record<string, string>
  return classes[color] || classes.primary
}
</script>
