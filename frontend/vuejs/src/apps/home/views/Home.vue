<!-- Home page -->
<template>
  <DefaultLayout>
    <div class="space-y-24 py-12">
      <!-- Hero Section -->
      <hero-section
        title="Transform Your Ideas Into"
        gradient-title="Web Applications"
        description="Create powerful, professional web applications using natural language with Imagi's AI technology"
      >
        <template #cta>
          <router-link
            to="/auth/register"
            class="inline-flex items-center justify-center px-8 py-3 text-base font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 transition-all transform hover:-translate-y-0.5"
          >
            <span>Start Building</span>
            <i class="fas fa-arrow-right ml-2"></i>
          </router-link>
        </template>
      </hero-section>

      <!-- Why Choose Imagi Section -->
      <features-grid
        title="Why Choose Imagi"
        description="Transform your ideas into reality with powerful AI-driven web development"
      >
        <feature-card
          icon="fas fa-keyboard"
          title="Natural Language Input"
          description="Describe your vision in plain English, and watch as it transforms into reality."
        />
        <feature-card
          icon="fas fa-bolt"
          title="Rapid Development"
          description="Build websites and applications in minutes, not months."
        />
        <feature-card
          icon="fas fa-code"
          title="Professional Code"
          description="Generate clean, maintainable code that follows industry best practices."
        />
      </features-grid>

      <!-- How It Works Section -->
      <features-grid
        title="How It Works"
        :columns="4"
      >
        <feature-card
          icon="fas fa-pencil-alt"
          title="1. Describe Your Vision"
          description="Tell us what you want to build using natural language. Describe your features, design preferences, and requirements."
        />
        <feature-card
          icon="fas fa-magic"
          title="2. AI Generation"
          description="Our advanced AI analyzes your description and generates all necessary code, from frontend interfaces to backend logic."
        />
        <feature-card
          icon="fas fa-sliders-h"
          title="3. Customize & Refine"
          description="Review the generated application, make adjustments, and refine details using natural language commands."
        />
        <feature-card
          icon="fas fa-rocket"
          title="4. Launch & Scale"
          description="Deploy your application with confidence, knowing it's built with scalable, secure, and maintainable code."
        />
      </features-grid>

      <!-- What You Can Build Section -->
      <features-grid
        title="What You Can Build"
        :columns="2"
      >
        <feature-card
          icon="fas fa-store"
          title="E-commerce Sites"
          description="Create full-featured online stores with product catalogs, shopping carts, and secure payment processing."
        />
        <feature-card
          icon="fas fa-briefcase"
          title="Business Applications"
          description="Build custom CRM systems, inventory management tools, and other business-specific applications."
        />
        <feature-card
          icon="fas fa-users"
          title="Community Platforms"
          description="Develop social networks, forums, and community-driven websites with user management and content sharing."
        />
        <feature-card
          icon="fas fa-chart-line"
          title="Analytics Dashboards"
          description="Create data visualization tools and interactive dashboards for business intelligence and reporting."
        />
      </features-grid>
    </div>
  </DefaultLayout>
</template>

<script>
import { DefaultLayout } from '@/shared/layouts'
import { HeroSection, FeaturesGrid, FeatureCard } from '../components'

export default {
  name: 'Home',
  components: {
    DefaultLayout,
    HeroSection,
    FeaturesGrid,
    FeatureCard
  }
}
</script> 