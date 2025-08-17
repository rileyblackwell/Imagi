<!-- Features Section Component with Modern UI -->
<template>
  <section class="py-16 sm:py-20 md:py-32 px-6 sm:px-8 lg:px-12 relative">
    <!-- Background decorative elements -->
    <div class="absolute inset-0 pointer-events-none overflow-hidden">
      <div class="absolute top-[30%] right-[5%] w-[400px] h-[400px] rounded-full bg-indigo-600/5 blur-[100px] animate-pulse-slow"></div>
      <div class="absolute bottom-[20%] left-[10%] w-[300px] h-[300px] rounded-full bg-violet-600/5 blur-[80px] animate-pulse-slow animation-delay-150"></div>
    </div>
    
    <div class="max-w-7xl mx-auto relative">
      <!-- Enhanced section header with modern badge -->
      <div class="text-center mb-12 sm:mb-16 relative">
        <!-- Modern pill badge -->
        <div class="inline-flex items-center px-4 py-1.5 bg-gradient-to-r from-indigo-500/10 to-violet-500/10 rounded-full border border-indigo-400/20 backdrop-blur-sm mb-6">
          <div class="w-1.5 h-1.5 bg-indigo-400 rounded-full mr-2 animate-pulse"></div>
          <span class="text-indigo-300 font-medium text-sm tracking-wide uppercase">Powerful Features</span>
        </div>
        
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-4 leading-tight">{{ title }}</h2>
        <p class="text-lg sm:text-xl text-gray-300 max-w-3xl mx-auto">{{ subtitle }}</p>
        
        <!-- Modern divider -->
        <div class="w-full h-px bg-gradient-to-r from-transparent via-primary-500/30 to-transparent mt-8"></div>
      </div>

      <!-- Enhanced feature cards with modern glassmorphism -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
        <div 
          v-for="(feature, index) in features" 
          :key="index"
          class="group relative transform transition-all duration-300 hover:-translate-y-1"
        >
          <!-- Modern glassmorphism container -->
          <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden h-full transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
            <!-- Sleek gradient header -->
            <div class="h-1 w-full transition-all duration-300"
                 :class="getHeaderGradientClass(feature.color)"></div>
            
            <!-- Subtle background effects -->
            <div class="absolute -top-32 -right-32 w-64 h-64 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"
                 :class="getOrbClass(feature.color)"></div>
            
            <div class="relative z-10 p-6 sm:p-8 h-full flex flex-col">
              <!-- Icon container with enhanced styling -->
              <div class="w-12 h-12 rounded-xl flex items-center justify-center mb-6 border transition-all duration-300"
                   :class="getIconContainerClass(feature.color)">
                <i :class="[feature.icon, 'text-lg', getIconClass(feature.color)]"></i>
              </div>
              
              <h3 class="text-xl font-semibold text-white mb-3 leading-tight">{{ feature.title }}</h3>
              <p class="text-gray-300 leading-relaxed flex-1">{{ feature.description }}</p>
              
              <!-- Modern separator -->
              <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent my-6"></div>
              
              <!-- Learn more link with modern styling -->
              <div class="flex items-center">
                <a href="#" class="text-sm font-medium flex items-center group/btn transition-all duration-300" :class="getLinkClass(feature.color)">
                  <span>Learn more</span>
                  <i class="fas fa-arrow-right ml-2 text-xs transform group-hover/btn:translate-x-1 transition-transform duration-300"></i>
                </a>
              </div>
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
      default: 'Full-Stack Apps Made Simple'
    },
    subtitle: {
      type: String,
      default: 'Build complete web applications with Vue.js frontends and Django backends in minutes - no technical knowledge required, just describe your vision.'
    },
    features: {
      type: Array,
      default: () => [
        {
          title: 'No Technical Skills Needed',
          description: 'Perfect for entrepreneurs, small business owners, and anyone with an idea. Just describe your app in plain English - no coding knowledge required.',
          icon: 'fas fa-user-friends',
          color: 'primary'
        },
        {
          title: 'Full-Stack Applications',
          description: 'Get complete web applications with professional Vue.js frontends and robust Django backends. Both parts work together seamlessly.',
          icon: 'fas fa-layer-group',
          color: 'purple'
        },
        {
          title: 'Minutes, Not Months',
          description: 'Build professional web applications in minutes that would normally take developers months and cost thousands of dollars to create.',
          icon: 'fas fa-bolt',
          color: 'blue'
        },
        {
          title: 'Affordable for Everyone',
          description: 'Pay only for what you build with our credit system. Create a complete full-stack web app for just a few dollars instead of hiring developers.',
          icon: 'fas fa-coins',
          color: 'teal'
        },
        {
          title: 'Natural Conversation',
          description: 'Edit and improve your app through simple conversation. Just describe changes you want, and the AI updates both frontend and backend instantly.',
          icon: 'fas fa-comments',
          color: 'indigo'
        },
        {
          title: 'Professional Results',
          description: 'Get production-ready applications with modern Vue.js interfaces and powerful Django APIs. Database integration and deployment coming soon.',
          icon: 'fas fa-rocket',
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
        primary: 'bg-gradient-to-r from-indigo-400 via-violet-400 to-indigo-400 opacity-80',
        blue: 'bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-400 opacity-80',
        indigo: 'bg-gradient-to-r from-indigo-400 via-purple-400 to-indigo-400 opacity-80',
        purple: 'bg-gradient-to-r from-purple-400 via-violet-400 to-purple-400 opacity-80',
        violet: 'bg-gradient-to-r from-violet-400 via-fuchsia-400 to-violet-400 opacity-80',
        teal: 'bg-gradient-to-r from-teal-400 via-emerald-400 to-teal-400 opacity-80'
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
        primary: 'bg-gradient-to-br from-indigo-400/4 to-violet-400/4',
        blue: 'bg-gradient-to-br from-blue-400/4 to-cyan-400/4',
        indigo: 'bg-gradient-to-br from-indigo-400/4 to-purple-400/4',
        purple: 'bg-gradient-to-br from-purple-400/4 to-violet-400/4',
        violet: 'bg-gradient-to-br from-violet-400/4 to-fuchsia-400/4',
        teal: 'bg-gradient-to-br from-teal-400/4 to-emerald-400/4'
      }
      return classes[color] || classes.primary
    },
    getIconContainerClass(color) {
      const classes = {
        primary: 'bg-gradient-to-br from-indigo-400/20 to-violet-400/20 border-indigo-400/20',
        blue: 'bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border-blue-400/20',
        indigo: 'bg-gradient-to-br from-indigo-400/20 to-purple-400/20 border-indigo-400/20',
        purple: 'bg-gradient-to-br from-purple-400/20 to-violet-400/20 border-purple-400/20',
        violet: 'bg-gradient-to-br from-violet-400/20 to-fuchsia-400/20 border-violet-400/20',
        teal: 'bg-gradient-to-br from-teal-400/20 to-emerald-400/20 border-teal-400/20'
      }
      return classes[color] || classes.primary
    },
    getIconClass(color) {
      const classes = {
        primary: 'text-indigo-300',
        blue: 'text-blue-300',
        indigo: 'text-indigo-300',
        purple: 'text-purple-300',
        violet: 'text-violet-300',
        teal: 'text-teal-300'
      }
      return classes[color] || classes.primary
    },
    getLinkClass(color) {
      const classes = {
        primary: 'text-indigo-400 hover:text-indigo-300',
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