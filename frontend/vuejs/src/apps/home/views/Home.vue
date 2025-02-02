<!-- Home page -->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="space-y-24 py-12">
      <!-- Hero Section -->
      <HeroSection
        title="Transform Your Ideas Into"
        gradient-title="Web Applications"
        description="Create powerful, professional web applications using natural language with Imagi's AI technology"
      >
        <template #cta>
          <IconButton
            :to="isAuthenticated ? '/builder' : '/auth/login'"
            variant="primary"
            size="lg"
            icon-right="fas fa-arrow-right"
          >
            Start Building
          </IconButton>
        </template>
      </HeroSection>

      <!-- Why Choose Imagi Section -->
      <FeaturesSection
        title="Why Choose Imagi"
        description="Transform your ideas into reality with powerful AI-driven web development"
        :features="whyChooseFeatures"
        :columns="3"
      />

      <!-- How It Works Section -->
      <FeaturesSection
        title="How It Works"
        :features="howItWorksFeatures"
        :columns="4"
      />

      <!-- What You Can Build Section -->
      <FeaturesSection
        title="What You Can Build"
        :features="whatYouCanBuildFeatures"
        :columns="2"
      />
    </div>
  </DefaultLayout>
</template>

<script>
import { computed } from 'vue'
import { DefaultLayout } from '@/shared/layouts'
import { HeroSection, FeaturesSection, IconButton } from '../components'
import { useAuthStore } from '@/apps/auth/store'

export default {
  name: 'Home',
  components: {
    DefaultLayout,
    HeroSection,
    FeaturesSection,
    IconButton
  },
  setup() {
    const authStore = useAuthStore()

    const whyChooseFeatures = [
      {
        icon: 'fas fa-keyboard',
        title: 'Natural Language Input',
        description: 'Describe your vision in plain English, and watch as it transforms into reality.'
      },
      {
        icon: 'fas fa-bolt',
        title: 'Rapid Development',
        description: 'Build websites and applications in minutes, not months.'
      },
      {
        icon: 'fas fa-code',
        title: 'Professional Code',
        description: 'Generate clean, maintainable code that follows industry best practices.'
      }
    ]

    const howItWorksFeatures = [
      {
        icon: 'fas fa-pencil-alt',
        title: '1. Describe Your Vision',
        description: 'Tell us what you want to build using natural language. Describe your features, design preferences, and requirements.'
      },
      {
        icon: 'fas fa-magic',
        title: '2. AI Generation',
        description: 'Our advanced AI analyzes your description and generates all necessary code, from frontend interfaces to backend logic.'
      },
      {
        icon: 'fas fa-sliders-h',
        title: '3. Customize & Refine',
        description: 'Review the generated application, make adjustments, and refine details using natural language commands.'
      },
      {
        icon: 'fas fa-rocket',
        title: '4. Launch & Scale',
        description: 'Deploy your application with confidence, knowing it\'s built with scalable, secure, and maintainable code.'
      }
    ]

    const whatYouCanBuildFeatures = [
      {
        icon: 'fas fa-store',
        title: 'E-commerce Sites',
        description: 'Create full-featured online stores with product catalogs, shopping carts, and secure payment processing.'
      },
      {
        icon: 'fas fa-briefcase',
        title: 'Business Applications',
        description: 'Build custom CRM systems, inventory management tools, and other business-specific applications.'
      },
      {
        icon: 'fas fa-users',
        title: 'Community Platforms',
        description: 'Develop social networks, forums, and community-driven websites with user management and content sharing.'
      },
      {
        icon: 'fas fa-chart-line',
        title: 'Analytics Dashboards',
        description: 'Create data visualization tools and interactive dashboards for business intelligence and reporting.'
      }
    ]

    return {
      isAuthenticated: computed(() => authStore.isAuthenticated),
      whyChooseFeatures,
      howItWorksFeatures,
      whatYouCanBuildFeatures
    }
  }
}
</script> 