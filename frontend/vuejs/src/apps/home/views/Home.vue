<!-- Home landing page -->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="bg-dark-950 min-h-screen">
      <!-- Main Content -->
      <main>
        <!-- Hero Section -->
        <HeroSection />
        
        <!-- Features Section -->
        <FeaturesSection />
        
        <!-- How It Works Section -->
        <HowItWorksSection />
        
        <!-- Use Cases Section -->
        <UseCasesSection />
        
        <!-- Stats Section -->
        <StatsSection />
        
        <!-- Testimonials Section -->
        <TestimonialsSection />
        
        <!-- CTA Section -->
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

/* Rainbow gradient for connecting lines */
:deep(.grid) .absolute.h-px.bg-gradient-to-r {
  background: linear-gradient(90deg, 
    rgba(99, 102, 241, 0) 0%,
    rgba(99, 102, 241, 0.6) 20%, 
    rgba(79, 70, 229, 0.6) 40%, 
    rgba(139, 92, 246, 0.6) 60%, 
    rgba(217, 70, 239, 0.6) 80%, 
    rgba(99, 102, 241, 0) 100%
  );
  background-size: 200% 100%;
  animation: gradient-shift 8s ease infinite;
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
</style>