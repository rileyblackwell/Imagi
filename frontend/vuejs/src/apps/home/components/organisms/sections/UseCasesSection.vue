<!-- Use Cases Section - Premium Design -->
<template>
  <section class="py-20 md:py-32 px-6 sm:px-8 lg:px-12 relative overflow-hidden">
    <div class="max-w-7xl mx-auto relative">
      <!-- Section header -->
      <div class="text-center mb-16 md:mb-20">
        <!-- Badge -->
        <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/[0.03] rounded-full border border-white/[0.08] mb-6">
          <i class="fas fa-cubes text-xs text-fuchsia-400/80"></i>
          <span class="text-sm font-medium text-white/60">Use Cases</span>
        </div>
        
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-semibold text-white/90 mb-5 tracking-tight">{{ title }}</h2>
        <p class="text-lg text-white/50 max-w-2xl mx-auto leading-relaxed">{{ subtitle }}</p>
      </div>

      <!-- Use case cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 md:gap-6">
        <div 
          v-for="(useCase, index) in useCases" 
          :key="index"
          class="group relative"
        >
          <!-- Card -->
          <div class="relative h-full p-6 rounded-2xl border border-white/[0.06] bg-white/[0.02] backdrop-blur-sm cursor-default overflow-hidden flex flex-col">
            
            <!-- Icon -->
            <div class="relative mb-5">
              <div 
                class="inline-flex items-center justify-center w-11 h-11 rounded-xl border"
                :class="getIconContainerClassStatic(useCase.color)"
              >
                <i :class="[useCase.icon, 'text-base', getIconClass(useCase.color)]"></i>
              </div>
            </div>
            
            <!-- Content -->
            <h3 class="relative text-base font-semibold text-white/90 mb-2">{{ useCase.title }}</h3>
            <p class="relative text-white/50 text-sm leading-relaxed mb-5 flex-1">{{ useCase.description }}</p>
            
            <!-- Features -->
            <ul class="relative space-y-2 mb-5">
              <li 
                v-for="(feature, fIndex) in useCase.features" 
                :key="fIndex" 
                class="flex items-start gap-2"
              >
                <i class="fas fa-check text-[10px] mt-1.5" :class="getIconClass(useCase.color)"></i>
                <span class="text-white/50 text-xs">{{ feature }}</span>
              </li>
            </ul>
            
            <!-- Learn more link -->
            <div class="relative mt-auto">
              <a href="#" class="inline-flex items-center gap-2 text-sm font-medium" :class="getLinkClassStatic(useCase.color)">
                <span>Explore</span>
                <i class="fas fa-arrow-right text-xs"></i>
              </a>
            </div>
          </div>
        </div>
      </div>
      
      <!-- CTA button -->
      <div class="mt-14 text-center">
        <HomeNavbarButton
          :to="{ name: isAuthenticated ? 'builder-dashboard' : 'login' }"
          class="inline-flex items-center gap-3 px-8 py-4 bg-white/[0.05] border border-white/[0.1] rounded-xl text-white font-medium"
        >
          Start Your Project
          <i class="fas fa-arrow-right text-sm"></i>
        </HomeNavbarButton>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent, computed } from 'vue'
import { useAuthStore } from '@/shared/stores/auth'
import { HomeNavbarButton } from '@/apps/home/components/atoms/buttons'

export default defineComponent({
  name: 'UseCasesSection',
  components: {
    HomeNavbarButton
  },
  props: {
    title: {
      type: String,
      default: 'Built for Every Business'
    },
    subtitle: {
      type: String,
      default: 'From small businesses to startups, build professional applications tailored to your needs.'
    },
    useCases: {
      type: Array,
      default: () => [
        {
          title: 'Business Platform',
          description: 'Complete business management with customer portal, booking system, and admin dashboard.',
          icon: 'fas fa-store',
          color: 'violet',
          features: [
            'Customer management',
            'Service booking',
            'Analytics dashboard'
          ]
        },
        {
          title: 'Portfolio & CRM',
          description: 'Professional portfolio with integrated client management and project tracking.',
          icon: 'fas fa-briefcase',
          color: 'fuchsia',
          features: [
            'Project gallery',
            'Client management',
            'Automated follow-ups'
          ]
        },
        {
          title: 'E-Learning',
          description: 'Educational platform with course management and student progress tracking.',
          icon: 'fas fa-graduation-cap',
          color: 'blue',
          features: [
            'Course content',
            'Progress tracking',
            'Interactive modules'
          ]
        },
        {
          title: 'Event Platform',
          description: 'Full event management with registration, attendees, and real-time updates.',
          icon: 'fas fa-calendar-alt',
          color: 'emerald',
          features: [
            'Registration system',
            'Attendee check-in',
            'Real-time updates'
          ]
        }
      ]
    }
  },
  setup() {
    const authStore = useAuthStore()
    
    return {
      isAuthenticated: computed(() => authStore.isAuthenticated)
    }
  },
  methods: {
    getGradientClass(color) {
      const gradients = {
        violet: 'from-violet-500 to-purple-500',
        fuchsia: 'from-fuchsia-500 to-pink-500',
        blue: 'from-blue-500 to-cyan-500',
        emerald: 'from-emerald-500 to-teal-500'
      }
      return gradients[color] || gradients.violet
    },
    getIconContainerClassStatic(color) {
      const classes = {
        violet: 'bg-violet-500/10 border-violet-500/20',
        fuchsia: 'bg-fuchsia-500/10 border-fuchsia-500/20',
        blue: 'bg-blue-500/10 border-blue-500/20',
        emerald: 'bg-emerald-500/10 border-emerald-500/20'
      }
      return classes[color] || classes.violet
    },
    getIconClass(color) {
      const classes = {
        violet: 'text-violet-400',
        fuchsia: 'text-fuchsia-400',
        blue: 'text-blue-400',
        emerald: 'text-emerald-400'
      }
      return classes[color] || classes.violet
    },
    getLinkClassStatic(color) {
      const classes = {
        violet: 'text-violet-400/70',
        fuchsia: 'text-fuchsia-400/70',
        blue: 'text-blue-400/70',
        emerald: 'text-emerald-400/70'
      }
      return classes[color] || classes.violet
    }
  }
})
</script>

<style scoped>
</style>
