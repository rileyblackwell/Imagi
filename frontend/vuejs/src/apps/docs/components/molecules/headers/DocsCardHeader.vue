<template>
  <div class="flex items-center gap-4 mb-5">
    <template v-if="useIconBadge || icon">
      <div class="flex items-center justify-center w-11 h-11 rounded-xl border transition-all duration-300"
           :class="getIconContainerClass(color)">
        <i :class="[icon, 'text-base', getIconClass(color)]"></i>
      </div>
    </template>
    <h3 class="text-lg font-semibold text-white/90 m-0">{{ title }}</h3>
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
    primary: 'bg-violet-500/10 border-violet-500/20 group-hover:bg-violet-500/15 group-hover:border-violet-500/30',
    violet: 'bg-violet-500/10 border-violet-500/20 group-hover:bg-violet-500/15 group-hover:border-violet-500/30',
    fuchsia: 'bg-fuchsia-500/10 border-fuchsia-500/20 group-hover:bg-fuchsia-500/15 group-hover:border-fuchsia-500/30',
    blue: 'bg-blue-500/10 border-blue-500/20 group-hover:bg-blue-500/15 group-hover:border-blue-500/30',
    cyan: 'bg-cyan-500/10 border-cyan-500/20 group-hover:bg-cyan-500/15 group-hover:border-cyan-500/30',
    emerald: 'bg-emerald-500/10 border-emerald-500/20 group-hover:bg-emerald-500/15 group-hover:border-emerald-500/30',
    green: 'bg-emerald-500/10 border-emerald-500/20 group-hover:bg-emerald-500/15 group-hover:border-emerald-500/30',
    amber: 'bg-amber-500/10 border-amber-500/20 group-hover:bg-amber-500/15 group-hover:border-amber-500/30',
    purple: 'bg-purple-500/10 border-purple-500/20 group-hover:bg-purple-500/15 group-hover:border-purple-500/30',
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
    purple: 'text-purple-400',
  } as Record<string, string>
  return classes[color] || classes.primary
}
</script>
