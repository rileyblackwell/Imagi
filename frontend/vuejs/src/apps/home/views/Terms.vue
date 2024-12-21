<template>
  <base-layout>
    <!-- Hero Section -->
    <template #hero>
      <div class="absolute inset-0 bg-gradient-radial from-primary-500/10 via-transparent to-transparent"></div>
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        <div class="text-center max-w-3xl mx-auto">
          <h1 class="text-5xl md:text-6xl font-extrabold tracking-tight text-white">
            Terms of Service
          </h1>
          <p class="mt-6 text-xl text-gray-300">
            Understanding our service agreement
          </p>
        </div>
      </div>
    </template>

    <!-- Main Content -->
    <template #default>
      <div class="py-24">
        <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <!-- Acceptance of Terms -->
          <section class="mb-16">
            <h2 class="text-3xl font-bold text-white mb-8">Acceptance of Terms</h2>
            <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
              <p class="text-gray-300 mb-4">By accessing or using Imagi's services, including our AI-powered website builder ("Imagi Oasis"), you agree to be bound by these Terms of Service.</p>
              <p class="text-gray-300">These Terms constitute a legally binding agreement between you and Imagi ("we," "us," or "our").</p>
            </div>
          </section>

          <!-- Service Description -->
          <section class="mb-16">
            <h2 class="text-3xl font-bold text-white mb-8">Service Description</h2>
            <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
              <p class="text-gray-300 mb-4">Imagi provides an AI-powered platform for generating code and websites using natural language input. Our services include:</p>
              <ul class="space-y-4 text-gray-300">
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span>Website creation tools</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span>Hosting services</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span>Collaboration features</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span>Technical support</span>
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
                  <span>Maintain the confidentiality of your account credentials and notify us immediately of any unauthorized access.</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span>Provide accurate, current, and complete information during registration and use of the services.</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span>Comply with all applicable laws, regulations, and these Terms when using our platform.</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span>Refrain from using Imagi to create or distribute content that is illegal, harmful, or violates intellectual property rights.</span>
                </li>
              </ul>
            </div>
          </section>

          <!-- Payment Terms -->
          <section class="mb-16">
            <h2 class="text-3xl font-bold text-white mb-8">Payment Terms</h2>
            <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
              <ul class="space-y-4 text-gray-300">
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span><strong>Non-Refundable Payments:</strong> All payments made for services or subscriptions are non-refundable unless required by law.</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span><strong>Subscription Fees:</strong> Recurring subscription fees will be charged automatically at the beginning of each billing cycle.</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span><strong>Price Changes:</strong> We reserve the right to change prices for our services. Any changes will be communicated to existing subscribers with reasonable notice.</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span><strong>Payment Methods:</strong> You must provide accurate payment information and ensure that your payment method remains valid.</span>
                </li>
              </ul>
            </div>
          </section>

          <!-- Intellectual Property -->
          <section class="mb-16">
            <h2 class="text-3xl font-bold text-white mb-8">Intellectual Property</h2>
            <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
              <p class="text-gray-300 mb-4">All content, features, and materials available through Imagi, including but not limited to text, graphics, code, designs, logos, and software, are the intellectual property of Imagi or its licensors. They are protected by copyright, trademark, and other intellectual property laws.</p>
              <p class="text-gray-300">You may not copy, distribute, modify, or create derivative works from any of our content without prior written consent from Imagi.</p>
            </div>
          </section>

          <!-- User-Generated Content -->
          <section class="mb-16">
            <h2 class="text-3xl font-bold text-white mb-8">User-Generated Content</h2>
            <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
              <p class="text-gray-300 mb-4">By using Imagi's services to generate or upload content, you grant us a non-exclusive, worldwide, royalty-free license to use, modify, and display such content solely for the purpose of providing our services.</p>
              <p class="text-gray-300">You represent and warrant that you have the rights to upload or create content using our platform and that such content does not violate any applicable laws or third-party rights.</p>
            </div>
          </section>

          <!-- Limitation of Liability -->
          <section class="mb-16">
            <h2 class="text-3xl font-bold text-white mb-8">Limitation of Liability</h2>
            <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
              <p class="text-gray-300 mb-4">To the fullest extent permitted by law, Imagi shall not be liable for any indirect, incidental, special, consequential, or punitive damages, including without limitation loss of profits, data, use, goodwill, or other intangible losses, arising from:</p>
              <ul class="space-y-4 text-gray-300">
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span>Your use of or inability to use the services.</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span>Any unauthorized access to or use of our servers and personal information.</span>
                </li>
                <li class="flex items-start">
                  <i class="fas fa-check text-primary-400 mt-1.5 mr-3"></i>
                  <span>Any bugs, viruses, or other harmful components transmitted through the services.</span>
                </li>
              </ul>
              <p class="text-gray-300 mt-4">Our total liability for any claim relating to the services shall not exceed the amount you paid to us in the 12 months preceding the claim.</p>
            </div>
          </section>

          <!-- Changes to Terms -->
          <section class="mb-16">
            <h2 class="text-3xl font-bold text-white mb-8">Changes to Terms</h2>
            <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
              <p class="text-gray-300">We reserve the right to modify these Terms of Service at any time. Material changes will be communicated to users via email or a prominent notice on our website. Continued use of the services after changes are made constitutes acceptance of the updated Terms.</p>
            </div>
          </section>

          <!-- Governing Law -->
          <section class="mb-16">
            <h2 class="text-3xl font-bold text-white mb-8">Governing Law</h2>
            <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
              <p class="text-gray-300">These Terms shall be governed by and construed in accordance with the laws of the state of Texas, United States, without regard to its conflict of law provisions. Any disputes arising from or relating to these Terms shall be resolved exclusively in the state or federal courts located in Texas.</p>
            </div>
          </section>

          <!-- Contact -->
          <section class="mb-16">
            <h2 class="text-3xl font-bold text-white mb-8">Contact Us</h2>
            <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
              <p class="text-gray-300">If you have any questions or concerns regarding these Terms, please contact us:</p>
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
  name: 'Terms',
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