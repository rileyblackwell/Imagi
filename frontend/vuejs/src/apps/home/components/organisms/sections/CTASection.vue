<!-- CTA Section Component -->
<template>
  <section class="py-16 sm:py-24 px-4 sm:px-6 lg:px-8">
    <div class="max-w-5xl mx-auto">
      <div class="group relative inline-flex w-full">
        <!-- Card with gradient border effect -->
        <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500 to-violet-500 rounded-xl blur opacity-75 group-hover:opacity-100 transition duration-300"></div>
        
        <!-- Card content -->
        <div class="relative w-full bg-dark-900 rounded-xl p-6 md:p-8">
          <div class="flex flex-col md:flex-row items-start gap-6">
            <!-- Icon with background -->
            <div class="w-12 h-12 flex-shrink-0 rounded-full bg-primary-500/20 flex items-center justify-center">
              <i :class="icon || 'fas fa-rocket'" class="text-primary-400 text-xl"></i>
            </div>
            
            <!-- Content section -->
            <div class="flex-1">
              <h2 class="text-2xl font-bold text-white mb-3">{{ title }} <span class="bg-gradient-to-r from-primary-300 to-violet-300 bg-clip-text text-transparent">{{ highlightedText }}</span></h2>
              
              <p class="text-white/80 mb-6">
                {{ description }}
                <span v-if="highlightedStat" class="font-semibold text-primary-200">{{ highlightedStat }}</span>
                {{ descriptionSuffix }}
              </p>
              
              <div class="flex flex-col sm:flex-row gap-4">
                <!-- Primary Button -->
                <router-link 
                  :to="getAuthenticatedRedirect"
                  class="group relative inline-flex items-center justify-center"
                >
                  <!-- Blurred gradient background -->
                  <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500 to-violet-500 rounded-xl blur opacity-75 group-hover:opacity-100 transition duration-300"></div>
                  
                  <!-- Button content -->
                  <div class="relative flex items-center justify-center px-6 py-3 bg-dark-900 rounded-xl transition-all duration-300">
                    <i :class="primaryButtonIcon" class="mr-2 text-primary-400 group-hover:text-primary-300"></i>
                    <span class="font-medium text-white">{{ primaryButtonText }}</span>
                    <i class="fas fa-arrow-right ml-2 text-primary-400 group-hover:text-primary-300 group-hover:translate-x-0.5 transition-transform duration-300"></i>
                  </div>
                </router-link>
                
                <!-- Secondary Button -->
                <router-link 
                  v-if="showSecondaryButton"
                  :to="secondaryButtonTo"
                  class="group relative inline-flex items-center justify-center"
                >
                  <div class="relative flex items-center justify-center px-6 py-3 bg-dark-800/50 rounded-xl border border-white/10 hover:border-primary-500/30 transition-all duration-300">
                    <i :class="secondaryButtonIcon" class="mr-2 text-primary-400/70 group-hover:text-primary-400"></i>
                    <span class="font-medium text-white/80 group-hover:text-white">{{ secondaryButtonText }}</span>
                  </div>
                </router-link>
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