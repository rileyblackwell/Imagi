<!-- Testimonials Section with Immersive 3D Cards -->
<template>
  <section class="py-24 md:py-36 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
    <!-- Decorative background elements -->
    <div class="absolute inset-0 pointer-events-none">
      <!-- Subtle pattern overlay -->
      <div class="absolute inset-0 bg-[url('/dot-pattern.svg')] opacity-[0.03]"></div>
      
      <!-- Glowing orbs -->
      <div class="absolute -top-[10%] right-[15%] w-[800px] h-[800px] rounded-full bg-indigo-600/5 blur-[150px]"></div>
      <div class="absolute bottom-[5%] left-[20%] w-[600px] h-[600px] rounded-full bg-fuchsia-600/5 blur-[120px]"></div>
      
      <!-- Animated gradient line -->
      <div class="absolute left-0 right-0 top-1/2 h-px bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent"></div>
    </div>

    <div class="max-w-7xl mx-auto relative z-10">
      <!-- Enhanced section header -->
      <div class="text-center mb-16">
        <div class="inline-block px-4 py-1.5 bg-indigo-500/10 rounded-full mb-3">
          <span class="text-indigo-400 font-semibold text-sm tracking-wider">SUCCESS STORIES</span>
        </div>
        <h2 class="text-4xl md:text-5xl font-bold text-white mb-4 leading-tight">{{ title }}</h2>
        <p class="text-xl text-gray-300 max-w-3xl mx-auto">{{ subtitle }}</p>
        
        <!-- Decorative element -->
        <div class="w-24 h-1 bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full mx-auto mt-8"></div>
      </div>

      <!-- 3D Testimonial Cards Showcase -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-10 lg:gap-12 relative">
        <div 
          v-for="(testimonial, index) in testimonials" 
          :key="index"
          class="testimonial-card group"
          :class="{ 'md:mt-12': index === 1 }"
        >
          <!-- 3D Glassmorphism Card -->
          <div class="relative h-full p-8 rounded-2xl border border-gray-800/60 bg-dark-900/40 backdrop-blur-sm transition-all duration-500 hover:shadow-glow hover:shadow-[--testimonial-color] hover:-translate-y-2 overflow-hidden"
               :style="{ '--testimonial-color': getTestimonialColor(testimonial.color) }">
            
            <!-- Background gradient -->
            <div class="absolute inset-0 bg-gradient-to-br opacity-10 -z-10 transition-opacity duration-300 group-hover:opacity-20"
                 :class="getGradientClass(testimonial.color)"></div>
                 
            <!-- Glowing orb effect -->
            <div class="absolute -bottom-20 -right-20 w-40 h-40 rounded-full opacity-10 blur-3xl transition-opacity duration-500 group-hover:opacity-20"
                 :class="getOrbClass(testimonial.color)"></div>
            
            <!-- Star rating (moved to top left) -->
            <div class="flex space-x-1 mb-4">
              <i v-for="star in 5" :key="star" class="fas fa-star text-xs" :class="getStarClass(testimonial.color)"></i>
            </div>
            
            <!-- Quote with subtle 3D effect -->
            <div class="relative z-10 mb-8 testimonial-content transform transition-all duration-300">
              <p class="text-gray-300 leading-relaxed">{{ testimonial.quote }}</p>
            </div>
            
            <!-- Author info with 3D avatar -->
            <div class="flex items-center space-x-4">
              <!-- 3D Avatar with glow -->
              <div class="relative">
                <div class="w-12 h-12 rounded-full flex items-center justify-center text-gray-100 font-semibold bg-gradient-to-br shadow-lg transform transition-all duration-300 scale-100 group-hover:scale-105"
                     :class="getAvatarClass(testimonial.color)">
                  {{ testimonial.avatarInitials }}
                </div>
                <!-- Avatar shadow/glow effect -->
                <div class="absolute -inset-1 rounded-full blur-md opacity-40 -z-10"
                     :class="getAvatarGlowClass(testimonial.color)"></div>
              </div>
              
              <div>
                <div class="font-bold text-white">{{ testimonial.name }}</div>
                <div class="text-sm text-gray-400">{{ testimonial.position }}</div>
              </div>
            </div>
            
            <!-- Subtle border glow on hover -->
            <div class="absolute inset-0 rounded-2xl border-2 opacity-0 transition-opacity duration-300 group-hover:opacity-10"
                 :class="getBorderClass(testimonial.color)"></div>
          </div>
        </div>
      </div>
      
      <!-- View more testimonials button -->
      <div class="text-center mt-16">
        <button class="inline-flex items-center px-6 py-3 rounded-full bg-dark-800/70 border border-indigo-500/30 text-white font-medium transition-all duration-300 hover:bg-indigo-500/20 hover:border-indigo-500/50 shadow-lg shadow-indigo-900/20">
          <span>Read More Testimonials</span>
          <i class="fas fa-arrow-right ml-2 text-xs transition-all duration-300 group-hover:translate-x-1"></i>
        </button>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'TestimonialsSection',
  props: {
    title: {
      type: String,
      default: 'What Developers Say'
    },
    subtitle: {
      type: String,
      default: 'Join thousands of satisfied developers who trust Imagi to build their applications'
    },
    testimonials: {
      type: Array,
      default: () => [
        {
          quote: 'Imagi has revolutionized how I build web applications. What used to take weeks now takes hours. The AI understands exactly what I need and the code quality is exceptional.',
          avatarInitials: 'JS',
          name: 'John Smith',
          position: 'Senior Developer',
          color: 'primary'
        },
        {
          quote: "The code quality is impressive. It's not just about speed - Imagi generates clean, maintainable code that follows best practices. Our team productivity has doubled since we started using it.",
          avatarInitials: 'AD',
          name: 'Alice Davis',
          position: 'Tech Lead',
          color: 'indigo'
        },
        {
          quote: "Perfect for startups and MVPs. We've cut our development time by 80% and can iterate much faster with customer feedback. Imagi has become an essential part of our tech stack.",
          avatarInitials: 'MR',
          name: 'Mike Ross',
          position: 'Startup Founder',
          color: 'violet'
        }
      ]
    }
  },
  methods: {
    getTestimonialColor(color) {
      const colors = {
        primary: 'rgba(59, 130, 246, 0.5)',
        indigo: 'rgba(99, 102, 241, 0.5)',
        violet: 'rgba(139, 92, 246, 0.5)',
        fuchsia: 'rgba(217, 70, 239, 0.5)'
      };
      return colors[color] || colors.primary;
    },
    getGradientClass(color) {
      const classes = {
        primary: 'from-primary-900 to-primary-600',
        indigo: 'from-indigo-900 to-indigo-600',
        violet: 'from-violet-900 to-violet-600',
        fuchsia: 'from-fuchsia-900 to-fuchsia-600'
      };
      return classes[color] || classes.primary;
    },
    getOrbClass(color) {
      const classes = {
        primary: 'bg-primary-500',
        indigo: 'bg-indigo-500',
        violet: 'bg-violet-500',
        fuchsia: 'bg-fuchsia-500'
      };
      return classes[color] || classes.primary;
    },
    getQuoteClass(color) {
      const classes = {
        primary: 'text-primary-500',
        indigo: 'text-indigo-500',
        violet: 'text-violet-500',
        fuchsia: 'text-fuchsia-500'
      };
      return classes[color] || classes.primary;
    },
    getAvatarClass(color) {
      const classes = {
        primary: 'from-primary-700 to-primary-900',
        indigo: 'from-indigo-700 to-indigo-900',
        violet: 'from-violet-700 to-violet-900',
        fuchsia: 'from-fuchsia-700 to-fuchsia-900'
      };
      return classes[color] || classes.primary;
    },
    getAvatarGlowClass(color) {
      const classes = {
        primary: 'bg-primary-500',
        indigo: 'bg-indigo-500',
        violet: 'bg-violet-500',
        fuchsia: 'bg-fuchsia-500'
      };
      return classes[color] || classes.primary;
    },
    getStarClass(color) {
      const classes = {
        primary: 'text-primary-400',
        indigo: 'text-indigo-400',
        violet: 'text-violet-400',
        fuchsia: 'text-fuchsia-400'
      };
      return classes[color] || classes.primary;
    },
    getBorderClass(color) {
      const classes = {
        primary: 'border-primary-500',
        indigo: 'border-indigo-500',
        violet: 'border-violet-500',
        fuchsia: 'border-fuchsia-500'
      };
      return classes[color] || classes.primary;
    }
  }
})
</script>

<style scoped>
.testimonial-card {
  perspective: 1000px;
}

.testimonial-content {
  transform: translateZ(5px);
}

.shadow-glow {
  box-shadow: 0 0 25px -5px var(--testimonial-color);
}

/* Custom animations for floating effect */
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

@keyframes float-delay {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-8px); }
}

.float {
  animation: float 6s ease-in-out infinite;
}

.float-delay {
  animation: float-delay 8s ease-in-out infinite;
}
</style> 