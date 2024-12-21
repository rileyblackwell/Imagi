<template>
  <base-layout>
    <!-- Hero Section -->
    <template #hero>
      <div class="absolute inset-0 bg-gradient-radial from-primary-500/10 via-transparent to-transparent"></div>
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        <div class="text-center max-w-3xl mx-auto">
          <h1 class="text-5xl md:text-6xl font-extrabold tracking-tight text-white">
            Privacy Policy
          </h1>
          <p class="mt-6 text-xl text-gray-300">
            Your privacy is important to us
          </p>
        </div>
      </div>
    </template>

    <!-- Main Content -->
    <template #default>
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

          <!-- Information Sharing -->
          <section class="mb-16">
            <h2 class="text-3xl font-bold text-white mb-8">Information Sharing</h2>
            <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
              <p class="text-gray-300 mb-4">Your personal information is not sold. However, we may share your data in the following situations:</p>
              <ul class="space-y-4 text-gray-300">
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span><strong>Service Providers:</strong> Trusted third-party providers that support our operations, such as hosting, analytics, and payment processing.</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span><strong>Legal Obligations:</strong> To comply with laws, regulations, or legal requests, including responses to subpoenas or court orders.</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span><strong>Professional Advisors:</strong> Consultants, auditors, or legal counsel for business or compliance purposes.</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span><strong>Business Transfers:</strong> In the event of a merger, sale, or acquisition, your data may be transferred as part of the transaction.</span>
                </li>
              </ul>
            </div>
          </section>

          <!-- Data Security -->
          <section class="mb-16">
            <h2 class="text-3xl font-bold text-white mb-8">Data Security</h2>
            <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
              <p class="text-gray-300 mb-4">We prioritize the security of your personal information by implementing industry-standard measures, including:</p>
              <ul class="space-y-4 text-gray-300">
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span>Encryption of sensitive data during transmission and storage.</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span>Secure server infrastructure with access controls.</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span>Regular security audits and monitoring for vulnerabilities.</span>
                </li>
              </ul>
              <p class="text-gray-300 mt-4">While we strive to protect your information, no system is 100% secure, and we cannot guarantee absolute security.</p>
            </div>
          </section>

          <!-- Your Rights -->
          <section class="mb-16">
            <h2 class="text-3xl font-bold text-white mb-8">Your Rights</h2>
            <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
              <p class="text-gray-300 mb-4">Depending on your jurisdiction (e.g., GDPR, CCPA), you may have the following rights:</p>
              <ul class="space-y-4 text-gray-300">
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span><strong>Access:</strong> Request a copy of the personal data we hold about you.</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span><strong>Correction:</strong> Update or correct inaccuracies in your personal data.</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span><strong>Deletion:</strong> Request deletion of your data, subject to certain legal obligations.</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span><strong>Data Portability:</strong> Obtain your data in a portable format.</span>
                </li>
              </ul>
            </div>
          </section>

          <!-- Contact Information -->
          <section class="mb-16">
            <h2 class="text-3xl font-bold text-white mb-8">Contact Us</h2>
            <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
              <p class="text-gray-300">If you have any questions about this Privacy Policy or our data practices, please contact us:</p>
              <div class="mt-4">
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
  name: 'Privacy',
  components: {
    BaseLayout
  }
}
</script>

<style>
.bg-gradient-radial {
  background: radial-gradient(circle at top right, var(--tw-gradient-from), var(--tw-gradient-to));
}
</style> 