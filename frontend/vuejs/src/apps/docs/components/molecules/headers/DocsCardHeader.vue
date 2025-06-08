<template>
  <h3 class="text-white mt-0 flex items-center mb-4">
    <template v-if="useIconBadge || icon">
      <div class="rounded-xl flex items-center justify-center mr-3 border transition-all duration-300"
           :class="[
             useIconBadge ? 'w-8 h-8' : 'w-6 h-6',
             getIconContainerClass(color)
           ]">
        <i :class="[icon, getIconClass(color), useIconBadge ? 'text-sm' : 'text-xs']"></i>
      </div>
    </template>
    <span class="text-lg font-semibold">{{ title }}</span>
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
  useIconBadge: true
});

const getIconContainerClass = (color: string) => {
  const classes = {
    primary: 'bg-gradient-to-br from-indigo-400/20 to-violet-400/20 border-indigo-400/20',
    violet: 'bg-gradient-to-br from-violet-400/20 to-purple-400/20 border-violet-400/20',
    blue: 'bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border-blue-400/20',
    green: 'bg-gradient-to-br from-emerald-400/20 to-green-400/20 border-emerald-400/20',
    purple: 'bg-gradient-to-br from-purple-400/20 to-fuchsia-400/20 border-purple-400/20',
    cyan: 'bg-gradient-to-br from-cyan-400/20 to-blue-400/20 border-cyan-400/20',
  } as Record<string, string>
  return classes[color] || classes.primary
}

const getIconClass = (color: string) => {
  const classes = {
    primary: 'text-indigo-300',
    violet: 'text-violet-300',
    blue: 'text-blue-300',
    green: 'text-emerald-300',
    purple: 'text-purple-300',
    cyan: 'text-cyan-300',
  } as Record<string, string>
  return classes[color] || classes.primary
}
</script> 