<!--
  Home landing page.

  Design direction: "quiet paper, loud product". The page itself is deliberately
  plain — one flat paper tone, one ink, one accent, hairline rules instead of
  cards — so the thing that carries the visual weight is the product itself:
  real screenshots of the build workspace and the project hub, shot from the
  running app and framed in a minimal window chrome.

  The palette and primitives live in shared/styles/editorial.css, scoped to the
  .editorial class every public page carries.
-->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="editorial home-page relative min-h-screen font-body">

      <!-- Whisper of grain: keeps the flat paper from reading as dead pixels -->
      <div class="grain-overlay absolute inset-0 z-[1] pointer-events-none" aria-hidden="true"></div>

      <main class="relative z-10">
        <HeroSection />
        <StatsSection />
        <FeaturesSection />
        <KeyFeaturesSection />
        <CTASection />
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
/* Everything else lives in shared/styles/editorial.css — this page only needs
   smooth in-page scrolling for the hero's "see how it works" jump. */
:deep(html) {
  scroll-behavior: smooth;
}
</style>
