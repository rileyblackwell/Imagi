<!-- Use Cases Section Component with Interactive 3D Cards -->
<template>
  <section class="py-24 md:py-36 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
    <!-- Decorative elements -->
    <div class="absolute inset-0 pointer-events-none">
      <!-- Pattern overlay -->
      <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
      
      <!-- Gradient spots -->
      <div class="absolute top-[10%] right-[20%] w-[600px] h-[600px] rounded-full bg-violet-600/5 blur-[120px] animate-pulse-slow"></div>
      <div class="absolute bottom-[20%] left-[10%] w-[500px] h-[500px] rounded-full bg-primary-600/5 blur-[100px] animate-pulse-slow animation-delay-150"></div>
    </div>
    
    <div class="max-w-7xl mx-auto">
      <!-- Section header with modern badge -->
      <div class="text-center mb-16 relative">
        <div class="inline-block px-4 py-1.5 bg-primary-500/10 rounded-full mb-3">
          <span class="text-primary-400 font-semibold text-sm tracking-wider">ENDLESS POSSIBILITIES</span>
        </div>
        <h2 class="text-4xl md:text-5xl font-bold text-white mb-4 leading-tight">{{ title }}</h2>
        <p class="text-xl text-gray-300 max-w-3xl mx-auto">{{ subtitle }}</p>
        
        <!-- Decorative element -->
        <div class="w-24 h-1 bg-gradient-to-r from-primary-500 to-violet-500 rounded-full mx-auto mt-8"></div>
      </div>

      <!-- Modern cards with enhanced glass morphism -->
      <div class="relative">
        <!-- Showcase cards with glass morphism effects -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 md:gap-6">
          <div 
            v-for="(useCase, index) in useCases" 
            :key="index"
            class="group relative transform transition-all duration-300 hover:-translate-y-2"
          >
            <!-- Enhanced glass morphism effect with glow -->
            <div class="absolute -inset-0.5 rounded-xl opacity-0 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"
                 :class="getGlowBorderClass(useCase.color)"></div>
            
            <!-- Card with enhanced glass morphism -->
            <div class="relative h-full bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden border border-dark-800/50 group-hover:border-opacity-0 transition-all duration-300">
              <!-- Card header with gradient -->
              <div class="h-2 w-full transition-all duration-300"
                   :class="getHeaderGradientClass(useCase.color)"></div>
              
              <!-- Card content -->
              <div class="p-6">
                <!-- Icon with enhanced styling -->
                <div class="w-14 h-14 rounded-xl mb-5 flex items-center justify-center transform transition-all duration-300 group-hover:scale-110"
                     :class="getIconContainerClass(useCase.color)">
                  <i :class="[useCase.icon, 'text-2xl', getIconClass(useCase.color)]"></i>
                </div>
                
                <!-- Title with enhanced styling -->
                <h3 class="text-xl font-bold text-white mb-2">{{ useCase.title }}</h3>
                
                <!-- Description with better readability -->
                <p class="text-gray-300 mb-4 text-sm leading-relaxed">{{ useCase.description }}</p>
                
                <!-- Feature list with modern styling -->
                <ul class="space-y-2 mb-5">
                  <li v-for="(feature, fIndex) in useCase.features" :key="fIndex" 
                      class="flex items-start gap-2">
                    <div class="w-5 h-5 rounded-full flex-shrink-0 flex items-center justify-center mt-0.5"
                         :class="getFeatureIconBgClass(useCase.color)">
                      <i class="fas fa-check text-xs" :class="getFeatureIconClass(useCase.color)"></i>
                    </div>
                    <span class="text-gray-300 text-sm">{{ feature }}</span>
                  </li>
                </ul>
                
                <!-- Learn more link with enhanced styling -->
                <div class="mt-auto pt-2 border-t border-dark-700/50">
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
      
      <!-- Enhanced CTA -->
      <div class="mt-16 text-center">
        <div class="inline-block group relative transform transition-all duration-300 hover:-translate-y-1">
          <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500/50 to-violet-500/50 rounded-xl opacity-30 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"></div>
          <HomeNavbarButton
            :to="{ name: isAuthenticated ? 'builder-dashboard' : 'login' }"
            class="relative !h-12 sm:!h-14 min-w-[160px] sm:min-w-[200px] px-6 sm:px-8 rounded-xl bg-dark-900/70 backdrop-blur-lg border border-dark-800/50 group-hover:border-opacity-0 transition-all duration-300"
          >
            <span class="relative z-10 flex items-center justify-center text-base sm:text-lg font-medium text-white">
              Start Your Project
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
    getGlowBorderClass(color) {
      const classes = {
        primary: 'bg-gradient-to-r from-primary-500/50 to-violet-500/50',
        violet: 'bg-gradient-to-r from-violet-500/50 to-purple-500/50',
        purple: 'bg-gradient-to-r from-purple-500/50 to-primary-500/50',
        blue: 'bg-gradient-to-r from-blue-500/50 to-violet-500/50',
      }
      return classes[color] || classes.primary
    },
    getHeaderGradientClass(color) {
      const classes = {
        primary: 'bg-gradient-to-r from-primary-500 to-violet-500',
        violet: 'bg-gradient-to-r from-violet-500 to-purple-500',
        purple: 'bg-gradient-to-r from-purple-500 to-primary-500',
        blue: 'bg-gradient-to-r from-blue-500 to-violet-500',
      }
      return classes[color] || classes.primary
    },
    getGradientClass(color) {
      const classes = {
        primary: 'from-primary-900 to-primary-700',
        violet: 'from-violet-900 to-violet-700',
        purple: 'from-purple-900 to-purple-700',
        blue: 'from-blue-900 to-blue-700',
      }
      return classes[color] || classes.primary
    },
    getIconContainerClass(color) {
      const classes = {
        primary: 'bg-primary-500/10 border border-primary-500/20',
        violet: 'bg-violet-500/10 border border-violet-500/20',
        purple: 'bg-purple-500/10 border border-purple-500/20',
        blue: 'bg-blue-500/10 border border-blue-500/20',
      }
      return classes[color] || classes.primary
    },
    getIconClass(color) {
      const classes = {
        primary: 'text-primary-400',
        violet: 'text-violet-400',
        purple: 'text-purple-400',
        blue: 'text-blue-400',
      }
      return classes[color] || classes.primary
    },
    getFeatureIconBgClass(color) {
      const classes = {
        primary: 'bg-primary-500/10',
        violet: 'bg-violet-500/10',
        purple: 'bg-purple-500/10',
        blue: 'bg-blue-500/10',
      }
      return classes[color] || classes.primary
    },
    getFeatureIconClass(color) {
      const classes = {
        primary: 'text-primary-400',
        violet: 'text-violet-400',
        purple: 'text-purple-400',
        blue: 'text-blue-400',
      }
      return classes[color] || classes.primary
    },
    getLinkClass(color) {
      const classes = {
        primary: 'text-primary-400 hover:text-primary-300',
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