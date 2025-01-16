<!-- Terms of Service page -->
<template>
  <div>
    <!-- Hero Section -->
    <hero-section
      title="Terms of Service"
      description="Understanding our service agreement"
    />

    <div class="max-w-4xl mx-auto px-4 py-16">
      <div class="space-y-16">
        <!-- Acceptance of Terms -->
        <section>
          <h2 class="text-3xl font-bold text-white mb-8">Acceptance of Terms</h2>
          <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
            <p class="text-gray-300">By accessing or using Imagi's services, you agree to be bound by these Terms of Service and all applicable laws and regulations.</p>
          </div>
        </section>

        <!-- User Responsibilities -->
        <section>
          <h2 class="text-3xl font-bold text-white mb-8">User Responsibilities</h2>
          <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
            <ul class="space-y-4 text-gray-300">
              <li>• Maintain the security of your account credentials</li>
              <li>• Comply with all applicable laws and regulations</li>
              <li>• Respect intellectual property rights</li>
              <li>• Use the service responsibly and ethically</li>
            </ul>
          </div>
        </section>

        <!-- Service Usage -->
        <section>
          <h2 class="text-3xl font-bold text-white mb-8">Service Usage</h2>
          <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
            <p class="text-gray-300">Our services are provided "as is" and "as available." We reserve the right to modify, suspend, or discontinue any part of our services at any time.</p>
          </div>
        </section>

        <!-- Contact -->
        <section>
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
  </div>
</template>

<script>
import { HeroSection } from '../components'

export default {
  name: 'Terms',
  components: {
    HeroSection
  }
}
</script> 