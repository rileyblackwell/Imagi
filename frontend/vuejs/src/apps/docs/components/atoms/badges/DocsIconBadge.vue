<template>
  <div 
    :class="[
      'flex-shrink-0 rounded-xl flex items-center justify-center border transition-all duration-300',
      size === 'sm' ? 'w-5 h-5 mr-3 mt-0.5' : size === 'md' ? 'w-6 h-6 mr-3 mt-0.5' : 'w-8 h-8 mr-3',
      getIconContainerClass(color)
    ]"
  >
    <i :class="[icon, getIconClass(color), size === 'sm' ? 'text-xs' : 'text-sm']"></i>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  icon: string;
  color?: string;
  size?: 'sm' | 'md' | 'lg';
}>(), {
  color: 'primary',
  size: 'sm'
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

<style scoped>
:root {
  --primary-rgb: 59, 130, 246;
  --violet-rgb: 139, 92, 246;
  --blue-rgb: 59, 130, 246;
  --green-rgb: 34, 197, 94;
  --purple-rgb: 168, 85, 247;
}
</style> 