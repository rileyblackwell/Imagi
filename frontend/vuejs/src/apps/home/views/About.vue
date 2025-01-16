<!-- About page -->
<template>
  <div>
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
  </div>
</template>

<script>
import { HeroSection, FeaturesGrid, FeatureCard } from '../components'

export default {
  name: 'About',
  components: {
    HeroSection,
    FeaturesGrid,
    FeatureCard
  }
}
</script> 