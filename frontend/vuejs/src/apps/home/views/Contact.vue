<!-- Contact page -->
<template>
  <base-layout>
    <!-- Hero Section -->
    <hero-section
      title="Get in Touch"
      description="We're here to help you bring your ideas to life"
    />

    <!-- Contact Methods -->
    <features-grid
      title="Contact Methods"
      :columns="2"
    >
      <feature-card
        icon="fas fa-envelope"
        title="Email Support"
        description="For general inquiries and support"
      >
        <template #footer>
          <a href="mailto:rileyblackwell5@gmail.com" class="text-primary-400 hover:text-primary-300">rileyblackwell5@gmail.com</a>
        </template>
      </feature-card>
      
      <feature-card
        icon="fas fa-phone"
        title="Phone Support"
        description="Available during business hours"
      >
        <template #footer>
          <a href="tel:6168813592" class="text-primary-400 hover:text-primary-300">616-881-3592</a>
        </template>
      </feature-card>
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
  </base-layout>
</template>

<script>
import BaseLayout from '@/shared/layouts/BaseLayout.vue'
import { HeroSection, FeaturesGrid, FeatureCard, ContactForm } from '../components'

export default {
  name: 'Contact',
  components: {
    BaseLayout,
    HeroSection,
    FeaturesGrid,
    FeatureCard,
    ContactForm
  }
}
</script> 