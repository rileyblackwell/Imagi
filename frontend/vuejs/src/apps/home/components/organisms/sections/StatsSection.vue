<!-- Stats Section - Premium Design -->
<template>
  <section class="py-20 md:py-32 px-6 sm:px-8 lg:px-12 relative overflow-hidden">
    <div class="max-w-7xl mx-auto relative">
      <!-- Section header -->
      <div class="text-center mb-16 md:mb-20">
        <!-- Badge -->
        <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/[0.05] rounded-full border border-white/10 mb-6">
          <i class="fas fa-chart-line text-xs text-emerald-400/90"></i>
          <span class="text-sm font-medium text-white/80">By The Numbers</span>
        </div>
        
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-semibold text-white mb-5 tracking-tight">{{ title }}</h2>
        <p class="text-lg text-white/70 max-w-2xl mx-auto leading-relaxed">{{ subtitle }}</p>
      </div>

      <!-- Stats grid -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-5 md:gap-6 mb-12">
        <div 
          v-for="(stat, index) in stats" 
          :key="index"
          class="group relative"
        >
          <!-- Card -->
          <div class="relative h-full p-6 md:p-7 rounded-2xl border border-white/10 bg-white/[0.04] backdrop-blur-sm hover:bg-white/[0.06] hover:border-white/20 transition-all duration-500 cursor-default overflow-hidden text-center">
            <!-- Hover glow -->
            <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
              <div class="absolute inset-0 bg-gradient-to-br opacity-[0.05]" :class="getGradientClass(stat.color)"></div>
            </div>
            
            <!-- Icon -->
            <div class="relative mb-4 inline-flex items-center justify-center w-11 h-11 rounded-xl border" :class="getIconContainerClass(stat.color)">
              <i :class="[stat.icon, 'text-base', getIconClass(stat.color)]"></i>
            </div>
            
            <!-- Value -->
            <div class="relative mb-2">
              <span class="text-3xl md:text-4xl font-semibold bg-gradient-to-r bg-clip-text text-transparent" :class="getValueClass(stat.color)">
                {{ stat.value }}
              </span>
              <span v-if="stat.unit" class="text-base font-medium ml-1" :class="getUnitClass(stat.color)">{{ stat.unit }}</span>
            </div>
            
            <!-- Label -->
            <p class="relative text-white/70 text-sm">{{ stat.label }}</p>

            <!-- Bottom accent -->
            <div 
              class="absolute bottom-0 left-0 right-0 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-500"
              :class="getAccentClass(stat.color)"
            ></div>
          </div>
        </div>
      </div>

      <!-- Metrics row -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-5 md:gap-6">
        <div 
          v-for="(metric, index) in metrics" 
          :key="index"
          class="group relative"
        >
          <!-- Card -->
          <div class="relative p-6 rounded-2xl border border-white/10 bg-white/[0.04] backdrop-blur-sm hover:bg-white/[0.06] hover:border-white/20 transition-all duration-500 cursor-default overflow-hidden">
            <!-- Hover glow -->
            <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
              <div class="absolute inset-0 bg-gradient-to-br opacity-[0.05]" :class="getGradientClass(metric.color)"></div>
            </div>
            
            <div class="relative flex items-center gap-4 mb-4">
              <!-- Icon -->
              <div class="flex items-center justify-center w-10 h-10 rounded-xl border" :class="getIconContainerClass(metric.color)">
                <i :class="[metric.icon, 'text-sm', getIconClass(metric.color)]"></i>
              </div>
              
              <div>
                <div class="font-semibold text-white">{{ metric.value }}</div>
                <div class="text-xs text-white/60">{{ metric.label }}</div>
              </div>
            </div>
            
            <!-- Divider -->
            <div class="relative w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-4"></div>
            
            <!-- Detail -->
            <p class="relative text-white/70 text-sm leading-relaxed">{{ metric.detail }}</p>

            <!-- Bottom accent -->
            <div 
              class="absolute bottom-0 left-0 right-0 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-500"
              :class="getAccentClass(metric.color)"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'StatsSection',
  props: {
    title: {
      type: String,
      default: 'Built for Speed & Savings'
    },
    subtitle: {
      type: String,
      default: 'Skip the months of development and thousands in costs. Build production-ready apps in minutes for dollars.'
    },
    stats: {
      type: Array,
      default: () => [
        {
          icon: 'fas fa-dollar-sign',
          value: '$5-15',
          unit: '',
          label: 'Typical App Cost',
          color: 'emerald'
        },
        {
          icon: 'fas fa-clock',
          value: '~30',
          unit: 'min',
          label: 'Build Time',
          color: 'violet'
        },
        {
          icon: 'fas fa-layer-group',
          value: '2',
          unit: '',
          label: 'Full Stacks',
          color: 'blue'
        },
        {
          icon: 'fas fa-code-branch',
          value: '0',
          unit: '',
          label: 'Lines to Write',
          color: 'fuchsia'
        }
      ]
    },
    metrics: {
      type: Array,
      default: () => [
        {
          icon: 'fas fa-palette',
          value: 'Vue.js + Tailwind',
          label: 'Frontend Stack',
          detail: 'Modern, responsive UI with component-based architecture',
          color: 'violet'
        },
        {
          icon: 'fas fa-server',
          value: 'Django + REST',
          label: 'Backend Stack',
          detail: 'Python backend with REST APIs and data models',
          color: 'fuchsia'
        },
        {
          icon: 'fas fa-rocket',
          value: 'Q1 2026',
          label: 'Imagi Hosting',
          detail: 'One-click deploy to .imagi.app domains with SSL',
          color: 'amber'
        }
      ]
    }
  },
  methods: {
    getGradientClass(color) {
      const gradients = {
        violet: 'from-violet-500 to-purple-500',
        fuchsia: 'from-fuchsia-500 to-pink-500',
        blue: 'from-blue-500 to-cyan-500',
        emerald: 'from-emerald-500 to-teal-500',
        amber: 'from-amber-500 to-orange-500'
      }
      return gradients[color] || gradients.violet
    },
    getIconContainerClass(color) {
      const classes = {
        violet: 'bg-violet-500/10 border-violet-500/20',
        fuchsia: 'bg-fuchsia-500/10 border-fuchsia-500/20',
        blue: 'bg-blue-500/10 border-blue-500/20',
        emerald: 'bg-emerald-500/10 border-emerald-500/20',
        amber: 'bg-amber-500/10 border-amber-500/20'
      }
      return classes[color] || classes.violet
    },
    getIconClass(color) {
      const classes = {
        violet: 'text-violet-400',
        fuchsia: 'text-fuchsia-400',
        blue: 'text-blue-400',
        emerald: 'text-emerald-400',
        amber: 'text-amber-400'
      }
      return classes[color] || classes.violet
    },
    getValueClass(color) {
      const classes = {
        violet: 'from-violet-300 to-purple-300',
        fuchsia: 'from-fuchsia-300 to-pink-300',
        blue: 'from-blue-300 to-cyan-300',
        emerald: 'from-emerald-300 to-teal-300',
        amber: 'from-amber-300 to-orange-300'
      }
      return classes[color] || classes.violet
    },
    getUnitClass(color) {
      const classes = {
        violet: 'text-violet-400/80',
        fuchsia: 'text-fuchsia-400/80',
        blue: 'text-blue-400/80',
        emerald: 'text-emerald-400/80',
        amber: 'text-amber-400/80'
      }
      return classes[color] || classes.violet
    },
    getAccentClass(color) {
      const classes = {
        violet: 'bg-gradient-to-r from-transparent via-violet-500/50 to-transparent',
        fuchsia: 'bg-gradient-to-r from-transparent via-fuchsia-500/50 to-transparent',
        blue: 'bg-gradient-to-r from-transparent via-blue-500/50 to-transparent',
        emerald: 'bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent',
        amber: 'bg-gradient-to-r from-transparent via-amber-500/50 to-transparent'
      }
      return classes[color] || classes.violet
    }
  }
})
</script>

<style scoped>
</style>
