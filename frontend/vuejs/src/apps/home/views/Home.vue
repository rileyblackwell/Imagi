<!-- Home landing page - Clean Apple/Cursor-inspired design -->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="min-h-screen bg-white dark:bg-[#0a0a0a] relative overflow-hidden transition-colors duration-500">
      <!-- Enhanced minimal background with subtle noise texture effect -->
      <div class="fixed inset-0 pointer-events-none">
        <!-- Subtle gradient - very minimal -->
        <div class="absolute inset-0 bg-gradient-to-b from-gray-50/50 via-white to-white dark:from-[#0a0a0a] dark:via-[#0a0a0a] dark:to-[#0a0a0a] transition-colors duration-500"></div>
        
        <!-- Very subtle grid pattern for texture (dark mode only) -->
        <div class="absolute inset-0 opacity-[0.015] dark:opacity-[0.02]" 
             style="background-image: linear-gradient(rgba(128,128,128,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(128,128,128,0.1) 1px, transparent 1px); background-size: 64px 64px;"></div>
      </div>

      <!-- Main Content -->
      <main class="relative z-10">
        <!-- Hero Section -->
        <HeroSection />
        
        <!-- Stats Section -->
        <StatsSection />
        
        <!-- Features Section -->
        <FeaturesSection />
        
        <!-- Key Features Section -->
        <KeyFeaturesSection />
        
        <!-- CTA Section -->
        <CTASection 
          title="Start building today" 
          description="Turn your ideas into web applications. Prototype quickly, test with real users, and build momentum."
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
  KeyFeaturesSection,
  StatsSection,
  CTASection
} from '@/apps/home/components/organisms/sections'

export default defineComponent({
  name: 'HomePage',
  components: {
    DefaultLayout,
    HeroSection,
    FeaturesSection,
    KeyFeaturesSection,
    StatsSection,
    CTASection
  }
})
</script>

<style scoped>
/* Refined minimal scrollbar */
:deep(::-webkit-scrollbar) {
  width: 8px;
}

:deep(::-webkit-scrollbar-track) {
  background: transparent;
}

:deep(::-webkit-scrollbar-thumb) {
  background: rgba(0, 0, 0, 0.12);
  border-radius: 4px;
  transition: background 0.2s ease;
}

:deep(::-webkit-scrollbar-thumb:hover) {
  background: rgba(0, 0, 0, 0.2);
}

:root.dark :deep(::-webkit-scrollbar-thumb) {
  background: rgba(255, 255, 255, 0.12);
}

:root.dark :deep(::-webkit-scrollbar-thumb:hover) {
  background: rgba(255, 255, 255, 0.2);
}

/* Smooth scroll behavior */
:deep(html) {
  scroll-behavior: smooth;
}
</style>
