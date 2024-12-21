<template>
  <base-layout>
    <!-- Hero Section -->
    <template #hero>
      <div class="absolute inset-0 bg-gradient-radial from-primary-500/10 via-transparent to-transparent"></div>
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        <div class="text-center max-w-3xl mx-auto">
          <h1 class="text-5xl md:text-6xl font-extrabold tracking-tight text-white">
            Cookie Policy
          </h1>
          <p class="mt-6 text-xl text-gray-300">
            Understanding how we use cookies to improve your experience
          </p>
        </div>
      </div>
    </template>

    <!-- Main Content -->
    <template #default>
      <div class="py-24">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <!-- Cookie Overview -->
          <section class="mb-24">
            <h2 class="text-3xl font-bold text-white text-center mb-16">Cookie Overview</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6">
                  <i class="fas fa-cookie-bite text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">What Are Cookies?</h3>
                <p class="text-gray-300">Small text files stored on your device that help us provide a better browsing experience.</p>
              </div>
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6">
                  <i class="fas fa-tasks text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">How We Use Them</h3>
                <p class="text-gray-300">To remember preferences, analyze site usage, and enhance functionality.</p>
              </div>
            </div>
          </section>

          <!-- Types of Cookies -->
          <section class="mb-24">
            <h2 class="text-3xl font-bold text-white text-center mb-16">Types of Cookies</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6">
                  <i class="fas fa-shield-alt text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Essential Cookies</h3>
                <p class="text-gray-300">Required for core website functionality. These cannot be disabled as they are necessary for the site to work properly.</p>
              </div>
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6">
                  <i class="fas fa-chart-line text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Analytics Cookies</h3>
                <p class="text-gray-300">Help us understand how visitors interact with our website by collecting anonymous information.</p>
              </div>
            </div>
          </section>

          <!-- Cookie Management -->
          <section class="mb-24">
            <h2 class="text-3xl font-bold text-white text-center mb-16">Cookie Management</h2>
            <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
              <p class="text-gray-300 mb-6">You have several options to manage your cookie preferences:</p>
              <ul class="space-y-4 text-gray-300">
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span>Browser Settings: Configure your browser to accept, reject, or delete cookies</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span>Privacy Settings: Adjust your privacy preferences directly on our website</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span>Third-Party Tools: Use available cookie management tools</span>
                </li>
              </ul>
            </div>
          </section>

          <!-- Third-Party Cookies -->
          <section class="mb-24">
            <h2 class="text-3xl font-bold text-white text-center mb-16">Third-Party Cookies</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6">
                  <i class="fas fa-chart-bar text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Analytics Partners</h3>
                <p class="text-gray-300">We use trusted analytics services to improve our website performance.</p>
              </div>
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6">
                  <i class="fas fa-credit-card text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Payment Processors</h3>
                <p class="text-gray-300">Secure payment processing through trusted financial partners.</p>
              </div>
            </div>
          </section>

          <!-- Updates & Contact -->
          <section>
            <h2 class="text-3xl font-bold text-white text-center mb-16">Updates & Contact</h2>
            <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
              <p class="text-gray-300 mb-6">We may update this Cookie Policy periodically. For questions or concerns, please contact us:</p>
              <div class="text-center">
                <router-link to="/contact" class="text-primary-400 hover:text-primary-300">Contact Form →</router-link>
              </div>
            </div>
          </section>
        </div>
      </div>
    </template>
  </base-layout>
</template>

<script>
import BaseLayout from '@/shared/layouts/BaseLayout.vue'

export default {
  name: 'CookiePolicy',
  components: {
    BaseLayout
  }
}
</script>

<style>
.shadow-glow {
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(0, 255, 204, 0.1);
}

.bg-gradient-radial {
  background: radial-gradient(circle at top right, var(--tw-gradient-from), var(--tw-gradient-to));
}
</style> 