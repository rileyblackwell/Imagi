<template>
  <div class="contact-page">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-container">
        <h1 class="hero-title">Contact Us</h1>
        <p class="hero-description">
          We're here to help with any questions or concerns
        </p>
      </div>
    </section>

    <!-- Content Section -->
    <section class="content-section">
      <div class="section-container">
        <div class="contact-grid">
          <!-- Contact Information -->
          <div class="contact-info">
            <div class="info-card">
              <div class="info-icon">
                <i class="fas fa-envelope"></i>
              </div>
              <h3>Email Us</h3>
              <p>We'll respond within 24 hours</p>
              <a href="mailto:support@imagi.ai" class="info-link">support@imagi.ai</a>
            </div>

            <div class="info-card">
              <div class="info-icon">
                <i class="fas fa-comments"></i>
              </div>
              <h3>Live Chat</h3>
              <p>Available Monday to Friday</p>
              <p>9:00 AM - 6:00 PM EST</p>
            </div>

            <div class="info-card">
              <div class="info-icon">
                <i class="fas fa-book"></i>
              </div>
              <h3>Documentation</h3>
              <p>Find answers in our docs</p>
              <router-link to="/docs" class="info-link">View Documentation</router-link>
            </div>
          </div>

          <!-- Contact Form -->
          <div class="contact-form-wrapper">
            <form class="contact-form" @submit.prevent="handleSubmit">
              <div class="form-group">
                <label for="name">Name</label>
                <input
                  type="text"
                  id="name"
                  v-model="form.name"
                  required
                  placeholder="Your name"
                  class="form-input"
                />
              </div>

              <div class="form-group">
                <label for="email">Email</label>
                <input
                  type="email"
                  id="email"
                  v-model="form.email"
                  required
                  placeholder="your@email.com"
                  class="form-input"
                />
              </div>

              <div class="form-group">
                <label for="subject">Subject</label>
                <select id="subject" v-model="form.subject" required class="form-input">
                  <option value="">Select a subject</option>
                  <option value="general">General Inquiry</option>
                  <option value="support">Technical Support</option>
                  <option value="billing">Billing Question</option>
                  <option value="feature">Feature Request</option>
                </select>
              </div>

              <div class="form-group">
                <label for="message">Message</label>
                <textarea
                  id="message"
                  v-model="form.message"
                  required
                  placeholder="How can we help you?"
                  class="form-input"
                  rows="5"
                ></textarea>
              </div>

              <button type="submit" class="btn btn-primary btn-block">
                Send Message
                <i class="fas fa-paper-plane"></i>
              </button>
            </form>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const form = ref({
  name: '',
  email: '',
  subject: '',
  message: ''
})

const handleSubmit = async () => {
  try {
    // TODO: Implement form submission
    console.log('Form submitted:', form.value)
  } catch (error) {
    console.error('Error submitting form:', error)
  }
}
</script>

<style scoped>
.contact-page {
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

/* Contact Grid */
.contact-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 3rem;
}

/* Contact Information */
.contact-info {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.info-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
}

.info-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.info-icon {
  width: 48px;
  height: 48px;
  background: var(--primary-gradient);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
}

.info-icon i {
  font-size: 1.5rem;
  color: white;
}

.info-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.info-card p {
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.info-link {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s;
}

.info-link:hover {
  color: var(--primary-hover);
}

/* Contact Form */
.contact-form-wrapper {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 24px;
  padding: 3rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 1rem;
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

textarea.form-input {
  resize: vertical;
  min-height: 120px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
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

.btn-block {
  width: 100%;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Responsive Design */
@media (max-width: 1024px) {
  .contact-grid {
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .contact-info {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .info-card {
    flex: 1 1 calc(33.333% - 1.5rem);
    min-width: 250px;
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }

  .hero-description {
    font-size: 1.125rem;
  }

  .contact-form-wrapper {
    padding: 2rem;
  }

  .info-card {
    flex: 1 1 100%;
  }
}
</style> 