<!-- About Page - warm porcelain editorial design -->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="home-page relative min-h-screen overflow-hidden font-body transition-colors duration-500">

      <!-- Grain texture over the whole canvas -->
      <div class="grain-overlay absolute inset-0 z-[1] pointer-events-none" aria-hidden="true"></div>

      <!-- Main Content -->
      <main class="relative z-10">
        <!-- Hero Section -->
        <section class="relative pt-32 pb-20 sm:pt-40 sm:pb-24 md:pt-48 md:pb-28 px-6 sm:px-8 lg:px-12 transition-colors duration-500">

          <!-- Atmosphere: soft apricot + baby-blue washes over the porcelain canvas -->
          <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
            <div class="wash-warm absolute -top-40 left-1/2 -translate-x-1/3 w-[900px] h-[560px]"></div>
            <div class="wash-cool absolute -top-24 -left-40 w-[700px] h-[520px]"></div>
          </div>

          <div class="relative max-w-4xl mx-auto text-center">

            <!-- Editorial kicker: tracked small caps flanked by fading hairline rules -->
            <div class="hero-item flex items-center justify-center gap-4 mb-8" style="animation-delay: 0ms">
              <span aria-hidden="true" class="hidden sm:block h-px w-12 md:w-16 bg-gradient-to-l from-blue-950/25 to-transparent dark:from-white/25"></span>
              <span class="flex items-center gap-3">
                <span aria-hidden="true" class="w-1 h-1 rotate-45 bg-orange-500/80 dark:bg-orange-400/80"></span>
                <span class="text-[10px] sm:text-[11px] font-semibold uppercase tracking-[0.25em] sm:tracking-[0.3em] leading-none text-blue-950/70 dark:text-blue-100/55 whitespace-nowrap">About Imagi</span>
                <span aria-hidden="true" class="w-1 h-1 rotate-45 bg-orange-500/80 dark:bg-orange-400/80"></span>
              </span>
              <span aria-hidden="true" class="hidden sm:block h-px w-12 md:w-16 bg-gradient-to-r from-blue-950/25 to-transparent dark:from-white/25"></span>
            </div>

            <!-- Hero title -->
            <h1 class="hero-item font-display font-semibold text-[2.9rem] sm:text-6xl md:text-7xl mb-7 tracking-[-0.02em] leading-[1.05] text-balance text-blue-950 dark:text-white transition-colors duration-300" style="animation-delay: 90ms">
              Build and run <em class="hero-accent not-italic">a business</em>
            </h1>

            <!-- Description -->
            <p class="hero-item text-lg sm:text-xl text-blue-950/65 dark:text-blue-100/65 max-w-3xl mx-auto leading-relaxed text-pretty transition-colors duration-300" style="animation-delay: 180ms">
              Imagi is an all-in-one platform for building and running a business. Create your web application with AI-powered tools, then run and grow it with everything you need for marketing, sales, and finance. We handle the technical complexity, so you can focus on your customers.
            </p>
          </div>
        </section>

        <!-- Mission Section -->
        <section class="relative py-20 md:py-28 px-6 sm:px-8 lg:px-12 transition-colors duration-500">

          <!-- Cool baby-blue wash behind the section -->
          <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
            <div class="wash-cool absolute -top-20 right-[-15%] w-[760px] h-[560px]"></div>
          </div>

          <div class="relative max-w-6xl mx-auto">

            <!-- Hairline divider -->
            <div class="section-divider mb-16 md:mb-20" aria-hidden="true"></div>

            <!-- Section header -->
            <div v-reveal class="text-center mb-14 md:mb-16">
              <p class="inline-flex items-center px-3.5 py-1.5 rounded-full border border-orange-200/70 dark:border-orange-400/25 bg-orange-50/80 dark:bg-orange-400/10 text-xs font-semibold text-orange-700 dark:text-orange-300 uppercase tracking-[0.18em] mb-6 transition-colors duration-300">Our Mission</p>
              <h2 class="font-display text-4xl sm:text-5xl md:text-[3.4rem] font-semibold text-blue-950 dark:text-white mb-6 tracking-[-0.015em] leading-[1.08] text-balance transition-colors duration-300">
                Making entrepreneurship accessible to <em class="section-accent not-italic">everyone</em>
              </h2>
              <p class="text-lg sm:text-xl text-blue-950/65 dark:text-blue-100/65 max-w-3xl mx-auto leading-relaxed text-pretty transition-colors duration-300">
                Our mission is to make starting and running a business accessible to everyone. We give you AI-powered tools to build your product and the marketing, sales, and finance tools to run it&mdash;so you can go from idea to thriving business without a technical team.
              </p>
            </div>

            <!-- Mission cards -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div
                v-for="(card, index) in missionCards"
                :key="index"
                v-reveal="{ delay: 90 + index * 90 }"
                class="lift-card relative h-full p-8 rounded-2xl bg-white/85 dark:bg-white/[0.045] border backdrop-blur-sm transition-all duration-300"
                :class="index % 2 === 1 ? 'border-orange-200/70 dark:border-orange-300/[0.14]' : 'border-blue-200/70 dark:border-blue-300/[0.14]'"
              >
                <h3 class="relative text-xl font-semibold tracking-tight text-blue-950 dark:text-white transition-colors duration-300 mb-3">
                  {{ card.title }}
                </h3>
                <p class="relative text-blue-950/65 dark:text-blue-100/65 leading-relaxed text-pretty transition-colors duration-300">
                  {{ card.description }}
                </p>
              </div>
            </div>
          </div>
        </section>

        <!-- What We Do Section -->
        <section class="relative py-20 md:py-28 px-6 sm:px-8 lg:px-12 transition-colors duration-500">

          <!-- Warm apricot wash behind the section -->
          <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
            <div class="wash-warm absolute -top-24 left-[-15%] w-[760px] h-[560px]"></div>
          </div>

          <div class="relative max-w-6xl mx-auto">

            <!-- Hairline divider -->
            <div class="section-divider mb-16 md:mb-20" aria-hidden="true"></div>

            <!-- Section header -->
            <div v-reveal class="text-center mb-14 md:mb-16">
              <p class="inline-flex items-center px-3.5 py-1.5 rounded-full border border-blue-200/70 dark:border-blue-400/25 bg-blue-50/80 dark:bg-blue-400/10 text-xs font-semibold text-blue-700 dark:text-blue-300 uppercase tracking-[0.18em] mb-6 transition-colors duration-300">What We Do</p>
              <h2 class="font-display text-4xl sm:text-5xl md:text-[3.4rem] font-semibold text-blue-950 dark:text-white mb-6 tracking-[-0.015em] leading-[1.08] text-balance transition-colors duration-300">
                One platform to build and run <em class="section-accent not-italic">it all</em>
              </h2>
              <p class="text-lg sm:text-xl text-blue-950/65 dark:text-blue-100/65 max-w-3xl mx-auto leading-relaxed text-pretty transition-colors duration-300">
                Imagi combines AI-powered app building with the everyday tools you need to operate&mdash;marketing, sales, and finance&mdash;so you can launch your product and run your business without stitching together a dozen services.
              </p>
            </div>

            <!-- Features grid -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div
                v-for="(feature, index) in features"
                :key="index"
                v-reveal="{ delay: 90 + index * 90 }"
                class="lift-card relative h-full p-8 rounded-2xl bg-white/85 dark:bg-white/[0.045] border backdrop-blur-sm transition-all duration-300"
                :class="index % 2 === 1 ? 'border-orange-200/70 dark:border-orange-300/[0.14]' : 'border-blue-200/70 dark:border-blue-300/[0.14]'"
              >
                <h3 class="relative text-xl font-semibold tracking-tight text-blue-950 dark:text-white transition-colors duration-300 mb-3">
                  {{ feature.title }}
                </h3>
                <p class="relative text-blue-950/65 dark:text-blue-100/65 leading-relaxed text-pretty transition-colors duration-300">
                  {{ feature.description }}
                </p>
              </div>
            </div>
          </div>
        </section>

        <!-- Who We Serve Section -->
        <section class="relative py-20 md:py-28 px-6 sm:px-8 lg:px-12 transition-colors duration-500">
          <div class="relative max-w-6xl mx-auto">

            <!-- Hairline divider -->
            <div class="section-divider mb-16 md:mb-20" aria-hidden="true"></div>

            <!-- Section header -->
            <div v-reveal class="text-center mb-14 md:mb-16">
              <p class="inline-flex items-center px-3.5 py-1.5 rounded-full border border-orange-200/70 dark:border-orange-400/25 bg-orange-50/80 dark:bg-orange-400/10 text-xs font-semibold text-orange-700 dark:text-orange-300 uppercase tracking-[0.18em] mb-6 transition-colors duration-300">Who We Serve</p>
              <h2 class="font-display text-4xl sm:text-5xl md:text-[3.4rem] font-semibold text-blue-950 dark:text-white mb-6 tracking-[-0.015em] leading-[1.08] text-balance transition-colors duration-300">
                Built for creators, entrepreneurs, and <em class="section-accent not-italic">innovators</em>
              </h2>
              <p class="text-lg sm:text-xl text-blue-950/65 dark:text-blue-100/65 max-w-3xl mx-auto leading-relaxed text-pretty transition-colors duration-300">
                Whether you're launching a startup, running a small business, or growing a side project, Imagi gives you the tools to build your product and run every part of your business.
              </p>
            </div>

            <!-- User types grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div
                v-for="(userType, index) in userTypes"
                :key="index"
                v-reveal="{ delay: 90 + index * 90 }"
                class="lift-card relative h-full p-8 rounded-2xl bg-white/85 dark:bg-white/[0.045] border backdrop-blur-sm transition-all duration-300"
                :class="index % 2 === 1 ? 'border-orange-200/70 dark:border-orange-300/[0.14]' : 'border-blue-200/70 dark:border-blue-300/[0.14]'"
              >
                <h3 class="relative text-xl font-semibold tracking-tight text-blue-950 dark:text-white transition-colors duration-300 mb-3">
                  {{ userType.title }}
                </h3>
                <p class="relative text-blue-950/65 dark:text-blue-100/65 leading-relaxed text-pretty transition-colors duration-300">
                  {{ userType.description }}
                </p>
              </div>
            </div>
          </div>
        </section>

        <!-- CTA Section -->
        <CTASection
          title="Ready to Start Your Business?"
          description="Build your web app and run your business—marketing, sales, and finance—all in one place. Just bring your idea, and let Imagi do the rest."
          primaryButtonText="Start Building"
          primaryButtonTo="/imagi/projects"
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
import { CTASection } from '@/apps/home/components/organisms/sections'
import reveal from '@/apps/home/directives/reveal'

export default defineComponent({
  name: 'About',
  components: {
    DefaultLayout,
    CTASection
  },
  directives: { reveal },
  setup() {
    const missionCards = [
      {
        title: 'Built for Entrepreneurs',
        description: 'Imagi is designed for creators, entrepreneurs, and business owners who have great ideas but lack a technical team. We provide tools that speak your language, not programmer jargon.'
      },
      {
        title: 'Build and Run in One Place',
        description: 'From building your product to marketing it, closing sales, and managing finances—everything lives in one platform. No more juggling a dozen disconnected tools to run your business.'
      },
      {
        title: 'AI Handles the Complexity',
        description: 'Our AI agents handle the technical details of building your app, and built-in tools take care of the operational heavy lifting. You focus on your vision and your customers; we handle the implementation.'
      }
    ]

    const features = [
      {
        title: 'AI App Builder',
        description: 'Build your web application by chatting with AI agents and using an intuitive visual interface. Describe what you want in plain English, then deploy to the web with a single click—no coding required.'
      },
      {
        title: 'Marketing & Sales',
        description: 'Reach customers and grow revenue with built-in tools for email and social campaigns, landing pages, lead management, and a sales pipeline—so you can turn visitors into paying customers.'
      },
      {
        title: 'Finance & Operations',
        description: 'Run the day-to-day of your business with tools for invoicing, billing, and revenue and expense tracking, plus dashboards that show the health of your business at a glance.'
      }
    ]

    const userTypes = [
      {
        title: 'Startup Founders',
        description: 'Go from idea to a running business without hiring a team. Build your product, launch it, and start finding customers and generating revenue—all before making major investments.'
      },
      {
        title: 'Small Business Owners',
        description: 'Get your business online and manage marketing, sales, and finances in one place. Replace a patchwork of subscriptions with a single platform built to run the whole operation.'
      },
      {
        title: 'Business Teams',
        description: 'Empower your team to launch products and run operations without waiting on engineering. Accelerate growth by removing the bottleneck of developer availability.'
      },
      {
        title: 'Creators & Side Hustlers',
        description: 'Turn a project or passion into a real business. Build the app, market it, take payments, and track the money—without spending months learning to code or run a company.'
      }
    ]

    return {
      missionCards,
      features,
      userTypes
    }
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

/* Staggered entrance: each .hero-item rises in sequence on page load */
.hero-item {
  animation: hero-rise 0.9s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes hero-rise {
  from {
    opacity: 0;
    transform: translateY(22px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero-item {
    animation: none;
  }
}

/* Atmosphere washes */
.wash-warm {
  background: radial-gradient(closest-side, rgba(251, 146, 60, 0.13), rgba(251, 146, 60, 0.04) 55%, transparent 75%);
  filter: blur(44px);
}

.wash-cool {
  background: radial-gradient(closest-side, rgba(158, 205, 243, 0.22), rgba(158, 205, 243, 0.07) 55%, transparent 75%);
  filter: blur(48px);
}

.dark .wash-warm {
  background: radial-gradient(closest-side, rgba(251, 146, 60, 0.07), rgba(251, 146, 60, 0.02) 55%, transparent 75%);
}

.dark .wash-cool {
  background: radial-gradient(closest-side, rgba(96, 165, 250, 0.09), rgba(96, 165, 250, 0.025) 55%, transparent 75%);
}

/* Italic serif accent with the hero's warm gradient ink */
.hero-accent {
  font-style: italic;
  font-variation-settings: 'SOFT' 30, 'WONK' 1;
  background: linear-gradient(115deg, #c2410c 5%, #ea580c 55%, #b45309 95%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  padding-right: 0.06em; /* keep the italic terminal from clipping */
}

.dark .hero-accent {
  background: linear-gradient(115deg, #fb923c 5%, #fcd34d 60%, #f59e0b 95%);
  -webkit-background-clip: text;
  background-clip: text;
}

/* Italic serif accent in blue ink for section headlines */
.section-accent {
  font-style: italic;
  font-variation-settings: 'SOFT' 30, 'WONK' 1;
  background: linear-gradient(115deg, #1d4ed8 5%, #2563eb 55%, #0284c7 95%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  padding-right: 0.05em;
}

.dark .section-accent {
  background: linear-gradient(115deg, #93c5fd 5%, #60a5fa 60%, #7dd3fc 95%);
  -webkit-background-clip: text;
  background-clip: text;
}

/* Hairline gradient divider that fades at the edges */
.section-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(23, 37, 84, 0.12), transparent);
}

.dark .section-divider {
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
}

/* Cards that lift gently on hover: hairline edge + tight layered shadow */
.lift-card {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}

.lift-card:hover {
  transform: translateY(-4px);
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.04),
    0 2px 4px rgba(15, 23, 42, 0.06),
    0 10px 20px -4px rgba(15, 23, 42, 0.1),
    0 24px 44px -12px rgba(15, 23, 42, 0.14);
}

.dark .lift-card {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 12px 28px -10px rgba(0, 0, 0, 0.55);
}

.dark .lift-card:hover {
  transform: translateY(-4px);
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.06),
    0 2px 4px rgba(0, 0, 0, 0.5),
    0 12px 24px -4px rgba(0, 0, 0, 0.5),
    0 28px 48px -12px rgba(0, 0, 0, 0.6);
}

@media (prefers-reduced-motion: reduce) {
  .lift-card:hover,
  .dark .lift-card:hover {
    transform: none;
  }
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

<!-- Unscoped: reveal + selection styles (mirrors Home.vue so the page works standalone) -->
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

/* Brand-tinted text selection */
.home-page ::selection {
  background: rgba(158, 205, 243, 0.55);
  color: #172554;
}

.dark .home-page ::selection {
  background: rgba(96, 165, 250, 0.4);
  color: #eff6ff;
}
</style>
