<!-- About Page - Clean Apple/Cursor-inspired design matching Home -->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="home-page min-h-screen bg-white dark:bg-[#0a0a0a] relative overflow-hidden transition-colors duration-500">

      <!-- Main Content -->
      <main class="relative z-10">
        <!-- Hero Section -->
        <section class="relative py-32 sm:py-40 md:py-48 px-6 sm:px-8 lg:px-12 bg-orange-50 dark:bg-orange-600 transition-colors duration-500 overflow-hidden">
          <div class="relative max-w-4xl mx-auto text-center">

            <!-- Hero title -->
            <h1 class="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-semibold text-blue-950 dark:text-white mb-6 tracking-[-0.025em] leading-[1.08] text-balance transition-colors duration-300">
              Web development for everyone
            </h1>

            <!-- Description -->
            <p class="text-lg sm:text-xl text-blue-950/70 dark:text-blue-100/70 max-w-3xl mx-auto leading-relaxed text-pretty transition-colors duration-300">
              Imagi provides a set of AI tools to non-technical users, creating a quick and easy experience to build and deploy web applications. We handle all the technical complexity behind the scenes, so you can focus on bringing your ideas to life through a clean visual interface.
            </p>
          </div>
        </section>

        <!-- Mission Section -->
        <section class="relative py-24 md:py-32 px-6 sm:px-8 lg:px-12 bg-blue-50 dark:bg-blue-400/[0.16] border-t border-blue-200/60 dark:border-blue-500/[0.12] transition-colors duration-500 overflow-hidden">
          <div class="relative max-w-6xl mx-auto">
            <!-- Section header -->
            <div class="text-center mb-16 md:mb-20">
              <p class="inline-flex items-center px-3.5 py-1.5 rounded-full border border-orange-200/70 dark:border-orange-400/30 bg-orange-50/80 dark:bg-orange-600 text-xs font-semibold text-orange-700 dark:text-white uppercase tracking-[0.18em] mb-5 transition-colors duration-300">Our Mission</p>
              <h2 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-blue-950 dark:text-white mb-6 tracking-tight text-balance transition-colors duration-300">
                Removing barriers between ideas and reality
              </h2>
              <p class="text-xl text-blue-950/70 dark:text-blue-100/70 max-w-3xl mx-auto leading-relaxed text-pretty transition-colors duration-300">
                Our mission is to democratize web development by providing powerful AI tools that handle all the technical complexity, empowering anyone to create professional web applications without needing to write a single line of code.
              </p>
            </div>

            <!-- Mission cards -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div v-for="(card, index) in missionCards" :key="index" class="relative">
                <div
                  class="relative h-full p-8 rounded-2xl border crisp-card transition-colors duration-300"
                  :class="index % 2 === 1 ? 'bg-white border-orange-200/70' : 'bg-white border-blue-200/70'"
                >
                  <!-- Content -->
                  <h3 class="text-xl font-semibold tracking-tight text-blue-950 transition-colors duration-300 mb-5">
                    {{ card.title }}
                  </h3>
                  <p class="text-blue-950/70 leading-relaxed text-pretty transition-colors duration-300">
                    {{ card.description }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- What We Do Section -->
        <section class="relative py-24 md:py-32 px-6 sm:px-8 lg:px-12 bg-orange-50 dark:bg-orange-600 border-t border-orange-200/60 dark:border-orange-500/[0.12] transition-colors duration-500 overflow-hidden">
          <div class="relative max-w-6xl mx-auto">
            <!-- Section header -->
            <div class="text-center mb-16 md:mb-20">
              <p class="inline-flex items-center px-3.5 py-1.5 rounded-full border border-blue-200/70 dark:border-blue-400/30 bg-blue-50/80 dark:bg-blue-600 text-xs font-semibold text-blue-700 dark:text-white uppercase tracking-[0.18em] mb-5 transition-colors duration-300">What We Do</p>
              <h2 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-blue-950 dark:text-white mb-6 tracking-tight text-balance transition-colors duration-300">
                A complete AI-powered development platform
              </h2>
              <p class="text-xl text-blue-950/70 dark:text-blue-100/70 max-w-3xl mx-auto leading-relaxed text-pretty transition-colors duration-300">
                Imagi combines intelligent AI agents with intuitive visual tools to give you everything you need to design, build, and deploy web applications—all without touching code.
              </p>
            </div>

            <!-- Features grid -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div v-for="(feature, index) in features" :key="index" class="relative">
                <div
                  class="relative h-full p-8 rounded-2xl border crisp-card transition-colors duration-300"
                  :class="index % 2 === 1 ? 'bg-white border-orange-200/70' : 'bg-white border-blue-200/70'"
                >
                  <!-- Content -->
                  <h3 class="text-xl font-semibold tracking-tight text-blue-950 transition-colors duration-300 mb-5 text-center">
                    {{ feature.title }}
                  </h3>
                  <p class="text-blue-950/70 leading-relaxed text-pretty transition-colors duration-300 text-center">
                    {{ feature.description }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Who We Serve Section -->
        <section class="relative py-24 md:py-32 px-6 sm:px-8 lg:px-12 bg-blue-50 dark:bg-blue-400/[0.16] border-t border-blue-200/60 dark:border-blue-500/[0.12] transition-colors duration-500 overflow-hidden">
          <div class="relative max-w-6xl mx-auto">
            <!-- Section header -->
            <div class="text-center mb-16 md:mb-20">
              <p class="inline-flex items-center px-3.5 py-1.5 rounded-full border border-orange-200/70 dark:border-orange-400/30 bg-orange-50/80 dark:bg-orange-600 text-xs font-semibold text-orange-700 dark:text-white uppercase tracking-[0.18em] mb-5 transition-colors duration-300">Who We Serve</p>
              <h2 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-blue-950 dark:text-white mb-6 tracking-tight text-balance transition-colors duration-300">
                Built for creators, entrepreneurs, and innovators
              </h2>
              <p class="text-xl text-blue-950/70 dark:text-blue-100/70 max-w-3xl mx-auto leading-relaxed text-pretty transition-colors duration-300">
                Whether you're validating a startup idea, prototyping for your company, or building a personal project, Imagi gives you the tools to turn your vision into reality.
              </p>
            </div>

            <!-- User types grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div v-for="(userType, index) in userTypes" :key="index" class="relative">
                <div
                  class="relative h-full p-8 rounded-2xl border crisp-card transition-colors duration-300"
                  :class="index % 2 === 1 ? 'bg-white border-orange-200/70' : 'bg-white border-blue-200/70'"
                >
                  <!-- Content -->
                  <h3 class="text-xl font-semibold tracking-tight text-blue-950 transition-colors duration-300 mb-5">
                    {{ userType.title }}
                  </h3>
                  <p class="text-blue-950/70 leading-relaxed text-pretty transition-colors duration-300">
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
          title="Ready to Build Your App?"
          highlightedText="No Coding Required!"
          description="Start building your own web application today. Just describe your idea, and let Imagi do the rest."
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
        title: 'Built for Non-Technical Users',
        description: 'Imagi is designed specifically for creators, entrepreneurs, and business owners who have great ideas but lack coding skills. We provide tools that speak your language, not programmer jargon.'
      },
      {
        title: 'AI Handles the Complexity',
        description: 'Our advanced AI agents understand what you want to build and handle all the technical details—from database design to API creation to frontend interfaces. You focus on your vision, we handle the implementation.'
      },
      {
        title: 'Quick and Easy Experience',
        description: 'Build and deploy complete web applications in minutes, not months. Our streamlined workflow removes the traditional barriers of hiring developers, managing infrastructure, and learning complex frameworks.'
      }
    ]
    
    const features = [
      {
        title: 'Visual Builder Interface',
        description: 'Design your application using our clean, intuitive visual interface. Build pages, components, and layouts by simply describing what you want or using drag-and-drop tools—no coding required.'
      },
      {
        title: 'AI Agents',
        description: 'Chat with intelligent AI agents that understand your requirements and build your application collaboratively. Describe what you want in plain English, iterate on features through conversation, and watch as the AI generates complete, production-ready code for you.'
      },
      {
        title: 'Deployment',
        description: 'Deploy your application to the web with a single click. We handle all the complexity—hosting, SSL certificates, domains, and infrastructure management—so you can focus on your users, not server configuration.'
      }
    ]
    
    const userTypes = [
      {
        title: 'Startup Founders',
        description: 'Validate your product ideas quickly without hiring a development team. Build working prototypes, test them with real users, and iterate based on feedback—all before making major technical investments.'
      },
      {
        title: 'Business Teams',
        description: 'Empower non-technical employees to prototype internal tools and customer-facing applications. Accelerate innovation within your organization by removing the bottleneck of developer availability.'
      },
      {
        title: 'Technical Professionals',
        description: 'Speed up your development workflow with AI-powered tools that handle boilerplate code and infrastructure. Focus on the unique aspects of your project while Imagi manages the repetitive tasks.'
      },
      {
        title: 'Hobbyists & Creators',
        description: 'Bring your personal projects to life without spending months learning to code. Whether it\'s a portfolio site, a tool for your community, or a creative experiment, Imagi makes it accessible.'
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
