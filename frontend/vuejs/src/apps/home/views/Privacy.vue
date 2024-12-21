<template>
  <div class="privacy-page">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-container">
        <h1 class="hero-title">Privacy Policy</h1>
        <p class="hero-description">
          Your privacy is important to us
        </p>
      </div>
    </section>

    <!-- Content Section -->
    <section class="content-section">
      <div class="section-container">
        <div class="policy-content">
          <!-- Information Collection -->
          <section class="policy-section">
            <h2 class="section-header">Information We Collect</h2>
            <p>We collect the following types of information to provide and improve our services:</p>
            <ul class="policy-list">
              <li>Account Information: Your name, email address, password, and other details provided during account registration.</li>
              <li>Profile Information: Details you provide to customize your user profile.</li>
              <li>Payment Information: Billing details and transaction data processed securely via third-party payment providers.</li>
              <li>Usage Data: Information about your interactions with our services.</li>
            </ul>
          </section>

          <!-- Information Usage -->
          <section class="policy-section">
            <h2 class="section-header">How We Use Your Information</h2>
            <p>We use the collected information for the following purposes:</p>
            <ul class="policy-list">
              <li>To provide, maintain, and improve our services</li>
              <li>To process payments securely and efficiently</li>
              <li>To send technical notices and support messages</li>
              <li>To analyze usage trends and enhance user experience</li>
            </ul>
          </section>

          <!-- Information Sharing -->
          <section class="policy-section">
            <h2 class="section-header">Information Sharing</h2>
            <p>Your personal information is not sold. However, we may share your data in the following situations:</p>
            <ul class="policy-list">
              <li><strong>Service Providers:</strong> Trusted third-party providers that support our operations.</li>
              <li><strong>Legal Obligations:</strong> To comply with laws, regulations, or legal requests.</li>
              <li><strong>Professional Advisors:</strong> Consultants, auditors, or legal counsel for business purposes.</li>
              <li><strong>Business Transfers:</strong> In the event of a merger, sale, or acquisition.</li>
            </ul>
          </section>

          <!-- Data Security -->
          <section class="policy-section">
            <h2 class="section-header">Data Security</h2>
            <p>We prioritize the security of your personal information by implementing industry-standard measures:</p>
            <ul class="policy-list">
              <li>Encryption of sensitive data during transmission and storage</li>
              <li>Secure server infrastructure with access controls</li>
              <li>Regular security audits and monitoring</li>
            </ul>
          </section>

          <!-- Your Rights -->
          <section class="policy-section">
            <h2 class="section-header">Your Rights</h2>
            <p>You have the following rights regarding your personal data:</p>
            <ul class="policy-list">
              <li><strong>Access:</strong> Request a copy of your personal data</li>
              <li><strong>Correction:</strong> Update or correct inaccuracies</li>
              <li><strong>Deletion:</strong> Request deletion of your data</li>
              <li><strong>Data Portability:</strong> Obtain your data in a portable format</li>
            </ul>
          </section>

          <!-- Contact -->
          <section class="policy-section">
            <h2 class="section-header">Contact Us</h2>
            <p>If you have any questions about this Privacy Policy, please contact us:</p>
            <div class="contact-button">
              <router-link to="/contact" class="btn btn-primary">
                Contact Us
                <i class="fas fa-arrow-right"></i>
              </router-link>
            </div>
          </section>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.privacy-page {
  background: var(--bg-primary);
}

/* Hero Section */
.hero-section {
  padding: 120px 0 80px;
  background: radial-gradient(
    circle at top right,
    rgba(0, 255, 204, 0.15),
    transparent 50%
  );
  text-align: center;
}

.hero-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 2rem;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  line-height: 1.1;
  margin-bottom: 1.5rem;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-description {
  font-size: 1.25rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

/* Content Section */
.content-section {
  padding: 80px 0;
}

.section-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 2rem;
}

.policy-content {
  background: var(--bg-primary);
  border-radius: 24px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  padding: 3rem;
}

.policy-section {
  margin-bottom: 3rem;
}

.policy-section:last-child {
  margin-bottom: 0;
}

.section-header {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1.5rem;
}

.policy-section p {
  font-size: 1.125rem;
  line-height: 1.7;
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

.policy-list {
  list-style: none;
  padding: 0;
  margin: 0 0 1.5rem;
}

.policy-list li {
  position: relative;
  padding-left: 1.5rem;
  margin-bottom: 1rem;
  font-size: 1.125rem;
  line-height: 1.7;
  color: var(--text-secondary);
}

.policy-list li::before {
  content: "•";
  position: absolute;
  left: 0;
  color: var(--primary-color);
}

.policy-list li strong {
  color: var(--text-primary);
  font-weight: 600;
}

.contact-button {
  margin-top: 2rem;
  text-align: center;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 1.125rem;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--primary-gradient);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }

  .hero-description {
    font-size: 1.125rem;
  }

  .policy-content {
    padding: 2rem;
  }

  .section-header {
    font-size: 1.75rem;
  }

  .policy-section p,
  .policy-list li {
    font-size: 1rem;
  }
}
</style> 