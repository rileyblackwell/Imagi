<!-- Privacy Policy page -->
<template>
  <div>
    <!-- Hero Section -->
    <hero-section
      title="Privacy Policy"
      description="Your privacy is important to us"
    />

    <div class="max-w-4xl mx-auto px-4 py-16">
      <div class="space-y-16">
        <!-- Information We Collect -->
        <section>
          <h2 class="text-3xl font-bold text-white mb-8">Information We Collect</h2>
          <div class="space-y-6">
            <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
              <h3 class="text-xl font-semibold text-white mb-4">Account Information</h3>
              <p class="text-gray-300">When you create an account, we collect your name, email address, and password.</p>
            </div>
            <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
              <h3 class="text-xl font-semibold text-white mb-4">Profile Information</h3>
              <p class="text-gray-300">You may choose to provide additional profile information such as a profile picture or bio.</p>
            </div>
            <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
              <h3 class="text-xl font-semibold text-white mb-4">Payment Information</h3>
              <p class="text-gray-300">For paid services, we collect payment information through our secure payment processor.</p>
            </div>
            <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
              <h3 class="text-xl font-semibold text-white mb-4">Usage Data</h3>
              <p class="text-gray-300">We collect information about how you use our services, including your interactions with our platform.</p>
            </div>
          </div>
        </section>

        <!-- How We Use Your Information -->
        <section>
          <h2 class="text-3xl font-bold text-white mb-8">How We Use Your Information</h2>
          <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
            <ul class="space-y-4 text-gray-300">
              <li>• To provide and maintain our services</li>
              <li>• To process your payments</li>
              <li>• To communicate with you about our services</li>
              <li>• To improve our platform and user experience</li>
              <li>• To detect and prevent fraud or abuse</li>
            </ul>
          </div>
        </section>

        <!-- Contact Us -->
        <section>
          <h2 class="text-3xl font-bold text-white mb-8">Contact Us</h2>
          <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
            <p class="text-gray-300 mb-4">If you have any questions about our Privacy Policy, please contact us:</p>
            <router-link to="/contact" class="text-primary-400 hover:text-primary-300">Contact Form →</router-link>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script>
import { HeroSection } from '../components'

export default {
  name: 'Privacy',
  components: {
    HeroSection
  }
}
</script> 