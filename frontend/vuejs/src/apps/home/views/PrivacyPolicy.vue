<!-- Privacy Policy page -->
<template>
  <base-layout>
    <!-- Hero Section -->
    <hero-section
      title="Privacy Policy"
      description="Your privacy is important to us"
    />

    <!-- Main Content -->
    <div class="py-24">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- Information We Collect -->
        <section class="mb-16">
          <h2 class="text-3xl font-bold text-white mb-8">Information We Collect</h2>
          <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
            <p class="text-gray-300 mb-4">We collect the following types of information to provide and improve our services:</p>
            <ul class="space-y-4 text-gray-300">
              <li class="flex items-start">
                <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                <span>Account Information: Your name, email address, password, and other details provided during account registration.</span>
              </li>
              <li class="flex items-start">
                <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                <span>Profile Information: Details you provide to customize your user profile.</span>
              </li>
              <li class="flex items-start">
                <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                <span>Payment Information: Billing details and transaction data processed securely via third-party payment providers.</span>
              </li>
              <li class="flex items-start">
                <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                <span>Usage Data: Information about your interactions with our services.</span>
              </li>
            </ul>
          </div>
        </section>

        <!-- How We Use Your Information -->
        <section class="mb-16">
          <h2 class="text-3xl font-bold text-white mb-8">How We Use Your Information</h2>
          <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
            <p class="text-gray-300 mb-4">We use the collected information for the following purposes:</p>
            <ul class="space-y-4 text-gray-300">
              <li class="flex items-start">
                <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                <span>To provide, maintain, and improve our services</span>
              </li>
              <li class="flex items-start">
                <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                <span>To process payments securely and efficiently</span>
              </li>
              <li class="flex items-start">
                <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                <span>To send technical notices and support messages</span>
              </li>
              <li class="flex items-start">
                <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                <span>To analyze usage trends and enhance user experience</span>
              </li>
            </ul>
          </div>
        </section>

        <!-- Contact -->
        <section class="mb-16">
          <h2 class="text-3xl font-bold text-white mb-8">Contact Us</h2>
          <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
            <p class="text-gray-300">If you have any questions about this Privacy Policy, please contact us:</p>
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
  name: 'Privacy',
  components: {
    BaseLayout,
    HeroSection
  }
}
</script> 