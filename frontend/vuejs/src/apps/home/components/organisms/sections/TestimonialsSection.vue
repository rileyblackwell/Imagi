<!-- Testimonials Section with Immersive 3D Cards -->
<template>
  <section class="py-24 md:py-36 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
    <!-- Decorative background elements -->
    <div class="absolute inset-0 pointer-events-none">
      <!-- Subtle pattern overlay -->
      <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
      
      <!-- Glowing orbs -->
      <div class="absolute -top-[10%] right-[15%] w-[800px] h-[800px] rounded-full bg-primary-600/5 blur-[150px] animate-pulse-slow"></div>
      <div class="absolute bottom-[5%] left-[20%] w-[600px] h-[600px] rounded-full bg-violet-600/5 blur-[120px] animate-pulse-slow animation-delay-150"></div>
    </div>

    <div class="max-w-7xl mx-auto relative z-10">
      <!-- Enhanced section header -->
      <div class="text-center mb-16">
        <div class="inline-block px-4 py-1.5 bg-primary-500/10 rounded-full mb-3">
          <span class="text-primary-400 font-semibold text-sm tracking-wider">SUCCESS STORIES</span>
        </div>
        <h2 class="text-4xl md:text-5xl font-bold text-white mb-4 leading-tight">{{ title }}</h2>
        <p class="text-xl text-gray-300 max-w-3xl mx-auto">{{ subtitle }}</p>
        
        <!-- Decorative element -->
        <div class="w-24 h-1 bg-gradient-to-r from-primary-500 to-violet-500 rounded-full mx-auto mt-8"></div>
      </div>

      <!-- 3D Testimonial Cards Showcase -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-10 lg:gap-12 relative">
        <div 
          v-for="(testimonial, index) in testimonials" 
          :key="index"
          class="group relative transform transition-all duration-300 hover:-translate-y-2"
          :class="{ 'md:mt-12': index === 1 }"
        >
          <!-- Enhanced glass morphism effect with glow -->
          <div class="absolute -inset-0.5 rounded-xl opacity-0 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"
               :class="getGlowBorderClass(testimonial.color)"></div>
          
          <!-- Testimonial card with enhanced glass morphism -->
          <div class="relative h-full bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden border border-dark-800/50 group-hover:border-opacity-0 transition-all duration-300">
            <!-- Card header with gradient -->
            <div class="h-2 w-full transition-all duration-300"
                 :class="getHeaderGradientClass(testimonial.color)"></div>
            
            <!-- Card content -->
            <div class="p-6 sm:p-8">
              <!-- Star rating and quote marks -->
              <div class="flex justify-between items-start mb-6">
                <!-- Star rating -->
                <div class="flex space-x-1">
                  <i v-for="n in 5" :key="n" class="fas fa-star text-sm" 
                     :class="n <= testimonial.rating ? getStarClass(testimonial.color) : 'text-gray-600'"></i>
                </div>
                
                <!-- Decorative quote mark -->
                <div class="text-4xl opacity-20 leading-none" :class="getQuoteClass(testimonial.color)">
                  "
                </div>
              </div>
              
              <!-- Testimonial text -->
              <p class="text-gray-300 mb-6 text-lg leading-relaxed">{{ testimonial.text }}</p>
              
              <!-- Author info with enhanced layout -->
              <div class="flex items-center mt-auto">
                <!-- Author avatar with enhanced styling -->
                <div class="mr-4 w-14 h-14 relative overflow-hidden rounded-xl flex-shrink-0 border border-dark-700/70">
                  <div class="absolute inset-0 bg-gradient-to-br w-full h-full opacity-10" 
                       :class="getGradientClass(testimonial.color)"></div>
                  <div class="relative w-full h-full flex items-center justify-center">
                    <i class="fas fa-user text-lg" :class="getAuthorIconClass(testimonial.color)"></i>
                  </div>
                </div>
                
                <!-- Author details with enhanced styling -->
                <div>
                  <h4 class="font-bold text-white">{{ testimonial.author }}</h4>
                  <p class="text-sm" :class="getPositionClass(testimonial.color)">{{ testimonial.position }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Enhanced CTA -->
      <div class="mt-20 text-center">
        <div class="inline-block group relative transform transition-all duration-300 hover:-translate-y-1">
          <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500/50 to-violet-500/50 rounded-xl opacity-30 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"></div>
          <HomeNavbarButton
            :to="{ name: 'about' }"
            class="relative !h-12 sm:!h-14 min-w-[160px] sm:min-w-[200px] px-6 sm:px-8 rounded-xl bg-dark-900/70 backdrop-blur-lg border border-dark-800/50 group-hover:border-opacity-0 transition-all duration-300"
          >
            <span class="relative z-10 flex items-center justify-center text-base sm:text-lg font-medium text-white">
              View More Stories
              <i class="fas fa-arrow-right ml-2 transform group-hover:translate-x-1 transition-transform duration-300"></i>
            </span>
          </HomeNavbarButton>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent, computed } from 'vue'
import { useAuthStore } from '@/shared/stores/auth'
import { HomeNavbarButton } from '@/apps/home/components/atoms/buttons'

export default defineComponent({
  name: 'TestimonialsSection',
  components: {
    HomeNavbarButton
  },
  props: {
    title: {
      type: String,
      default: 'What Our Users Say'
    },
    subtitle: {
      type: String,
      default: 'See how developers are transforming their workflow with our AI-powered platform'
    },
    testimonials: {
      type: Array,
      default: () => [
        {
          author: 'Sarah Johnson',
          position: 'Frontend Developer',
          text: 'I was skeptical at first, but this platform has completely changed how I approach web development. What used to take me days now takes hours.',
          rating: 5,
          color: 'primary'
        },
        {
          author: 'Michael Chen',
          position: 'Full-Stack Engineer',
          text: 'The code quality is what impressed me the most. Clean, well-structured, and following best practices. It feels like code written by a senior developer, not an AI.',
          rating: 5,
          color: 'violet'
        },
        {
          author: 'Emily Rodriguez',
          position: 'Tech Lead',
          text: 'We\'ve integrated this into our team\'s workflow and it\'s been a game-changer for productivity. Our sprint velocity has increased by at least 40%.',
          rating: 5,
          color: 'blue'
        }
      ]
    }
  },
  setup() {
    const authStore = useAuthStore()
    
    return {
      isAuthenticated: computed(() => authStore.isAuthenticated)
    }
  },
  methods: {
    getTestimonialColor(color) {
      const colors = {
        primary: 'rgba(59, 130, 246, 0.5)',
        violet: 'rgba(139, 92, 246, 0.5)',
        blue: 'rgba(37, 99, 235, 0.5)',
      }
      return colors[color] || colors.primary
    },
    getGradientClass(color) {
      const classes = {
        primary: 'from-primary-600 to-primary-800',
        violet: 'from-violet-600 to-violet-800',
        blue: 'from-blue-600 to-blue-800',
      }
      return classes[color] || classes.primary
    },
    getGlowBorderClass(color) {
      const classes = {
        primary: 'bg-gradient-to-r from-primary-500/50 to-violet-500/50',
        violet: 'bg-gradient-to-r from-violet-500/50 to-purple-500/50',
        blue: 'bg-gradient-to-r from-blue-500/50 to-violet-500/50',
      }
      return classes[color] || classes.primary
    },
    getHeaderGradientClass(color) {
      const classes = {
        primary: 'bg-gradient-to-r from-primary-500 to-violet-500',
        violet: 'bg-gradient-to-r from-violet-500 to-purple-500',
        blue: 'bg-gradient-to-r from-blue-500 to-violet-500',
      }
      return classes[color] || classes.primary
    },
    getStarClass(color) {
      const classes = {
        primary: 'text-primary-400',
        violet: 'text-violet-400',
        blue: 'text-blue-400',
      }
      return classes[color] || classes.primary
    },
    getQuoteClass(color) {
      const classes = {
        primary: 'text-primary-500',
        violet: 'text-violet-500',
        blue: 'text-blue-500',
      }
      return classes[color] || classes.primary
    },
    getAuthorIconClass(color) {
      const classes = {
        primary: 'text-primary-400',
        violet: 'text-violet-400',
        blue: 'text-blue-400',
      }
      return classes[color] || classes.primary
    },
    getPositionClass(color) {
      const classes = {
        primary: 'text-primary-400',
        violet: 'text-violet-400',
        blue: 'text-blue-400',
      }
      return classes[color] || classes.primary
    }
  }
})
</script>

<style scoped>
@keyframes pulse-slow {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.8; }
}

.animate-pulse-slow {
  animation: pulse-slow 3s ease-in-out infinite;
}

.animation-delay-150 {
  animation-delay: 150ms;
}
</style> 