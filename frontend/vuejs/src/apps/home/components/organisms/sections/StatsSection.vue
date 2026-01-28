<!-- Stats Section - Clean Apple/Cursor-inspired design -->
<template>
  <section class="py-24 md:py-32 px-6 sm:px-8 lg:px-12 bg-gray-50 dark:bg-[#0f0f0f] transition-colors duration-500">
    <div class="max-w-6xl mx-auto">
      
      <!-- Section header -->
      <div class="text-center mb-16">
        <p class="text-sm font-medium text-gray-500 dark:text-white/50 uppercase tracking-widest mb-4 transition-colors duration-300">By the numbers</p>
        <h2 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight transition-colors duration-300">
          Built for speed
        </h2>
        <p class="text-xl text-gray-500 dark:text-white/60 max-w-2xl mx-auto transition-colors duration-300">
          Skip months of development and thousands in costs. Build production-ready apps in minutes.
        </p>
      </div>

      <!-- Stats grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl mx-auto mb-16">
        <div 
          v-for="(stat, index) in stats" 
          :key="index"
          class="text-center p-10 rounded-2xl bg-white dark:bg-white/[0.02] border border-gray-200 dark:border-white/10 transition-all duration-300"
        >
          <div class="text-5xl md:text-6xl font-semibold text-gray-900 dark:text-white mb-3 transition-colors duration-300">
            {{ stat.value }}<span v-if="stat.unit" class="text-3xl text-gray-500 dark:text-white/50 ml-1">{{ stat.unit }}</span>
          </div>
          <p class="text-lg text-gray-500 dark:text-white/60 transition-colors duration-300">{{ stat.label }}</p>
        </div>
      </div>

      <!-- Tech stack cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div 
          v-for="(metric, index) in metrics" 
          :key="index"
          class="p-6 rounded-2xl bg-white dark:bg-white/[0.02] border border-gray-200 dark:border-white/10 transition-all duration-300"
        >
          <div class="flex items-center gap-4 mb-4">
            <div class="flex items-center justify-center w-10 h-10 rounded-xl bg-gray-100 dark:bg-white/5 transition-colors duration-300">
              <i :class="[metric.icon, 'text-lg text-gray-700 dark:text-white/70']"></i>
            </div>
            <div>
              <div class="font-semibold text-gray-900 dark:text-white transition-colors duration-300">{{ metric.value }}</div>
              <div class="text-xs text-gray-500 dark:text-white/50 transition-colors duration-300">{{ metric.label }}</div>
            </div>
          </div>
          <p class="text-gray-500 dark:text-white/60 text-sm leading-relaxed transition-colors duration-300">{{ metric.detail }}</p>
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
    stats: {
      type: Array,
      default: () => [
        {
          value: '$10-20',
          unit: '',
          label: 'Typical App Cost'
        },
        {
          value: '~1',
          unit: 'hr',
          label: 'Typical Build Time'
        }
      ]
    },
    metrics: {
      type: Array,
      default: () => [
        {
          icon: 'fab fa-vuejs',
          value: 'Vue.js + Tailwind',
          label: 'Frontend Stack',
          detail: 'Modern, responsive UI with component-based architecture'
        },
        {
          icon: 'fab fa-python',
          value: 'Django + REST',
          label: 'Backend Stack',
          detail: 'Python backend with REST APIs and data models'
        },
        {
          icon: 'fas fa-rocket',
          value: 'Q1 2026',
          label: 'Imagi Hosting',
          detail: 'One-click deploy to .imagi.app domains with SSL'
        }
      ]
    }
  }
})
</script>
