<!-- Features Section Component - Premium Design -->
<template>
  <section class="py-20 md:py-32 px-6 sm:px-8 lg:px-12 relative">
    <div class="max-w-7xl mx-auto relative">
      <!-- Section header -->
      <div class="text-center mb-16 md:mb-20">
        <!-- Badge -->
        <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/[0.08] rounded-full border border-white/20 mb-6">
          <i class="fas fa-sparkles text-xs text-amber-400"></i>
          <span class="text-sm font-medium text-white/90">Powerful Features</span>
        </div>
        
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-semibold text-white mb-5 tracking-tight">{{ title }}</h2>
        <p class="text-lg text-white/85 max-w-2xl mx-auto leading-relaxed">{{ subtitle }}</p>
      </div>

      <!-- Feature cards grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 md:gap-6">
        <div 
          v-for="(feature, index) in features" 
          :key="index"
          class="group relative"
          :style="{ animationDelay: `${index * 100}ms` }"
        >
          <!-- Card -->
          <div class="relative h-full p-6 md:p-8 rounded-2xl border border-white/15 bg-white/[0.07] backdrop-blur-sm hover:bg-white/[0.1] hover:border-white/25 transition-all duration-500 cursor-default overflow-hidden">
            <!-- Subtle hover glow -->
            <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
              <div class="absolute inset-0 bg-gradient-to-br opacity-[0.08]" :class="getGradientClass(feature.color)"></div>
            </div>
            
            <!-- Icon -->
            <div class="relative mb-6">
              <div 
                class="inline-flex items-center justify-center w-12 h-12 rounded-xl border transition-all duration-300"
                :class="getIconContainerClass(feature.color)"
              >
                <i :class="[feature.icon, 'text-lg', getIconClass(feature.color)]"></i>
              </div>
            </div>
            
            <!-- Content -->
            <h3 class="relative text-lg font-semibold text-white mb-3">{{ feature.title }}</h3>
            <p class="relative text-white/85 text-sm leading-relaxed mb-6">{{ feature.description }}</p>
            
            <!-- Learn more link -->
            <div class="relative flex items-center gap-2 text-sm font-medium transition-colors duration-300" :class="getLinkClass(feature.color)">
              <span>Learn more</span>
              <i class="fas fa-arrow-right text-xs transform group-hover:translate-x-1 transition-transform duration-300"></i>
            </div>

            <!-- Bottom accent line on hover -->
            <div 
              class="absolute bottom-0 left-0 right-0 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-500"
              :class="getAccentLineClass(feature.color)"
            ></div>
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
      default: 'Everything You Need to Ship'
    },
    subtitle: {
      type: String,
      default: 'Imagi generates complete, production-ready applications with modern frontends and robust backends — all from plain English descriptions.'
    },
    features: {
      type: Array,
      default: () => [
        {
          title: 'Vue.js Frontend',
          description: 'Beautiful, responsive user interfaces built with Vue.js and Tailwind CSS. Modern component architecture that scales with your needs.',
          icon: 'fas fa-palette',
          color: 'violet'
        },
        {
          title: 'Django Backend',
          description: 'Powerful Python backend with Django REST framework. Secure APIs, data models, and business logic generated automatically.',
          icon: 'fas fa-server',
          color: 'fuchsia'
        },
        {
          title: 'Instant Generation',
          description: 'Go from idea to working app in minutes. Describe what you want and watch as Imagi builds your entire application stack.',
          icon: 'fas fa-bolt',
          color: 'amber'
        },
        {
          title: 'Chat-Based Editing',
          description: 'Refine your app through natural conversation. Request changes, add features, or tweak designs — no coding required.',
          icon: 'fas fa-comments',
          color: 'blue'
        },
        {
          title: 'Pay Per Build',
          description: 'No subscriptions or hidden fees. Purchase credits and use them when you need. Build a complete app for just a few dollars.',
          icon: 'fas fa-coins',
          color: 'emerald'
        },
        {
          title: 'Own Your Code',
          description: 'Download your complete source code anytime. Standard Vue.js and Django that you can modify, extend, and host anywhere.',
          icon: 'fas fa-download',
          color: 'rose'
        }
      ]
    }
  },
  methods: {
    getGradientClass(color) {
      const gradients = {
        violet: 'from-violet-500 to-purple-500',
        fuchsia: 'from-fuchsia-500 to-pink-500',
        amber: 'from-amber-500 to-orange-500',
        emerald: 'from-emerald-500 to-teal-500',
        blue: 'from-blue-500 to-cyan-500',
        rose: 'from-rose-500 to-pink-500'
      }
      return gradients[color] || gradients.violet
    },
    getIconContainerClass(color) {
      const classes = {
        violet: 'bg-violet-500/15 border-violet-500/30 group-hover:bg-violet-500/20 group-hover:border-violet-500/40',
        fuchsia: 'bg-fuchsia-500/15 border-fuchsia-500/30 group-hover:bg-fuchsia-500/20 group-hover:border-fuchsia-500/40',
        amber: 'bg-amber-500/15 border-amber-500/30 group-hover:bg-amber-500/20 group-hover:border-amber-500/40',
        emerald: 'bg-emerald-500/15 border-emerald-500/30 group-hover:bg-emerald-500/20 group-hover:border-emerald-500/40',
        blue: 'bg-blue-500/15 border-blue-500/30 group-hover:bg-blue-500/20 group-hover:border-blue-500/40',
        rose: 'bg-rose-500/15 border-rose-500/30 group-hover:bg-rose-500/20 group-hover:border-rose-500/40'
      }
      return classes[color] || classes.violet
    },
    getIconClass(color) {
      const classes = {
        violet: 'text-violet-400',
        fuchsia: 'text-fuchsia-400',
        amber: 'text-amber-400',
        emerald: 'text-emerald-400',
        blue: 'text-blue-400',
        rose: 'text-rose-400'
      }
      return classes[color] || classes.violet
    },
    getLinkClass(color) {
      const classes = {
        violet: 'text-violet-400/85 group-hover:text-violet-400',
        fuchsia: 'text-fuchsia-400/85 group-hover:text-fuchsia-400',
        amber: 'text-amber-400/85 group-hover:text-amber-400',
        emerald: 'text-emerald-400/85 group-hover:text-emerald-400',
        blue: 'text-blue-400/85 group-hover:text-blue-400',
        rose: 'text-rose-400/85 group-hover:text-rose-400'
      }
      return classes[color] || classes.violet
    },
    getAccentLineClass(color) {
      const classes = {
        violet: 'bg-gradient-to-r from-transparent via-violet-500/60 to-transparent',
        fuchsia: 'bg-gradient-to-r from-transparent via-fuchsia-500/60 to-transparent',
        amber: 'bg-gradient-to-r from-transparent via-amber-500/60 to-transparent',
        emerald: 'bg-gradient-to-r from-transparent via-emerald-500/60 to-transparent',
        blue: 'bg-gradient-to-r from-transparent via-blue-500/60 to-transparent',
        rose: 'bg-gradient-to-r from-transparent via-rose-500/60 to-transparent'
      }
      return classes[color] || classes.violet
    }
  }
})
</script>

<style scoped>
/* Subtle entrance animation */
@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
