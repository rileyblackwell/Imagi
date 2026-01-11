<!-- Testimonials Section - Premium Design -->
<template>
  <section class="py-20 md:py-32 px-6 sm:px-8 lg:px-12 relative overflow-hidden">
    <div class="max-w-7xl mx-auto relative">
      <!-- Section header -->
      <div class="text-center mb-16 md:mb-20">
        <!-- Badge -->
        <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/[0.05] rounded-full border border-white/10 mb-6">
          <i class="fas fa-heart text-xs text-rose-400/90"></i>
          <span class="text-sm font-medium text-white/80">Success Stories</span>
        </div>
        
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-semibold text-white mb-5 tracking-tight">{{ title }}</h2>
        <p class="text-lg text-white/70 max-w-2xl mx-auto leading-relaxed">{{ subtitle }}</p>
      </div>

      <!-- Testimonial cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8">
        <div 
          v-for="(testimonial, index) in testimonials" 
          :key="index"
          class="group relative"
          :class="{ 'md:translate-y-6': index === 1 }"
        >
          <!-- Card -->
          <div class="relative h-full p-7 md:p-8 rounded-2xl border border-white/10 bg-white/[0.04] backdrop-blur-sm hover:bg-white/[0.06] hover:border-white/20 transition-all duration-500 cursor-default overflow-hidden flex flex-col">
            <!-- Hover glow -->
            <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
              <div class="absolute inset-0 bg-gradient-to-br opacity-[0.05]" :class="getGradientClass(testimonial.color)"></div>
            </div>
            
            <!-- Star rating -->
            <div class="relative flex gap-1 mb-5">
              <i 
                v-for="n in 5" 
                :key="n" 
                class="fas fa-star text-sm"
                :class="n <= testimonial.rating ? getStarClass(testimonial.color) : 'text-white/20'"
              ></i>
            </div>
            
            <!-- Testimonial text -->
            <p class="relative text-white/90 text-base leading-relaxed mb-8 flex-1">
              {{ testimonial.text }}
            </p>
            
            <!-- Divider -->
            <div class="relative w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-6"></div>
            
            <!-- Author info -->
            <div class="relative flex items-center gap-4">
              <!-- Avatar -->
              <div 
                class="flex items-center justify-center w-11 h-11 rounded-full border"
                :class="getAvatarClass(testimonial.color)"
              >
                <span class="text-sm font-semibold" :class="getAvatarTextClass(testimonial.color)">
                  {{ getInitials(testimonial.author) }}
                </span>
              </div>
              
              <!-- Name and position -->
              <div>
                <h4 class="font-semibold text-white text-sm">{{ testimonial.author }}</h4>
                <p class="text-xs" :class="getPositionClass(testimonial.color)">{{ testimonial.position }}</p>
              </div>
            </div>

            <!-- Bottom accent -->
            <div 
              class="absolute bottom-0 left-0 right-0 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-500"
              :class="getAccentClass(testimonial.color)"
            ></div>
          </div>
        </div>
      </div>
      
      <!-- CTA button -->
      <div class="mt-14 text-center">
        <HomeNavbarButton
          :to="{ name: 'about' }"
          class="group inline-flex items-center gap-3 px-8 py-4 bg-white/[0.05] border border-white/[0.1] hover:bg-white/[0.08] hover:border-white/[0.15] rounded-xl text-white font-medium transition-all duration-300 hover:-translate-y-0.5"
        >
          View More Stories
          <i class="fas fa-arrow-right text-sm transform group-hover:translate-x-1 transition-transform duration-300"></i>
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
      default: 'Loved by Builders'
    },
    subtitle: {
      type: String,
      default: 'See how entrepreneurs and creators are shipping full-stack apps without writing a single line of code.'
    },
    testimonials: {
      type: Array,
      default: () => [
        {
          author: 'Sarah Mitchell',
          position: 'Startup Founder',
          text: 'I went from idea to working MVP in one afternoon. The AI understood exactly what I needed — a customer portal with booking and payments. Would have cost me $5k+ with a developer.',
          rating: 5,
          color: 'violet'
        },
        {
          author: 'David Park',
          position: 'Agency Owner',
          text: 'The chat-based editing is a game changer. I can iterate on designs and features just by describing what I want. Built three client dashboards last month for under $30 total.',
          rating: 5,
          color: 'fuchsia'
        },
        {
          author: 'Maria Santos',
          position: 'Course Creator',
          text: 'Finally, a no-code tool that gives me real code I can own and customize. Built my entire course platform with Imagi and downloaded the source to host myself.',
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
    getInitials(name) {
      return name.split(' ').map(n => n[0]).join('').toUpperCase()
    },
    getGradientClass(color) {
      const gradients = {
        violet: 'from-violet-500 to-purple-500',
        fuchsia: 'from-fuchsia-500 to-pink-500',
        blue: 'from-blue-500 to-cyan-500'
      }
      return gradients[color] || gradients.violet
    },
    getQuoteClass(color) {
      const classes = {
        violet: 'text-violet-500/20',
        fuchsia: 'text-fuchsia-500/20',
        blue: 'text-blue-500/20'
      }
      return classes[color] || classes.violet
    },
    getStarClass(color) {
      const classes = {
        violet: 'text-violet-400',
        fuchsia: 'text-fuchsia-400',
        blue: 'text-blue-400'
      }
      return classes[color] || classes.violet
    },
    getAvatarClass(color) {
      const classes = {
        violet: 'bg-violet-500/10 border-violet-500/20',
        fuchsia: 'bg-fuchsia-500/10 border-fuchsia-500/20',
        blue: 'bg-blue-500/10 border-blue-500/20'
      }
      return classes[color] || classes.violet
    },
    getAvatarTextClass(color) {
      const classes = {
        violet: 'text-violet-400',
        fuchsia: 'text-fuchsia-400',
        blue: 'text-blue-400'
      }
      return classes[color] || classes.violet
    },
    getPositionClass(color) {
      const classes = {
        violet: 'text-violet-400/70',
        fuchsia: 'text-fuchsia-400/70',
        blue: 'text-blue-400/70'
      }
      return classes[color] || classes.violet
    },
    getAccentClass(color) {
      const classes = {
        violet: 'bg-gradient-to-r from-transparent via-violet-500/50 to-transparent',
        fuchsia: 'bg-gradient-to-r from-transparent via-fuchsia-500/50 to-transparent',
        blue: 'bg-gradient-to-r from-transparent via-blue-500/50 to-transparent'
      }
      return classes[color] || classes.violet
    }
  }
})
</script>

<style scoped>
</style>
