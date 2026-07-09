<!-- Features Section - Clean Apple/Cursor-inspired design -->
<template>
  <section class="relative py-24 md:py-32 px-6 sm:px-8 lg:px-12 bg-white dark:bg-[#0a0a0a] transition-colors duration-500 overflow-hidden">

    <!-- Subtle ambient background -->
    <div class="absolute inset-0 pointer-events-none">
      <div class="absolute top-1/2 left-1/2 w-[800px] h-[400px] bg-gradient-radial from-blue-200/20 dark:from-blue-500/[0.04] via-transparent to-transparent rounded-full blur-3xl transform -translate-x-1/2 -translate-y-1/2"></div>
    </div>

    <div class="relative max-w-6xl mx-auto">

      <!-- Section header -->
      <div class="text-center mb-16 md:mb-20">
        <span class="inline-flex items-center gap-2 px-3 py-1 mb-5 rounded-full border border-gray-200/80 dark:border-white/10 bg-white/70 dark:bg-white/[0.04] backdrop-blur-md text-xs font-semibold uppercase tracking-widest text-gray-600 dark:text-white/60 transition-colors duration-300">
          <span class="w-1.5 h-1.5 rounded-full bg-gradient-to-r from-blue-500 to-violet-500"></span>
          How it works
        </span>
        <h2 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight transition-colors duration-300">
          Your product-building partner
        </h2>
        <p class="text-xl text-gray-600 dark:text-white/70 max-w-2xl mx-auto transition-colors duration-300">
          Three simple tools that work together to help you build, test, and launch web applications.
        </p>
      </div>

      <!-- Features grid with enhanced cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">

        <div
          v-for="(feature, index) in features"
          :key="index"
          class="sleek-card group relative h-full overflow-hidden p-8 rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-200/80 dark:border-white/10 transition-all duration-300"
        >
          <span class="card-topline"></span>

          <!-- Step number + icon -->
          <div class="relative flex items-center justify-between mb-6">
            <div class="flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500/10 to-violet-500/10 dark:from-blue-500/20 dark:to-violet-500/20 border border-blue-500/10 dark:border-white/10 transition-all duration-300 group-hover:scale-105">
              <i :class="[feature.icon, 'text-xl text-blue-600 dark:text-blue-300']"></i>
            </div>
            <span class="text-sm font-semibold text-gray-300 dark:text-white/20 tabular-nums transition-colors duration-300">0{{ index + 1 }}</span>
          </div>

          <!-- Title -->
          <h3 class="relative text-xl font-semibold text-gray-900 dark:text-white transition-colors duration-300 mb-3">
            {{ feature.title }}
          </h3>

          <!-- Description -->
          <p class="relative text-gray-600 dark:text-white/60 leading-relaxed transition-colors duration-300">
            {{ feature.description }}
          </p>

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
