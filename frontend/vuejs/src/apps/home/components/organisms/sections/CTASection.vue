<!-- CTA Section - Ultra Premium Design -->
<template>
  <section class="py-24 sm:py-32 px-6 sm:px-8 lg:px-12 pb-28 sm:pb-36">
    <div class="max-w-4xl mx-auto">
      <!-- CTA Card with premium styling -->
      <div class="group relative">
        <!-- Multi-layer background glow - refined -->
        <div class="absolute -inset-3 bg-gradient-to-r from-violet-600/20 via-fuchsia-600/25 to-violet-600/20 rounded-[2rem] blur-2xl opacity-45 group-hover:opacity-60 transition-opacity duration-700"></div>
        <div class="absolute -inset-1.5 bg-gradient-to-br from-violet-500/15 to-fuchsia-500/15 rounded-3xl blur-xl opacity-55 group-hover:opacity-70 transition-opacity duration-500"></div>
        
        <!-- Card container with refined glass effect -->
        <div class="relative rounded-2xl overflow-hidden">
          <!-- Border gradient -->
          <div class="absolute inset-0 rounded-2xl p-[1px] bg-gradient-to-b from-white/25 via-white/[0.08] to-white/[0.03]">
            <div class="w-full h-full rounded-2xl bg-[#0a0a14]"></div>
          </div>
          
          <!-- Card content -->
          <div class="relative p-8 md:p-12 bg-gradient-to-b from-white/[0.03] to-transparent rounded-2xl">
            <!-- Top accent line -->
            <div class="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-violet-500/60 to-transparent"></div>
            
            <!-- Content layout -->
            <div class="flex flex-col md:flex-row items-start gap-8">
              <!-- Icon with glow effect -->
              <div class="flex-shrink-0 relative">
                <div class="absolute -inset-3 bg-gradient-to-br from-violet-500/25 to-fuchsia-500/15 rounded-2xl blur-xl opacity-55"></div>
                <div class="relative inline-flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br from-violet-500/20 to-fuchsia-500/15 border border-violet-500/30 shadow-lg shadow-violet-500/10">
                  <i :class="icon" class="text-violet-400 text-xl"></i>
                </div>
              </div>
              
              <!-- Text content -->
              <div class="flex-1">
                <h2 class="text-2xl md:text-3xl lg:text-4xl font-bold text-white mb-4 leading-tight tracking-[-0.02em]">
                  {{ title }} 
                  <span class="bg-gradient-to-r from-violet-400 via-fuchsia-400 to-violet-400 bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient-x">{{ highlightedText }}</span>
                </h2>
                
                <p class="text-base md:text-lg text-white/70 mb-8 leading-relaxed max-w-xl font-light">
                  {{ description }}
                  <span v-if="highlightedStat" class="font-medium text-violet-400">{{ highlightedStat }}</span>{{ descriptionSuffix }}
                </p>
                
                <!-- Buttons - enhanced -->
                <div class="flex flex-col sm:flex-row gap-4">
                  <!-- Primary Button with premium styling -->
                  <router-link 
                    :to="getAuthenticatedRedirect"
                    class="group/btn relative inline-flex items-center justify-center overflow-hidden rounded-xl"
                  >
                    <!-- Button glow -->
                    <div class="absolute -inset-1 bg-gradient-to-r from-violet-600 via-fuchsia-600 to-violet-600 rounded-xl blur-lg opacity-40 group-hover/btn:opacity-60 transition-opacity duration-500"></div>
                    <!-- Button background -->
                    <div class="absolute inset-0 bg-gradient-to-r from-violet-600 via-fuchsia-600 to-violet-600 bg-[length:200%_100%] transition-all duration-700 group-hover/btn:bg-[length:150%_100%]"></div>
                    <!-- Inner highlight -->
                    <div class="absolute inset-[1px] bg-gradient-to-b from-white/15 to-transparent rounded-xl opacity-85"></div>
                    <!-- Shimmer effect -->
                    <div class="absolute inset-0 opacity-0 group-hover/btn:opacity-100 transition-opacity duration-500">
                      <div class="absolute inset-0 -translate-x-full group-hover/btn:translate-x-full transition-transform duration-1000 ease-out bg-gradient-to-r from-transparent via-white/20 to-transparent skew-x-12"></div>
                    </div>
                    <!-- Button content -->
                    <span class="relative flex items-center gap-3 px-7 py-3.5 text-white font-semibold">
                      <i :class="primaryButtonIcon"></i>
                      <span>{{ primaryButtonText }}</span>
                      <i class="fas fa-arrow-right text-sm transform group-hover/btn:translate-x-1 transition-transform duration-300"></i>
                    </span>
                  </router-link>
                  
                  <!-- Secondary Button - refined glass style -->
                  <router-link 
                    v-if="showSecondaryButton"
                    :to="secondaryButtonTo"
                    class="group/btn relative inline-flex items-center justify-center gap-3 px-7 py-3.5 rounded-xl text-white font-medium transition-all duration-300 overflow-hidden"
                  >
                    <!-- Background -->
                    <div class="absolute inset-0 bg-white/[0.05] rounded-xl border border-white/[0.10] group-hover/btn:bg-white/[0.08] group-hover/btn:border-white/[0.18] transition-all duration-300"></div>
                    <!-- Content -->
                    <i :class="secondaryButtonIcon" class="text-violet-400 relative"></i>
                    <span class="relative">{{ secondaryButtonText }}</span>
                  </router-link>
                </div>
              </div>
            </div>
            
            <!-- Decorative elements -->
            <div class="absolute -bottom-20 -right-20 w-44 h-44 bg-gradient-to-br from-violet-500/6 to-fuchsia-500/4 rounded-full blur-3xl"></div>
            <div class="absolute -top-20 -left-20 w-36 h-36 bg-gradient-to-tr from-fuchsia-500/6 to-violet-500/4 rounded-full blur-3xl"></div>
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
/* Gradient animation for highlighted text */
@keyframes gradient-x {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.animate-gradient-x {
  animation: gradient-x 5s ease infinite;
}
</style>
