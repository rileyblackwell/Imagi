<!-- Contact page -->
<template>
  <div>
    <!-- Hero Section -->
    <hero-section
      title="Contact Us"
      description="Get in touch with our team"
    />

    <!-- Contact Methods -->
    <features-grid
      title="Contact Methods"
      :columns="2"
    >
      <feature-card
        icon="fas fa-envelope"
        title="Email Support"
        description="Send us an email and we'll get back to you within 24 hours."
      />
      <feature-card
        icon="fas fa-phone"
        title="Phone Support"
        description="For urgent matters, call us during business hours."
      />
    </features-grid>

    <!-- Contact Form Section -->
    <section class="py-24">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 class="text-3xl font-bold text-white text-center mb-16">Send Us a Message</h2>
        <div class="max-w-2xl mx-auto">
          <contact-form />
        </div>
      </div>
    </section>

    <!-- Response Time -->
    <features-grid
      title="Response Time"
      :columns="2"
    >
      <feature-card
        icon="fas fa-clock"
        title="General Support"
        description="We typically respond within 24 hours during business days."
      />
      <feature-card
        icon="fas fa-exclamation-circle"
        title="Urgent Issues"
        description="For urgent matters, please use our phone support for immediate assistance."
      />
    </features-grid>
  </div>
</template>

<script>
import { HeroSection, FeaturesGrid, FeatureCard, ContactForm } from '../components'

export default {
  name: 'Contact',
  components: {
    HeroSection,
    FeaturesGrid,
    FeatureCard,
    ContactForm
  }
}
</script> 