<!-- Terms of Service page -->
<template>
  <base-layout>
    <!-- Hero Section -->
    <hero-section
      title="Terms of Service"
      description="Understanding our service agreement"
    />

    <!-- Main Content -->
    <div class="py-24">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- Acceptance of Terms -->
        <section class="mb-16">
          <h2 class="text-3xl font-bold text-white mb-8">Acceptance of Terms</h2>
          <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
            <p class="text-gray-300">By accessing or using Imagi's services, you agree to be bound by these Terms and our Privacy Policy. If you do not agree to these Terms, you must not access or use our services.</p>
          </div>
        </section>

        <!-- Service Description -->
        <section class="mb-16">
          <h2 class="text-3xl font-bold text-white mb-8">Service Description</h2>
          <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
            <p class="text-gray-300 mb-4">Imagi provides a platform that enables users to:</p>
            <ul class="space-y-4 text-gray-300">
              <li class="flex items-start">
                <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                <span>Create web applications using natural language prompts</span>
              </li>
              <li class="flex items-start">
                <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                <span>Generate and modify code through AI assistance</span>
              </li>
              <li class="flex items-start">
                <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                <span>Deploy and manage web applications</span>
              </li>
              <li class="flex items-start">
                <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                <span>Access documentation and support resources</span>
              </li>
            </ul>
          </div>
        </section>

        <!-- User Responsibilities -->
        <section class="mb-16">
          <h2 class="text-3xl font-bold text-white mb-8">User Responsibilities</h2>
          <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
            <p class="text-gray-300 mb-4">By using our services, you agree to:</p>
            <ul class="space-y-4 text-gray-300">
              <li class="flex items-start">
                <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                <span>Maintain the confidentiality of your account credentials</span>
              </li>
              <li class="flex items-start">
                <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                <span>Provide accurate and complete information</span>
              </li>
              <li class="flex items-start">
                <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                <span>Comply with all applicable laws and regulations</span>
              </li>
              <li class="flex items-start">
                <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                <span>Respect intellectual property rights</span>
              </li>
            </ul>
          </div>
        </section>

        <!-- Contact -->
        <section class="mb-16">
          <h2 class="text-3xl font-bold text-white mb-8">Contact Us</h2>
          <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
            <p class="text-gray-300">If you have any questions about these Terms, please contact us:</p>
            <div class="mt-4">
              <router-link to="/contact" class="text-primary-400 hover:text-primary-300">Contact Form →</router-link>
            </div>
          </div>
        </section>
      </div>
    </div>
  </base-layout>
</template>

<script>
import BaseLayout from '@/shared/layouts/BaseLayout.vue'
import { HeroSection } from '../components'

export default {
  name: 'Terms',
  components: {
    BaseLayout,
    HeroSection
  }
}
</script> 