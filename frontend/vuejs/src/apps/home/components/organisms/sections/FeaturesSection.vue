<!-- Features Section Component with Modern UI -->
<template>
  <section class="py-16 sm:py-20 md:py-32 px-4 sm:px-6 lg:px-8 relative">
    <!-- Background decorative elements -->
    <div class="absolute inset-0 pointer-events-none overflow-hidden">
      <div class="absolute top-[30%] right-[5%] w-[300px] sm:w-[400px] md:w-[500px] h-[300px] sm:h-[400px] md:h-[500px] rounded-full bg-primary-600/10 blur-[100px] animate-pulse-slow"></div>
      <div class="absolute bottom-[20%] left-[10%] w-[250px] sm:w-[300px] md:w-[400px] h-[250px] sm:h-[300px] md:h-[400px] rounded-full bg-violet-600/10 blur-[80px] animate-pulse-slow animation-delay-150"></div>
    </div>
    
    <div class="max-w-7xl mx-auto relative">
      <!-- Enhanced section header with animation -->
      <div class="text-center mb-10 sm:mb-16 relative">
        <div class="inline-block px-3 sm:px-4 py-1 sm:py-1.5 bg-primary-500/10 rounded-full mb-3">
          <span class="text-primary-400 font-semibold text-xs sm:text-sm tracking-wider">POWERFUL FEATURES</span>
        </div>
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-3 sm:mb-4 leading-tight">{{ title }}</h2>
        <p class="text-base sm:text-lg md:text-xl text-gray-300 max-w-3xl mx-auto">{{ subtitle }}</p>
        
        <!-- Decorative element -->
        <div class="w-16 sm:w-24 h-1 bg-gradient-to-r from-primary-500 to-violet-500 rounded-full mx-auto mt-6 sm:mt-8"></div>
      </div>

      <!-- Enhanced 3D-like feature cards with improved glassmorphism -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8 lg:gap-10">
        <div 
          v-for="(feature, index) in features" 
          :key="index"
          class="feature-card group relative transform transition-all duration-300 hover:-translate-y-2"
        >
          <!-- Enhanced glass morphism effect with glow -->
          <div class="absolute -inset-0.5 rounded-2xl opacity-0 blur group-hover:blur-md transition-all duration-300"
               :class="getGradientBorderClass(feature.color)"></div>
               
          <!-- Card with enhanced glass morphism effect -->
          <div class="relative h-full bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden p-6 sm:p-8 border border-dark-800/50 group-hover:border-opacity-0 transition-all duration-300">
            
            <!-- Card header with gradient -->
            <div class="absolute top-0 inset-x-0 h-1.5 w-full transition-all duration-300"
                 :class="getHeaderGradientClass(feature.color)"></div>
            
            <!-- Subtle gradient background -->
            <div class="absolute inset-0 bg-gradient-to-br opacity-10 -z-10 transition-opacity duration-300 group-hover:opacity-20"
                 :class="getGradientClass(feature.color)"></div>
            
            <!-- Glowing orb in corner -->
            <div class="absolute -top-20 -right-20 w-32 sm:w-40 h-32 sm:h-40 rounded-full opacity-20 blur-2xl transition-all duration-300 group-hover:opacity-40 group-hover:scale-125"
                 :class="getOrbClass(feature.color)"></div>
                 
            <!-- Icon container with enhanced 3D effect -->
            <div class="w-12 h-12 sm:w-14 sm:h-14 flex items-center justify-center rounded-xl mb-4 sm:mb-6 transform transition-all duration-300 shadow-lg group-hover:shadow-xl group-hover:scale-110"
                 :class="getIconContainerClass(feature.color)">
              <i :class="[feature.icon, 'text-xl sm:text-2xl transition-all duration-300', getIconClass(feature.color)]"></i>
            </div>
            
            <h3 class="text-lg sm:text-xl font-bold mb-2 sm:mb-3 transition-all duration-300 group-hover:text-white">{{ feature.title }}</h3>
            <p class="text-sm sm:text-base text-gray-400 transition-all duration-300 group-hover:text-gray-300">{{ feature.description }}</p>
            
            <!-- Learn more button with subtle styling -->
            <div class="mt-4 pt-3 border-t border-dark-700/50 flex items-center">
              <a href="#" class="text-sm font-medium flex items-center group/btn transition-all duration-300" :class="getLinkClass(feature.color)">
                <span>Learn more</span>
                <i class="fas fa-arrow-right ml-2 text-xs transform group-hover/btn:translate-x-1 transition-transform duration-300"></i>
              </a>
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
  name: 'FeaturesSection',
  props: {
    title: {
      type: String,
      default: 'Supercharge Your Web Development'
    },
    subtitle: {
      type: String,
      default: 'Our platform combines AI-powered code generation with intuitive tools to streamline the development process.'
    },
    features: {
      type: Array,
      default: () => [
        {
          title: 'AI-Powered Code Generation',
          description: 'Generate clean, production-ready code from natural language descriptions with our advanced AI models.',
          icon: 'fas fa-robot',
          color: 'primary'
        },
        {
          title: 'Responsive Design',
          description: 'Create applications that look great on any device with automatic responsive layouts and components.',
          icon: 'fas fa-mobile-alt',
          color: 'purple'
        },
        {
          title: 'Database Integration',
          description: 'Connect to your database of choice with seamless integration and automatic schema generation.',
          icon: 'fas fa-database',
          color: 'blue'
        },
        {
          title: 'API Development',
          description: 'Build robust APIs quickly with automatic endpoint generation and documentation.',
          icon: 'fas fa-code',
          color: 'teal'
        },
        {
          title: 'Collaboration Tools',
          description: 'Work together smoothly with real-time collaboration features and version control integration.',
          icon: 'fas fa-users',
          color: 'indigo'
        },
        {
          title: 'Deployment Ready',
          description: 'Deploy your applications to your favorite cloud provider with one-click deployment options.',
          icon: 'fas fa-cloud-upload-alt',
          color: 'violet'
        }
      ]
    }
  },
  methods: {
    getFeatureColor(color) {
      const colors = {
        primary: 'rgba(59, 130, 246, 0.5)',
        blue: 'rgba(37, 99, 235, 0.5)',
        indigo: 'rgba(79, 70, 229, 0.5)',
        purple: 'rgba(147, 51, 234, 0.5)',
        violet: 'rgba(139, 92, 246, 0.5)',
        teal: 'rgba(20, 184, 166, 0.5)'
      }
      return colors[color] || colors.primary
    },
    getGradientClass(color) {
      const classes = {
        primary: 'from-primary-900 to-primary-700',
        blue: 'from-blue-900 to-blue-700',
        indigo: 'from-indigo-900 to-indigo-700',
        purple: 'from-purple-900 to-purple-700',
        violet: 'from-violet-900 to-violet-700',
        teal: 'from-teal-900 to-teal-700'
      }
      return classes[color] || classes.primary
    },
    getHeaderGradientClass(color) {
      const classes = {
        primary: 'bg-gradient-to-r from-primary-500 to-primary-600',
        blue: 'bg-gradient-to-r from-blue-500 to-blue-600',
        indigo: 'bg-gradient-to-r from-indigo-500 to-indigo-600',
        purple: 'bg-gradient-to-r from-purple-500 to-purple-600',
        violet: 'bg-gradient-to-r from-violet-500 to-violet-600',
        teal: 'bg-gradient-to-r from-teal-500 to-teal-600'
      }
      return classes[color] || classes.primary
    },
    getGradientBorderClass(color) {
      const classes = {
        primary: 'bg-gradient-to-r from-primary-500/50 to-violet-500/50 group-hover:opacity-70',
        blue: 'bg-gradient-to-r from-blue-500/50 to-indigo-500/50 group-hover:opacity-70',
        indigo: 'bg-gradient-to-r from-indigo-500/50 to-purple-500/50 group-hover:opacity-70',
        purple: 'bg-gradient-to-r from-purple-500/50 to-violet-500/50 group-hover:opacity-70',
        violet: 'bg-gradient-to-r from-violet-500/50 to-fuchsia-500/50 group-hover:opacity-70',
        teal: 'bg-gradient-to-r from-teal-500/50 to-emerald-500/50 group-hover:opacity-70'
      }
      return classes[color] || classes.primary
    },
    getOrbClass(color) {
      const classes = {
        primary: 'bg-primary-500',
        blue: 'bg-blue-500',
        indigo: 'bg-indigo-500',
        purple: 'bg-purple-500',
        violet: 'bg-violet-500',
        teal: 'bg-teal-500'
      }
      return classes[color] || classes.primary
    },
    getIconContainerClass(color) {
      const classes = {
        primary: 'bg-primary-500/10 border border-primary-500/20',
        blue: 'bg-blue-500/10 border border-blue-500/20',
        indigo: 'bg-indigo-500/10 border border-indigo-500/20',
        purple: 'bg-purple-500/10 border border-purple-500/20',
        violet: 'bg-violet-500/10 border border-violet-500/20',
        teal: 'bg-teal-500/10 border border-teal-500/20'
      }
      return classes[color] || classes.primary
    },
    getIconClass(color) {
      const classes = {
        primary: 'text-primary-400 group-hover:text-primary-300',
        blue: 'text-blue-400 group-hover:text-blue-300',
        indigo: 'text-indigo-400 group-hover:text-indigo-300',
        purple: 'text-purple-400 group-hover:text-purple-300',
        violet: 'text-violet-400 group-hover:text-violet-300',
        teal: 'text-teal-400 group-hover:text-teal-300'
      }
      return classes[color] || classes.primary
    },
    getLinkClass(color) {
      const classes = {
        primary: 'text-primary-400 hover:text-primary-300',
        blue: 'text-blue-400 hover:text-blue-300',
        indigo: 'text-indigo-400 hover:text-indigo-300',
        purple: 'text-purple-400 hover:text-purple-300',
        violet: 'text-violet-400 hover:text-violet-300',
        teal: 'text-teal-400 hover:text-teal-300'
      }
      return classes[color] || classes.primary
    }
  }
})
</script>

<style scoped>
/* Custom glow shadow for feature cards */
.shadow-glow {
  box-shadow: 0 0 20px var(--feature-color);
}

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