<template>
  <div class="group relative transform transition-all duration-300 hover:-translate-y-1 my-8">
    <!-- Modern glassmorphism container -->
    <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
      <!-- Sleek gradient header -->
      <div class="h-1 w-full transition-all duration-300"
           :class="getHeaderGradientClass(colorVariant)"></div>
      
      <!-- Subtle background effects -->
      <div class="absolute -top-32 -right-32 w-64 h-64 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"
           :class="getCardBackgroundClass(colorVariant)"></div>
      
      <!-- Card content -->
      <div class="relative z-10 p-6">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  colorVariant?: 'default' | 'primary' | 'violet' | 'blue' | 'cyan';
}>(), {
  colorVariant: 'default'
});

// Methods for styling
const getHeaderGradientClass = (color: string) => {
  const classes = {
    default: 'bg-gradient-to-r from-indigo-400 via-violet-400 to-indigo-400 opacity-80',
    primary: 'bg-gradient-to-r from-indigo-400 via-violet-400 to-indigo-400 opacity-80',
    violet: 'bg-gradient-to-r from-violet-400 via-purple-400 to-violet-400 opacity-80',
    blue: 'bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-400 opacity-80',
    cyan: 'bg-gradient-to-r from-cyan-400 via-blue-400 to-cyan-400 opacity-80',
  } as Record<string, string>
  return classes[color] || classes.default
}

const getCardBackgroundClass = (color: string) => {
  const classes = {
    default: 'bg-gradient-to-br from-indigo-400/4 to-violet-400/4',
    primary: 'bg-gradient-to-br from-indigo-400/4 to-violet-400/4',
    violet: 'bg-gradient-to-br from-violet-400/4 to-purple-400/4',
    blue: 'bg-gradient-to-br from-blue-400/4 to-cyan-400/4',
    cyan: 'bg-gradient-to-br from-cyan-400/4 to-blue-400/4',
  } as Record<string, string>
  return classes[color] || classes.default
}
</script> 