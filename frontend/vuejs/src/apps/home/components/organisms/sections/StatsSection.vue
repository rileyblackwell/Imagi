<!-- Stats Section with Modern 3D Visualization -->
<template>
  <section class="py-28 md:py-36 relative overflow-hidden">
    <!-- Enhanced decorative background elements -->
    <div class="absolute inset-0 pointer-events-none overflow-hidden">
      <!-- 3D grid effect -->
      <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
      
      <!-- Large gradient orbs -->
      <div class="absolute top-[10%] right-[15%] w-[700px] h-[700px] rounded-full bg-primary-600/5 blur-[150px] animate-pulse-slow"></div>
      <div class="absolute bottom-[15%] left-[10%] w-[600px] h-[600px] rounded-full bg-violet-600/5 blur-[130px] animate-pulse-slow animation-delay-150"></div>
      
      <!-- Particle effect (static representation) -->
      <div class="absolute inset-0 overflow-hidden opacity-30">
        <div class="particle-container w-full h-full"></div>
      </div>
    </div>
    
    <div class="container mx-auto px-6 relative z-10">
      <!-- Modern Section Header -->
      <div class="max-w-3xl mx-auto text-center mb-20">
        <div class="inline-block px-4 py-1.5 bg-primary-500/10 rounded-full mb-3">
          <span class="text-primary-400 font-semibold text-sm tracking-wider">BY THE NUMBERS</span>
        </div>
        <h2 class="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">{{ title }}</h2>
        <p class="text-xl text-gray-300 leading-relaxed">{{ subtitle }}</p>
        
        <!-- Animated decorative line -->
        <div class="w-32 h-1.5 bg-gradient-to-r from-primary-500 to-violet-500 rounded-full mx-auto mt-10 opacity-80"></div>
      </div>
      
      <!-- 3D Stats Dashboard -->
      <div class="relative max-w-7xl mx-auto">
        <!-- Animated connection lines between stats -->
        <div class="absolute top-1/2 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary-500/40 to-transparent -z-10 hidden lg:block animate-pulse-slow"></div>
        <div class="absolute top-[calc(50%-10px)] left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-500/30 to-transparent -z-10 hidden lg:block animate-pulse-slow animation-delay-150"></div>
        <div class="absolute top-[calc(50%+10px)] left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-500/30 to-transparent -z-10 hidden lg:block animate-pulse-slow animation-delay-300"></div>
        
        <!-- Stats Grid with enhanced glass morphism cards -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-6">
          <div 
            v-for="(stat, index) in stats"
            :key="index"
            class="group relative transform transition-all duration-300 hover:-translate-y-2"
          >
            <!-- Enhanced glass morphism effect with glow -->
            <div class="absolute -inset-0.5 rounded-xl opacity-0 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"
                 :class="getGlowBorderClass(stat.color)"></div>
            
            <!-- Stat card with enhanced glass morphism -->
            <div class="relative h-full bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden border border-dark-800/50 group-hover:border-opacity-0 transition-all duration-300">
              <!-- Card header with gradient -->
              <div class="h-2 w-full transition-all duration-300"
                   :class="getHeaderGradientClass(stat.color)"></div>
              
              <!-- Card content -->
              <div class="p-6">
                <!-- Icon with enhanced styling -->
                <div class="w-12 h-12 rounded-lg mb-4 flex items-center justify-center transform transition-all duration-300 group-hover:scale-110"
                     :class="getIconContainerClass(stat.color)">
                  <i :class="[stat.icon, 'text-xl', getIconClass(stat.color)]"></i>
                </div>
                
                <!-- Value with enhanced gradient text -->
                <div class="flex items-baseline gap-1 mb-1">
                  <div class="text-4xl font-bold bg-gradient-to-r bg-clip-text text-transparent"
                       :class="getValueGradientClass(stat.color)">{{ stat.value }}</div>
                  <div class="text-sm font-medium" :class="getUnitClass(stat.color)">{{ stat.unit }}</div>
                </div>
                
                <!-- Label -->
                <div class="text-base text-gray-300">{{ stat.label }}</div>
                
                <!-- Growth indicator with arrow -->
                <div v-if="stat.growth" class="mt-3 flex items-center text-sm font-medium" 
                     :class="getGrowthClass(stat.growth > 0 ? 'positive' : 'negative')">
                  <i :class="[
                    stat.growth > 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down',
                    'mr-1'
                  ]"></i>
                  {{ Math.abs(stat.growth) }}% <span class="ml-1 opacity-70">from last month</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Secondary Stats Row with enhanced styling -->
        <div class="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div v-for="(metric, index) in metrics" :key="index"
               class="group relative transform transition-all duration-300 hover:-translate-y-1">
            <!-- Subtle glow effect -->
            <div class="absolute -inset-0.5 rounded-xl opacity-0 group-hover:opacity-50 blur group-hover:blur-sm transition-all duration-300"
                 :class="getGlowBorderClass(metric.color)"></div>
                 
            <div class="relative bg-dark-900/60 backdrop-blur-md rounded-xl overflow-hidden border border-dark-800/50 group-hover:border-opacity-0 transition-all duration-300 p-6">
              <div class="flex items-center gap-4">
                <!-- Icon with enhanced styling -->
                <div class="w-10 h-10 rounded-lg flex items-center justify-center"
                     :class="getIconContainerClass(metric.color)">
                  <i :class="[metric.icon, 'text-lg', getIconClass(metric.color)]"></i>
                </div>
                
                <div>
                  <!-- Value with enhanced styling -->
                  <div class="text-2xl font-bold text-white">{{ metric.value }}</div>
                  
                  <!-- Label -->
                  <div class="text-sm text-gray-400">{{ metric.label }}</div>
                </div>
              </div>
              
              <!-- Detail text -->
              <div class="mt-3 pt-3 border-t border-dark-700/30 text-xs text-gray-400 leading-relaxed">
                {{ metric.detail }}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Enhanced Rainbow Gradient Decorative Line -->
      <div class="w-full max-w-6xl h-px mx-auto mt-28 overflow-hidden relative">
        <div class="absolute inset-0 bg-gradient-to-r from-primary-500/0 via-indigo-500/70 to-primary-500/0 animate-pulse-slow"></div>
        <div class="absolute inset-0 bg-gradient-to-r from-fuchsia-500/0 via-violet-500/50 to-fuchsia-500/0 animate-pulse-slower opacity-70"></div>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'StatsSection',
  props: {
    title: {
      type: String,
      default: 'Build Web Apps Without Code'
    },
    subtitle: {
      type: String,
      default: 'Create web apps in minutes for dollars instead of paying thousands for a developer to build it over months.'
    },
    stats: {
      type: Array,
      default: () => [
        {
          icon: 'fas fa-dollar-sign',
          value: '$5-10',
          unit: '',
          label: 'Average Web App Cost',
          color: 'primary'
        },
        {
          icon: 'fas fa-clock',
          value: '30',
          unit: 'min',
          label: 'Avg. Build Time',
          color: 'violet'
        },
        {
          icon: 'fas fa-credit-card',
          value: 'Pay',
          unit: '',
          label: 'Per AI Request',
          color: 'blue'
        },
        {
          icon: 'fas fa-code',
          value: '0',
          unit: '',
          label: 'Coding Skills Needed',
          color: 'purple'
        }
      ]
    },
    metrics: {
      type: Array,
      default: () => [
        {
          icon: 'fas fa-file-code',
          value: 'HTML, CSS & JS',
          label: 'Current Support',
          detail: 'Build simple Django web apps with static frontend',
          color: 'primary'
        },
        {
          icon: 'fas fa-globe',
          value: 'Coming Soon',
          label: 'Web Deployment',
          detail: 'Deploy user Imagi Django web apps to the internet',
          color: 'violet'
        },
        {
          icon: 'fas fa-tools',
          value: 'In Development',
          label: 'Database, Auth & Payments',
          detail: 'User auth for Imagi projects, database support, and payments',
          color: 'blue'
        }
      ]
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
    getValueGradientClass(color) {
      const classes = {
        primary: 'from-primary-300 to-violet-300',
        violet: 'from-violet-300 to-purple-300',
        purple: 'from-purple-300 to-primary-300',
        blue: 'from-blue-300 to-violet-300',
      }
      return classes[color] || classes.primary
    },
    getUnitClass(color) {
      const classes = {
        primary: 'text-primary-400',
        violet: 'text-violet-400',
        purple: 'text-purple-400',
        blue: 'text-blue-400',
      }
      return classes[color] || classes.primary
    },
    getGrowthClass(type) {
      return type === 'positive' ? 'text-emerald-400' : 'text-rose-400'
    }
  }
})
</script>

<style scoped>
/* 3D effects */
.stat-card {
  perspective: 1500px;
}

.stat-icon-container {
  transform-style: preserve-3d;
  box-shadow: 0 10px 20px -10px rgba(2, 12, 27, 0.5);
}

.stat-value-container {
  transform: translateZ(5px);
}

/* Gradient text effect */
.gradient-text {
  background: linear-gradient(90deg, #3B82F6, #8B5CF6, #D946EF);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  background-size: 200% auto;
  animation: gradient-shift 8s ease infinite;
}

/* Chart bar animations */
.stat-bar {
  transform: scaleY(0);
  transform-origin: bottom;
  animation: bar-rise 2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes bar-rise {
  0% { transform: scaleY(0); }
  100% { transform: scaleY(1); }
}

/* Animation for gradient shifting */
@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* Ping animation for the status dot */
@keyframes ping {
  75%, 100% {
    transform: scale(2);
    opacity: 0;
  }
}

.animate-ping {
  animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;
}

/* Custom pulse animations at different speeds */
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

.animation-delay-300 {
  animation-delay: 300ms;
}

/* Particle container styles */
.particle-container {
  background-image: radial-gradient(circle, rgba(255, 255, 255, 0.1) 1px, transparent 1px);
  background-size: 30px 30px;
}
</style> 