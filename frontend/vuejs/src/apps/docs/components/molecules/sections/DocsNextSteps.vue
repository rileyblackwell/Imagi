<template>
  <div class="mt-12">
    <h2 class="text-2xl font-semibold text-white/90 mb-6">{{ title }}</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <router-link 
        v-for="link in links" 
        :key="link.to"
        :to="link.to" 
        class="group block transform transition-all duration-300 hover:-translate-y-1"
      >
        <div class="relative p-5 rounded-2xl border border-white/[0.06] bg-white/[0.02] backdrop-blur-sm hover:bg-white/[0.04] hover:border-white/[0.1] transition-all duration-500 overflow-hidden h-full">
          <!-- Top accent line -->
          <div class="absolute top-0 left-0 right-0 h-px" :class="getAccentClass(link.color || 'violet')"></div>
          
          <!-- Hover glow -->
          <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
            <div class="absolute -top-20 -right-20 w-40 h-40 rounded-full blur-3xl" :class="getGlowClass(link.color || 'violet')"></div>
          </div>
          
          <div class="relative flex items-start gap-4">
            <div class="flex items-center justify-center w-12 h-12 rounded-xl border transition-all duration-300 group-hover:scale-110 flex-shrink-0"
                 :class="getIconContainerClass(link.color || 'violet')">
              <i :class="[link.icon, 'text-xl', getIconClass(link.color || 'violet')]"></i>
            </div>
            <div>
              <h3 class="text-white/90 group-hover:text-white font-semibold text-lg mb-2 transition-colors duration-300">{{ link.title }}</h3>
              <p class="text-white/50 text-sm leading-relaxed">{{ link.description }}</p>
            </div>
          </div>
          
          <!-- Bottom accent on hover -->
          <div class="absolute bottom-0 left-0 right-0 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-500"
               :class="getAccentClass(link.color || 'violet')"></div>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
interface DocLink {
  title: string;
  description: string;
  to: string;
  icon: string;
  color?: string;
}

withDefaults(defineProps<{
  title?: string;
  links: DocLink[];
}>(), {
  title: "What's Next?"
});

const getAccentClass = (color: string) => {
  const classes = {
    violet: 'bg-gradient-to-r from-transparent via-violet-500/50 to-transparent',
    fuchsia: 'bg-gradient-to-r from-transparent via-fuchsia-500/50 to-transparent',
    blue: 'bg-gradient-to-r from-transparent via-blue-500/50 to-transparent',
    cyan: 'bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent',
    emerald: 'bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent',
    amber: 'bg-gradient-to-r from-transparent via-amber-500/50 to-transparent',
  } as Record<string, string>
  return classes[color] || classes.violet
}

const getGlowClass = (color: string) => {
  const classes = {
    violet: 'bg-violet-500/10',
    fuchsia: 'bg-fuchsia-500/10',
    blue: 'bg-blue-500/10',
    cyan: 'bg-cyan-500/10',
    emerald: 'bg-emerald-500/10',
    amber: 'bg-amber-500/10',
  } as Record<string, string>
  return classes[color] || classes.violet
}

const getIconContainerClass = (color: string) => {
  const classes = {
    violet: 'bg-violet-500/10 border-violet-500/20 group-hover:bg-violet-500/15 group-hover:border-violet-500/30',
    fuchsia: 'bg-fuchsia-500/10 border-fuchsia-500/20 group-hover:bg-fuchsia-500/15 group-hover:border-fuchsia-500/30',
    blue: 'bg-blue-500/10 border-blue-500/20 group-hover:bg-blue-500/15 group-hover:border-blue-500/30',
    cyan: 'bg-cyan-500/10 border-cyan-500/20 group-hover:bg-cyan-500/15 group-hover:border-cyan-500/30',
    emerald: 'bg-emerald-500/10 border-emerald-500/20 group-hover:bg-emerald-500/15 group-hover:border-emerald-500/30',
    amber: 'bg-amber-500/10 border-amber-500/20 group-hover:bg-amber-500/15 group-hover:border-amber-500/30',
  } as Record<string, string>
  return classes[color] || classes.violet
}

const getIconClass = (color: string) => {
  const classes = {
    violet: 'text-violet-400',
    fuchsia: 'text-fuchsia-400',
    blue: 'text-blue-400',
    cyan: 'text-cyan-400',
    emerald: 'text-emerald-400',
    amber: 'text-amber-400',
  } as Record<string, string>
  return classes[color] || classes.violet
}
</script>
