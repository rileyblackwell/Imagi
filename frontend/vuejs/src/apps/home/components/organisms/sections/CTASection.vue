<!-- CTA Section Component -->
<template>
  <section class="py-16 sm:py-24 px-6 sm:px-8 lg:px-12">
    <div class="max-w-5xl mx-auto">
      <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
        <!-- Modern glassmorphism container -->
        <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden">
          <!-- Sleek gradient header -->
          <div class="h-1 w-full bg-gradient-to-r from-rose-400 via-pink-400 to-rose-400 opacity-80"></div>
          
          <!-- Subtle background effects -->
          <div class="absolute -top-32 -right-32 w-64 h-64 bg-gradient-to-br from-rose-400/4 to-pink-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
          
          <div class="relative z-10 p-8 md:p-12">
            <div class="flex flex-col md:flex-row items-start gap-8">
              <!-- Icon with enhanced styling -->
              <div class="w-16 h-16 flex-shrink-0 rounded-xl bg-gradient-to-br from-rose-400/20 to-pink-400/20 flex items-center justify-center border border-rose-400/20">
                <i :class="icon || 'fas fa-rocket'" class="text-rose-300 text-2xl"></i>
              </div>
              
              <!-- Content section -->
              <div class="flex-1">
                <h2 class="text-3xl font-bold text-white mb-4 leading-tight">
                  {{ title }} 
                  <span class="inline-block bg-gradient-to-r from-rose-400 to-pink-400 bg-clip-text text-transparent">{{ highlightedText }}</span>
                </h2>
                
                <p class="text-lg text-gray-300 mb-8 leading-relaxed">
                  {{ description }}
                  <span v-if="highlightedStat" class="font-semibold text-rose-300">{{ highlightedStat }}</span>
                  {{ descriptionSuffix }}
                </p>
                
                <div class="flex flex-col sm:flex-row gap-4">
                  <!-- Primary Button -->
                  <router-link 
                    :to="getAuthenticatedRedirect"
                    class="group/btn relative inline-flex items-center justify-center px-8 py-3 bg-gradient-to-r from-rose-500 to-pink-500 hover:from-rose-400 hover:to-pink-400 text-white font-medium rounded-xl shadow-lg shadow-rose-500/25 transition-all duration-200 transform hover:-translate-y-1"
                  >
                    <i :class="primaryButtonIcon" class="mr-2"></i>
                    <span>{{ primaryButtonText }}</span>
                    <i class="fas fa-arrow-right ml-2 transform group-hover/btn:translate-x-1 transition-transform duration-300"></i>
                  </router-link>
                  
                  <!-- Secondary Button -->
                  <router-link 
                    v-if="showSecondaryButton"
                    :to="secondaryButtonTo"
                    class="group/btn relative inline-flex items-center justify-center px-8 py-3 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-rose-400/30 text-white font-medium rounded-xl transition-all duration-200"
                  >
                    <i :class="secondaryButtonIcon" class="mr-2 text-rose-400"></i>
                    <span>{{ secondaryButtonText }}</span>
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent, computed } from 'vue'
import { useAuthStore } from '@/shared/stores/auth'
import { HomeNavbarButton } from '@/apps/home/components/atoms/buttons'

export default defineComponent({
  name: 'CTASection',
  components: {
    HomeNavbarButton
  },
  props: {
    title: {
      type: String,
      default: 'Build for Dollars, Not'
    },
    highlightedText: {
      type: String,
      default: 'Thousands'
    },
    icon: {
      type: String,
      default: 'fas fa-lightbulb'
    },
    description: {
      type: String,
      default: 'Create your web app in minutes instead of waiting months. With Imagi, you\'ll build your app for'
    },
    highlightedStat: {
      type: String,
      default: ' a fraction of the cost'
    },
    descriptionSuffix: {
      type: String,
      default: ' of hiring a professional developer.'
    },
    primaryButtonText: {
      type: String,
      default: 'Start Building'
    },
    primaryButtonIcon: {
      type: String,
      default: 'fas fa-rocket'
    },
    primaryButtonTo: {
      type: [String, Object],
      default: '/products/oasis/builder/dashboard'
    },
    showSecondaryButton: {
      type: Boolean,
      default: false
    },
    secondaryButtonText: {
      type: String,
      default: 'Learn More'
    },
    secondaryButtonTo: {
      type: [String, Object],
      default: '/docs'
    },
    secondaryButtonIcon: {
      type: String,
      default: 'fas fa-book'
    }
  },
  setup(props) {
    const authStore = useAuthStore()
    const isAuthenticated = computed(() => authStore.isAuthenticated)
    
    const getAuthenticatedRedirect = computed(() => {
      return isAuthenticated.value 
        ? (typeof props.primaryButtonTo === 'string' ? props.primaryButtonTo : '/products/oasis/builder/dashboard')
        : '/auth/login'
    })
    
    return {
      isAuthenticated,
      getAuthenticatedRedirect
    }
  }
})
</script>

<style scoped>
@keyframes pulse-slow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

@keyframes pulse-horizontal {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(4px); }
}

.animate-pulse-slow {
  animation: pulse-slow 3s ease-in-out infinite;
}

.animate-pulse-horizontal {
  animation: pulse-horizontal 1.5s ease-in-out infinite;
}
</style> 