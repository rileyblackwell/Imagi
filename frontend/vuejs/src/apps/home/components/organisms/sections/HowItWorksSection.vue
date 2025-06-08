<!-- How It Works Section Component with 3D Timeline UI -->
<template>
  <section id="how-it-works" class="py-24 md:py-36 px-6 sm:px-8 lg:px-12 relative overflow-hidden">
    <!-- Animated background elements -->
    <div class="absolute inset-0 pointer-events-none">
      <!-- 3D grid effect for depth -->
      <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
      
      <!-- Animated glowing orbs -->
      <div class="absolute top-[30%] right-[10%] w-[400px] h-[400px] rounded-full bg-indigo-600/5 blur-[100px] animate-pulse-slow"></div>
      <div class="absolute bottom-[20%] left-[10%] w-[300px] h-[300px] rounded-full bg-violet-600/5 blur-[80px] animate-pulse-slow animation-delay-150"></div>
    </div>
    
    <div class="max-w-7xl mx-auto relative z-10">
      <!-- Modern section header with badge -->
      <div class="text-center mb-20 relative">
        <!-- Modern pill badge -->
        <div class="inline-flex items-center px-4 py-1.5 bg-gradient-to-r from-indigo-500/10 to-violet-500/10 rounded-full border border-indigo-400/20 backdrop-blur-sm mb-6">
          <div class="w-1.5 h-1.5 bg-indigo-400 rounded-full mr-2 animate-pulse"></div>
          <span class="text-indigo-300 font-medium text-sm tracking-wide uppercase">Seamless Workflow</span>
        </div>
        <h2 class="text-4xl md:text-5xl font-bold text-white mb-4 leading-tight">{{ title }}</h2>
        <p class="text-xl text-gray-300 max-w-3xl mx-auto">{{ subtitle }}</p>
        
        <!-- Modern divider -->
        <div class="w-full h-px bg-gradient-to-r from-transparent via-primary-500/30 to-transparent mt-8"></div>
      </div>

      <!-- 3D Timeline with Connected Steps -->
      <div class="relative">
        <!-- Center timeline line -->
        <div class="absolute top-0 bottom-0 left-1/2 w-0.5 bg-gradient-to-b from-indigo-500/70 via-violet-500/70 to-violet-500/70 transform -translate-x-1/2 hidden md:block"></div>
        
        <div class="space-y-24 relative">
          <div 
            v-for="(step, index) in steps" 
            :key="index"
            class="timeline-item relative"
            :class="{'md:ml-auto': index % 2 !== 0}"
          >
            <!-- Timeline connector bubble - now positioned directly on the timeline -->
            <div 
              class="absolute top-1/2 left-1/2 w-10 h-10 rounded-full transform -translate-x-1/2 -translate-y-1/2 z-20 hidden md:flex items-center justify-center border-2 border-dark-950"
              :class="getDotBgClasses(step.color)"
            >
              <div class="absolute -inset-1 rounded-full blur-md opacity-50 animate-pulse-slow"
                   :class="getDotGlowClasses(step.color)"></div>
              <span class="text-white font-bold text-sm relative z-10">{{ index + 1 }}</span>
            </div>

            <!-- Enhanced connecting line from timeline bubble to card -->
            <div 
              class="absolute top-1/2 z-10 hidden md:block"
              :class="[
                'h-0.5 transform -translate-y-1/2',
                index % 2 === 0 ? 'left-1/2 ml-5 w-8' : 'right-1/2 mr-5 w-8',
                getConnectorLineClasses(step.color)
              ]"
            >
              <!-- Animated gradient line -->
              <div class="h-full w-full rounded-full opacity-80 animate-pulse-slow"
                   :class="getConnectorGradientClasses(step.color)"></div>
              
              <!-- Arrow indicator -->
              <div 
                class="absolute top-1/2 w-2 h-2 transform -translate-y-1/2 rotate-45"
                :class="[
                  index % 2 === 0 ? 'right-0 translate-x-1' : 'left-0 -translate-x-1',
                  getDotBgClasses(step.color)
                ]"
              ></div>
            </div>
            
            <!-- Step container with enhanced glass morphism -->
            <div 
              class="md:w-[calc(50%-4rem)] group relative transform transition-all duration-300 hover:-translate-y-2"
              :class="{'ml-auto md:mr-0': index % 2 === 0, 'mr-auto md:ml-0': index % 2 !== 0}"
            >
              <!-- Modern glassmorphism container -->
              <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                <!-- Sleek gradient header -->
                <div class="h-1 w-full transition-all duration-300"
                     :class="getCardHeaderClasses(step.color)"></div>
                
                <!-- Subtle background effects -->
                <div class="absolute -top-32 -right-32 w-64 h-64 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"
                     :class="getCardBackgroundClasses(step.color)"></div>
                
                <!-- Content container -->
                <div class="relative z-10 p-6 sm:p-8">
                  <!-- Step number and icon in a fancy container -->
                  <div class="flex items-center gap-4 mb-6">
                    <!-- Step icon container -->
                    <div 
                      class="w-12 h-12 sm:w-14 sm:h-14 flex items-center justify-center rounded-xl transform transition-all duration-300 border"
                      :class="getIconContainerClasses(step.color)"
                    >
                      <i :class="[step.icon, 'text-lg sm:text-xl', getIconClasses(step.color)]"></i>
                    </div>
                    
                    <div class="flex-1">
                      <!-- Step label with modern badge styling -->
                      <div class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium mb-2 border backdrop-blur-sm"
                           :class="getTagClasses(step.color)">
                        Step {{ index + 1 }}
                      </div>
                      
                      <!-- Step title with larger font -->
                      <h3 class="text-xl sm:text-2xl font-semibold text-white leading-tight">{{ step.title }}</h3>
                    </div>
                  </div>
                  
                  <!-- Step description -->
                  <p class="text-gray-300 mb-6 leading-relaxed">{{ step.description }}</p>
                  
                  <!-- Modern separator -->
                  <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-6"></div>
                  
                  <!-- Feature highlights with improved styling -->
                  <ul class="space-y-3">
                    <li v-for="(feature, fIndex) in step.features" :key="fIndex" 
                        class="flex items-start gap-3">
                      <div class="w-5 h-5 rounded-full flex-shrink-0 flex items-center justify-center mt-0.5 border"
                           :class="getFeatureIconBgClasses(step.color)">
                        <i class="fas fa-check text-xs" :class="getFeatureIconClasses(step.color)"></i>
                      </div>
                      <span class="text-gray-300 text-sm leading-relaxed">{{ feature }}</span>
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
        <HomeNavbarButton
          :to="{ name: isAuthenticated ? 'builder-dashboard' : 'login' }"
          class="group relative !h-12 sm:!h-14 px-8 rounded-xl bg-gradient-to-r from-rose-500 to-pink-500 hover:from-rose-400 hover:to-pink-400 text-white font-medium transition-all duration-300 transform hover:-translate-y-1 shadow-lg shadow-rose-500/25"
        >
          <span class="flex items-center justify-center text-lg">
            Try It Yourself
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
        primary: 'bg-gradient-to-br from-indigo-500 to-violet-500',
        violet: 'bg-gradient-to-br from-violet-500 to-purple-500',
        purple: 'bg-gradient-to-br from-purple-500 to-fuchsia-500',
        blue: 'bg-gradient-to-br from-blue-500 to-cyan-500',
      }
      return classes[color] || classes.primary
    },
    getDotGlowClasses(color) {
      const classes = {
        primary: 'bg-gradient-to-br from-indigo-500 to-violet-500',
        violet: 'bg-gradient-to-br from-violet-500 to-purple-500',
        purple: 'bg-gradient-to-br from-purple-500 to-fuchsia-500',
        blue: 'bg-gradient-to-br from-blue-500 to-cyan-500',
      }
      return classes[color] || classes.primary
    },
    getCardHeaderClasses(color) {
      const classes = {
        primary: 'bg-gradient-to-r from-indigo-400 via-violet-400 to-indigo-400 opacity-80',
        violet: 'bg-gradient-to-r from-violet-400 via-purple-400 to-violet-400 opacity-80',
        purple: 'bg-gradient-to-r from-purple-400 via-fuchsia-400 to-purple-400 opacity-80',
        blue: 'bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-400 opacity-80',
      }
      return classes[color] || classes.primary
    },
    getIconContainerClasses(color) {
      const classes = {
        primary: 'bg-gradient-to-br from-indigo-400/20 to-violet-400/20 border-indigo-400/20',
        violet: 'bg-gradient-to-br from-violet-400/20 to-purple-400/20 border-violet-400/20',
        purple: 'bg-gradient-to-br from-purple-400/20 to-fuchsia-400/20 border-purple-400/20',
        blue: 'bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border-blue-400/20',
      }
      return classes[color] || classes.primary
    },
    getIconClasses(color) {
      const classes = {
        primary: 'text-indigo-300',
        violet: 'text-violet-300',
        purple: 'text-purple-300',
        blue: 'text-blue-300',
      }
      return classes[color] || classes.primary
    },
    getTagClasses(color) {
      const classes = {
        primary: 'bg-gradient-to-r from-indigo-500/10 to-violet-500/10 text-indigo-300 border-indigo-400/20',
        violet: 'bg-gradient-to-r from-violet-500/10 to-purple-500/10 text-violet-300 border-violet-400/20',
        purple: 'bg-gradient-to-r from-purple-500/10 to-fuchsia-500/10 text-purple-300 border-purple-400/20',
        blue: 'bg-gradient-to-r from-blue-500/10 to-cyan-500/10 text-blue-300 border-blue-400/20',
      }
      return classes[color] || classes.primary
    },
    getFeatureIconBgClasses(color) {
      const classes = {
        primary: 'bg-gradient-to-br from-indigo-400/20 to-violet-400/20 border-indigo-400/20',
        violet: 'bg-gradient-to-br from-violet-400/20 to-purple-400/20 border-violet-400/20',
        purple: 'bg-gradient-to-br from-purple-400/20 to-fuchsia-400/20 border-purple-400/20',
        blue: 'bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border-blue-400/20',
      }
      return classes[color] || classes.primary
    },
    getFeatureIconClasses(color) {
      const classes = {
        primary: 'text-indigo-300',
        violet: 'text-violet-300',
        purple: 'text-purple-300',
        blue: 'text-blue-300',
      }
      return classes[color] || classes.primary
    },
    getConnectorLineClasses(color) {
      const classes = {
        primary: 'bg-indigo-500',
        violet: 'bg-violet-500',
        purple: 'bg-purple-500',
        blue: 'bg-blue-500',
      }
      return classes[color] || classes.primary
    },
    getConnectorGradientClasses(color) {
      const classes = {
        primary: 'bg-gradient-to-r from-indigo-400/60 to-violet-400/60',
        violet: 'bg-gradient-to-r from-violet-400/60 to-purple-400/60',
        purple: 'bg-gradient-to-r from-purple-400/60 to-fuchsia-400/60',
        blue: 'bg-gradient-to-r from-blue-400/60 to-cyan-400/60',
      }
      return classes[color] || classes.primary
    },
    getCardBackgroundClasses(color) {
      const classes = {
        primary: 'bg-gradient-to-br from-indigo-400/4 to-violet-400/4',
        violet: 'bg-gradient-to-br from-violet-400/4 to-purple-400/4',
        purple: 'bg-gradient-to-br from-purple-400/4 to-fuchsia-400/4',
        blue: 'bg-gradient-to-br from-blue-400/4 to-cyan-400/4',
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