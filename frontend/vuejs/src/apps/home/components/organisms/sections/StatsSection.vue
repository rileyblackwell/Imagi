<!-- Stats Section with Modern 3D Visualization -->
<template>
  <section class="py-24 md:py-36 px-6 sm:px-8 lg:px-12 relative overflow-hidden">
    <!-- Enhanced decorative background elements -->
    <div class="absolute inset-0 pointer-events-none overflow-hidden">
      <!-- 3D grid effect -->
      <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
      
      <!-- Large gradient orbs -->
      <div class="absolute top-[10%] right-[15%] w-[700px] h-[700px] rounded-full bg-indigo-600/5 blur-[150px] animate-pulse-slow"></div>
      <div class="absolute bottom-[15%] left-[10%] w-[600px] h-[600px] rounded-full bg-violet-600/5 blur-[130px] animate-pulse-slow animation-delay-150"></div>
      
      <!-- Particle effect (static representation) -->
      <div class="absolute inset-0 overflow-hidden opacity-30">
        <div class="particle-container w-full h-full"></div>
      </div>
    </div>
    
    <div class="max-w-7xl mx-auto relative z-10">
      <!-- Modern Section Header -->
      <div class="text-center mb-16">
        <!-- Modern pill badge -->
        <div class="inline-flex items-center px-4 py-1.5 bg-gradient-to-r from-cyan-500/10 to-blue-500/10 rounded-full border border-cyan-400/20 backdrop-blur-sm mb-6">
          <div class="w-1.5 h-1.5 bg-cyan-400 rounded-full mr-2 animate-pulse"></div>
          <span class="text-cyan-300 font-medium text-sm tracking-wide uppercase">By The Numbers</span>
        </div>
        <h2 class="text-4xl md:text-5xl font-bold text-white mb-4 leading-tight">{{ title }}</h2>
        <p class="text-xl text-gray-300 max-w-3xl mx-auto">{{ subtitle }}</p>
        
        <!-- Modern divider -->
        <div class="w-full h-px bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent mt-8"></div>
      </div>
      
      <!-- Stats Grid with enhanced glass morphism cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8 mb-16">
        <div 
          v-for="(stat, index) in stats"
          :key="index"
          class="group relative transform transition-all duration-300 hover:-translate-y-1"
        >
          <!-- Modern glassmorphism container -->
          <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden h-full transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
            <!-- Sleek gradient header -->
            <div class="h-1 w-full transition-all duration-300"
                 :class="getHeaderGradientClass(stat.color)"></div>
            
            <!-- Subtle background effects -->
            <div class="absolute -top-32 -right-32 w-64 h-64 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"
                 :class="getCardBackgroundClass(stat.color)"></div>
            
            <!-- Card content -->
            <div class="relative z-10 p-6">
              <!-- Icon with enhanced styling -->
              <div class="w-12 h-12 rounded-xl mb-5 flex items-center justify-center border transition-all duration-300"
                   :class="getIconContainerClass(stat.color)">
                <i :class="[stat.icon, 'text-lg', getIconClass(stat.color)]"></i>
              </div>
              
              <!-- Value with enhanced gradient text -->
              <div class="flex items-baseline gap-1 mb-3">
                <div class="text-3xl font-bold bg-gradient-to-r bg-clip-text text-transparent"
                     :class="getValueGradientClass(stat.color)">{{ stat.value }}</div>
                <div v-if="stat.unit" class="text-sm font-medium" :class="getUnitClass(stat.color)">{{ stat.unit }}</div>
              </div>
              
              <!-- Label -->
              <div class="text-sm text-gray-300 leading-relaxed">{{ stat.label }}</div>
              
              <!-- Growth indicator with arrow -->
              <div v-if="stat.growth" class="mt-3 flex items-center text-xs font-medium" 
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
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8">
        <div v-for="(metric, index) in metrics" :key="index"
             class="group relative transform transition-all duration-300 hover:-translate-y-1">
          <!-- Modern glassmorphism container -->
          <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
            <!-- Sleek gradient header -->
            <div class="h-1 w-full transition-all duration-300"
                 :class="getHeaderGradientClass(metric.color)"></div>
            
            <!-- Subtle background effects -->
            <div class="absolute -top-32 -right-32 w-64 h-64 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"
                 :class="getCardBackgroundClass(metric.color)"></div>
            
            <div class="relative z-10 p-6">
              <div class="flex items-center gap-4 mb-4">
                <!-- Icon with enhanced styling -->
                <div class="w-10 h-10 rounded-xl flex items-center justify-center border"
                     :class="getIconContainerClass(metric.color)">
                  <i :class="[metric.icon, 'text-sm', getIconClass(metric.color)]"></i>
                </div>
                
                <div>
                  <!-- Value with enhanced styling -->
                  <div class="text-lg font-semibold text-white leading-tight">{{ metric.value }}</div>
                  
                  <!-- Label -->
                  <div class="text-xs text-gray-400">{{ metric.label }}</div>
                </div>
              </div>
              
              <!-- Modern separator -->
              <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-4"></div>
              
              <!-- Detail text -->
              <div class="text-xs text-gray-400 leading-relaxed">
                {{ metric.detail }}
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
    getValueGradientClass(color) {
      const classes = {
        primary: 'from-indigo-300 to-violet-300',
        violet: 'from-violet-300 to-purple-300',
        purple: 'from-purple-300 to-fuchsia-300',
        blue: 'from-blue-300 to-cyan-300',
      }
      return classes[color] || classes.primary
    },
    getUnitClass(color) {
      const classes = {
        primary: 'text-indigo-400',
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