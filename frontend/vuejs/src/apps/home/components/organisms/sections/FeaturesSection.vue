<!-- Features Section - Clean Apple/Cursor-inspired design -->
<template>
  <section class="py-24 md:py-32 px-6 sm:px-8 lg:px-12 bg-gray-50 dark:bg-[#0f0f0f] transition-colors duration-500">
    <div class="max-w-6xl mx-auto">
      
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

      <!-- Features grid - uniform layout -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 lg:gap-10">
        
        <div 
          v-for="(feature, index) in features" 
          :key="index"
          class="group relative text-center"
        >
          <!-- Icon -->
          <div class="mb-6 flex justify-center">
            <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-white dark:bg-white/[0.02] border border-gray-200 dark:border-white/10 transition-all duration-300 group-hover:border-gray-300 dark:group-hover:border-white/20 group-hover:scale-110">
              <i :class="[feature.icon, 'text-2xl text-gray-700 dark:text-white/70 transition-colors duration-300']"></i>
            </div>
          </div>
          
          <!-- Content -->
          <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-3 transition-colors duration-300">
            {{ feature.title }}
          </h3>
          <p class="text-gray-500 dark:text-white/60 leading-relaxed transition-colors duration-300">
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
          title: 'Chat and Plan',
          description: 'An AI agent that understands your ideas. Chat together to plan features, solve problems, and write the code collaboratively.',
          icon: 'fas fa-comments'
        },
        {
          title: 'Design Visually',
          description: 'A simple graphical interface for building and shaping your application. See changes instantly as you design.',
          icon: 'fas fa-pencil-ruler'
        },
        {
          title: 'Launch to the Web',
          description: 'Deploy your application with a single click. Get it online quickly so you can test with real users.',
          icon: 'fas fa-rocket'
        },
        {
          title: 'Perfect for Prototyping',
          description: 'Validate ideas inside companies, test startup concepts, or build personal projects. Often the first step before bringing in engineers.',
          icon: 'fas fa-lightbulb'
        },
        {
          title: 'Built to Grow',
          description: 'Start simple, then scale. Everything is designed so professional engineers can extend and enhance what you create.',
          icon: 'fas fa-arrow-up'
        },
        {
          title: 'Fast and Affordable',
          description: 'Skip months of development time and thousands in costs. Pay only for what you build, with no monthly subscriptions.',
          icon: 'fas fa-gauge-high'
        }
      ]
    }
  }
})
</script>
