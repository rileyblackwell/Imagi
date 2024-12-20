<template>
  <div class="cookie-policy-page">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-container">
        <h1 class="hero-title">Cookie Policy</h1>
        <p class="hero-description">
          Understanding how we use cookies to improve your experience
        </p>
      </div>
    </section>

    <!-- Content Section -->
    <section class="content-section">
      <div class="section-container">
        <div class="policy-content">
          <!-- Introduction -->
          <section class="policy-section">
            <h2 class="section-header">What Are Cookies</h2>
            <p>Cookies are small text files that are placed on your device when you visit our website. They help us provide you with a better experience by:</p>
            <ul class="policy-list">
              <li>Remembering your preferences and settings</li>
              <li>Understanding how you use our website</li>
              <li>Improving our services based on your behavior</li>
              <li>Providing personalized content and features</li>
            </ul>
          </section>

          <!-- Types of Cookies -->
          <section class="policy-section">
            <h2 class="section-header">Types of Cookies We Use</h2>
            
            <h3 class="subsection-header">Essential Cookies</h3>
            <p>These cookies are necessary for the website to function properly. They enable core functionality such as:</p>
            <ul class="policy-list">
              <li>User authentication and security</li>
              <li>Account information and preferences</li>
              <li>Shopping cart functionality</li>
            </ul>

            <h3 class="subsection-header">Analytics Cookies</h3>
            <p>These cookies help us understand how visitors interact with our website:</p>
            <ul class="policy-list">
              <li>Page views and navigation patterns</li>
              <li>Time spent on different pages</li>
              <li>Error encounters and usage statistics</li>
            </ul>

            <h3 class="subsection-header">Functionality Cookies</h3>
            <p>These cookies enable enhanced functionality and personalization:</p>
            <ul class="policy-list">
              <li>Remembering your preferences</li>
              <li>Customizing content based on your choices</li>
              <li>Saving your session state</li>
            </ul>
          </section>

          <!-- Cookie Management -->
          <section class="policy-section">
            <h2 class="section-header">Managing Your Cookie Preferences</h2>
            <p>You can control and manage cookies in various ways:</p>
            <ul class="policy-list">
              <li>Browser Settings: Configure your browser to block or alert you about cookies</li>
              <li>Cookie Consent: Use our cookie consent tool to manage your preferences</li>
              <li>Third-Party Tools: Utilize privacy tools and browser extensions</li>
            </ul>
            <div class="cookie-preferences">
              <button class="btn btn-primary" @click="openCookiePreferences">
                Manage Cookie Preferences
                <i class="fas fa-cog"></i>
              </button>
            </div>
          </section>

          <!-- Third-Party Cookies -->
          <section class="policy-section">
            <h2 class="section-header">Third-Party Cookies</h2>
            <p>Some features and integrations on our website use cookies from third-party services:</p>
            <ul class="policy-list">
              <li>Analytics providers (e.g., Google Analytics)</li>
              <li>Payment processors</li>
              <li>Social media integrations</li>
              <li>Advertising partners</li>
            </ul>
          </section>

          <!-- Updates -->
          <section class="policy-section">
            <h2 class="section-header">Updates to This Policy</h2>
            <p>We may update this Cookie Policy to reflect changes in our practices or for legal compliance. We encourage you to review this policy periodically.</p>
            <div class="contact-button">
              <router-link to="/contact" class="btn btn-secondary">
                Questions? Contact Us
                <i class="fas fa-arrow-right"></i>
              </router-link>
            </div>
          </section>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
const openCookiePreferences = () => {
  // TODO: Implement cookie preferences modal
  console.log('Opening cookie preferences')
}
</script>

<style scoped>
.cookie-policy-page {
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

.subsection-header {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 2rem 0 1rem;
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

.cookie-preferences,
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
  border: none;
  cursor: pointer;
}

.btn-primary {
  background: var(--primary-gradient);
  color: white;
}

.btn-secondary {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.btn-secondary:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
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

  .subsection-header {
    font-size: 1.25rem;
  }

  .policy-section p,
  .policy-list li {
    font-size: 1rem;
  }
}
</style> 