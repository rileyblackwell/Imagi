<!-- Features Section - Clean Apple/Cursor-inspired design -->
<template>
  <section class="relative py-24 md:py-32 px-6 sm:px-8 lg:px-12 bg-orange-50 dark:bg-orange-600 border-t border-orange-200/60 dark:border-orange-500/[0.12] transition-colors duration-500 overflow-hidden">

    <div class="relative max-w-6xl mx-auto">

      <!-- Section header -->
      <div class="text-center mb-16 md:mb-20">
        <p class="inline-flex items-center px-3.5 py-1.5 rounded-full border border-blue-200/70 dark:border-blue-400/30 bg-blue-50/80 dark:bg-blue-600 text-xs font-semibold text-blue-700 dark:text-white uppercase tracking-[0.18em] mb-5 transition-colors duration-300">How it works</p>
        <h2 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-blue-950 dark:text-white mb-6 tracking-tight text-balance transition-colors duration-300">
          Your product-building partner
        </h2>
        <p class="text-xl text-blue-950/70 dark:text-blue-100/70 leading-relaxed text-pretty max-w-2xl mx-auto transition-colors duration-300">
          Three simple tools that work together to help you build, test, and launch web applications.
        </p>
      </div>

      <!-- Features grid with enhanced cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">

        <div
          v-for="(feature, index) in features"
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
              <i :class="[feature.icon, 'text-lg', index % 2 === 1 ? 'text-orange-600' : 'text-blue-600']"></i>
            </div>

            <!-- Title -->
            <h3 class="relative text-xl font-semibold tracking-tight text-blue-950 transition-colors duration-300 mb-4 text-center">
              {{ feature.title }}
            </h3>

            <!-- Description -->
            <p class="relative text-blue-950/70 leading-relaxed text-pretty transition-colors duration-300 text-center">
              {{ feature.description }}
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
  name: 'FeaturesSection',
  props: {
    features: {
      type: Array,
      default: () => [
        {
          title: 'Design Visually',
          description: 'A simple graphical interface for building and shaping your application. See changes instantly as you design.',
          icon: 'fas fa-pencil-ruler',
          highlights: [
            'Drag-and-drop builder',
            'Real-time preview',
            'Component library'
          ]
        },
        {
          title: 'Chat and Plan',
          description: 'An AI agent that understands your ideas. Chat together to plan features, solve problems, and write the code collaboratively.',
          icon: 'fas fa-comments',
          highlights: [
            'Natural conversation',
            'Intelligent code generation',
            'Iterative refinement'
          ]
        },
        {
          title: 'Launch to the Web',
          description: 'Deploy your application with a single click. Get it online quickly so you can test with real users.',
          icon: 'fas fa-rocket',
          highlights: [
            'One-click deployment',
            'Custom domains',
            'Instant updates'
          ]
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
