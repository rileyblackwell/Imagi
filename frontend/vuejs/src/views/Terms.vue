<template>
  <div class="terms">
    <!-- Hero Section -->
    <section class="hero terms-hero">
      <div class="hero-content">
        <h1 class="hero-title">Terms of Service</h1>
        <p class="hero-lead">Understanding our service agreement</p>
      </div>
    </section>

    <!-- Terms Content -->
    <section class="content-section">
      <div class="text-content">
        <section>
          <h2 class="section-header">Acceptance of Terms</h2>
          <div class="content-text">
            <p>By accessing or using Imagi's services, including our AI-powered website builder ("Imagi Oasis"), you agree to be bound by these Terms of Service.</p>
            <p>These Terms constitute a legally binding agreement between you and Imagi ("we," "us," or "our").</p>
          </div>
        </section>

        <section>
          <h2 class="section-header">Service Description</h2>
          <div class="content-text">
            <p>Imagi provides an AI-powered platform for generating code and websites using natural language input. Our services include:</p>
            <ul>
              <li>Website creation tools</li>
              <li>Hosting services</li>
              <li>Collaboration features</li>
              <li>Technical support</li>
            </ul>
          </div>
        </section>

        <section>
          <h2 class="section-header">User Responsibilities</h2>
          <div class="content-text">
            <p>By using our services, you agree to:</p>
            <ul>
              <li>Maintain the confidentiality of your account credentials and notify us immediately of any unauthorized access.</li>
              <li>Provide accurate, current, and complete information during registration and use of the services.</li>
              <li>Comply with all applicable laws, regulations, and these Terms when using our platform.</li>
              <li>Refrain from using Imagi to create or distribute content that is illegal, harmful, or violates intellectual property rights.</li>
            </ul>
          </div>
        </section>

        <section>
          <h2 class="section-header">Payment Terms</h2>
          <div class="content-text">
            <ul>
              <li><strong>Non-Refundable Payments:</strong> All payments made for services or subscriptions are non-refundable unless required by law.</li>
              <li><strong>Subscription Fees:</strong> Recurring subscription fees will be charged automatically at the beginning of each billing cycle.</li>
              <li><strong>Price Changes:</strong> We reserve the right to change prices for our services. Any changes will be communicated to existing subscribers with reasonable notice.</li>
              <li><strong>Payment Methods:</strong> You must provide accurate payment information and ensure that your payment method remains valid.</li>
            </ul>
          </div>
        </section>

        <section>
          <h2 class="section-header">Intellectual Property</h2>
          <div class="content-text">
            <p>All content, features, and materials available through Imagi, including but not limited to text, graphics, code, designs, logos, and software, are the intellectual property of Imagi or its licensors. They are protected by copyright, trademark, and other intellectual property laws.</p>
            <p>You may not copy, distribute, modify, or create derivative works from any of our content without prior written consent from Imagi.</p>
          </div>
        </section>

        <section>
          <h2 class="section-header">User-Generated Content</h2>
          <div class="content-text">
            <p>By using Imagi's services to generate or upload content, you grant us a non-exclusive, worldwide, royalty-free license to use, modify, and display such content solely for the purpose of providing our services.</p>
            <p>You represent and warrant that you have the rights to upload or create content using our platform and that such content does not violate any applicable laws or third-party rights.</p>
          </div>
        </section>

        <section>
          <h2 class="section-header">Limitation of Liability</h2>
          <div class="content-text">
            <p>To the fullest extent permitted by law, Imagi shall not be liable for any indirect, incidental, special, consequential, or punitive damages, including without limitation loss of profits, data, use, goodwill, or other intangible losses, arising from:</p>
            <ul>
              <li>Your use of or inability to use the services.</li>
              <li>Any unauthorized access to or use of our servers and personal information.</li>
              <li>Any bugs, viruses, or other harmful components transmitted through the services.</li>
            </ul>
            <p>Our total liability for any claim relating to the services shall not exceed the amount you paid to us in the 12 months preceding the claim.</p>
          </div>
        </section>

        <section>
          <h2 class="section-header">Changes to Terms</h2>
          <div class="content-text">
            <p>We reserve the right to modify these Terms of Service at any time. Material changes will be communicated to users via email or a prominent notice on our website. Continued use of the services after changes are made constitutes acceptance of the updated Terms.</p>
          </div>
        </section>

        <section>
          <h2 class="section-header">Governing Law</h2>
          <div class="content-text">
            <p>These Terms shall be governed by and construed in accordance with the laws of the state of Texas, United States, without regard to its conflict of law provisions. Any disputes arising from or relating to these Terms shall be resolved exclusively in the state or federal courts located in Texas.</p>
          </div>
        </section>

        <section>
          <h2 class="section-header">Contact Us</h2>
          <div class="content-text">
            <p>If you have any questions or concerns regarding these Terms, please <router-link to="/contact" class="link">contact us</router-link>.</p>
          </div>
        </section>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'TermsView'
}
</script>

<style scoped>
.terms {
  flex: 1;
}

/* Hero Section */
.terms-hero {
  min-height: 40vh;
  background: linear-gradient(135deg, 
    rgba(99, 102, 241, 0.15),
    rgba(0, 255, 198, 0.15)
  );
}

/* Text Content */
.text-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 var(--global-container-padding);
}

.content-text {
  margin-bottom: 3rem;
}

.content-text:last-child {
  margin-bottom: 0;
}

.content-text p {
  color: var(--global-muted-text-color);
  font-size: 1.125rem;
  line-height: 1.8;
  margin-bottom: 1.5rem;
}

.content-text ul {
  list-style-type: none;
  padding-left: 0;
  margin: 1.5rem 0;
}

.content-text li {
  color: var(--global-muted-text-color);
  font-size: 1.125rem;
  line-height: 1.8;
  margin-bottom: 1rem;
  padding-left: 1.5rem;
  position: relative;
}

.content-text li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: var(--link-hover);
}

.content-text strong {
  color: var(--global-text-color);
  font-weight: 600;
}

.link {
  color: var(--link-hover);
  text-decoration: none;
  transition: color 0.2s ease;
}

.link:hover {
  color: var(--global-text-color);
  text-decoration: underline;
}

/* Inherit global styles from Home.vue */
.hero {
  position: relative;
  padding: 6rem 0;
  text-align: center;
  border-bottom: 1px solid var(--global-border-light);
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 var(--global-container-padding);
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  background: var(--global-highlight-gradient);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1.2;
}

.hero-lead {
  font-size: 1.25rem;
  color: var(--global-muted-text-color);
  margin-bottom: 2.5rem;
  line-height: 1.6;
}

.content-section {
  padding: 5rem 0;
}

.section-header {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 2rem;
  color: var(--global-text-color);
}

/* Mobile styles */
@media screen and (max-width: 768px) {
  .terms-hero {
    min-height: 30vh;
  }

  .hero {
    padding: 4rem 0;
  }

  .hero-title {
    font-size: 2.5rem;
  }

  .hero-lead {
    font-size: 1.125rem;
  }

  .content-section {
    padding: 3rem 0;
  }

  .section-header {
    font-size: 1.75rem;
    margin-bottom: 1.5rem;
  }

  .content-text p,
  .content-text li {
    font-size: 1rem;
  }
}
</style> 