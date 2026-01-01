<!-- Features Section Component - Premium Design -->
<template>
  <section class="py-20 md:py-32 px-6 sm:px-8 lg:px-12 relative">
    <div class="max-w-7xl mx-auto relative">
      <!-- Section header -->
      <div class="text-center mb-16 md:mb-20">
        <!-- Badge -->
        <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/[0.03] rounded-full border border-white/[0.08] mb-6">
          <i class="fas fa-sparkles text-xs text-amber-400/80"></i>
          <span class="text-sm font-medium text-white/60">Powerful Features</span>
        </div>
        
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-semibold text-white/90 mb-5 tracking-tight">{{ title }}</h2>
        <p class="text-lg text-white/50 max-w-2xl mx-auto leading-relaxed">{{ subtitle }}</p>
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
          <div class="relative h-full p-6 md:p-8 rounded-2xl border border-white/[0.06] bg-white/[0.02] backdrop-blur-sm hover:bg-white/[0.04] hover:border-white/[0.1] transition-all duration-500 cursor-default overflow-hidden">
            <!-- Subtle hover glow -->
            <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
              <div class="absolute inset-0 bg-gradient-to-br opacity-[0.03]" :class="getGradientClass(feature.color)"></div>
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
            <h3 class="relative text-lg font-semibold text-white/90 mb-3">{{ feature.title }}</h3>
            <p class="relative text-white/50 text-sm leading-relaxed mb-6">{{ feature.description }}</p>
            
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
      default: 'Full-Stack Apps Made Simple'
    },
    subtitle: {
      type: String,
      default: 'Build complete web applications with Vue.js frontends and Django backends in minutes — no technical knowledge required.'
    },
    features: {
      type: Array,
      default: () => [
        {
          title: 'No Technical Skills Needed',
          description: 'Perfect for entrepreneurs, small business owners, and anyone with an idea. Just describe your app in plain English.',
          icon: 'fas fa-user-friends',
          color: 'violet'
        },
        {
          title: 'Full-Stack Applications',
          description: 'Get complete web applications with professional Vue.js frontends and robust Django backends that work together seamlessly.',
          icon: 'fas fa-layer-group',
          color: 'fuchsia'
        },
        {
          title: 'Minutes, Not Months',
          description: 'Build professional web applications in minutes that would normally take developers months and cost thousands.',
          icon: 'fas fa-bolt',
          color: 'amber'
        },
        {
          title: 'Affordable for Everyone',
          description: 'Pay only for what you build with our credit system. Create a complete full-stack web app for just a few dollars.',
          icon: 'fas fa-coins',
          color: 'emerald'
        },
        {
          title: 'Natural Conversation',
          description: 'Edit and improve your app through simple conversation. Describe changes you want, and the AI updates everything instantly.',
          icon: 'fas fa-comments',
          color: 'blue'
        },
        {
          title: 'Professional Results',
          description: 'Get production-ready applications with modern Vue.js interfaces and powerful Django APIs. Database integration coming soon.',
          icon: 'fas fa-rocket',
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
        violet: 'bg-violet-500/10 border-violet-500/20 group-hover:bg-violet-500/15 group-hover:border-violet-500/30',
        fuchsia: 'bg-fuchsia-500/10 border-fuchsia-500/20 group-hover:bg-fuchsia-500/15 group-hover:border-fuchsia-500/30',
        amber: 'bg-amber-500/10 border-amber-500/20 group-hover:bg-amber-500/15 group-hover:border-amber-500/30',
        emerald: 'bg-emerald-500/10 border-emerald-500/20 group-hover:bg-emerald-500/15 group-hover:border-emerald-500/30',
        blue: 'bg-blue-500/10 border-blue-500/20 group-hover:bg-blue-500/15 group-hover:border-blue-500/30',
        rose: 'bg-rose-500/10 border-rose-500/20 group-hover:bg-rose-500/15 group-hover:border-rose-500/30'
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
        violet: 'text-violet-400/70 group-hover:text-violet-400',
        fuchsia: 'text-fuchsia-400/70 group-hover:text-fuchsia-400',
        amber: 'text-amber-400/70 group-hover:text-amber-400',
        emerald: 'text-emerald-400/70 group-hover:text-emerald-400',
        blue: 'text-blue-400/70 group-hover:text-blue-400',
        rose: 'text-rose-400/70 group-hover:text-rose-400'
      }
      return classes[color] || classes.violet
    },
    getAccentLineClass(color) {
      const classes = {
        violet: 'bg-gradient-to-r from-transparent via-violet-500/50 to-transparent',
        fuchsia: 'bg-gradient-to-r from-transparent via-fuchsia-500/50 to-transparent',
        amber: 'bg-gradient-to-r from-transparent via-amber-500/50 to-transparent',
        emerald: 'bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent',
        blue: 'bg-gradient-to-r from-transparent via-blue-500/50 to-transparent',
        rose: 'bg-gradient-to-r from-transparent via-rose-500/50 to-transparent'
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
