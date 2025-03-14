<!-- Stats Section with Modern 3D Visualization -->
<template>
  <section class="py-28 md:py-36 relative overflow-hidden">
    <!-- Enhanced decorative background elements -->
    <div class="absolute inset-0 pointer-events-none overflow-hidden">
      <!-- 3D grid effect -->
      <div class="absolute inset-0 bg-[url('/grid-pattern-dark.svg')] opacity-[0.03]"></div>
      
      <!-- Large gradient orbs -->
      <div class="absolute top-[10%] right-[15%] w-[700px] h-[700px] rounded-full bg-primary-600/5 blur-[150px] opacity-60"></div>
      <div class="absolute bottom-[15%] left-[10%] w-[600px] h-[600px] rounded-full bg-violet-600/5 blur-[130px] opacity-50"></div>
      
      <!-- Particle effect (static representation) -->
      <div class="absolute inset-0 overflow-hidden opacity-30">
        <div class="particle-container w-full h-full"></div>
      </div>
    </div>
    
    <div class="container mx-auto px-6 relative z-10">
      <!-- Modern Section Header -->
      <div class="max-w-3xl mx-auto text-center mb-20">
        <div class="inline-block px-4 py-1.5 bg-violet-500/10 rounded-full mb-3">
          <span class="text-violet-400 font-semibold text-sm tracking-wider">BY THE NUMBERS</span>
        </div>
        <h2 class="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight gradient-text">{{ title }}</h2>
        <p class="text-xl text-gray-300 leading-relaxed">{{ subtitle }}</p>
        
        <!-- Animated decorative line -->
        <div class="w-32 h-1.5 bg-gradient-to-r from-primary-500 via-violet-500 to-fuchsia-500 rounded-full mx-auto mt-10 opacity-80"></div>
      </div>
      
      <!-- 3D Stats Dashboard -->
      <div class="relative max-w-7xl mx-auto">
        <!-- Animated connection lines between stats -->
        <div class="absolute top-1/2 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-500/40 to-transparent -z-10 hidden lg:block animate-pulse-slow"></div>
        <div class="absolute top-[calc(50%-10px)] left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary-500/30 to-transparent -z-10 hidden lg:block animate-pulse-slower"></div>
        <div class="absolute top-[calc(50%+10px)] left-0 right-0 h-px bg-gradient-to-r from-transparent via-fuchsia-500/30 to-transparent -z-10 hidden lg:block animate-pulse-slowest"></div>
        
        <!-- Stats Grid with 3D cards -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-6">
          <div 
            v-for="(stat, index) in stats"
            :key="index"
            class="stat-card transform transition-all duration-500 hover:scale-105 hover:-translate-y-2"
          >
            <!-- 3D Glassmorphism Stat Card -->
            <div class="relative h-full p-6 rounded-2xl border border-gray-800/60 bg-dark-900/40 backdrop-blur-sm overflow-hidden group">
              <!-- Gradient background -->
              <div class="absolute inset-0 bg-gradient-to-br opacity-10 -z-10 transition-opacity duration-300 group-hover:opacity-20"
                   :class="getGradientClass(stat.color)"></div>
                   
              <!-- Glowing orb -->
              <div class="absolute -bottom-20 -right-20 w-48 h-48 rounded-full opacity-20 blur-3xl transition-all duration-300 group-hover:opacity-30 group-hover:scale-110"
                   :class="getOrbClass(stat.color)"></div>
              
              <!-- Stat card top section -->
              <div class="flex items-start justify-between mb-6">
                <!-- Icon with 3D effect -->
                <div class="stat-icon-container relative w-14 h-14 rounded-xl flex items-center justify-center transform transition-all duration-300 group-hover:-translate-y-1"
                     :class="getIconBgClass(stat.color)">
                  <i :class="[stat.icon, 'text-2xl', getIconClass(stat.color)]"></i>
                  
                  <!-- Secondary icon for layered effect -->
                  <div class="absolute -right-2 -bottom-2 w-6 h-6 rounded-lg flex items-center justify-center bg-dark-800 border border-gray-700/50"
                       v-if="stat.secondaryIcon">
                    <i :class="[stat.secondaryIcon, 'text-xs', getIconClass(stat.color)]"></i>
                  </div>
                  
                  <!-- Icon shadow -->
                  <div class="absolute w-full h-full rounded-xl top-0 left-0 blur-md -z-10 opacity-60 scale-90"
                       :class="getIconShadowClass(stat.color)"></div>
                </div>
                
                <!-- Mini chart/visualization -->
                <div class="w-24 h-12 rounded-lg overflow-hidden bg-dark-800/70 flex items-end p-1">
                  <div 
                    v-for="bar in 8" 
                    :key="bar" 
                    class="stat-bar mx-0.5 rounded-t-sm w-full" 
                    :class="getBarClass(stat.color)"
                    :style="{
                      height: `${15 + Math.floor(Math.random() * 20)}px`,
                      animationDelay: `${bar * 0.1}s`
                    }"
                  ></div>
                </div>
              </div>
              
              <!-- Stat value with 3D counter effect -->
              <div class="stat-value-container">
                <div class="text-3xl md:text-4xl font-bold text-white mb-1 flex items-baseline">
                  <span>{{ stat.value }}</span>
                  
                  <!-- Progress bar for percentage stats -->
                  <div v-if="stat.percent" class="ml-3 w-20 h-1.5 bg-dark-700 rounded-full overflow-hidden">
                    <div class="h-full rounded-full transition-all duration-1000" 
                         :class="getProgressClass(stat.color)"
                         :style="{ width: `${stat.percent}%` }"></div>
                  </div>
                </div>
                <div class="text-gray-400 text-lg font-medium">{{ stat.label }}</div>
                
                <!-- 24/7 indicator with pulsing dots -->
                <div v-if="stat.isClock" class="flex items-center mt-2 space-x-2">
                  <span class="text-xs font-medium uppercase tracking-wide" :class="getIconClass(stat.color)">Always Available</span>
                  <span class="relative flex h-2 w-2">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" :class="getDotClass(stat.color)"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2" :class="getDotClass(stat.color)"></span>
                  </span>
                </div>
              </div>
              
              <!-- Hover border effect -->
              <div class="absolute inset-0 rounded-2xl border opacity-0 transition-all duration-300 group-hover:opacity-20 pointer-events-none"
                   :class="getBorderClass(stat.color)"></div>
                   
              <!-- Hover indicator -->
              <div class="absolute bottom-3 right-3 w-2 h-2 rounded-full opacity-0 transition-all duration-300 group-hover:opacity-100"
                   :class="getDotClass(stat.color)"></div>
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
import { defineComponent, ref } from 'vue'

export default defineComponent({
  name: 'StatsSection',
  setup() {
    const title = ref('Our Impact')
    const subtitle = ref('Imagi is revolutionizing web development for businesses and developers around the world')
    
    const stats = ref([
      {
        icon: 'fas fa-users',
        secondaryIcon: 'fas fa-user-group',
        value: '5K+',
        label: 'Active Users',
        percent: null,
        color: 'primary'
      },
      {
        icon: 'fas fa-code',
        secondaryIcon: 'fas fa-laptop-code',
        value: '10K+',
        label: 'Apps Created',
        percent: null,
        color: 'indigo'
      },
      {
        icon: 'fas fa-clock',
        value: '80%',
        label: 'Dev Time Saved',
        percent: 80,
        color: 'green'
      },
      {
        icon: 'fas fa-headset',
        value: '24/7',
        label: 'AI Support',
        percent: 100,
        isClock: true,
        color: 'purple'
      }
    ])
    
    return {
      title,
      subtitle,
      stats
    }
  },
  methods: {
    getGradientClass(color) {
      const classes = {
        primary: 'from-primary-900 to-primary-600',
        indigo: 'from-indigo-900 to-indigo-600',
        violet: 'from-violet-900 to-violet-600',
        fuchsia: 'from-fuchsia-900 to-fuchsia-600',
        purple: 'from-purple-900 to-purple-600',
        green: 'from-emerald-900 to-emerald-600'
      };
      return classes[color] || classes.primary;
    },
    getOrbClass(color) {
      const classes = {
        primary: 'bg-primary-500',
        indigo: 'bg-indigo-500',
        violet: 'bg-violet-500',
        fuchsia: 'bg-fuchsia-500',
        purple: 'bg-purple-500',
        green: 'bg-emerald-500'
      };
      return classes[color] || classes.primary;
    },
    getIconBgClass(color) {
      const classes = {
        primary: 'bg-primary-900/80 border border-primary-700/50',
        indigo: 'bg-indigo-900/80 border border-indigo-700/50',
        violet: 'bg-violet-900/80 border border-violet-700/50',
        fuchsia: 'bg-fuchsia-900/80 border border-fuchsia-700/50',
        purple: 'bg-purple-900/80 border border-purple-700/50',
        green: 'bg-emerald-900/80 border border-emerald-700/50'
      };
      return classes[color] || classes.primary;
    },
    getIconClass(color) {
      const classes = {
        primary: 'text-primary-400',
        indigo: 'text-indigo-400',
        violet: 'text-violet-400',
        fuchsia: 'text-fuchsia-400',
        purple: 'text-purple-400',
        green: 'text-emerald-400'
      };
      return classes[color] || classes.primary;
    },
    getIconShadowClass(color) {
      const classes = {
        primary: 'bg-primary-500/30',
        indigo: 'bg-indigo-500/30',
        violet: 'bg-violet-500/30',
        fuchsia: 'bg-fuchsia-500/30',
        purple: 'bg-purple-500/30',
        green: 'bg-emerald-500/30'
      };
      return classes[color] || classes.primary;
    },
    getDotClass(color) {
      const classes = {
        primary: 'bg-primary-500',
        indigo: 'bg-indigo-500',
        violet: 'bg-violet-500',
        fuchsia: 'bg-fuchsia-500',
        purple: 'bg-purple-500',
        green: 'bg-emerald-500'
      };
      return classes[color] || classes.primary;
    },
    getBarClass(color) {
      const classes = {
        primary: 'bg-primary-500',
        indigo: 'bg-indigo-500',
        violet: 'bg-violet-500',
        fuchsia: 'bg-fuchsia-500',
        purple: 'bg-purple-500',
        green: 'bg-emerald-500'
      };
      return classes[color] || classes.primary;
    },
    getProgressClass(color) {
      const classes = {
        primary: 'bg-primary-500',
        indigo: 'bg-indigo-500',
        violet: 'bg-violet-500',
        fuchsia: 'bg-fuchsia-500',
        purple: 'bg-purple-500',
        green: 'bg-emerald-500'
      };
      return classes[color] || classes.primary;
    },
    getClockClass(color) {
      const classes = {
        primary: 'bg-primary-400',
        indigo: 'bg-indigo-400',
        violet: 'bg-violet-400',
        fuchsia: 'bg-fuchsia-400',
        purple: 'bg-purple-400',
        green: 'bg-emerald-400'
      };
      return classes[color] || classes.primary;
    },
    getBorderClass(color) {
      const classes = {
        primary: 'border-primary-500',
        indigo: 'border-indigo-500',
        violet: 'border-violet-500',
        fuchsia: 'border-fuchsia-500',
        purple: 'border-purple-500',
        green: 'border-emerald-500'
      };
      return classes[color] || classes.primary;
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
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.7; }
}

@keyframes pulse-slower {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 0.6; }
}

@keyframes pulse-slowest {
  0%, 100% { opacity: 0.1; }
  50% { opacity: 0.5; }
}

.animate-pulse-slow {
  animation: pulse-slow 4s ease-in-out infinite;
}

.animate-pulse-slower {
  animation: pulse-slower 6s ease-in-out infinite;
}

.animate-pulse-slowest {
  animation: pulse-slowest 8s ease-in-out infinite;
}

/* Particle container styles */
.particle-container {
  background-image: radial-gradient(circle, rgba(255, 255, 255, 0.1) 1px, transparent 1px);
  background-size: 30px 30px;
}
</style> 