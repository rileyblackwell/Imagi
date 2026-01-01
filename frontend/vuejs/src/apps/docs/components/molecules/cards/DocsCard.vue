<template>
  <div class="group relative my-8">
    <!-- Card container matching homepage feature cards -->
    <div class="relative p-6 md:p-8 rounded-2xl border border-white/[0.06] bg-white/[0.02] backdrop-blur-sm hover:bg-white/[0.04] hover:border-white/[0.1] transition-all duration-500 overflow-hidden">
      <!-- Subtle hover glow -->
      <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
        <div class="absolute inset-0 bg-gradient-to-br opacity-[0.03]" :class="getGradientClass(colorVariant)"></div>
      </div>
      
      <!-- Top accent line -->
      <div class="absolute top-0 left-0 right-0 h-px" :class="getAccentLineClass(colorVariant)"></div>
      
      <!-- Decorative corner glow -->
      <div class="absolute -top-20 -right-20 w-40 h-40 rounded-full blur-3xl opacity-30 group-hover:opacity-50 transition-opacity duration-500"
           :class="getCardBackgroundClass(colorVariant)"></div>
      
      <!-- Card content -->
      <div class="relative z-10">
        <slot></slot>
      </div>
      
      <!-- Bottom accent line on hover -->
      <div 
        class="absolute bottom-0 left-0 right-0 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        :class="getBottomAccentClass(colorVariant)"
      ></div>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  colorVariant?: 'default' | 'primary' | 'violet' | 'blue' | 'cyan' | 'fuchsia' | 'emerald' | 'amber';
}>(), {
  colorVariant: 'default'
});

// Methods for styling matching homepage
const getGradientClass = (color: string) => {
  const classes = {
    default: 'from-violet-500 to-purple-500',
    primary: 'from-violet-500 to-fuchsia-500',
    violet: 'from-violet-500 to-purple-500',
    fuchsia: 'from-fuchsia-500 to-pink-500',
    blue: 'from-blue-500 to-cyan-500',
    cyan: 'from-cyan-500 to-blue-500',
    emerald: 'from-emerald-500 to-teal-500',
    amber: 'from-amber-500 to-orange-500',
  } as Record<string, string>
  return classes[color] || classes.default
}

const getAccentLineClass = (color: string) => {
  const classes = {
    default: 'bg-gradient-to-r from-transparent via-violet-500/50 to-transparent',
    primary: 'bg-gradient-to-r from-transparent via-violet-500/50 to-transparent',
    violet: 'bg-gradient-to-r from-transparent via-violet-500/50 to-transparent',
    fuchsia: 'bg-gradient-to-r from-transparent via-fuchsia-500/50 to-transparent',
    blue: 'bg-gradient-to-r from-transparent via-blue-500/50 to-transparent',
    cyan: 'bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent',
    emerald: 'bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent',
    amber: 'bg-gradient-to-r from-transparent via-amber-500/50 to-transparent',
  } as Record<string, string>
  return classes[color] || classes.default
}

const getCardBackgroundClass = (color: string) => {
  const classes = {
    default: 'bg-gradient-to-br from-violet-500/10 to-purple-500/5',
    primary: 'bg-gradient-to-br from-violet-500/10 to-fuchsia-500/5',
    violet: 'bg-gradient-to-br from-violet-500/10 to-purple-500/5',
    fuchsia: 'bg-gradient-to-br from-fuchsia-500/10 to-pink-500/5',
    blue: 'bg-gradient-to-br from-blue-500/10 to-cyan-500/5',
    cyan: 'bg-gradient-to-br from-cyan-500/10 to-blue-500/5',
    emerald: 'bg-gradient-to-br from-emerald-500/10 to-teal-500/5',
    amber: 'bg-gradient-to-br from-amber-500/10 to-orange-500/5',
  } as Record<string, string>
  return classes[color] || classes.default
}

const getBottomAccentClass = (color: string) => {
  const classes = {
    default: 'bg-gradient-to-r from-transparent via-violet-500/50 to-transparent',
    primary: 'bg-gradient-to-r from-transparent via-violet-500/50 to-transparent',
    violet: 'bg-gradient-to-r from-transparent via-violet-500/50 to-transparent',
    fuchsia: 'bg-gradient-to-r from-transparent via-fuchsia-500/50 to-transparent',
    blue: 'bg-gradient-to-r from-transparent via-blue-500/50 to-transparent',
    cyan: 'bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent',
    emerald: 'bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent',
    amber: 'bg-gradient-to-r from-transparent via-amber-500/50 to-transparent',
  } as Record<string, string>
  return classes[color] || classes.default
}
</script>
