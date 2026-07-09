<!-- Stats Section - Clean Apple/Cursor-inspired design -->
<template>
  <section class="relative py-24 md:py-32 px-6 sm:px-8 lg:px-12 bg-blue-50 dark:bg-blue-400/[0.16] border-t border-blue-200/60 dark:border-blue-500/[0.12] transition-colors duration-500">
    <div class="max-w-6xl mx-auto">

      <!-- Section header -->
      <div class="text-center mb-16">
        <p class="inline-flex items-center px-3.5 py-1.5 rounded-full border border-orange-200/70 dark:border-orange-400/30 bg-orange-50/80 dark:bg-orange-600 text-xs font-semibold text-orange-700 dark:text-white uppercase tracking-[0.18em] mb-5 transition-colors duration-300">Why Imagi</p>
        <h2 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-blue-950 dark:text-white mb-6 tracking-tight text-balance transition-colors duration-300">
          Fast, affordable, approachable
        </h2>
        <p class="text-xl text-blue-950/70 dark:text-blue-100/70 leading-relaxed text-pretty max-w-2xl mx-auto transition-colors duration-300">
          Your practical partner for building web applications. We handle the technical complexity while you focus on your ideas.
        </p>
      </div>

      <!-- Stats grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl mx-auto mb-16">
        <div
          v-for="(stat, index) in stats"
          :key="index"
          class="relative text-center p-10 rounded-2xl bg-white border border-blue-200/70 crisp-card"
        >
          <p class="relative text-sm font-medium uppercase tracking-widest text-blue-700/70 mb-4 transition-colors duration-300">{{ stat.label }}</p>
          <div class="relative text-5xl md:text-6xl font-semibold tracking-tight tabular-nums text-blue-950 transition-colors duration-300">
            {{ stat.value }}<span v-if="stat.unit" class="text-3xl text-blue-950/70 ml-1.5 font-medium">{{ stat.unit }}</span>
          </div>
        </div>
      </div>

      <!-- Use case cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">

        <div
          v-for="(metric, index) in metrics"
          :key="index"
          class="relative"
        >
          <!-- Card with tinted background matching its accent color -->
          <div
            class="relative h-full p-8 rounded-2xl border crisp-card transition-colors duration-300"
            :class="index % 2 === 1 ? 'bg-white border-orange-200/70' : 'bg-white border-blue-200/70'"
          >

            <!-- Icon -->
            <div
              class="relative flex items-center justify-center w-12 h-12 rounded-xl mx-auto mb-5 ring-1 transition-colors duration-300"
              :class="index % 2 === 1 ? 'bg-orange-100 ring-orange-900/[0.08]' : 'bg-gradient-to-br from-[#dbeeff] to-[#9ecdf3] ring-blue-900/[0.08]'"
            >
              <i :class="[metric.icon, 'text-lg', index % 2 === 1 ? 'text-orange-600' : 'text-blue-600']"></i>
            </div>

            <!-- Title -->
            <h3 class="relative text-xl font-semibold tracking-tight text-blue-950 transition-colors duration-300 mb-4 text-center">
              {{ metric.title }}
            </h3>

            <!-- Description -->
            <p class="relative text-blue-950/70 leading-relaxed text-pretty transition-colors duration-300 text-center">
              {{ metric.description }}
            </p>
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
/* Crisp, sharply-defined cards: hairline edge + tight layered shadow */
.crisp-card {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}
</style>
