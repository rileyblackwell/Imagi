<!-- Home landing page - Clean Apple/Cursor-inspired design -->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="home-page min-h-screen bg-white dark:bg-[#0a0a0a] relative overflow-hidden transition-colors duration-500">

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
          primaryButtonTo="/products/imagi/projects"
          :showSecondaryButton="false"
        />
      </main>
    </div>
  </DefaultLayout>
</template>

<script>
import { defineComponent, onMounted } from 'vue'
import { DefaultLayout } from '@/shared/layouts'
import {
  HeroSection,
  FeaturesSection,
  KeyFeaturesSection,
  StatsSection,
  CTASection
} from '@/apps/home/components/organisms/sections'
import { checkBackendHealth } from '@/apps/home/services/healthService'

export default defineComponent({
  name: 'HomePage',
  components: {
    DefaultLayout,
    HeroSection,
    FeaturesSection,
    KeyFeaturesSection,
    StatsSection,
    CTASection
  },
  setup() {
    onMounted(async () => {
      try {
        const health = await checkBackendHealth()
        console.log(`Health check passed: ${health.status}, database: ${health.database}`)
      } catch (error) {
        console.error('Health check failed: unable to reach backend', error)
      }
    })
  }
})
</script>

<style scoped>
/* Crisp, sharp text rendering across the landing page */
.home-page {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

.home-page :deep(h1),
.home-page :deep(h2),
.home-page :deep(h3) {
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
  font-feature-settings: 'kern' 1, 'liga' 1, 'calt' 1;
}

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
