<!-- Stats Section - Clean Apple/Cursor-inspired design -->
<template>
  <section class="relative py-24 md:py-32 px-6 sm:px-8 lg:px-12 bg-gray-50 dark:bg-[#0d0d0d] transition-colors duration-500">
    <div class="max-w-6xl mx-auto">

      <!-- Section header -->
      <div class="text-center mb-16">
        <span class="inline-flex items-center gap-2 px-3 py-1 mb-5 rounded-full border border-gray-200/80 dark:border-white/10 bg-white/70 dark:bg-white/[0.04] backdrop-blur-md text-xs font-semibold uppercase tracking-widest text-gray-600 dark:text-white/60 transition-colors duration-300">
          <span class="w-1.5 h-1.5 rounded-full bg-gradient-to-r from-blue-500 to-violet-500"></span>
          Why Imagi
        </span>
        <h2 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight transition-colors duration-300">
          Fast, affordable, approachable
        </h2>
        <p class="text-xl text-gray-600 dark:text-white/70 max-w-2xl mx-auto transition-colors duration-300">
          Your practical partner for building web applications. We handle the technical complexity while you focus on your ideas.
        </p>
      </div>

      <!-- Stats grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl mx-auto mb-16">
        <div
          v-for="(stat, index) in stats"
          :key="index"
          class="sleek-card group relative overflow-hidden text-center p-10 rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-200/80 dark:border-white/10 transition-all duration-300"
        >
          <span class="card-topline"></span>
          <p class="relative text-lg text-gray-500 dark:text-white/50 mb-3 transition-colors duration-300">{{ stat.label }}</p>
          <div class="relative text-5xl md:text-6xl font-semibold tracking-tight bg-gradient-to-br from-gray-900 to-gray-600 dark:from-white dark:to-white/70 bg-clip-text text-transparent transition-colors duration-300">
            {{ stat.value }}<span v-if="stat.unit" class="text-3xl text-gray-400 dark:text-white/40 ml-1">{{ stat.unit }}</span>
          </div>
        </div>
      </div>

      <!-- Use case cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div
          v-for="(metric, index) in metrics"
          :key="index"
          class="sleek-card group relative overflow-hidden p-8 rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-200/80 dark:border-white/10 transition-all duration-300"
        >
          <span class="card-topline"></span>
          <!-- Icon and Title (side by side) -->
          <div class="relative flex items-center gap-3 mb-4">
            <div class="flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500/10 to-violet-500/10 dark:from-blue-500/20 dark:to-violet-500/20 border border-blue-500/10 dark:border-white/10 flex-shrink-0 transition-all duration-300 group-hover:scale-105">
              <i :class="[metric.icon, 'text-xl text-blue-600 dark:text-blue-300']"></i>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white transition-colors duration-300">
              {{ metric.title }}
            </h3>

            <!-- Description -->
            <p class="relative text-blue-950/70 leading-relaxed text-pretty transition-colors duration-300 text-center">
              {{ metric.description }}
            </p>
          </div>

          <!-- Description -->
          <p class="relative text-gray-600 dark:text-white/60 text-base leading-relaxed transition-colors duration-300">
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
/* Crisp, sharply-defined cards: hairline edge + tight layered shadow, with subtle hover lift */
.sleek-card {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}

.sleek-card:hover {
  transform: translateY(-4px);
  border-color: rgba(59, 130, 246, 0.25);
  box-shadow:
    0 0 0 1px rgba(59, 130, 246, 0.06),
    0 2px 4px rgba(15, 23, 42, 0.06),
    0 10px 20px -4px rgba(15, 23, 42, 0.10),
    0 24px 48px -14px rgba(59, 130, 246, 0.18);
}

.dark .sleek-card {
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.4),
    0 8px 24px -12px rgba(0, 0, 0, 0.6);
}

.dark .sleek-card:hover {
  transform: translateY(-4px);
  border-color: rgba(96, 165, 250, 0.3);
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.4),
    0 12px 32px -10px rgba(0, 0, 0, 0.7),
    0 0 32px -8px rgba(59, 130, 246, 0.25);
}

/* Gradient accent line that appears along the top edge on hover */
.card-topline {
  position: absolute;
  top: 0;
  left: 1.5rem;
  right: 1.5rem;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.6), rgba(139, 92, 246, 0.6), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.sleek-card:hover .card-topline {
  opacity: 1;
}

@media (prefers-reduced-motion: reduce) {
  .sleek-card:hover {
    transform: none;
  }
}
</style>
