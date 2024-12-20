<template>
  <div class="contact">
    <!-- Hero Section -->
    <section class="hero contact-hero">
      <div class="hero-content">
        <h1 class="hero-title">Get in Touch</h1>
        <p class="hero-lead">We're here to help you bring your ideas to life</p>
      </div>
    </section>

    <!-- Contact Methods -->
    <section class="content-section">
      <h2 class="section-header">Contact Methods</h2>
      <div class="content-grid">
        <div class="content-card">
          <div class="feature-icon-wrapper">
            <i class="fas fa-envelope"></i>
          </div>
          <h3 class="feature-title">Email Support</h3>
          <p>For general inquiries and support</p>
          <a href="mailto:rileyblackwell5@gmail.com" class="link">rileyblackwell5@gmail.com</a>
        </div>
        <div class="content-card">
          <div class="feature-icon-wrapper">
            <i class="fas fa-phone"></i>
          </div>
          <h3 class="feature-title">Phone Support</h3>
          <p>Available during business hours</p>
          <a href="tel:6168813592" class="link">616-881-3592</a>
        </div>
      </div>
    </section>

    <!-- Contact Form -->
    <section class="content-section">
      <h2 class="section-header">Send Us a Message</h2>
      <div class="text-content">
        <form class="contact-form" @submit.prevent="handleSubmit">
          <div class="form-group">
            <label>
              <i class="fas fa-user"></i>
              Name
            </label>
            <input 
              type="text" 
              class="form-control" 
              id="name" 
              v-model="formData.name"
              required
            >
          </div>
          <div class="form-group">
            <label>
              <i class="fas fa-envelope"></i>
              Email
            </label>
            <input 
              type="email" 
              class="form-control" 
              id="email" 
              v-model="formData.email"
              required
            >
          </div>
          <div class="form-group">
            <label>
              <i class="fas fa-tag"></i>
              Subject
            </label>
            <input 
              type="text" 
              class="form-control" 
              id="subject" 
              v-model="formData.subject"
              required
            >
          </div>
          <div class="form-group">
            <label>
              <i class="fas fa-comment"></i>
              Message
            </label>
            <textarea 
              class="form-control" 
              id="message" 
              rows="5" 
              v-model="formData.message"
              required
            ></textarea>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-success btn-lg">
              <span>Send Message</span>
              <i class="fas fa-paper-plane"></i>
            </button>
          </div>
        </form>
      </div>
    </section>

    <!-- Response Time -->
    <section class="content-section">
      <h2 class="section-header">Response Time</h2>
      <div class="content-grid">
        <div class="content-card">
          <div class="feature-icon-wrapper">
            <i class="fas fa-clock"></i>
          </div>
          <h3 class="feature-title">General Support</h3>
          <p>We typically respond within 24 hours during business days.</p>
        </div>
        <div class="content-card">
          <div class="feature-icon-wrapper">
            <i class="fas fa-exclamation-circle"></i>
          </div>
          <h3 class="feature-title">Urgent Issues</h3>
          <p>For urgent matters, please use our phone support for immediate assistance.</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'ContactView',
  data() {
    return {
      formData: {
        name: '',
        email: '',
        subject: '',
        message: ''
      }
    }
  },
  methods: {
    handleSubmit() {
      // TODO: Implement form submission logic
      console.log('Form submitted:', this.formData)
    }
  }
}
</script>

<style scoped>
.contact {
  flex: 1;
}

/* Hero Section */
.contact-hero {
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

/* Form Styles */
.contact-form {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--global-border-light);
  border-radius: 1rem;
  padding: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--global-text-color);
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.form-group i {
  color: var(--link-hover);
}

.form-control {
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  line-height: 1.5;
  color: var(--global-text-color);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--global-border-light);
  border-radius: 0.5rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-control:focus {
  outline: none;
  border-color: var(--link-hover);
  box-shadow: 0 0 0 2px rgba(0, 255, 204, 0.2);
}

textarea.form-control {
  resize: vertical;
  min-height: 120px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 2rem;
}

/* Content Grid */
.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--global-container-padding);
}

.content-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--global-border-light);
  border-radius: 1rem;
  padding: 2rem;
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.content-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.feature-icon-wrapper {
  width: 4rem;
  height: 4rem;
  margin: 0 auto 1.5rem;
  background: var(--btn-primary-gradient);
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.feature-icon-wrapper i {
  font-size: 1.5rem;
  color: var(--global-text-color);
}

.feature-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--global-text-color);
}

.content-card p {
  color: var(--global-muted-text-color);
  margin: 0;
  line-height: 1.6;
}

.link {
  color: var(--link-hover);
  text-decoration: none;
  transition: color 0.2s ease;
  display: inline-block;
  margin-top: 1rem;
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
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 3rem;
  color: var(--global-text-color);
  text-align: center;
}

/* Mobile styles */
@media screen and (max-width: 768px) {
  .contact-hero {
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
    font-size: 2rem;
    margin-bottom: 2rem;
  }

  .content-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .contact-form {
    padding: 1.5rem;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .form-control {
    font-size: 0.875rem;
  }
}
</style> 