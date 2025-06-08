<!-- Home landing page -->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="min-h-screen bg-dark-950 relative overflow-hidden">
      <!-- Enhanced Background Effects matching dashboard pages -->
      <div class="absolute inset-0 pointer-events-none">
        <!-- Enhanced Pattern Overlay -->
        <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
        <div class="absolute inset-0 bg-noise opacity-[0.015]"></div>
        <div class="absolute inset-0 bg-gradient-to-br from-primary-950/10 via-dark-900 to-violet-950/10"></div>
        
        <!-- Enhanced Glowing Orbs Animation -->
        <div class="absolute -top-[10%] right-[15%] w-[800px] h-[800px] rounded-full bg-indigo-600/5 blur-[150px] animate-float"></div>
        <div class="absolute bottom-[5%] left-[20%] w-[600px] h-[600px] rounded-full bg-fuchsia-600/5 blur-[120px] animate-float-delay"></div>
        <div class="absolute top-[40%] left-[10%] w-[400px] h-[400px] rounded-full bg-cyan-600/3 blur-[100px] animate-float-slow"></div>
        
        <!-- Animated Lines and Particles -->
        <div class="absolute left-0 right-0 top-1/4 h-px bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent animate-pulse-slow"></div>
        <div class="absolute left-0 right-0 top-1/2 h-px bg-gradient-to-r from-transparent via-violet-500/15 to-transparent animate-pulse-slow delay-1000"></div>
        <div class="absolute left-0 right-0 top-3/4 h-px bg-gradient-to-r from-transparent via-cyan-500/20 to-transparent animate-pulse-slow delay-2000"></div>
      </div>

      <!-- Main Content -->
      <main class="relative z-10">
        <!-- Hero Section with enhanced design -->
        <HeroSection />
        
        <!-- Modern Divider with animated line -->
        <div class="relative py-16 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
          <div class="w-full h-px bg-gradient-to-r from-transparent via-primary-500/30 to-transparent animate-pulse-slow"></div>
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
        <CTASection 
          icon="fas fa-rocket" 
          title="Build for Dollars, Not" 
          highlightedText="Thousands" 
          description="Create your web app in minutes instead of waiting months. With Imagi, you'll build your app for"
          highlightedStat="a fraction of the cost"
          descriptionSuffix=" of hiring a professional developer."
          primaryButtonText="Start Building"
          primaryButtonTo="/products/oasis/builder/dashboard"
          :showSecondaryButton="true"
          secondaryButtonText="Learn More"
          secondaryButtonTo="/docs"
        />
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

/* Float animation for background orbs */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

@keyframes float-delay {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(20px); }
}

@keyframes float-slow {
  0%, 100% { transform: translateY(0) translateX(0); }
  50% { transform: translateY(-15px) translateX(10px); }
}

.animate-float {
  animation: float 15s ease-in-out infinite;
}

.animate-float-delay {
  animation: float-delay 18s ease-in-out infinite;
}

.animate-float-slow {
  animation: float-slow 22s ease-in-out infinite;
}

/* Add subtle animation for pulse effects */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.animate-pulse-slow {
  animation: pulse 3s ease-in-out infinite;
}

.delay-1000 {
  animation-delay: 1000ms;
}

.delay-2000 {
  animation-delay: 2000ms;
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