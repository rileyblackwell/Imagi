<!-- Use Cases Section Component with Interactive 3D Cards -->
<template>
  <section class="py-24 md:py-36 px-6 sm:px-8 lg:px-12 relative overflow-hidden">
    <!-- Decorative elements -->
    <div class="absolute inset-0 pointer-events-none">
      <!-- Pattern overlay -->
      <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
      
      <!-- Gradient spots -->
      <div class="absolute top-[10%] right-[20%] w-[600px] h-[600px] rounded-full bg-violet-600/5 blur-[120px] animate-pulse-slow"></div>
      <div class="absolute bottom-[20%] left-[10%] w-[500px] h-[500px] rounded-full bg-indigo-600/5 blur-[100px] animate-pulse-slow animation-delay-150"></div>
    </div>
    
    <div class="max-w-7xl mx-auto">
      <!-- Section header with modern badge -->
      <div class="text-center mb-16 relative">
        <!-- Modern pill badge -->
        <div class="inline-flex items-center px-4 py-1.5 bg-gradient-to-r from-violet-500/10 to-purple-500/10 rounded-full border border-violet-400/20 backdrop-blur-sm mb-6">
          <div class="w-1.5 h-1.5 bg-violet-400 rounded-full mr-2 animate-pulse"></div>
          <span class="text-violet-300 font-medium text-sm tracking-wide uppercase">Endless Possibilities</span>
        </div>
        <h2 class="text-4xl md:text-5xl font-bold text-white mb-4 leading-tight">{{ title }}</h2>
        <p class="text-xl text-gray-300 max-w-3xl mx-auto">{{ subtitle }}</p>
        
        <!-- Modern divider -->
        <div class="w-full h-px bg-gradient-to-r from-transparent via-violet-500/30 to-transparent mt-8"></div>
      </div>

      <!-- Modern cards with enhanced glass morphism -->
      <div class="relative">
        <!-- Showcase cards with glass morphism effects -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8">
          <div 
            v-for="(useCase, index) in useCases" 
            :key="index"
            class="group relative transform transition-all duration-300 hover:-translate-y-1"
          >
            <!-- Modern glassmorphism container -->
            <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden h-full transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
              <!-- Sleek gradient header -->
              <div class="h-1 w-full transition-all duration-300"
                   :class="getHeaderGradientClass(useCase.color)"></div>
              
              <!-- Subtle background effects -->
              <div class="absolute -top-32 -right-32 w-64 h-64 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"
                   :class="getCardBackgroundClass(useCase.color)"></div>
              
              <!-- Card content -->
              <div class="relative z-10 p-6 h-full flex flex-col">
                <!-- Icon with enhanced styling -->
                <div class="w-12 h-12 rounded-xl mb-5 flex items-center justify-center border transition-all duration-300"
                     :class="getIconContainerClass(useCase.color)">
                  <i :class="[useCase.icon, 'text-lg', getIconClass(useCase.color)]"></i>
                </div>
                
                <!-- Title with enhanced styling -->
                <h3 class="text-xl font-semibold text-white mb-3 leading-tight">{{ useCase.title }}</h3>
                
                <!-- Description with better readability -->
                <p class="text-gray-300 mb-4 text-sm leading-relaxed flex-1">{{ useCase.description }}</p>
                
                <!-- Modern separator -->
                <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-4"></div>
                
                <!-- Feature list with modern styling -->
                <ul class="space-y-2 mb-5">
                  <li v-for="(feature, fIndex) in useCase.features" :key="fIndex" 
                      class="flex items-start gap-2">
                    <div class="w-4 h-4 rounded-full flex-shrink-0 flex items-center justify-center mt-0.5 border"
                         :class="getFeatureIconBgClass(useCase.color)">
                      <i class="fas fa-check text-xs" :class="getFeatureIconClass(useCase.color)"></i>
                    </div>
                    <span class="text-gray-300 text-xs leading-relaxed">{{ feature }}</span>
                  </li>
                </ul>
                
                <!-- Learn more link with enhanced styling -->
                <div class="mt-auto">
                  <a href="#" class="text-sm font-medium flex items-center group/btn transition-all duration-300"
                     :class="getLinkClass(useCase.color)">
                    <span>Learn more</span>
                    <i class="fas fa-arrow-right ml-2 text-xs transform group-hover/btn:translate-x-1 transition-transform duration-300"></i>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Simple CTA Button -->
      <div class="mt-16 text-center">
        <HomeNavbarButton
          :to="{ name: isAuthenticated ? 'builder-dashboard' : 'login' }"
          class="group relative !h-12 sm:!h-14 px-8 rounded-xl bg-gradient-to-r from-violet-500 to-purple-500 hover:from-violet-400 hover:to-purple-400 text-white font-medium transition-all duration-300 transform hover:-translate-y-1 shadow-lg shadow-violet-500/25"
        >
          <span class="flex items-center justify-center text-lg">
            Start Your Project
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
  name: 'UseCasesSection',
  components: {
    HomeNavbarButton
  },
  props: {
    title: {
      type: String,
      default: 'What Can You Build Today?'
    },
    subtitle: {
      type: String,
      default: 'Currently, Imagi supports basic web apps with HTML, CSS, and JavaScript. Here are some types of apps you can build right now for just a few dollars.'
    },
    useCases: {
      type: Array,
      default: () => [
        {
          title: 'Personal Resume',
          description: 'Create a professional online resume web app to showcase your skills, experience, and achievements to potential employers.',
          icon: 'fas fa-id-card',
          color: 'primary',
          features: [
            'Professional layout',
            'Skills and experience sections',
            'Contact information'
          ]
        },
        {
          title: 'Business Info Web App',
          description: 'Build a simple web app for your business with information about your services, team members, and how to contact you.',
          icon: 'fas fa-building',
          color: 'violet',
          features: [
            'Service descriptions',
            'Company information',
            'Contact details'
          ]
        },
        {
          title: 'Personal Bio',
          description: 'Create a personal web app to share your story, interests, and accomplishments with friends, family, or the world.',
          icon: 'fas fa-user',
          color: 'blue',
          features: [
            'About me section',
            'Photo gallery',
            'Personal achievements'
          ]
        },
        {
          title: 'Content Display',
          description: 'Build a web app to display any type of content - like a digital portfolio, hobby showcase, or informational resource.',
          icon: 'fas fa-newspaper',
          color: 'purple',
          features: [
            'Custom content sections',
            'Image galleries',
            'Information displays'
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
    getHeaderGradientClass(color) {
      const classes = {
        primary: 'bg-gradient-to-r from-indigo-400 via-violet-400 to-indigo-400 opacity-80',
        violet: 'bg-gradient-to-r from-violet-400 via-purple-400 to-violet-400 opacity-80',
        purple: 'bg-gradient-to-r from-purple-400 via-fuchsia-400 to-purple-400 opacity-80',
        blue: 'bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-400 opacity-80',
      }
      return classes[color] || classes.primary
    },
    getCardBackgroundClass(color) {
      const classes = {
        primary: 'bg-gradient-to-br from-indigo-400/4 to-violet-400/4',
        violet: 'bg-gradient-to-br from-violet-400/4 to-purple-400/4',
        purple: 'bg-gradient-to-br from-purple-400/4 to-fuchsia-400/4',
        blue: 'bg-gradient-to-br from-blue-400/4 to-cyan-400/4',
      }
      return classes[color] || classes.primary
    },
    getIconContainerClass(color) {
      const classes = {
        primary: 'bg-gradient-to-br from-indigo-400/20 to-violet-400/20 border-indigo-400/20',
        violet: 'bg-gradient-to-br from-violet-400/20 to-purple-400/20 border-violet-400/20',
        purple: 'bg-gradient-to-br from-purple-400/20 to-fuchsia-400/20 border-purple-400/20',
        blue: 'bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border-blue-400/20',
      }
      return classes[color] || classes.primary
    },
    getIconClass(color) {
      const classes = {
        primary: 'text-indigo-300',
        violet: 'text-violet-300',
        purple: 'text-purple-300',
        blue: 'text-blue-300',
      }
      return classes[color] || classes.primary
    },
    getFeatureIconBgClass(color) {
      const classes = {
        primary: 'bg-gradient-to-br from-indigo-400/20 to-violet-400/20 border-indigo-400/20',
        violet: 'bg-gradient-to-br from-violet-400/20 to-purple-400/20 border-violet-400/20',
        purple: 'bg-gradient-to-br from-purple-400/20 to-fuchsia-400/20 border-purple-400/20',
        blue: 'bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border-blue-400/20',
      }
      return classes[color] || classes.primary
    },
    getFeatureIconClass(color) {
      const classes = {
        primary: 'text-indigo-300',
        violet: 'text-violet-300',
        purple: 'text-purple-300',
        blue: 'text-blue-300',
      }
      return classes[color] || classes.primary
    },
    getLinkClass(color) {
      const classes = {
        primary: 'text-indigo-400 hover:text-indigo-300',
        violet: 'text-violet-400 hover:text-violet-300',
        purple: 'text-purple-400 hover:text-purple-300',
        blue: 'text-blue-400 hover:text-blue-300',
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