<!--
  Home landing page.

  Design direction: "quiet paper, loud product". The page itself is deliberately
  plain — one flat paper tone, one ink, one accent, hairline rules instead of
  cards — so the thing that carries the visual weight is the product itself:
  real screenshots of the build workspace and the project hub, shot from the
  running app and framed in a minimal window chrome.

  The palette lives here as custom properties. Custom properties inherit through
  the DOM regardless of style scoping, so every section below reads the same
  tokens without importing anything.
-->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="home-page relative min-h-screen font-body">

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
.home-page {
  background: var(--paper);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

/* Fine film grain — the one piece of texture the design keeps */
.grain-overlay {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160' viewBox='0 0 160 160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='160' height='160' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E");
  background-size: 160px 160px;
  opacity: 0.028;
  mix-blend-mode: multiply;
}

:root.dark .grain-overlay,
.dark .grain-overlay {
  opacity: 0.045;
  mix-blend-mode: overlay;
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

:deep(html) {
  scroll-behavior: smooth;
}
</style>

<!-- Unscoped: design tokens + motion, shared by every section below -->
<style>
.home-page {
  /* Paper and ink. One accent, used sparingly — everything else is ink at a
     lower opacity, which is what keeps the page from looking decorated. */
  --paper: #fbfaf7;
  --paper-raised: #ffffff;
  --ink: #131a2c;
  --ink-70: rgba(19, 26, 44, 0.72);
  --ink-55: rgba(19, 26, 44, 0.58);
  --ink-40: rgba(19, 26, 44, 0.42);
  --rule: rgba(19, 26, 44, 0.11);
  --rule-strong: rgba(19, 26, 44, 0.18);
  --accent: #c2410c;
  --accent-soft: rgba(194, 65, 12, 0.1);
}

.dark .home-page {
  --paper: #08080a;
  --paper-raised: rgba(255, 255, 255, 0.035);
  --ink: #f6f4f0;
  --ink-70: rgba(246, 244, 240, 0.7);
  --ink-55: rgba(246, 244, 240, 0.56);
  --ink-40: rgba(246, 244, 240, 0.4);
  --rule: rgba(255, 255, 255, 0.1);
  --rule-strong: rgba(255, 255, 255, 0.18);
  --accent: #fbbf24;
  --accent-soft: rgba(251, 191, 36, 0.12);
}

/* Scroll reveal (classes applied by the v-reveal directive) */
.reveal-init {
  opacity: 0;
  transform: translateY(20px);
  transition:
    opacity 0.7s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.7s cubic-bezier(0.22, 1, 0.36, 1);
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

.home-page ::selection {
  background: var(--accent-soft);
  color: var(--ink);
}

/* --- Shared primitives ------------------------------------------------- */

/* Section shell: one measure, one rhythm, everywhere. */
.home-page .section-shell {
  max-width: 68rem;
  margin: 0 auto;
  padding-left: 1.5rem;
  padding-right: 1.5rem;
}

@media (min-width: 640px) {
  .home-page .section-shell {
    padding-left: 2rem;
    padding-right: 2rem;
  }
}

/* Full-bleed hairline that opens each section */
.home-page .section-rule {
  height: 1px;
  background: var(--rule);
}

/* Editorial eyebrow: numeral, hairline, tracked label */
.home-page .eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--ink-55);
}

.home-page .eyebrow__num {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 0.78rem;
  font-variant-numeric: tabular-nums;
  color: var(--accent);
}

.home-page .eyebrow__rule {
  width: 1.75rem;
  height: 1px;
  background: var(--rule-strong);
}

/* Accent diamond — the closing section's one warm mark, standing in for the
   step numeral the numbered sections carry. */
.home-page .eyebrow__mark {
  width: 0.3rem;
  height: 0.3rem;
  transform: rotate(45deg);
  background: var(--accent);
}

/* Headline scale — Fraunces, tight, balanced */
.home-page .display {
  font-family: 'Fraunces', Georgia, Cambria, 'Times New Roman', serif;
  font-weight: 600;
  letter-spacing: -0.02em;
  line-height: 1.06;
  color: var(--ink);
  text-wrap: balance;
}

.home-page .lede {
  color: var(--ink-55);
  line-height: 1.65;
  text-wrap: pretty;
}

/* --- Buttons ------------------------------------------------------------
   Shared by the hero and the closing CTA so the page's two asks look like
   one. Flat ink, no layered shadow — the drop-shadowed pill read as a glossy
   chip against paper and fought the hairline-and-ink language everywhere
   else. */

.home-page .btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  padding: 0.85rem 1.6rem;
  border-radius: 999px;
  font-size: 1rem;
  font-weight: 500;
  background: var(--ink);
  color: var(--paper);
  border: 1px solid var(--ink);
  transition: background 0.18s ease, border-color 0.18s ease, color 0.18s ease;
}

.home-page .btn-primary:hover {
  background: transparent;
  color: var(--ink);
}

.home-page .btn-quiet {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.85rem 0;
  font-size: 1rem;
  font-weight: 500;
  color: var(--ink-70);
  border-radius: 0.25rem;
  transition: color 0.18s ease;
}

.home-page .btn-quiet:hover {
  color: var(--ink);
}

.home-page .btn-quiet span {
  border-bottom: 1px solid var(--rule-strong);
  padding-bottom: 2px;
  transition: border-color 0.18s ease;
}

.home-page .btn-quiet:hover span {
  border-bottom-color: var(--accent);
}

.home-page .btn-primary:focus-visible,
.home-page .btn-quiet:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 3px;
}
</style>
