<!-- How It Works Section Component with 3D Timeline UI -->
<template>
  <section id="how-it-works" class="py-24 md:py-36 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
    <!-- Animated background elements -->
    <div class="absolute inset-0 pointer-events-none">
      <!-- 3D grid effect for depth -->
      <div class="absolute inset-0 bg-[url('/grid-pattern-dark.svg')] opacity-[0.06]"></div>
      
      <!-- Subtle gradient overlays -->
      <div class="absolute top-0 left-0 w-full h-1/3 bg-gradient-to-b from-primary-900/30 to-transparent opacity-20 blur-3xl"></div>
      <div class="absolute bottom-0 right-0 w-full h-1/3 bg-gradient-to-t from-violet-900/30 to-transparent opacity-20 blur-3xl"></div>
    </div>
    
    <div class="max-w-7xl mx-auto relative z-10">
      <!-- Modern section header with badge -->
      <div class="text-center mb-20 relative">
        <div class="inline-block px-4 py-1.5 bg-indigo-500/10 rounded-full mb-3">
          <span class="text-indigo-400 font-semibold text-sm tracking-wider">SEAMLESS WORKFLOW</span>
        </div>
        <h2 class="text-4xl md:text-5xl font-bold text-white mb-4 leading-tight">{{ title }}</h2>
        <p class="text-xl text-gray-300 max-w-3xl mx-auto">{{ subtitle }}</p>
        
        <!-- Decorative line -->
        <div class="w-24 h-1 bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full mx-auto mt-8"></div>
      </div>

      <!-- 3D Timeline with Connected Steps -->
      <div class="relative">
        <!-- Center timeline line -->
        <div class="absolute top-0 bottom-0 left-1/2 w-px bg-gradient-to-b from-primary-500/70 via-indigo-500/70 to-fuchsia-500/70 transform -translate-x-1/2 hidden md:block"></div>
        
        <div class="space-y-24 relative">
          <div 
            v-for="(step, index) in steps" 
            :key="index"
            class="timeline-item relative"
            :class="{'md:ml-auto': index % 2 !== 0}"
          >
            <!-- Timeline connector bubble - now positioned directly on the timeline -->
            <div 
              class="absolute top-1/2 left-1/2 w-6 h-6 rounded-full border-2 transition-all duration-300 transform -translate-x-1/2 -translate-y-1/2 z-10 hidden md:block"
              :class="getDotClasses(step.color)"
            ></div>
            
            <!-- Step container with 3D and glassmorphism effect -->
            <div 
              class="md:w-[calc(50%-3rem)] step-card group transition-all duration-500 hover:-translate-y-1 relative"
              :class="{'ml-auto md:mr-0': index % 2 === 0, 'mr-auto md:ml-0': index % 2 !== 0}"
            >
              <!-- Connecting line from timeline bubble to card -->
              <div 
                class="absolute top-1/2 h-px hidden md:block" 
                :class="[
                  index % 2 === 0 ? 'right-full w-[3rem]' : 'left-full w-[3rem]',
                  getLineClasses(step.color)
                ]"
              ></div>
            
              <!-- Glass card container -->
              <div class="p-8 rounded-2xl border border-gray-800/60 bg-dark-900/40 backdrop-blur-sm transition-all duration-300 relative group-hover:shadow-glow group-hover:shadow-[--step-color] overflow-hidden"
                   :style="{ '--step-color': getStepColor(step.color) }">
                
                <!-- Subtle gradient background -->
                <div class="absolute inset-0 bg-gradient-to-br opacity-10 -z-10 transition-opacity duration-300 group-hover:opacity-20"
                     :class="getGradientClass(step.color)"></div>
                
                <!-- Step number with glass effect -->
                <div class="flex items-center space-x-4 mb-6">
                  <div class="w-12 h-12 rounded-xl flex items-center justify-center text-xl font-bold shadow-lg border border-gray-700/30 backdrop-blur-sm"
                       :class="getNumberContainerClass(step.color)">
                    <span :class="getNumberClass(step.color)">{{ index + 1 }}</span>
                  </div>
                  <h3 class="text-2xl font-bold text-white">{{ step.title }}</h3>
                </div>
                
                <p class="text-gray-400 transition-all duration-300 group-hover:text-gray-300 text-lg">{{ step.description }}</p>
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
  name: 'HowItWorksSection',
  props: {
    title: {
      type: String,
      default: 'How It Works'
    },
    subtitle: {
      type: String,
      default: 'Follow these simple steps to create your web application'
    },
    steps: {
      type: Array,
      default: () => [
        {
          title: 'Describe Your Vision',
          description: 'Tell us what you want to build using natural language. Describe your features, design preferences, and requirements with as much detail as you need.',
          icon: 'fas fa-pencil-alt',
          color: 'primary'
        },
        {
          title: 'AI Generation',
          description: 'Our advanced AI analyzes your description and generates all necessary code, from responsive frontend interfaces to powerful backend logic and database schemas.',
          icon: 'fas fa-magic',
          color: 'indigo'
        },
        {
          title: 'Customize & Refine',
          description: 'Review the generated application, make adjustments, and refine details using natural language commands. Our AI understands your feedback and implements changes instantly.',
          icon: 'fas fa-sliders-h',
          color: 'violet'
        },
        {
          title: 'Launch & Scale',
          description: "Deploy your application with confidence, knowing it's built with scalable, secure, and maintainable code that follows industry best practices and modern architecture.",
          icon: 'fas fa-rocket',
          color: 'fuchsia'
        }
      ]
    }
  },
  methods: {
    getStepColor(color) {
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
    getDotClasses(color) {
      const classes = {
        primary: 'border-primary-500 bg-primary-500/30',
        indigo: 'border-indigo-500 bg-indigo-500/30',
        violet: 'border-violet-500 bg-violet-500/30',
        fuchsia: 'border-fuchsia-500 bg-fuchsia-500/30'
      };
      return classes[color] || classes.primary;
    },
    getLineClasses(color) {
      const classes = {
        primary: 'bg-primary-500/70',
        indigo: 'bg-indigo-500/70',
        violet: 'bg-violet-500/70',
        fuchsia: 'bg-fuchsia-500/70'
      };
      return classes[color] || classes.primary;
    },
    getNumberContainerClass(color) {
      const classes = {
        primary: 'bg-primary-500/10',
        indigo: 'bg-indigo-500/10',
        violet: 'bg-violet-500/10',
        fuchsia: 'bg-fuchsia-500/10'
      };
      return classes[color] || classes.primary;
    },
    getNumberClass(color) {
      const classes = {
        primary: 'text-primary-400',
        indigo: 'text-indigo-400',
        violet: 'text-violet-400',
        fuchsia: 'text-fuchsia-400'
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
    }
  }
})
</script>

<style scoped>
/* 3D and animated styles */
.shadow-glow {
  box-shadow: 0 0 25px -5px var(--step-color);
}

.timeline-item {
  perspective: 1000px;
}

.step-card {
  transform-style: preserve-3d;
}

@media (min-width: 768px) {
  .timeline-item:nth-child(odd) .step-card {
    transform: translateZ(0) translateX(40px);
  }
  
  .timeline-item:nth-child(even) .step-card {
    transform: translateZ(0) translateX(-40px);
  }
  
  .timeline-item:nth-child(odd) .step-card:hover {
    transform: translateZ(0) translateX(40px) translateY(-8px);
  }
  
  .timeline-item:nth-child(even) .step-card:hover {
    transform: translateZ(0) translateX(-40px) translateY(-8px);
  }
}
</style> 