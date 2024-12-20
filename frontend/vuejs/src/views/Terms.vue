<template>
  <div class="terms-page">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-container">
        <h1 class="hero-title">Terms of Service</h1>
        <p class="hero-description">
          Please read these terms carefully before using our services
        </p>
      </div>
    </section>

    <!-- Content Section -->
    <section class="content-section">
      <div class="section-container">
        <div class="policy-content">
          <!-- Agreement -->
          <section class="policy-section">
            <h2 class="section-header">Agreement to Terms</h2>
            <p>By accessing or using Imagi's services, you agree to be bound by these Terms of Service and all applicable laws and regulations. If you do not agree with any of these terms, you are prohibited from using our services.</p>
          </section>

          <!-- Services -->
          <section class="policy-section">
            <h2 class="section-header">Our Services</h2>
            <p>Imagi provides AI-powered web development services, including but not limited to:</p>
            <ul class="policy-list">
              <li>Natural language to code generation</li>
              <li>Web application development tools</li>
              <li>Project management features</li>
              <li>Hosting and deployment services</li>
            </ul>
          </section>

          <!-- User Responsibilities -->
          <section class="policy-section">
            <h2 class="section-header">User Responsibilities</h2>
            <p>As a user of our services, you agree to:</p>
            <ul class="policy-list">
              <li>Provide accurate and complete information</li>
              <li>Maintain the security of your account credentials</li>
              <li>Use our services in compliance with applicable laws</li>
              <li>Not engage in any unauthorized or harmful activities</li>
            </ul>
          </section>

          <!-- Intellectual Property -->
          <section class="policy-section">
            <h2 class="section-header">Intellectual Property</h2>
            <p>Users retain ownership of their content while granting Imagi necessary licenses to:</p>
            <ul class="policy-list">
              <li>Host and display your content</li>
              <li>Improve our AI models and services</li>
              <li>Provide features and functionality</li>
            </ul>
          </section>

          <!-- Payments -->
          <section class="policy-section">
            <h2 class="section-header">Payments and Credits</h2>
            <p>Our payment terms include:</p>
            <ul class="policy-list">
              <li>Credit-based system for using AI services</li>
              <li>Secure payment processing through trusted providers</li>
              <li>No refunds for used credits or services</li>
              <li>Automatic renewal of subscription plans</li>
            </ul>
          </section>

          <!-- Limitation of Liability -->
          <section class="policy-section">
            <h2 class="section-header">Limitation of Liability</h2>
            <p>Imagi provides services "as is" and disclaims all warranties. We are not liable for:</p>
            <ul class="policy-list">
              <li>Service interruptions or downtime</li>
              <li>Data loss or security breaches</li>
              <li>Generated code quality or performance</li>
              <li>Third-party services or integrations</li>
            </ul>
          </section>

          <!-- Termination -->
          <section class="policy-section">
            <h2 class="section-header">Account Termination</h2>
            <p>We reserve the right to terminate or suspend accounts that:</p>
            <ul class="policy-list">
              <li>Violate these terms of service</li>
              <li>Engage in fraudulent activity</li>
              <li>Abuse our services or resources</li>
              <li>Fail to pay for services</li>
            </ul>
          </section>

          <!-- Contact -->
          <section class="policy-section">
            <h2 class="section-header">Questions About Terms</h2>
            <p>If you have any questions about these Terms of Service, please contact us:</p>
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
.terms-page {
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