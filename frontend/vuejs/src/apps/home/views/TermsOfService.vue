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
          <div class="prose prose-invert max-w-none">
            <p>By accessing or using Imagi's services, including our AI-powered website builder ("Imagi Oasis"), you agree to be bound by these Terms of Service.</p>
            <p>These Terms constitute a legally binding agreement between you and Imagi ("we," "us," or "our").</p>
          </div>
        </section>

        <!-- Service Description -->
        <section>
          <h2 class="text-3xl font-bold text-white mb-8">Service Description</h2>
          <div class="prose prose-invert max-w-none">
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
        <section>
          <h2 class="text-3xl font-bold text-white mb-8">User Responsibilities</h2>
          <div class="prose prose-invert max-w-none">
            <p>By using our services, you agree to:</p>
            <ul>
              <li>Maintain the confidentiality of your account credentials and notify us immediately of any unauthorized access.</li>
              <li>Provide accurate, current, and complete information during registration and use of the services.</li>
              <li>Comply with all applicable laws, regulations, and these Terms when using our platform.</li>
              <li>Refrain from using Imagi to create or distribute content that is illegal, harmful, or violates intellectual property rights.</li>
            </ul>
          </div>
        </section>

        <!-- Payment Terms -->
        <section>
          <h2 class="text-3xl font-bold text-white mb-8">Payment Terms</h2>
          <div class="prose prose-invert max-w-none">
            <ul>
              <li><strong>Non-Refundable Payments:</strong> All payments made for services or subscriptions are non-refundable unless required by law.</li>
              <li><strong>Subscription Fees:</strong> Recurring subscription fees will be charged automatically at the beginning of each billing cycle.</li>
              <li><strong>Price Changes:</strong> We reserve the right to change prices for our services. Any changes will be communicated to existing subscribers with reasonable notice.</li>
              <li><strong>Payment Methods:</strong> You must provide accurate payment information and ensure that your payment method remains valid.</li>
            </ul>
          </div>
        </section>

        <!-- Intellectual Property -->
        <section>
          <h2 class="text-3xl font-bold text-white mb-8">Intellectual Property</h2>
          <div class="prose prose-invert max-w-none">
            <p>All content, features, and materials available through Imagi, including but not limited to text, graphics, code, designs, logos, and software, are the intellectual property of Imagi or its licensors. They are protected by copyright, trademark, and other intellectual property laws.</p>
            <p>You may not copy, distribute, modify, or create derivative works from any of our content without prior written consent from Imagi.</p>
          </div>
        </section>

        <!-- User-Generated Content -->
        <section>
          <h2 class="text-3xl font-bold text-white mb-8">User-Generated Content</h2>
          <div class="prose prose-invert max-w-none">
            <p>By using Imagi's services to generate or upload content, you grant us a non-exclusive, worldwide, royalty-free license to use, modify, and display such content solely for the purpose of providing our services.</p>
            <p>You represent and warrant that you have the rights to upload or create content using our platform and that such content does not violate any applicable laws or third-party rights.</p>
          </div>
        </section>

        <!-- Limitation of Liability -->
        <section>
          <h2 class="text-3xl font-bold text-white mb-8">Limitation of Liability</h2>
          <div class="prose prose-invert max-w-none">
            <p>To the fullest extent permitted by law, Imagi shall not be liable for any indirect, incidental, special, consequential, or punitive damages, including without limitation loss of profits, data, use, goodwill, or other intangible losses, arising from:</p>
            <ul>
              <li>Your use of or inability to use the services.</li>
              <li>Any unauthorized access to or use of our servers and personal information.</li>
              <li>Any bugs, viruses, or other harmful components transmitted through the services.</li>
            </ul>
            <p>Our total liability for any claim relating to the services shall not exceed the amount you paid to us in the 12 months preceding the claim.</p>
          </div>
        </section>

        <!-- Changes to Terms -->
        <section>
          <h2 class="text-3xl font-bold text-white mb-8">Changes to Terms</h2>
          <div class="prose prose-invert max-w-none">
            <p>We reserve the right to modify these Terms of Service at any time. Material changes will be communicated to users via email or a prominent notice on our website. Continued use of the services after changes are made constitutes acceptance of the updated Terms.</p>
          </div>
        </section>

        <!-- Governing Law -->
        <section>
          <h2 class="text-3xl font-bold text-white mb-8">Governing Law</h2>
          <div class="prose prose-invert max-w-none">
            <p>These Terms shall be governed by and construed in accordance with the laws of the state of Texas, United States, without regard to its conflict of law provisions. Any disputes arising from or relating to these Terms shall be resolved exclusively in the state or federal courts located in Texas.</p>
          </div>
        </section>

        <!-- Contact Us -->
        <section>
          <h2 class="text-3xl font-bold text-white mb-8">Contact Us</h2>
          <div class="prose prose-invert max-w-none">
            <p>If you have any questions or concerns regarding these Terms, please <router-link to="/contact" class="text-primary-400 hover:text-primary-300">contact us</router-link>.</p>
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