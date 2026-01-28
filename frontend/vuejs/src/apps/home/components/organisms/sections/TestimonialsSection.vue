<!-- Testimonials Section - Clean Apple/Cursor-inspired design -->
<template>
  <section class="py-24 md:py-32 px-6 sm:px-8 lg:px-12">
    <div class="max-w-6xl mx-auto">
      
      <!-- Section header -->
      <div class="text-center mb-16">
        <p class="text-sm font-medium text-gray-500 dark:text-white/50 uppercase tracking-widest mb-4 transition-colors duration-300">Testimonials</p>
        <h2 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight transition-colors duration-300">
          Loved by builders
        </h2>
        <p class="text-xl text-gray-500 dark:text-white/60 max-w-2xl mx-auto transition-colors duration-300">
          See how creators are shipping full-stack apps without writing code.
        </p>
      </div>

      <!-- Testimonial cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div 
          v-for="(testimonial, index) in testimonials" 
          :key="index"
          class="flex flex-col p-8 rounded-2xl bg-white dark:bg-white/[0.02] border border-gray-200 dark:border-white/10 transition-all duration-300"
        >
          <!-- Star rating -->
          <div class="flex gap-1 mb-6">
            <svg 
              v-for="n in 5" 
              :key="n" 
              class="w-5 h-5"
              :class="n <= testimonial.rating ? 'text-yellow-400' : 'text-gray-200 dark:text-white/10'"
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          </div>
          
          <!-- Testimonial text -->
          <p class="text-gray-700 dark:text-white/80 leading-relaxed mb-8 flex-1 transition-colors duration-300">
            "{{ testimonial.text }}"
          </p>
          
          <!-- Author info -->
          <div class="flex items-center gap-4 pt-6 border-t border-gray-100 dark:border-white/5 transition-colors duration-300">
            <div class="flex items-center justify-center w-12 h-12 rounded-full bg-gray-100 dark:bg-white/5 transition-colors duration-300">
              <span class="text-sm font-semibold text-gray-600 dark:text-white/60">
                {{ getInitials(testimonial.author) }}
              </span>
            </div>
            <div>
              <h4 class="font-semibold text-gray-900 dark:text-white transition-colors duration-300">{{ testimonial.author }}</h4>
              <p class="text-sm text-gray-500 dark:text-white/50 transition-colors duration-300">{{ testimonial.position }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'TestimonialsSection',
  props: {
    testimonials: {
      type: Array,
      default: () => [
        {
          author: 'Sarah Mitchell',
          position: 'Startup Founder',
          text: 'I went from idea to working MVP in one afternoon. The AI understood exactly what I needed — a customer portal with booking and payments. Would have cost me $5k+ with a developer.',
          rating: 5
        },
        {
          author: 'David Park',
          position: 'Agency Owner',
          text: 'The chat-based editing is a game changer. I can iterate on designs and features just by describing what I want. Built three client dashboards last month for under $30 total.',
          rating: 5
        },
        {
          author: 'Maria Santos',
          position: 'Course Creator',
          text: 'Finally, a no-code tool that gives me real code I can own and customize. Built my entire course platform with Imagi and downloaded the source to host myself.',
          rating: 5
        }
      ]
    }
  },
  methods: {
    getInitials(name) {
      return name.split(' ').map(n => n[0]).join('').toUpperCase()
    }
  }
})
</script>
