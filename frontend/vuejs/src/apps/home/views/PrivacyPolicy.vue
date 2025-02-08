<!-- Privacy Policy page -->
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
            <span class="text-white block">Privacy Policy</span>
            <GradientText variant="primary" class="font-bold block text-3xl sm:text-4xl lg:text-5xl">
              Your Privacy Matters
            </GradientText>
          </h1>
          <p class="text-lg sm:text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            We are committed to protecting your privacy and ensuring the security of your personal information.
          </p>
        </div>
      </section>

      <div class="max-w-4xl mx-auto px-4 py-16 relative">
        <div class="space-y-16">
          <!-- Information We Collect -->
          <section class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/20 transition-all duration-300">
            <div class="flex items-center mb-8">
              <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mr-4">
                <i class="fas fa-database text-2xl text-primary-400"></i>
              </div>
              <h2 class="text-3xl font-bold text-white">Information We Collect</h2>
            </div>
            <div class="prose prose-invert max-w-none prose-p:text-gray-300 prose-li:text-gray-300 prose-strong:text-white">
              <p>We collect the following types of information to provide and improve our services:</p>
              <ul>
                <li>Account Information: Your name, email address, password, and other details provided during account registration.</li>
                <li>Profile Information: Details you provide to customize your user profile.</li>
                <li>Payment Information: Billing details and transaction data processed securely via third-party payment providers.</li>
                <li>Usage Data: Information about your interactions with our services.</li>
              </ul>
            </div>
          </section>

          <!-- How We Use Your Information -->
          <section class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/20 transition-all duration-300">
            <div class="flex items-center mb-8">
              <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mr-4">
                <i class="fas fa-cog text-2xl text-primary-400"></i>
              </div>
              <h2 class="text-3xl font-bold text-white">How We Use Your Information</h2>
            </div>
            <div class="prose prose-invert max-w-none prose-p:text-gray-300 prose-li:text-gray-300 prose-strong:text-white">
              <p>We use the collected information for the following purposes:</p>
              <ul>
                <li>To provide, maintain, and improve our services</li>
                <li>To process payments securely and efficiently</li>
                <li>To send technical notices and support messages</li>
                <li>To analyze usage trends and enhance user experience</li>
              </ul>
            </div>
          </section>

          <!-- Information Sharing -->
          <section class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/20 transition-all duration-300">
            <div class="flex items-center mb-8">
              <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mr-4">
                <i class="fas fa-share-nodes text-2xl text-primary-400"></i>
              </div>
              <h2 class="text-3xl font-bold text-white">Information Sharing</h2>
            </div>
            <div class="prose prose-invert max-w-none prose-p:text-gray-300 prose-li:text-gray-300 prose-strong:text-white">
              <p>Your personal information is not sold. However, we may share your data in the following situations:</p>
              <ul>
                <li><strong>Service Providers:</strong> Trusted third-party providers that support our operations.</li>
                <li><strong>Legal Obligations:</strong> To comply with laws, regulations, or legal requests.</li>
                <li><strong>Professional Advisors:</strong> Consultants, auditors, or legal counsel for business purposes.</li>
                <li><strong>Business Transfers:</strong> In the event of a merger, sale, or acquisition.</li>
              </ul>
            </div>
          </section>

          <!-- Data Security -->
          <section class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/20 transition-all duration-300">
            <div class="flex items-center mb-8">
              <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mr-4">
                <i class="fas fa-shield-halved text-2xl text-primary-400"></i>
              </div>
              <h2 class="text-3xl font-bold text-white">Data Security</h2>
            </div>
            <div class="prose prose-invert max-w-none prose-p:text-gray-300 prose-li:text-gray-300 prose-strong:text-white">
              <p>We prioritize the security of your personal information by implementing industry-standard measures, including:</p>
              <ul>
                <li>Encryption of sensitive data during transmission and storage</li>
                <li>Secure server infrastructure with access controls</li>
                <li>Regular security audits and monitoring for vulnerabilities</li>
              </ul>
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
              <p>If you have any questions or concerns about this Privacy Policy, please <router-link to="/contact" class="text-primary-400 hover:text-primary-300 transition-colors">contact us</router-link>.</p>
            </div>
          </section>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script>
import { DefaultLayout } from '@/shared/layouts'
import { GradientText, HeroSection } from '@/apps/home/components'

export default {
  name: 'Privacy',
  components: {
    DefaultLayout,
    GradientText,
    HeroSection
  }
}
</script>

<style>
/* Reset default prose list styles */
.prose :where(ul):not(:where([class~="not-prose"] *)) {
  padding-left: 0;
  list-style-type: none;
  margin: 0;
}

.prose :where(ul > li):not(:where([class~="not-prose"] *)) {
  position: relative;
  padding-left: 2rem;
  margin-top: 0.75em;
  margin-bottom: 0.75em;
}

/* Custom bullet point styling */
.prose :where(ul > li):not(:where([class~="not-prose"] *))::before {
  content: "";
  position: absolute;
  left: 0.5rem;
  top: 0.75em;
  height: 6px;
  width: 6px;
  border-radius: 50%;
  background-color: theme('colors.primary.400');
}

/* Ensure proper spacing for nested content */
.prose :where(ul > li > *):not(:where([class~="not-prose"] *)) {
  margin-top: 0;
  margin-bottom: 0;
}

/* Adjust spacing for paragraphs within list items */
.prose :where(ul > li p):not(:where([class~="not-prose"] *)) {
  margin: 0;
}
</style> 