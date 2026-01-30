<!-- Stats Section - Clean Apple/Cursor-inspired design -->
<template>
  <section class="relative py-24 md:py-32 px-6 sm:px-8 lg:px-12 bg-gray-100 dark:bg-[#0d0d0d] transition-colors duration-500">
    <div class="max-w-6xl mx-auto">
      
      <!-- Section header -->
      <div class="text-center mb-16">
        <p class="text-sm font-medium text-gray-600 dark:text-white/60 uppercase tracking-widest mb-4 transition-colors duration-300">Why Imagi</p>
        <h2 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight transition-colors duration-300">
          Fast, affordable, approachable
        </h2>
        <p class="text-xl text-gray-700 dark:text-white/70 max-w-2xl mx-auto transition-colors duration-300">
          Your practical partner for building web applications. We handle the technical complexity while you focus on your ideas.
        </p>
      </div>

      <!-- Stats grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl mx-auto mb-16">
        <div 
          v-for="(stat, index) in stats" 
          :key="index"
          class="relative text-center p-10 rounded-2xl bg-white dark:bg-white border border-gray-200 dark:border-gray-300 transition-colors duration-300 shadow-md"
        >
          <p class="relative text-lg text-gray-600 dark:text-black mb-3 transition-colors duration-300">{{ stat.label }}</p>
          <div class="relative text-5xl md:text-6xl font-semibold text-gray-900 dark:text-black transition-colors duration-300">
            {{ stat.value }}<span v-if="stat.unit" class="text-3xl text-gray-600 dark:text-black ml-1">{{ stat.unit }}</span>
          </div>
        </div>
      </div>

      <!-- Use case cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div 
          v-for="(metric, index) in metrics" 
          :key="index"
          class="relative p-8 rounded-2xl bg-white dark:bg-white border border-gray-200 dark:border-gray-300 transition-colors duration-300 shadow-md"
        >
          <!-- Icon and Title (side by side) -->
          <div class="relative flex items-center gap-3 mb-4">
            <div class="flex items-center justify-center w-12 h-12 rounded-2xl bg-gray-200 dark:bg-gray-200 flex-shrink-0 transition-colors duration-300">
              <i :class="[metric.icon, 'text-xl text-gray-700 dark:text-gray-700']"></i>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-black transition-colors duration-300">
              {{ metric.title }}
            </h3>
          </div>
          
          <!-- Description -->
          <p class="relative text-gray-600 dark:text-black text-base leading-relaxed transition-colors duration-300">
            {{ metric.description }}
          </p>
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
          value: '30',
          unit: 'min',
          label: 'Typical Build Time'
        }
      ]
    },
    metrics: {
      type: Array,
      default: () => [
        {
          icon: 'fas fa-seedling',
          title: 'Ideal for Startup Founders',
          description: 'No coding experience needed. Quickly get up and running to prototype and validate your ideas with real users.'
        },
        {
          icon: 'fas fa-users',
          title: 'Ideal for Non-Technical Teams',
          description: 'Empower your team to rapidly prototype and test ideas without waiting for engineering resources.'
        },
        {
          icon: 'fas fa-code',
          title: 'Ideal for Technical Teams',
          description: 'A quick, easy interface to get something up and running and test it out.'
        }
      ]
    }
  }
})
</script>

<style scoped>
/* Styles removed - cards now use simple shadows */
</style>
