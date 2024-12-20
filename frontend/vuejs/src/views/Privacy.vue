<template>
  <div class="privacy">
    <!-- Hero Section -->
    <section class="hero privacy-hero">
      <div class="hero-content">
        <h1 class="hero-title">Privacy Policy</h1>
        <p class="hero-lead">Your privacy is important to us</p>
      </div>
    </section>

    <!-- Privacy Content -->
    <section class="content-section">
      <div class="text-content">
        <section>
          <h2 class="section-header">Information We Collect</h2>
          <div class="content-text">
            <p>We collect the following types of information to provide and improve our services:</p>
            <ul>
              <li>Account Information: Your name, email address, password, and other details provided during account registration.</li>
              <li>Profile Information: Details you provide to customize your user profile.</li>
              <li>Payment Information: Billing details and transaction data processed securely via third-party payment providers.</li>
              <li>Usage Data: Information about your interactions with our services.</li>
            </ul>
          </div>
        </section>

        <section>
          <h2 class="section-header">How We Use Your Information</h2>
          <div class="content-text">
            <p>We use the collected information for the following purposes:</p>
            <ul>
              <li>To provide, maintain, and improve our services</li>
              <li>To process payments securely and efficiently</li>
              <li>To send technical notices and support messages</li>
              <li>To analyze usage trends and enhance user experience</li>
            </ul>
          </div>
        </section>

        <section>
          <h2 class="section-header">Information Sharing</h2>
          <div class="content-text">
            <p>Your personal information is not sold. However, we may share your data in the following situations:</p>
            <ul>
              <li><strong>Service Providers:</strong> Trusted third-party providers that support our operations, such as hosting, analytics, and payment processing.</li>
              <li><strong>Legal Obligations:</strong> To comply with laws, regulations, or legal requests, including responses to subpoenas or court orders.</li>
              <li><strong>Professional Advisors:</strong> Consultants, auditors, or legal counsel for business or compliance purposes.</li>
              <li><strong>Business Transfers:</strong> In the event of a merger, sale, or acquisition, your data may be transferred as part of the transaction.</li>
            </ul>
          </div>
        </section>

        <section>
          <h2 class="section-header">Data Security</h2>
          <div class="content-text">
            <p>We prioritize the security of your personal information by implementing industry-standard measures, including:</p>
            <ul>
              <li>Encryption of sensitive data during transmission and storage.</li>
              <li>Secure server infrastructure with access controls.</li>
              <li>Regular security audits and monitoring for vulnerabilities.</li>
            </ul>
            <p>While we strive to protect your information, no system is 100% secure, and we cannot guarantee absolute security.</p>
          </div>
        </section>

        <section>
          <h2 class="section-header">Your Rights</h2>
          <div class="content-text">
            <p>Depending on your jurisdiction (e.g., GDPR, CCPA), you may have the following rights:</p>
            <ul>
              <li><strong>Access:</strong> Request a copy of the personal data we hold about you.</li>
              <li><strong>Correction:</strong> Update or correct inaccuracies in your personal data.</li>
              <li><strong>Deletion:</strong> Request deletion of your data, subject to certain legal obligations.</li>
              <li><strong>Data Portability:</strong> Obtain your data in a portable format.</li>
              <li><strong>Objection:</strong> Object to the processing of your data in certain circumstances.</li>
              <li><strong>Opt-Out:</strong> Under CCPA, opt out of the sale of your personal data (if applicable).</li>
            </ul>
            <p>To exercise your rights, please contact us using the details below.</p>
          </div>
        </section>

        <section>
          <h2 class="section-header">Cookies and Tracking</h2>
          <div class="content-text">
            <p>We use cookies and similar technologies to enhance your experience, including:</p>
            <ul>
              <li>Remembering your preferences and login details.</li>
              <li>Analyzing website traffic and usage patterns.</li>
              <li>Providing personalized content and recommendations.</li>
            </ul>
            <p>You can manage your cookie preferences through your browser settings or read our <router-link to="/cookie-policy" class="link">Cookie Policy</router-link> for more information.</p>
          </div>
        </section>

        <section>
          <h2 class="section-header">Data Retention</h2>
          <div class="content-text">
            <p>We retain your personal information only for as long as necessary to fulfill the purposes outlined in this policy or as required by law. Anonymized or aggregated data may be retained indefinitely for research and analysis purposes.</p>
          </div>
        </section>

        <section>
          <h2 class="section-header">Changes to This Privacy Policy</h2>
          <div class="content-text">
            <p>We may update this Privacy Policy periodically to reflect changes in our practices or legal requirements. The "Last Updated" date at the top of this page indicates the most recent revision. Significant changes will be communicated to you directly where required.</p>
          </div>
        </section>

        <section>
          <h2 class="section-header">Contact Us</h2>
          <div class="content-text">
            <p>If you have any questions, concerns, or requests regarding this Privacy Policy, please <router-link to="/contact" class="link">contact us</router-link>.</p>
          </div>
        </section>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'PrivacyView'
}
</script>

<style scoped>
.privacy {
  flex: 1;
}

/* Hero Section */
.privacy-hero {
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
  .privacy-hero {
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