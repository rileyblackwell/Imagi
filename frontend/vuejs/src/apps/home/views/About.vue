<!-- About Page - Clean Apple/Cursor-inspired design matching Home -->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="home-page min-h-screen bg-white dark:bg-[#0a0a0a] relative overflow-hidden transition-colors duration-500">

      <!-- Main Content -->
      <main class="relative z-10">
        <!-- Hero Section -->
        <section class="relative py-32 sm:py-40 md:py-48 px-6 sm:px-8 lg:px-12 bg-orange-50 dark:bg-[#16120e] transition-colors duration-500 overflow-hidden">
          <div class="relative max-w-4xl mx-auto text-center">

            <!-- Hero title -->
            <h1 class="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-semibold text-blue-950 dark:text-white mb-6 tracking-[-0.025em] leading-[1.08] text-balance transition-colors duration-300">
              Build and run a business
            </h1>

            <!-- Description -->
            <p class="text-lg sm:text-xl text-blue-950/70 dark:text-blue-100/70 max-w-3xl mx-auto leading-relaxed text-pretty transition-colors duration-300">
              Imagi is an all-in-one platform for building and running a business. Create your web application with AI-powered tools, then run and grow it with everything you need for marketing, sales, and finance. We handle the technical complexity, so you can focus on your customers.
            </p>
          </div>
        </section>

        <!-- Mission Section -->
        <section class="relative py-24 md:py-32 px-6 sm:px-8 lg:px-12 bg-blue-50 dark:bg-[#0e141f] border-t border-blue-200/60 dark:border-blue-400/[0.14] transition-colors duration-500 overflow-hidden">
          <div class="relative max-w-6xl mx-auto">
            <!-- Section header -->
            <div class="text-center mb-16 md:mb-20">
              <p class="inline-flex items-center px-3.5 py-1.5 rounded-full border border-orange-200/70 dark:border-orange-400/25 bg-orange-50/80 dark:bg-orange-400/10 text-xs font-semibold text-orange-700 dark:text-orange-300 uppercase tracking-[0.18em] mb-5 transition-colors duration-300">Our Mission</p>
              <h2 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-blue-950 dark:text-white mb-6 tracking-tight text-balance transition-colors duration-300">
                Making entrepreneurship accessible to everyone
              </h2>
              <p class="text-xl text-blue-950/70 dark:text-blue-100/70 max-w-3xl mx-auto leading-relaxed text-pretty transition-colors duration-300">
                Our mission is to make starting and running a business accessible to everyone. We give you AI-powered tools to build your product and the marketing, sales, and finance tools to run it—so you can go from idea to thriving business without a technical team.
              </p>
            </div>

            <!-- Mission cards -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div v-for="(card, index) in missionCards" :key="index" class="relative">
                <div
                  class="relative h-full p-8 rounded-2xl border crisp-card transition-colors duration-300"
                  :class="index % 2 === 1 ? 'bg-white dark:bg-white/[0.05] border-orange-200/70 dark:border-orange-300/[0.16]' : 'bg-white dark:bg-white/[0.05] border-blue-200/70 dark:border-blue-300/[0.16]'"
                >
                  <!-- Content -->
                  <h3 class="text-xl font-semibold tracking-tight text-blue-950 dark:text-white transition-colors duration-300 mb-5">
                    {{ card.title }}
                  </h3>
                  <p class="text-blue-950/70 dark:text-blue-100/70 leading-relaxed text-pretty transition-colors duration-300">
                    {{ card.description }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- What We Do Section -->
        <section class="relative py-24 md:py-32 px-6 sm:px-8 lg:px-12 bg-orange-50 dark:bg-[#16120e] border-t border-orange-200/60 dark:border-orange-400/[0.14] transition-colors duration-500 overflow-hidden">
          <div class="relative max-w-6xl mx-auto">
            <!-- Section header -->
            <div class="text-center mb-16 md:mb-20">
              <p class="inline-flex items-center px-3.5 py-1.5 rounded-full border border-blue-200/70 dark:border-blue-400/25 bg-blue-50/80 dark:bg-blue-400/10 text-xs font-semibold text-blue-700 dark:text-blue-300 uppercase tracking-[0.18em] mb-5 transition-colors duration-300">What We Do</p>
              <h2 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-blue-950 dark:text-white mb-6 tracking-tight text-balance transition-colors duration-300">
                One platform to build and run it all
              </h2>
              <p class="text-xl text-blue-950/70 dark:text-blue-100/70 max-w-3xl mx-auto leading-relaxed text-pretty transition-colors duration-300">
                Imagi combines AI-powered app building with the everyday tools you need to operate—marketing, sales, and finance—so you can launch your product and run your business without stitching together a dozen services.
              </p>
            </div>

            <!-- Features grid -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div v-for="(feature, index) in features" :key="index" class="relative">
                <div
                  class="relative h-full p-8 rounded-2xl border crisp-card transition-colors duration-300"
                  :class="index % 2 === 1 ? 'bg-white dark:bg-white/[0.05] border-orange-200/70 dark:border-orange-300/[0.16]' : 'bg-white dark:bg-white/[0.05] border-blue-200/70 dark:border-blue-300/[0.16]'"
                >
                  <!-- Content -->
                  <h3 class="text-xl font-semibold tracking-tight text-blue-950 dark:text-white transition-colors duration-300 mb-5 text-center">
                    {{ feature.title }}
                  </h3>
                  <p class="text-blue-950/70 dark:text-blue-100/70 leading-relaxed text-pretty transition-colors duration-300 text-center">
                    {{ feature.description }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Who We Serve Section -->
        <section class="relative py-24 md:py-32 px-6 sm:px-8 lg:px-12 bg-blue-50 dark:bg-[#0e141f] border-t border-blue-200/60 dark:border-blue-400/[0.14] transition-colors duration-500 overflow-hidden">
          <div class="relative max-w-6xl mx-auto">
            <!-- Section header -->
            <div class="text-center mb-16 md:mb-20">
              <p class="inline-flex items-center px-3.5 py-1.5 rounded-full border border-orange-200/70 dark:border-orange-400/25 bg-orange-50/80 dark:bg-orange-400/10 text-xs font-semibold text-orange-700 dark:text-orange-300 uppercase tracking-[0.18em] mb-5 transition-colors duration-300">Who We Serve</p>
              <h2 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-blue-950 dark:text-white mb-6 tracking-tight text-balance transition-colors duration-300">
                Built for creators, entrepreneurs, and innovators
              </h2>
              <p class="text-xl text-blue-950/70 dark:text-blue-100/70 max-w-3xl mx-auto leading-relaxed text-pretty transition-colors duration-300">
                Whether you're launching a startup, running a small business, or growing a side project, Imagi gives you the tools to build your product and run every part of your business.
              </p>
            </div>

            <!-- User types grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div v-for="(userType, index) in userTypes" :key="index" class="relative">
                <div
                  class="relative h-full p-8 rounded-2xl border crisp-card transition-colors duration-300"
                  :class="index % 2 === 1 ? 'bg-white dark:bg-white/[0.05] border-orange-200/70 dark:border-orange-300/[0.16]' : 'bg-white dark:bg-white/[0.05] border-blue-200/70 dark:border-blue-300/[0.16]'"
                >
                  <!-- Content -->
                  <h3 class="text-xl font-semibold tracking-tight text-blue-950 dark:text-white transition-colors duration-300 mb-5">
                    {{ userType.title }}
                  </h3>
                  <p class="text-blue-950/70 dark:text-blue-100/70 leading-relaxed text-pretty transition-colors duration-300">
                    {{ userType.description }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- CTA Section -->
        <CTASection 
          icon="fas fa-rocket"
          title="Ready to Start Your Business?"
          highlightedText="No Coding Required!"
          description="Build your web app and run your business—marketing, sales, and finance—all in one place. Just bring your idea, and let Imagi do the rest."
          highlightedStat=""
          descriptionSuffix=""
          primaryButtonText="Start Building"
          primaryButtonTo="/products/imagi/projects"
          :showSecondaryButton="true"
          secondaryButtonText="Learn More"
          secondaryButtonTo="/docs"
          secondaryButtonIcon="fas fa-book"
        />
      </main>
    </div>
  </DefaultLayout>
</template>

<script>
import { defineComponent } from 'vue'
import { DefaultLayout } from '@/shared/layouts'
import { CTASection } from '@/apps/home/components/organisms/sections'

export default defineComponent({
  name: 'About',
  components: {
    DefaultLayout,
    CTASection
  },
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
/* Crisp, sharp text rendering across the page */
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

/* Crisp, sharply-defined cards: hairline edge + tight layered shadow */
.crisp-card {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}

.dark .crisp-card {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 12px 28px -10px rgba(0, 0, 0, 0.55);
}

/* Minimal scrollbar matching Home page */
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
