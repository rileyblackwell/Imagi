<!-- About Page - Clean Apple/Cursor-inspired design matching Home -->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="min-h-screen bg-white dark:bg-[#0a0a0a] relative overflow-hidden transition-colors duration-500">
      <!-- Minimal background -->
      <div class="fixed inset-0 pointer-events-none">
        <!-- Subtle gradient -->
        <div class="absolute inset-0 bg-gradient-to-b from-gray-50/50 via-white to-white dark:from-[#0a0a0a] dark:via-[#0a0a0a] dark:to-[#0a0a0a] transition-colors duration-500"></div>
        
        <!-- Very subtle grid pattern -->
        <div class="absolute inset-0 opacity-[0.015] dark:opacity-[0.02]" 
             style="background-image: linear-gradient(rgba(128,128,128,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(128,128,128,0.1) 1px, transparent 1px); background-size: 64px 64px;"></div>
      </div>

      <!-- Main Content -->
      <main class="relative z-10">
        <!-- Hero Section -->
        <section class="relative py-32 sm:py-40 md:py-48 px-6 sm:px-8 lg:px-12 bg-white dark:bg-[#0a0a0a] transition-colors duration-500 overflow-hidden">
          <div class="relative max-w-4xl mx-auto text-center">
            
            <!-- Hero title -->
            <h1 class="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight leading-[1.1] transition-colors duration-300">
              Web development for everyone
            </h1>
            
            <!-- Description -->
            <p class="text-lg sm:text-xl text-gray-600 dark:text-white/70 max-w-3xl mx-auto leading-relaxed transition-colors duration-300">
              Imagi provides a set of AI tools to non-technical users, creating a quick and easy experience to build and deploy web applications. We handle all the technical complexity behind the scenes, so you can focus on bringing your ideas to life through a clean visual interface.
            </p>
          </div>
        </section>

        <!-- Mission Section -->
        <section class="relative py-24 md:py-32 px-6 sm:px-8 lg:px-12 bg-gray-100 dark:bg-[#0d0d0d] transition-colors duration-500 overflow-hidden">
          <!-- Subtle ambient background -->
          <div class="absolute inset-0 pointer-events-none">
            <div class="absolute top-1/2 left-1/2 w-[800px] h-[400px] bg-gradient-radial from-gray-200/30 dark:from-white/[0.02] via-transparent to-transparent rounded-full blur-3xl transform -translate-x-1/2 -translate-y-1/2"></div>
          </div>

          <div class="relative max-w-6xl mx-auto">
            <!-- Section header -->
            <div class="text-center mb-16 md:mb-20">
              <p class="text-sm font-medium text-gray-500 dark:text-white/50 uppercase tracking-widest mb-4 transition-colors duration-300">Our Mission</p>
              <h2 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight transition-colors duration-300">
                Removing barriers between ideas and reality
              </h2>
              <p class="text-xl text-gray-500 dark:text-white/60 max-w-3xl mx-auto transition-colors duration-300">
                Our mission is to democratize web development by providing powerful AI tools that handle all the technical complexity, empowering anyone to create professional web applications without needing to write a single line of code.
              </p>
            </div>
                
            <!-- Mission cards -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div v-for="(card, index) in missionCards" :key="index" class="relative">
                <div class="relative h-full p-8 rounded-2xl bg-white dark:bg-white border border-gray-200 dark:border-gray-300 transition-colors duration-300 shadow-md">
                  <!-- Content -->
                  <h3 class="text-xl font-semibold text-gray-900 dark:text-black transition-colors duration-300 mb-5">
                    {{ card.title }}
                  </h3>
                  <p class="text-gray-600 dark:text-black leading-relaxed transition-colors duration-300">
                    {{ card.description }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- What We Do Section -->
        <section class="relative py-24 md:py-32 px-6 sm:px-8 lg:px-12 bg-white dark:bg-[#0a0a0a] transition-colors duration-500 overflow-hidden">
          <!-- Subtle ambient background -->
          <div class="absolute inset-0 pointer-events-none">
            <div class="absolute top-1/2 left-1/2 w-[800px] h-[400px] bg-gradient-radial from-gray-200/30 dark:from-white/[0.02] via-transparent to-transparent rounded-full blur-3xl transform -translate-x-1/2 -translate-y-1/2"></div>
          </div>

          <div class="relative max-w-6xl mx-auto">
            <!-- Section header -->
            <div class="text-center mb-16 md:mb-20">
              <p class="text-sm font-medium text-gray-500 dark:text-white/50 uppercase tracking-widest mb-4 transition-colors duration-300">What We Do</p>
              <h2 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight transition-colors duration-300">
                A complete AI-powered development platform
              </h2>
              <p class="text-xl text-gray-500 dark:text-white/60 max-w-3xl mx-auto transition-colors duration-300">
                Imagi combines intelligent AI agents with intuitive visual tools to give you everything you need to design, build, and deploy web applications—all without touching code.
              </p>
            </div>
                      
            <!-- Features grid -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div v-for="(feature, index) in features" :key="index" class="relative">
                <div class="relative h-full p-8 rounded-2xl bg-white dark:bg-white border border-gray-200 dark:border-gray-300 transition-colors duration-300 shadow-md">
                  <!-- Content -->
                  <h3 class="text-xl font-semibold text-gray-900 dark:text-black transition-colors duration-300 mb-5 text-center">
                    {{ feature.title }}
                  </h3>
                  <p class="text-gray-600 dark:text-black leading-relaxed transition-colors duration-300 text-center">
                    {{ feature.description }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Who We Serve Section -->
        <section class="relative py-24 md:py-32 px-6 sm:px-8 lg:px-12 bg-gray-100 dark:bg-[#0d0d0d] transition-colors duration-500 overflow-hidden">
          <!-- Subtle ambient background -->
          <div class="absolute inset-0 pointer-events-none">
            <div class="absolute top-1/2 left-1/2 w-[800px] h-[400px] bg-gradient-radial from-gray-200/30 dark:from-white/[0.02] via-transparent to-transparent rounded-full blur-3xl transform -translate-x-1/2 -translate-y-1/2"></div>
          </div>

          <div class="relative max-w-6xl mx-auto">
            <!-- Section header -->
            <div class="text-center mb-16 md:mb-20">
              <p class="text-sm font-medium text-gray-500 dark:text-white/50 uppercase tracking-widest mb-4 transition-colors duration-300">Who We Serve</p>
              <h2 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight transition-colors duration-300">
                Built for creators, entrepreneurs, and innovators
              </h2>
              <p class="text-xl text-gray-500 dark:text-white/60 max-w-3xl mx-auto transition-colors duration-300">
                Whether you're validating a startup idea, prototyping for your company, or building a personal project, Imagi gives you the tools to turn your vision into reality.
              </p>
            </div>
                      
            <!-- User types grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div v-for="(userType, index) in userTypes" :key="index" class="relative">
                <div class="relative h-full p-8 rounded-2xl bg-white dark:bg-white border border-gray-200 dark:border-gray-300 transition-colors duration-300 shadow-md">
                  <!-- Content -->
                  <h3 class="text-xl font-semibold text-gray-900 dark:text-black transition-colors duration-300 mb-5">
                    {{ userType.title }}
                  </h3>
                  <p class="text-gray-600 dark:text-black leading-relaxed transition-colors duration-300">
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
