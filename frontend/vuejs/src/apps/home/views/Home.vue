<!-- Home landing page -->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="min-h-screen bg-gradient-to-b from-dark-950 to-dark-900">
      <!-- Decorative Elements -->
      <div class="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <!-- Gradient orbs -->
        <div class="absolute top-[10%] left-[5%] w-[300px] sm:w-[500px] md:w-[800px] h-[300px] sm:h-[500px] md:h-[800px] rounded-full bg-primary-500/5 blur-[80px] sm:blur-[120px] animate-float"></div>
        <div class="absolute bottom-[20%] right-[10%] w-[200px] sm:w-[400px] md:w-[600px] h-[200px] sm:h-[400px] md:h-[600px] rounded-full bg-violet-500/5 blur-[60px] sm:blur-[100px] animate-float-delay"></div>
        <!-- Grid pattern overlay -->
        <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
        <!-- Subtle noise texture -->
        <div class="absolute inset-0 bg-noise opacity-[0.015]"></div>
      </div>

      <!-- Main Content -->
      <main class="relative z-10 overflow-x-hidden">
        <!-- Hero Section with enhanced design -->
        <HeroSection />
        
        <!-- Divider with animated line -->
        <div class="relative h-16 sm:h-24 max-w-7xl mx-auto">
          <div class="absolute inset-x-0 h-px mx-auto w-2/3 sm:w-1/2 bg-gradient-to-r from-transparent via-primary-500/30 to-transparent animate-pulse-slow"></div>
        </div>
        
        <!-- Features Section with improved cards -->
        <FeaturesSection />
        
        <!-- How It Works Section with better visualization -->
        <HowItWorksSection />
        
        <!-- Use Cases Section with improved interaction -->
        <UseCasesSection />
        
        <!-- Testimonials Section with enhanced visuals -->
        <TestimonialsSection />
        
        <!-- Stats Section with modern data visualization -->
        <StatsSection />
        
        <!-- Enhanced CTA Section -->
        <CTASection />
      </main>
    </div>
  </DefaultLayout>
</template>

<script>
import { defineComponent } from 'vue'
import { DefaultLayout } from '@/shared/layouts'
import { 
  HeroSection,
  FeaturesSection,
  HowItWorksSection,
  UseCasesSection,
  StatsSection,
  TestimonialsSection,
  CTASection
} from '@/apps/home/components/organisms/sections'

export default defineComponent({
  name: 'HomePage',
  components: {
    DefaultLayout,
    HeroSection,
    FeaturesSection,
    HowItWorksSection,
    UseCasesSection,
    StatsSection,
    TestimonialsSection,
    CTASection
  }
})
</script>

<style scoped>
/* Noise texture */
.bg-noise {
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.15'/%3E%3C/svg%3E");
}

/* Floating animations for background elements */
@keyframes float {
  0% { transform: translate(0, 0) rotate(0deg); }
  50% { transform: translate(-15px, 15px) rotate(1deg); }
  100% { transform: translate(0, 0) rotate(0deg); }
}

@keyframes float-delay {
  0% { transform: translate(0, 0) rotate(0deg); }
  50% { transform: translate(15px, -15px) rotate(-1deg); }
  100% { transform: translate(0, 0) rotate(0deg); }
}

.animate-float {
  animation: float 20s ease-in-out infinite;
}

.animate-float-delay {
  animation: float-delay 25s ease-in-out infinite;
}

/* Gradient animation for connecting lines */
@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.bg-gradient-to-r {
  background-size: 200% 100%;
  animation: gradient-shift 8s ease infinite;
}

/* Pulsing animation for highlights */
@keyframes pulse-slow {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 0.5; }
}

.animate-pulse-slow {
  animation: pulse-slow 4s ease-in-out infinite;
}

/* Override any dark-950 if not available in Tailwind config */
.bg-dark-950 {
  background-color: rgba(9, 11, 17, 0.95);
}

.from-dark-950 {
  --tw-gradient-from: rgba(9, 11, 17, 0.95);
}

.to-dark-950 {
  --tw-gradient-to: rgba(9, 11, 17, 0.95);
}

/* Add subtle scrollbar styling */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(9, 11, 17, 0.5);
}

::-webkit-scrollbar-thumb {
  background: rgba(59, 130, 246, 0.3);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(59, 130, 246, 0.5);
}
</style>