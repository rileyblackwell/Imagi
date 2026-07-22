<!-- Home landing page - warm porcelain editorial design -->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="home-page relative min-h-screen overflow-hidden font-body transition-colors duration-500">

      <!-- Grain texture over the whole canvas -->
      <div class="grain-overlay absolute inset-0 z-[1] pointer-events-none" aria-hidden="true"></div>

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
          title="Start your business today"
          description="Build your web app with AI, then run it with tools for marketing, sales, and finance. Everything you need to launch and grow, in one place."
          primaryButtonText="Get Started"
          primaryButtonTo="/imagi/projects"
          :showSecondaryButton="false"
          footnote="Start for free. Upgrade anytime as you grow."
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
/* One continuous warm-porcelain canvas; sections paint soft washes on top.
   The gradient ends on the footer's exact background so the page hands off
   seamlessly (footer is bg-white / dark #0a0a0a). */
.home-page {
  background: linear-gradient(180deg, #fdf9f2 0%, #faf7f1 45%, #ffffff 100%);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

:root.dark .home-page,
.dark .home-page {
  background: linear-gradient(180deg, #0c0c0e 0%, #0a0b0f 50%, #0a0a0a 100%);
}

/* Fine film grain keeps large soft gradients from banding and adds texture */
.grain-overlay {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160' viewBox='0 0 160 160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='160' height='160' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E");
  background-size: 160px 160px;
  opacity: 0.035;
  mix-blend-mode: multiply;
}

:root.dark .grain-overlay,
.dark .grain-overlay {
  opacity: 0.05;
  mix-blend-mode: overlay;
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

<!-- Unscoped: shared motion + selection styles used across home sections -->
<style>
/* Scroll reveal (classes applied by the v-reveal directive) */
.reveal-init {
  opacity: 0;
  transform: translateY(26px);
  transition:
    opacity 0.8s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.8s cubic-bezier(0.22, 1, 0.36, 1);
  will-change: opacity, transform;
}

.reveal-init.is-revealed {
  opacity: 1;
  transform: none;
}

@media (prefers-reduced-motion: reduce) {
  .reveal-init {
    opacity: 1;
    transform: none;
    transition: none;
  }
}

/* Brand-tinted text selection on the landing page */
.home-page ::selection {
  background: rgba(158, 205, 243, 0.55);
  color: #172554;
}

.dark .home-page ::selection {
  background: rgba(96, 165, 250, 0.4);
  color: #eff6ff;
}
</style>
