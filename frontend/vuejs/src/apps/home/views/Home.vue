<!--
  Home landing page — "Spotlight".

  A dark stage: warm coral-to-amber light falls from above onto a blue-black
  floor, the prompt sits in it like a command bar, and the real product
  screenshots further down are lit like objects on stage.

  The tokens and shared primitives live in apps/home/styles/spotlight.css,
  scoped to .spotlight. `dark` sits on the same wrapper so the shared navbar
  and footer render in their dark variant here whatever the visitor's saved
  theme is (see the note at the top of spotlight.css).
-->
<template>
  <div class="spotlight dark home-page">
    <DefaultLayout>
      <div class="relative">
        <HeroSection />
        <StatsSection />
        <div class="sl-divider" aria-hidden="true"></div>
        <FeaturesSection />
        <div class="sl-divider" aria-hidden="true"></div>
        <KeyFeaturesSection />
        <ClosingSection />
      </div>
    </DefaultLayout>
  </div>
</template>

<script>
import { defineComponent, onMounted } from 'vue'
import { DefaultLayout } from '@/shared/layouts'
import {
  HeroSection,
  FeaturesSection,
  KeyFeaturesSection,
  StatsSection,
  ClosingSection
} from '@/apps/home/components/organisms/sections'
import { checkBackendHealth } from '@/apps/home/services/healthService'
import '@/apps/home/styles/spotlight.css'

export default defineComponent({
  name: 'HomePage',
  components: {
    DefaultLayout,
    HeroSection,
    FeaturesSection,
    KeyFeaturesSection,
    StatsSection,
    ClosingSection
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
/* Everything else lives in apps/home/styles/spotlight.css — this page only
   needs smooth in-page scrolling for the hero's "see how it works" jump. */
:deep(html) {
  scroll-behavior: smooth;
}
</style>
