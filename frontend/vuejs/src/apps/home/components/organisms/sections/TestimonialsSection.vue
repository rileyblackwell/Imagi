<!-- Testimonials Section with Immersive 3D Cards -->
<template>
  <section class="py-24 md:py-36 px-6 sm:px-8 lg:px-12 relative overflow-hidden">
    <!-- Decorative background elements -->
    <div class="absolute inset-0 pointer-events-none">
      <!-- Subtle pattern overlay -->
      <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
      
      <!-- Glowing orbs -->
      <div class="absolute -top-[10%] right-[15%] w-[800px] h-[800px] rounded-full bg-indigo-600/5 blur-[150px] animate-pulse-slow"></div>
      <div class="absolute bottom-[5%] left-[20%] w-[600px] h-[600px] rounded-full bg-violet-600/5 blur-[120px] animate-pulse-slow animation-delay-150"></div>
    </div>

    <div class="max-w-7xl mx-auto relative z-10">
      <!-- Enhanced section header -->
      <div class="text-center mb-16">
        <!-- Modern pill badge -->
        <div class="inline-flex items-center px-4 py-1.5 bg-gradient-to-r from-indigo-500/10 to-violet-500/10 rounded-full border border-indigo-400/20 backdrop-blur-sm mb-6">
          <div class="w-1.5 h-1.5 bg-indigo-400 rounded-full mr-2 animate-pulse"></div>
          <span class="text-indigo-300 font-medium text-sm tracking-wide uppercase">Success Stories</span>
        </div>
        <h2 class="text-4xl md:text-5xl font-bold text-white mb-4 leading-tight">{{ title }}</h2>
        <p class="text-xl text-gray-300 max-w-3xl mx-auto">{{ subtitle }}</p>
        
        <!-- Modern divider -->
        <div class="w-full h-px bg-gradient-to-r from-transparent via-indigo-500/30 to-transparent mt-8"></div>
      </div>

      <!-- 3D Testimonial Cards Showcase -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 lg:gap-10 relative">
        <div 
          v-for="(testimonial, index) in testimonials" 
          :key="index"
          class="group relative transform transition-all duration-300 hover:-translate-y-1"
          :class="{ 'md:mt-8': index === 1 }"
        >
          <!-- Modern glassmorphism container -->
          <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden h-full transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
            <!-- Sleek gradient header -->
            <div class="h-1 w-full transition-all duration-300"
                 :class="getHeaderGradientClass(testimonial.color)"></div>
            
            <!-- Subtle background effects -->
            <div class="absolute -top-32 -right-32 w-64 h-64 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"
                 :class="getCardBackgroundClass(testimonial.color)"></div>
            
            <!-- Card content -->
            <div class="relative z-10 p-6 sm:p-8 h-full flex flex-col">
              <!-- Star rating -->
              <div class="flex space-x-1 mb-6">
                <i v-for="n in 5" :key="n" class="fas fa-star text-sm" 
                   :class="n <= testimonial.rating ? getStarClass(testimonial.color) : 'text-gray-600'"></i>
              </div>
              
              <!-- Testimonial text -->
              <p class="text-gray-300 mb-6 text-base leading-relaxed flex-1">{{ testimonial.text }}</p>
              
              <!-- Modern separator -->
              <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-6"></div>
              
              <!-- Author info with enhanced layout -->
              <div class="flex items-center">
                <!-- Author avatar with enhanced styling -->
                <div class="mr-4 w-12 h-12 relative overflow-hidden rounded-xl flex-shrink-0 border"
                     :class="getAvatarContainerClass(testimonial.color)">
                  <div class="relative w-full h-full flex items-center justify-center">
                    <i class="fas fa-user text-sm" :class="getAuthorIconClass(testimonial.color)"></i>
                  </div>
                </div>
                
                <!-- Author details with enhanced styling -->
                <div>
                  <h4 class="font-semibold text-white text-sm leading-tight">{{ testimonial.author }}</h4>
                  <p class="text-xs leading-relaxed" :class="getPositionClass(testimonial.color)">{{ testimonial.position }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Simple CTA Button -->
      <div class="mt-16 text-center">
        <HomeNavbarButton
          :to="{ name: 'about' }"
          class="group relative !h-12 sm:!h-14 px-8 rounded-xl bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-400 hover:to-violet-400 text-white font-medium transition-all duration-300 transform hover:-translate-y-1 shadow-lg shadow-indigo-500/25"
        >
          <span class="flex items-center justify-center text-lg">
            View More Stories
            <i class="fas fa-arrow-right ml-3 transform group-hover:translate-x-1 transition-transform duration-300"></i>
          </span>
        </HomeNavbarButton>
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
      default: 'Why People Love Imagi'
    },
    subtitle: {
      type: String,
      default: 'See how non-technical users are creating web apps in minutes for a fraction of what professional developers charge'
    },
    testimonials: {
      type: Array,
      default: () => [
        {
          author: 'Sarah Johnson',
          position: 'Small Business Owner',
          text: 'I was quoted $4,500 by a web developer to build my business web app. With Imagi, I built it myself for under $10 in just one afternoon - no coding needed!',
          rating: 5,
          color: 'primary'
        },
        {
          author: 'Michael Chen',
          position: 'Marketing Consultant',
          text: 'I love how you only pay for the AI requests you make. I created my entire professional web app for $8 in AI credits. The different AI models are great for different tasks.',
          rating: 5,
          color: 'violet'
        },
        {
          author: 'Emily Rodriguez',
          position: 'Content Creator',
          text: 'Being able to chat with the AI to build my web app was amazing! I just described what I wanted, and it created the HTML and CSS for me. Saved me thousands of dollars!',
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
    getCardBackgroundClass(color) {
      const classes = {
        primary: 'bg-gradient-to-br from-indigo-400/4 to-violet-400/4',
        violet: 'bg-gradient-to-br from-violet-400/4 to-purple-400/4',
        blue: 'bg-gradient-to-br from-blue-400/4 to-cyan-400/4',
      }
      return classes[color] || classes.primary
    },
    getHeaderGradientClass(color) {
      const classes = {
        primary: 'bg-gradient-to-r from-indigo-400 via-violet-400 to-indigo-400 opacity-80',
        violet: 'bg-gradient-to-r from-violet-400 via-purple-400 to-violet-400 opacity-80',
        blue: 'bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-400 opacity-80',
      }
      return classes[color] || classes.primary
    },
    getStarClass(color) {
      const classes = {
        primary: 'text-indigo-400',
        violet: 'text-violet-400',
        blue: 'text-blue-400',
      }
      return classes[color] || classes.primary
    },
    getAuthorIconClass(color) {
      const classes = {
        primary: 'text-indigo-300',
        violet: 'text-violet-300',
        blue: 'text-blue-300',
      }
      return classes[color] || classes.primary
    },
    getPositionClass(color) {
      const classes = {
        primary: 'text-indigo-400',
        violet: 'text-violet-400',
        blue: 'text-blue-400',
      }
      return classes[color] || classes.primary
    },
    getAvatarContainerClass(color) {
      const classes = {
        primary: 'bg-gradient-to-br from-indigo-400/20 to-violet-400/20 border-indigo-400/20',
        violet: 'bg-gradient-to-br from-violet-400/20 to-purple-400/20 border-violet-400/20',
        blue: 'bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border-blue-400/20',
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