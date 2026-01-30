<!-- Features Section - Clean Apple/Cursor-inspired design -->
<template>
  <section class="relative py-24 md:py-32 px-6 sm:px-8 lg:px-12 bg-white dark:bg-[#0a0a0a] transition-colors duration-500 overflow-hidden">
    
    <!-- Subtle ambient background -->
    <div class="absolute inset-0 pointer-events-none">
      <div class="absolute top-1/2 left-1/2 w-[800px] h-[400px] bg-gradient-radial from-gray-200/30 dark:from-white/[0.02] via-transparent to-transparent rounded-full blur-3xl transform -translate-x-1/2 -translate-y-1/2"></div>
    </div>
    
    <div class="relative max-w-6xl mx-auto">
      
      <!-- Section header -->
      <div class="text-center mb-16 md:mb-20">
        <p class="text-sm font-medium text-gray-500 dark:text-white/50 uppercase tracking-widest mb-4 transition-colors duration-300">How it works</p>
        <h2 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight transition-colors duration-300">
          Your product-building partner
        </h2>
        <p class="text-xl text-gray-500 dark:text-white/60 max-w-2xl mx-auto transition-colors duration-300">
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
          <!-- Card with solid background -->
          <div class="relative h-full p-8 rounded-2xl bg-white dark:bg-white border border-gray-200 dark:border-gray-300 transition-colors duration-300 shadow-md">
            
            <!-- Title -->
            <h3 class="relative text-xl font-semibold text-gray-900 dark:text-black transition-colors duration-300 mb-5 text-center">
              {{ feature.title }}
            </h3>
            
            <!-- Description -->
            <p class="relative text-gray-600 dark:text-black leading-relaxed transition-colors duration-300 text-center">
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
/* Styles removed - cards now use simple shadows */
</style>
