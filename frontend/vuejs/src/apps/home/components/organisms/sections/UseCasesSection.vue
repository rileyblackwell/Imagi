<!-- Use Cases Section Component with Interactive 3D Cards -->
<template>
  <section class="py-24 md:py-36 px-4 sm:px-6 lg:px-8 relative overflow-hidden bg-dark-950/40">
    <!-- Decorative elements -->
    <div class="absolute inset-0 pointer-events-none">
      <!-- Pattern overlay -->
      <div class="absolute inset-0 bg-[url('/circuit-pattern.svg')] opacity-[0.04]"></div>
      
      <!-- Gradient spots -->
      <div class="absolute top-[10%] right-[20%] w-[600px] h-[600px] rounded-full bg-violet-600/5 blur-[120px]"></div>
      <div class="absolute bottom-[20%] left-[10%] w-[500px] h-[500px] rounded-full bg-primary-600/5 blur-[100px]"></div>
    </div>
    
    <div class="max-w-7xl mx-auto">
      <!-- Section header with modern badge -->
      <div class="text-center mb-16 relative">
        <div class="inline-block px-4 py-1.5 bg-violet-500/10 rounded-full mb-3">
          <span class="text-violet-400 font-semibold text-sm tracking-wider">ENDLESS POSSIBILITIES</span>
        </div>
        <h2 class="text-4xl md:text-5xl font-bold text-white mb-4 leading-tight">{{ title }}</h2>
        <p class="text-xl text-gray-300 max-w-3xl mx-auto">{{ subtitle }}</p>
        
        <!-- Decorative element -->
        <div class="w-24 h-1 bg-gradient-to-r from-violet-500 to-fuchsia-500 rounded-full mx-auto mt-8"></div>
      </div>

      <!-- Modern 3D carousel-style layout -->
      <div class="relative">
        <!-- Showcase cards with 3D effects -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 md:gap-6">
          <div 
            v-for="(useCase, index) in useCases" 
            :key="index"
            class="use-case-card relative transform transition-all duration-500 hover:scale-105 hover:-translate-y-2"
          >
            <!-- 3D tilting card with glassmorphism -->
            <div class="card-3d h-full bg-dark-900/40 backdrop-blur-sm border border-gray-800/50 rounded-2xl p-6 overflow-hidden relative group">
              <!-- Gradient background -->
              <div class="absolute inset-0 bg-gradient-to-br opacity-10 -z-10 transition-opacity duration-300 group-hover:opacity-20"
                   :class="getGradientClass(useCase.color)"></div>
              
              <!-- Glowing orb effect -->
              <div class="absolute -bottom-24 -left-24 w-48 h-48 rounded-full blur-3xl opacity-20 transition-all duration-500 group-hover:opacity-30 group-hover:scale-125"
                   :class="getOrbClass(useCase.color)"></div>
                   
              <!-- Icon with advanced 3D effect -->
              <div class="icon-container relative w-16 h-16 rounded-2xl flex items-center justify-center mb-5 transform transition-all duration-500 group-hover:-translate-y-1"
                   :class="getIconBgClass(useCase.color)">
                <i :class="[useCase.icon, 'text-2xl', getIconClass(useCase.color)]"></i>
                
                <!-- Icon shadow -->
                <div class="absolute w-full h-full rounded-2xl top-0 left-0 blur-md -z-10 opacity-70 scale-90"
                     :class="getIconShadowClass(useCase.color)"></div>
              </div>
              
              <!-- Content with 3D stacking -->
              <div class="stack-content relative z-10">
                <h3 class="text-xl font-bold mb-3 text-white">{{ useCase.title }}</h3>
                <p class="text-gray-400 mb-5 transition-all duration-300 group-hover:text-gray-300">{{ useCase.description }}</p>
                
                <!-- Interactive "Examples" badge -->
                <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-medium border transition-all duration-300"
                     :class="getBadgeClass(useCase.color)">
                  <span class="relative flex h-2 w-2">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
                          :class="getPingClass(useCase.color)"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2"
                          :class="getDotClass(useCase.color)"></span>
                  </span>
                  <span>View Examples</span>
                </div>
              </div>
              
              <!-- Interactive hover effect overlay -->
              <div class="absolute inset-0 rounded-2xl border-2 opacity-0 transition-opacity duration-300 group-hover:opacity-20 pointer-events-none"
                   :class="getBorderClass(useCase.color)"></div>
            </div>
          </div>
        </div>
        
        <!-- Centered gradient line -->
        <div class="absolute top-[calc(50%-1px)] left-0 right-0 h-px bg-gradient-to-r from-transparent via-fuchsia-500/30 to-transparent -z-10 hidden lg:block"></div>
      </div>
      
      <!-- "View All Use Cases" button -->
      <div class="text-center mt-16">
        <button class="px-8 py-3 rounded-full bg-dark-800/70 border border-violet-500/30 text-white font-medium transition-all duration-300 hover:bg-violet-500/20 hover:border-violet-500/50 shadow-lg shadow-violet-900/20">
          <span>View All Use Cases</span>
          <i class="fas fa-arrow-right ml-2"></i>
        </button>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'UseCasesSection',
  props: {
    title: {
      type: String,
      default: 'What You Can Build'
    },
    subtitle: {
      type: String,
      default: 'Create a wide range of applications for any purpose with Imagi'
    },
    useCases: {
      type: Array,
      default: () => [
        {
          title: 'E-commerce Sites',
          description: 'Create full-featured online stores with product catalogs, shopping carts, and secure payment processing systems.',
          icon: 'fas fa-store',
          color: 'primary'
        },
        {
          title: 'Business Applications',
          description: 'Build custom CRM systems, inventory management tools, and other business-specific applications with robust workflows.',
          icon: 'fas fa-briefcase',
          color: 'indigo'
        },
        {
          title: 'Community Platforms',
          description: 'Develop social networks, forums, and community-driven websites with user management and content sharing features.',
          icon: 'fas fa-users',
          color: 'violet'
        },
        {
          title: 'Analytics Dashboards',
          description: 'Create data visualization tools and interactive dashboards for business intelligence with customizable charts and reports.',
          icon: 'fas fa-chart-line',
          color: 'fuchsia'
        }
      ]
    }
  },
  methods: {
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
    getIconBgClass(color) {
      const classes = {
        primary: 'bg-primary-900/80 border border-primary-700/50',
        indigo: 'bg-indigo-900/80 border border-indigo-700/50',
        violet: 'bg-violet-900/80 border border-violet-700/50',
        fuchsia: 'bg-fuchsia-900/80 border border-fuchsia-700/50'
      };
      return classes[color] || classes.primary;
    },
    getIconClass(color) {
      const classes = {
        primary: 'text-primary-400',
        indigo: 'text-indigo-400',
        violet: 'text-violet-400',
        fuchsia: 'text-fuchsia-400'
      };
      return classes[color] || classes.primary;
    },
    getIconShadowClass(color) {
      const classes = {
        primary: 'bg-primary-500/30',
        indigo: 'bg-indigo-500/30',
        violet: 'bg-violet-500/30',
        fuchsia: 'bg-fuchsia-500/30'
      };
      return classes[color] || classes.primary;
    },
    getBadgeClass(color) {
      const classes = {
        primary: 'border-primary-500/30 text-primary-400 hover:bg-primary-500/10',
        indigo: 'border-indigo-500/30 text-indigo-400 hover:bg-indigo-500/10',
        violet: 'border-violet-500/30 text-violet-400 hover:bg-violet-500/10',
        fuchsia: 'border-fuchsia-500/30 text-fuchsia-400 hover:bg-fuchsia-500/10'
      };
      return classes[color] || classes.primary;
    },
    getPingClass(color) {
      const classes = {
        primary: 'bg-primary-500/50',
        indigo: 'bg-indigo-500/50',
        violet: 'bg-violet-500/50',
        fuchsia: 'bg-fuchsia-500/50'
      };
      return classes[color] || classes.primary;
    },
    getDotClass(color) {
      const classes = {
        primary: 'bg-primary-500',
        indigo: 'bg-indigo-500',
        violet: 'bg-violet-500',
        fuchsia: 'bg-fuchsia-500'
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
/* 3D card effect with tilt */
.use-case-card {
  perspective: 1500px;
}

.card-3d {
  transform-style: preserve-3d;
  box-shadow: 0 10px 30px -15px rgba(2, 12, 27, 0.7);
  transition: all 0.25s cubic-bezier(0.645, 0.045, 0.355, 1);
}

.stack-content {
  transform: translateZ(10px);
}

.icon-container {
  transform-style: preserve-3d;
  box-shadow: 0 10px 30px -10px rgba(2, 12, 27, 0.5);
}

/* Animate ping for live effect */
@keyframes ping {
  75%, 100% {
    transform: scale(1.5);
    opacity: 0;
  }
}

.animate-ping {
  animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;
}

/* Selective hover effects */
@media (hover: hover) {
  .card-3d:hover {
    box-shadow: 0 20px 30px -15px rgba(2, 12, 27, 0.7);
  }
}
</style> 