<!-- CTA Section - Premium Design -->
<template>
  <section class="py-16 sm:py-24 px-6 sm:px-8 lg:px-12">
    <div class="max-w-4xl mx-auto">
      <!-- CTA Card -->
      <div class="group relative">
        <!-- Background glow -->
        <div class="absolute -inset-1 bg-gradient-to-r from-violet-600/30 via-fuchsia-600/30 to-violet-600/30 rounded-3xl blur-xl opacity-60 group-hover:opacity-80 transition-opacity duration-500"></div>
        
        <!-- Card content -->
        <div class="relative p-8 md:p-12 rounded-2xl border border-white/25 bg-[#12121d]/85 backdrop-blur-xl overflow-hidden">
          <!-- Accent line -->
          <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-500/60 to-transparent"></div>
          
          <!-- Content layout -->
          <div class="flex flex-col md:flex-row items-start gap-8">
            <!-- Icon -->
            <div class="flex-shrink-0">
              <div class="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br from-violet-500/30 to-fuchsia-500/30 border border-violet-500/40">
                <i :class="icon" class="text-violet-400 text-xl"></i>
              </div>
            </div>
            
            <!-- Text content -->
            <div class="flex-1">
              <h2 class="text-2xl md:text-3xl font-semibold text-white mb-4 leading-tight">
                {{ title }} 
                <span class="bg-gradient-to-r from-violet-400 to-fuchsia-400 bg-clip-text text-transparent">{{ highlightedText }}</span>
              </h2>
              
              <p class="text-base md:text-lg text-white/85 mb-8 leading-relaxed max-w-xl">
                {{ description }}
                <span v-if="highlightedStat" class="font-medium text-violet-400">{{ highlightedStat }}</span>{{ descriptionSuffix }}
              </p>
              
              <!-- Buttons -->
              <div class="flex flex-col sm:flex-row gap-4">
                <!-- Primary Button -->
                <router-link 
                  :to="getAuthenticatedRedirect"
                  class="group/btn inline-flex items-center justify-center gap-2 px-7 py-3.5 bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-xl text-white font-medium shadow-lg shadow-violet-500/25 hover:shadow-xl hover:shadow-violet-500/30 transition-all duration-300 hover:-translate-y-0.5"
                >
                  <i :class="primaryButtonIcon"></i>
                  <span>{{ primaryButtonText }}</span>
                  <i class="fas fa-arrow-right text-sm transform group-hover/btn:translate-x-1 transition-transform duration-300"></i>
                </router-link>
                
                <!-- Secondary Button -->
                <router-link 
                  v-if="showSecondaryButton"
                  :to="secondaryButtonTo"
                  class="group/btn inline-flex items-center justify-center gap-2 px-7 py-3.5 bg-white/[0.08] border border-white/[0.2] hover:bg-white/[0.12] hover:border-white/[0.25] rounded-xl text-white font-medium transition-all duration-300"
                >
                  <i :class="secondaryButtonIcon" class="text-violet-400"></i>
                  <span>{{ secondaryButtonText }}</span>
                </router-link>
              </div>
            </div>
          </div>
          
          <!-- Decorative elements -->
          <div class="absolute -bottom-20 -right-20 w-40 h-40 bg-violet-500/5 rounded-full blur-3xl"></div>
          <div class="absolute -top-20 -left-20 w-32 h-32 bg-fuchsia-500/5 rounded-full blur-3xl"></div>
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
</style>
