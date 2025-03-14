<!-- Features Section Component with Modern UI -->
<template>
  <section class="py-20 md:py-32 px-4 sm:px-6 lg:px-8 relative">
    <!-- Background decorative elements -->
    <div class="absolute inset-0 pointer-events-none overflow-hidden">
      <div class="absolute top-[30%] right-[5%] w-[500px] h-[500px] rounded-full bg-primary-600/10 blur-[100px]"></div>
      <div class="absolute bottom-[20%] left-[10%] w-[400px] h-[400px] rounded-full bg-violet-600/10 blur-[80px]"></div>
    </div>
    
    <div class="max-w-7xl mx-auto relative">
      <!-- Enhanced section header with animation -->
      <div class="text-center mb-16 relative">
        <div class="inline-block px-4 py-1.5 bg-primary-500/10 rounded-full mb-3">
          <span class="text-primary-400 font-semibold text-sm tracking-wider">POWERFUL FEATURES</span>
        </div>
        <h2 class="text-4xl md:text-5xl font-bold text-white mb-4 leading-tight">{{ title }}</h2>
        <p class="text-xl text-gray-300 max-w-3xl mx-auto">{{ subtitle }}</p>
        
        <!-- Decorative element -->
        <div class="w-24 h-1 bg-gradient-to-r from-primary-500 to-violet-500 rounded-full mx-auto mt-8"></div>
      </div>

      <!-- 3D-like feature cards with glassmorphism -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 lg:gap-10">
        <div 
          v-for="(feature, index) in features" 
          :key="index"
          class="feature-card relative group"
        >
          <!-- Card with 3D hover effect -->
          <div class="relative h-full p-8 rounded-2xl border border-gray-800/50 bg-dark-900/40 backdrop-blur-sm transition-all duration-300 overflow-hidden group-hover:shadow-glow group-hover:shadow-[--feature-color] group-hover:-translate-y-1"
               :style="{ '--feature-color': getFeatureColor(feature.color) }">
            
            <!-- Subtle gradient background -->
            <div class="absolute inset-0 bg-gradient-to-br opacity-20 -z-10 transition-opacity duration-300 group-hover:opacity-30"
                 :class="getGradientClass(feature.color)"></div>
            
            <!-- Glowing orb in corner -->
            <div class="absolute -top-20 -right-20 w-40 h-40 rounded-full opacity-20 blur-2xl transition-all duration-300 group-hover:opacity-40 group-hover:scale-125"
                 :class="getOrbClass(feature.color)"></div>
                 
            <!-- Icon container with 3D effect -->
            <div class="w-14 h-14 flex items-center justify-center rounded-xl mb-6 transform transition-all duration-300 shadow-lg group-hover:shadow-xl"
                 :class="getIconContainerClass(feature.color)">
              <i :class="[feature.icon, 'text-2xl transition-all duration-300', getIconClass(feature.color)]"></i>
            </div>
            
            <h3 class="text-xl font-bold mb-3 transition-all duration-300 group-hover:text-white">{{ feature.title }}</h3>
            <p class="text-gray-400 transition-all duration-300 group-hover:text-gray-300">{{ feature.description }}</p>
            
            <!-- Subtle "Learn more" link -->
            <div class="mt-6 flex items-center text-sm font-medium transition-all duration-300"
                 :class="getLinkClass(feature.color)">
              <span>Learn more</span>
              <i class="fas fa-arrow-right ml-2 text-xs transition-all duration-300 group-hover:translate-x-1"></i>
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
      default: 'Why Choose Imagi'
    },
    subtitle: {
      type: String,
      default: 'Transform your ideas into reality with powerful AI-driven web development'
    },
    features: {
      type: Array,
      default: () => [
        {
          title: 'Natural Language Input',
          description: 'Describe your vision in plain English, and watch as it transforms into reality with our advanced AI technology.',
          icon: 'fas fa-keyboard',
          color: 'primary'
        },
        {
          title: 'Rapid Development',
          description: 'Build websites and applications in minutes, not months. Our AI optimizes the entire development lifecycle.',
          icon: 'fas fa-bolt',
          color: 'indigo'
        },
        {
          title: 'Professional Code',
          description: 'Generate clean, maintainable code that follows industry best practices and scales with your business needs.',
          icon: 'fas fa-code',
          color: 'violet'
        }
      ]
    }
  },
  methods: {
    getFeatureColor(color) {
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
    getIconContainerClass(color) {
      const classes = {
        primary: 'bg-primary-500/10 border border-primary-500/20',
        indigo: 'bg-indigo-500/10 border border-indigo-500/20',
        violet: 'bg-violet-500/10 border border-violet-500/20',
        fuchsia: 'bg-fuchsia-500/10 border border-fuchsia-500/20'
      };
      return classes[color] || classes.primary;
    },
    getIconClass(color) {
      const classes = {
        primary: 'text-primary-400 group-hover:text-primary-300',
        indigo: 'text-indigo-400 group-hover:text-indigo-300',
        violet: 'text-violet-400 group-hover:text-violet-300',
        fuchsia: 'text-fuchsia-400 group-hover:text-fuchsia-300'
      };
      return classes[color] || classes.primary;
    },
    getLinkClass(color) {
      const classes = {
        primary: 'text-primary-400 group-hover:text-primary-300',
        indigo: 'text-indigo-400 group-hover:text-indigo-300',
        violet: 'text-violet-400 group-hover:text-violet-300',
        fuchsia: 'text-fuchsia-400 group-hover:text-fuchsia-300'
      };
      return classes[color] || classes.primary;
    }
  }
})
</script>

<style scoped>
.feature-card {
  perspective: 1000px;
}

.shadow-glow {
  box-shadow: 0 0 25px -5px var(--feature-color);
}

/* Custom animations for subtle hover effects */
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-5px); }
}

.animate-float {
  animation: float 5s ease-in-out infinite;
}
</style> 