<!-- Home landing page - Clean Apple/Cursor-inspired design -->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="min-h-screen bg-white dark:bg-[#0a0a0a] relative overflow-hidden transition-colors duration-500">
      <!-- Clean minimal background -->
      <div class="fixed inset-0 pointer-events-none">
        <!-- Subtle gradient - very minimal -->
        <div class="absolute inset-0 bg-gradient-to-b from-gray-50/50 via-white to-white dark:from-[#0a0a0a] dark:via-[#0a0a0a] dark:to-[#0a0a0a] transition-colors duration-500"></div>
      </div>

      <!-- Main Content -->
      <main class="relative z-10">
        <!-- Hero Section -->
        <HeroSection />
        
        <!-- Features Section -->
        <FeaturesSection />
        
        <!-- Stats Section -->
        <StatsSection />
        
        <!-- CTA Section -->
        <CTASection 
          title="Ready to build?" 
          description="Transform your ideas into production-ready web applications. Start building for free today."
          primaryButtonText="Get Started"
          primaryButtonTo="/products/oasis/builder/dashboard"
          :showSecondaryButton="false"
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
  StatsSection,
  CTASection
} from '@/apps/home/components/organisms/sections'

export default defineComponent({
  name: 'HomePage',
  components: {
    DefaultLayout,
    HeroSection,
    FeaturesSection,
    StatsSection,
    CTASection
  }
})
</script>

<style scoped>
/* Minimal scrollbar */
:deep(::-webkit-scrollbar) {
  width: 8px;
}

:deep(::-webkit-scrollbar-track) {
  background: transparent;
}

:deep(::-webkit-scrollbar-thumb) {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 4px;
}

:deep(::-webkit-scrollbar-thumb:hover) {
  background: rgba(0, 0, 0, 0.25);
}

:root.dark :deep(::-webkit-scrollbar-thumb) {
  background: rgba(255, 255, 255, 0.15);
}

:root.dark :deep(::-webkit-scrollbar-thumb:hover) {
  background: rgba(255, 255, 255, 0.25);
}
</style>
