<!-- How It Works Section Component with 3D Timeline UI -->
<template>
  <section id="how-it-works" class="py-24 md:py-36 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
    <!-- Animated background elements -->
    <div class="absolute inset-0 pointer-events-none">
      <!-- 3D grid effect for depth -->
      <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
      
      <!-- Animated glowing orbs -->
      <div class="absolute top-[30%] right-[10%] w-[300px] sm:w-[400px] md:w-[600px] h-[300px] sm:h-[400px] md:h-[600px] rounded-full bg-primary-600/5 blur-[100px] animate-pulse-slow"></div>
      <div class="absolute bottom-[20%] left-[10%] w-[250px] sm:w-[350px] md:w-[500px] h-[250px] sm:h-[350px] md:h-[500px] rounded-full bg-violet-600/5 blur-[80px] animate-pulse-slow animation-delay-150"></div>
    </div>
    
    <div class="max-w-7xl mx-auto relative z-10">
      <!-- Modern section header with badge -->
      <div class="text-center mb-20 relative">
        <div class="inline-block px-4 py-1.5 bg-primary-500/10 rounded-full mb-3">
          <span class="text-primary-400 font-semibold text-sm tracking-wider">SEAMLESS WORKFLOW</span>
        </div>
        <h2 class="text-4xl md:text-5xl font-bold text-white mb-4 leading-tight">{{ title }}</h2>
        <p class="text-xl text-gray-300 max-w-3xl mx-auto">{{ subtitle }}</p>
        
        <!-- Decorative line -->
        <div class="w-24 h-1 bg-gradient-to-r from-primary-500 to-violet-500 rounded-full mx-auto mt-8"></div>
      </div>

      <!-- 3D Timeline with Connected Steps -->
      <div class="relative">
        <!-- Center timeline line -->
        <div class="absolute top-0 bottom-0 left-1/2 w-px bg-gradient-to-b from-primary-500/70 via-violet-500/70 to-violet-500/70 transform -translate-x-1/2 hidden md:block"></div>
        
        <div class="space-y-24 relative">
          <div 
            v-for="(step, index) in steps" 
            :key="index"
            class="timeline-item relative"
            :class="{'md:ml-auto': index % 2 !== 0}"
          >
            <!-- Timeline connector bubble - now positioned directly on the timeline -->
            <div 
              class="absolute top-1/2 left-1/2 w-8 h-8 rounded-full transform -translate-x-1/2 -translate-y-1/2 z-10 hidden md:flex items-center justify-center"
              :class="getDotBgClasses(step.color)"
            >
              <div class="absolute -inset-1 rounded-full blur-md opacity-50 animate-pulse-slow"
                   :class="getDotGlowClasses(step.color)"></div>
              <span class="text-white font-bold text-sm">{{ index + 1 }}</span>
            </div>
            
            <!-- Step container with enhanced glass morphism -->
            <div 
              class="md:w-[calc(50%-3rem)] group relative transform transition-all duration-300 hover:-translate-y-2"
              :class="{'ml-auto md:mr-0': index % 2 === 0, 'mr-auto md:ml-0': index % 2 !== 0}"
            >
              <!-- Enhanced glass morphism effect with glow -->
              <div class="absolute -inset-0.5 rounded-xl opacity-0 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"
                   :class="getCardGlowClasses(step.color)"></div>
              
              <!-- Step content with glass morphism -->
              <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden border border-dark-800/50 group-hover:border-opacity-0 transition-all duration-300">
                <!-- Card header with gradient -->
                <div class="h-2 w-full transition-all duration-300"
                     :class="getCardHeaderClasses(step.color)"></div>
                
                <!-- Connecting line from timeline bubble to card on smaller screens -->
                <div 
                  class="absolute top-1/2 h-px w-6 md:hidden transform -translate-y-1/2"
                  :class="[
                    getLineClasses(step.color),
                    {'left-full': index % 2 === 0, 'right-full': index % 2 !== 0}
                  ]"
                ></div>
                
                <!-- Content container -->
                <div class="p-6 sm:p-8">
                  <!-- Step number and icon in a fancy container -->
                  <div class="flex items-center gap-3 mb-4">
                    <!-- Step icon container -->
                    <div 
                      class="w-12 h-12 sm:w-14 sm:h-14 flex items-center justify-center rounded-xl mb-0 transform transition-all duration-300 shadow-lg"
                      :class="getIconContainerClasses(step.color)"
                    >
                      <i :class="[step.icon, 'text-xl sm:text-2xl', getIconClasses(step.color)]"></i>
                    </div>
                    
                    <div>
                      <!-- Step label with modern badge styling -->
                      <div class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mb-1"
                           :class="getTagClasses(step.color)">
                        Step {{ index + 1 }}
                      </div>
                      
                      <!-- Step title with larger font -->
                      <h3 class="text-xl sm:text-2xl font-bold text-white">{{ step.title }}</h3>
                    </div>
                  </div>
                  
                  <!-- Step description -->
                  <p class="text-gray-300 mb-4">{{ step.description }}</p>
                  
                  <!-- Feature highlights with improved styling -->
                  <ul class="space-y-2">
                    <li v-for="(feature, fIndex) in step.features" :key="fIndex" 
                        class="flex items-start gap-2">
                      <div class="w-5 h-5 rounded-full flex-shrink-0 flex items-center justify-center mt-0.5"
                           :class="getFeatureIconBgClasses(step.color)">
                        <i class="fas fa-check text-xs" :class="getFeatureIconClasses(step.color)"></i>
                      </div>
                      <span class="text-gray-300 text-sm">{{ feature }}</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Action button at the end of the timeline -->
      <div class="text-center mt-16">
        <div class="inline-block group relative transform transition-all duration-300 hover:-translate-y-1">
          <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500/50 to-violet-500/50 rounded-xl opacity-30 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"></div>
          <HomeNavbarButton
            :to="{ name: isAuthenticated ? 'builder-dashboard' : 'login' }"
            class="relative !h-12 sm:!h-14 min-w-[160px] sm:min-w-[200px] px-6 sm:px-8 rounded-xl bg-dark-900/70 backdrop-blur-lg border border-dark-800/50 group-hover:border-opacity-0 transition-all duration-300"
          >
            <span class="relative z-10 flex items-center justify-center text-base sm:text-lg font-medium text-white">
              Try It Yourself
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
  name: 'HowItWorksSection',
  components: {
    HomeNavbarButton
  },
  props: {
    title: {
      type: String,
      default: 'How Imagi Works'
    },
    subtitle: {
      type: String,
      default: 'From idea to web app, our platform makes web development accessible to everyone - no coding skills required.'
    },
    steps: {
      type: Array,
      default: () => [
        {
          title: 'Describe Your Idea',
          description: 'Tell us what kind of web app you want to create. We currently support basic HTML, CSS, and JavaScript apps for displaying content like personal bios or company information.',
          icon: 'fas fa-lightbulb',
          color: 'primary',
          features: [
            'No technical terms needed',
            'Use regular, everyday language',
            'Explain your web app goals'
          ]
        },
        {
          title: 'Select Your AI Model',
          description: 'Choose which AI model you want to power your project. Different models have different strengths depending on your specific needs.',
          icon: 'fas fa-robot',
          color: 'violet',
          features: [
            'Multiple AI options',
            'Select the file to edit',
            'Switch between chat and build modes'
          ]
        },
        {
          title: 'Chat and Build',
          description: 'Use our intuitive interface to either chat about your project or directly build and edit your files using simple natural language commands.',
          icon: 'fas fa-comments',
          color: 'purple',
          features: [
            'Pay per AI request',
            'Instant file updates',
            'Switch between modes anytime'
          ]
        },
        {
          title: 'Get Your Web App',
          description: 'Within minutes, you\'ll have a complete web app that would have cost thousands of dollars and taken months if built by a professional developer.',
          icon: 'fas fa-globe',
          color: 'blue',
          features: [
            'Complete in minutes, not months',
            'Costs dollars, not thousands',
            'Ready for future advanced features'
          ]
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
    getDotBgClasses(color) {
      const classes = {
        primary: 'bg-primary-500',
        violet: 'bg-violet-500',
        purple: 'bg-purple-500',
        blue: 'bg-blue-500',
      }
      return classes[color] || classes.primary
    },
    getDotGlowClasses(color) {
      const classes = {
        primary: 'bg-primary-500',
        violet: 'bg-violet-500',
        purple: 'bg-purple-500',
        blue: 'bg-blue-500',
      }
      return classes[color] || classes.primary
    },
    getCardGlowClasses(color) {
      const classes = {
        primary: 'bg-gradient-to-r from-primary-500/50 to-violet-500/50',
        violet: 'bg-gradient-to-r from-violet-500/50 to-purple-500/50',
        purple: 'bg-gradient-to-r from-purple-500/50 to-primary-500/50',
        blue: 'bg-gradient-to-r from-blue-500/50 to-violet-500/50',
      }
      return classes[color] || classes.primary
    },
    getCardHeaderClasses(color) {
      const classes = {
        primary: 'bg-gradient-to-r from-primary-500 to-violet-500',
        violet: 'bg-gradient-to-r from-violet-500 to-purple-500',
        purple: 'bg-gradient-to-r from-purple-500 to-primary-500',
        blue: 'bg-gradient-to-r from-blue-500 to-violet-500',
      }
      return classes[color] || classes.primary
    },
    getLineClasses(color) {
      const classes = {
        primary: 'bg-primary-500',
        violet: 'bg-violet-500',
        purple: 'bg-purple-500',
        blue: 'bg-blue-500',
      }
      return classes[color] || classes.primary
    },
    getIconContainerClasses(color) {
      const classes = {
        primary: 'bg-primary-500/10 border border-primary-500/20 group-hover:bg-primary-500/20',
        violet: 'bg-violet-500/10 border border-violet-500/20 group-hover:bg-violet-500/20',
        purple: 'bg-purple-500/10 border border-purple-500/20 group-hover:bg-purple-500/20',
        blue: 'bg-blue-500/10 border border-blue-500/20 group-hover:bg-blue-500/20',
      }
      return classes[color] || classes.primary
    },
    getIconClasses(color) {
      const classes = {
        primary: 'text-primary-400 group-hover:text-primary-300',
        violet: 'text-violet-400 group-hover:text-violet-300',
        purple: 'text-purple-400 group-hover:text-purple-300',
        blue: 'text-blue-400 group-hover:text-blue-300',
      }
      return classes[color] || classes.primary
    },
    getTagClasses(color) {
      const classes = {
        primary: 'bg-primary-500/10 text-primary-400',
        violet: 'bg-violet-500/10 text-violet-400',
        purple: 'bg-purple-500/10 text-purple-400',
        blue: 'bg-blue-500/10 text-blue-400',
      }
      return classes[color] || classes.primary
    },
    getFeatureIconBgClasses(color) {
      const classes = {
        primary: 'bg-primary-500/10',
        violet: 'bg-violet-500/10',
        purple: 'bg-purple-500/10',
        blue: 'bg-blue-500/10',
      }
      return classes[color] || classes.primary
    },
    getFeatureIconClasses(color) {
      const classes = {
        primary: 'text-primary-400',
        violet: 'text-violet-400',
        purple: 'text-purple-400',
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