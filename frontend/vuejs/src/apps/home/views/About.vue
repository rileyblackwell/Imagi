<!-- About page -->
<template>
  <base-layout>
    <!-- Hero Section -->
    <hero-section
      title="About Imagi"
      description="Transforming natural language into powerful web applications"
    />

    <!-- Mission Section -->
    <features-grid
      title="Our Mission"
      :columns="2"
    >
      <feature-card
        icon="fas fa-bullseye"
        title="Democratizing Web Development"
        description="Our mission is to make web development accessible to everyone by transforming natural language into professional code."
      />
      <feature-card
        icon="fas fa-star"
        title="AI-Powered Innovation"
        description="By combining cutting-edge AI with intuitive design, we're revolutionizing how websites and applications are built."
      />
    </features-grid>

    <!-- Story Section -->
    <section class="py-24 bg-dark-800">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 class="text-3xl font-bold text-white text-center">Our Story</h2>
        <div class="mt-12 max-w-3xl mx-auto bg-dark-900/50 rounded-2xl p-8 border border-dark-700">
          <p class="text-gray-300 mb-6">Founded in 2024, Imagi was born from a simple observation: while the world is full of innovative ideas, many remain unrealized due to the technical complexity of web development.</p>
          <p class="text-gray-300">This insight led to the creation of Imagi's natural language processing platform, which transforms plain English descriptions into functional code.</p>
        </div>
      </div>
    </section>

    <!-- Technology Section -->
    <features-grid
      title="Our Technology"
      :columns="2"
    >
      <feature-card
        icon="fas fa-robot"
        title="AI Understanding"
        description="Advanced natural language processing to understand context, requirements, and user intent."
      />
      <feature-card
        icon="fas fa-code-branch"
        title="Clean Code"
        description="Generate maintainable code following industry best practices."
      />
    </features-grid>

    <!-- Vision Section -->
    <features-grid
      title="Our Vision"
      :columns="2"
    >
      <feature-card
        icon="fas fa-rocket"
        title="Future of Development"
        description="We envision a future where creating web applications is as simple as describing your idea."
      />
      <feature-card
        icon="fas fa-users"
        title="Community Impact"
        description="Empowering entrepreneurs, businesses, and creators to bring their digital ideas to life."
      />
    </features-grid>
  </base-layout>
</template>

<script>
import BaseLayout from '@/shared/layouts/BaseLayout.vue'
import { HeroSection, FeaturesGrid, FeatureCard } from '../components'

export default {
  name: 'About',
  components: {
    BaseLayout,
    HeroSection,
    FeaturesGrid,
    FeatureCard
  }
}
</script> 