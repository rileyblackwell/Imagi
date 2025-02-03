<!-- Terms of Service page -->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="min-h-screen bg-dark-900">
      <!-- Hero Section -->
      <section class="relative min-h-[60vh] flex items-center justify-center overflow-hidden">
        <!-- Background Effects -->
        <div class="absolute inset-0 bg-dark-900">
          <div class="absolute inset-0 bg-gradient-to-br from-primary-500/10 via-dark-900 to-violet-500/10"></div>
          <div class="absolute top-20 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-gradient-to-r from-primary-500/20 to-violet-500/20 rounded-full blur-[120px] opacity-70"></div>
        </div>

        <!-- Content -->
        <div class="relative w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
            <span class="text-white block">Terms of Service</span>
            <GradientText variant="primary" class="font-bold block text-3xl sm:text-4xl lg:text-5xl">
              Our Service Agreement
            </GradientText>
          </h1>
          <p class="text-lg sm:text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Please read these terms carefully before using our services.
          </p>
        </div>
      </section>

      <div class="max-w-4xl mx-auto px-4 py-16 relative">
        <div class="space-y-16">
          <!-- Acceptance of Terms -->
          <section class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/20 transition-all duration-300">
            <div class="flex items-center mb-8">
              <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mr-4">
                <i class="fas fa-check-circle text-2xl text-primary-400"></i>
              </div>
              <h2 class="text-3xl font-bold text-white">Acceptance of Terms</h2>
            </div>
            <div class="prose prose-invert max-w-none prose-p:text-gray-300 prose-li:text-gray-300 prose-strong:text-white">
              <p>By accessing or using Imagi's services, including our AI-powered website builder ("Imagi Oasis"), you agree to be bound by these Terms of Service.</p>
              <p>These Terms constitute a legally binding agreement between you and Imagi ("we," "us," or "our").</p>
            </div>
          </section>

          <!-- Service Description -->
          <section class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/20 transition-all duration-300">
            <div class="flex items-center mb-8">
              <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mr-4">
                <i class="fas fa-cube text-2xl text-primary-400"></i>
              </div>
              <h2 class="text-3xl font-bold text-white">Service Description</h2>
            </div>
            <div class="prose prose-invert max-w-none prose-p:text-gray-300 prose-li:text-gray-300 prose-strong:text-white">
              <p>Imagi provides an AI-powered platform for generating code and websites using natural language input. Our services include:</p>
              <ul>
                <li>Website creation tools</li>
                <li>Hosting services</li>
                <li>Collaboration features</li>
                <li>Technical support</li>
              </ul>
            </div>
          </section>

          <!-- User Responsibilities -->
          <section class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/20 transition-all duration-300">
            <div class="flex items-center mb-8">
              <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mr-4">
                <i class="fas fa-user-shield text-2xl text-primary-400"></i>
              </div>
              <h2 class="text-3xl font-bold text-white">User Responsibilities</h2>
            </div>
            <div class="prose prose-invert max-w-none prose-p:text-gray-300 prose-li:text-gray-300 prose-strong:text-white">
              <p>By using our services, you agree to:</p>
              <ul>
                <li>Maintain the confidentiality of your account credentials</li>
                <li>Provide accurate and complete information</li>
                <li>Comply with all applicable laws and regulations</li>
                <li>Respect intellectual property rights</li>
              </ul>
            </div>
          </section>

          <!-- Payment Terms -->
          <section class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/20 transition-all duration-300">
            <div class="flex items-center mb-8">
              <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mr-4">
                <i class="fas fa-credit-card text-2xl text-primary-400"></i>
              </div>
              <h2 class="text-3xl font-bold text-white">Payment Terms</h2>
            </div>
            <div class="prose prose-invert max-w-none prose-p:text-gray-300 prose-li:text-gray-300 prose-strong:text-white">
              <ul>
                <li><strong>Non-Refundable Payments:</strong> All payments are non-refundable unless required by law</li>
                <li><strong>Subscription Fees:</strong> Recurring fees charged at the start of each billing cycle</li>
                <li><strong>Price Changes:</strong> We reserve the right to change prices with reasonable notice</li>
                <li><strong>Payment Methods:</strong> You must provide valid and accurate payment information</li>
              </ul>
            </div>
          </section>

          <!-- Intellectual Property -->
          <section class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/20 transition-all duration-300">
            <div class="flex items-center mb-8">
              <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mr-4">
                <i class="fas fa-copyright text-2xl text-primary-400"></i>
              </div>
              <h2 class="text-3xl font-bold text-white">Intellectual Property</h2>
            </div>
            <div class="prose prose-invert max-w-none prose-p:text-gray-300 prose-li:text-gray-300 prose-strong:text-white">
              <p>All content, features, and materials available through Imagi are protected by intellectual property laws. You may not copy, distribute, modify, or create derivative works without our consent.</p>
            </div>
          </section>

          <!-- Contact Us -->
          <section class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700">
            <div class="flex items-center mb-8">
              <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mr-4">
                <i class="fas fa-envelope text-2xl text-primary-400"></i>
              </div>
              <h2 class="text-3xl font-bold text-white">Contact Us</h2>
            </div>
            <div class="prose prose-invert max-w-none prose-p:text-gray-300">
              <p>If you have any questions about these Terms, please <router-link to="/contact" class="text-primary-400 hover:text-primary-300 transition-colors">contact us</router-link>.</p>
            </div>
          </section>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script>
import { DefaultLayout } from '../../../shared/layouts'
import { HeroSection } from '../components'
import GradientText from '../components/shared/GradientText.vue'

export default {
  name: 'Terms',
  components: {
    DefaultLayout,
    HeroSection,
    GradientText
  }
}
</script>

<style>
.prose :where(ul):not(:where([class~="not-prose"] *)) {
  padding-left: 0;
  list-style-type: none;
}

.prose :where(ul > li):not(:where([class~="not-prose"] *)) {
  position: relative;
  padding-left: 1.75em;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
}

.prose :where(ul > li):not(:where([class~="not-prose"] *))::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0.75em;
  height: 6px;
  width: 6px;
  border-radius: 50%;
  background-color: theme('colors.primary.400');
}
</style> 