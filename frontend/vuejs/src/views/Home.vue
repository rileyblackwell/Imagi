<template>
  <div class="home">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-container">
        <h1 class="hero-title">Transform Your Ideas Into Web Applications</h1>
        <p class="hero-description">
          Create powerful, professional web applications using natural language with Imagi's AI technology
        </p>
        <div class="cta-container">
          <router-link 
            :to="isAuthenticated ? '/builder' : '/auth/login'" 
            class="btn btn-success btn-lg"
          >
            <span>Start Building</span>
            <i class="fas fa-arrow-right"></i>
          </router-link>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="content-section">
      <h2 class="section-header">Why Choose Imagi</h2>
      <p class="section-description">
        Transform your ideas into reality with powerful AI-driven web development
      </p>
      
      <div class="content-grid">
        <div class="content-card">
          <div class="feature-icon-wrapper">
            <i class="fas fa-keyboard"></i>
          </div>
          <h3 class="feature-title">Natural Language Input</h3>
          <p>Describe your vision in plain English, and watch as it transforms into reality.</p>
        </div>

        <div class="content-card">
          <div class="feature-icon-wrapper">
            <i class="fas fa-bolt"></i>
          </div>
          <h3 class="feature-title">Rapid Development</h3>
          <p>Build websites and applications in minutes, not months.</p>
        </div>

        <div class="content-card">
          <div class="feature-icon-wrapper">
            <i class="fas fa-code"></i>
          </div>
          <h3 class="feature-title">Professional Code</h3>
          <p>Generate clean, maintainable code that follows industry best practices.</p>
        </div>
      </div>
    </section>

    <!-- How It Works -->
    <section class="content-section">
      <h2 class="section-header">How It Works</h2>
      <div class="content-grid">
        <div class="content-card">
          <div class="feature-icon-wrapper">
            <i class="fas fa-pencil-alt"></i>
          </div>
          <h3 class="card-header">1. Describe Your Vision</h3>
          <p>Tell us what you want to build using natural language. Describe your features, design preferences, and requirements.</p>
        </div>
        <div class="content-card">
          <div class="feature-icon-wrapper">
            <i class="fas fa-magic"></i>
          </div>
          <h3 class="card-header">2. AI Generation</h3>
          <p>Our advanced AI analyzes your description and generates all necessary code, from frontend interfaces to backend logic.</p>
        </div>
        <div class="content-card">
          <div class="feature-icon-wrapper">
            <i class="fas fa-sliders-h"></i>
          </div>
          <h3 class="card-header">3. Customize & Refine</h3>
          <p>Review the generated application, make adjustments, and refine details using natural language commands.</p>
        </div>
        <div class="content-card">
          <div class="feature-icon-wrapper">
            <i class="fas fa-rocket"></i>
          </div>
          <h3 class="card-header">4. Launch & Scale</h3>
          <p>Deploy your application with confidence, knowing it's built with scalable, secure, and maintainable code.</p>
        </div>
      </div>
    </section>

    <!-- Use Cases -->
    <section class="content-section">
      <h2 class="section-header">What You Can Build</h2>
      <div class="content-grid">
        <div class="content-card">
          <div class="feature-icon-wrapper">
            <i class="fas fa-store"></i>
          </div>
          <h3 class="card-header">E-commerce Sites</h3>
          <p>Create full-featured online stores with product catalogs, shopping carts, and secure payment processing.</p>
        </div>
        <div class="content-card">
          <div class="feature-icon-wrapper">
            <i class="fas fa-briefcase"></i>
          </div>
          <h3 class="card-header">Business Applications</h3>
          <p>Build custom CRM systems, inventory management tools, and other business-specific applications.</p>
        </div>
        <div class="content-card">
          <div class="feature-icon-wrapper">
            <i class="fas fa-users"></i>
          </div>
          <h3 class="card-header">Community Platforms</h3>
          <p>Develop social networks, forums, and community-driven websites with user management and content sharing.</p>
        </div>
        <div class="content-card">
          <div class="feature-icon-wrapper">
            <i class="fas fa-chart-line"></i>
          </div>
          <h3 class="card-header">Analytics Dashboards</h3>
          <p>Create data visualization tools and interactive dashboards for business intelligence and reporting.</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useAuth } from '@/composables/useAuth'

const { isAuthenticated } = useAuth()
</script>

<style scoped>
/* Root Variables */
:root {
  --primary-gradient: linear-gradient(135deg, #00ffcc, #00a2ff);
  --text-primary: #ffffff;
  --text-secondary: rgba(255, 255, 255, 0.8);
  --text-muted: rgba(255, 255, 255, 0.6);
  --bg-card: rgba(255, 255, 255, 0.03);
  --border-color: rgba(255, 255, 255, 0.1);
  --shadow-color: rgba(0, 0, 0, 0.2);
  --hover-bg: rgba(255, 255, 255, 0.05);
}

/* Remove top padding since we're inside main-content */
.home {
  margin-top: calc(-1 * var(--spacing-8));
}

/* Hero Section - Inspired by Stripe */
.hero-section {
  padding: 120px 0;
  position: relative;
  overflow: hidden;
  background: radial-gradient(
    circle at top right,
    rgba(0, 255, 204, 0.15),
    transparent 50%
  );
}

.hero-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  position: relative;
  z-index: 1;
}

.hero-title {
  font-size: 4rem;
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.03em;
  margin-bottom: 1.5rem;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  text-align: center;
}

.hero-description {
  font-size: 1.25rem;
  color: var(--text-secondary);
  max-width: 600px;
  margin: 0 auto 2rem;
  line-height: 1.6;
  text-align: center;
}

/* Content Sections - Inspired by Airbnb */
.content-section {
  padding: 100px 0;
  position: relative;
}

.section-header {
  font-size: 3rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin-bottom: 1rem;
  text-align: center;
}

.section-description {
  font-size: 1.2rem;
  color: var(--text-secondary);
  max-width: 700px;
  margin: 0 auto 4rem;
  text-align: center;
  line-height: 1.6;
}

/* Grid Layout - Inspired by Meta */
.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
}

/* Cards - Inspired by Google */
.content-card {
  background: var(--bg-card);
  border-radius: 24px;
  padding: 2.5rem;
  border: 1px solid var(--border-color);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.content-card:hover {
  transform: translateY(-5px);
  border-color: rgba(0, 255, 204, 0.2);
  box-shadow: 
    0 20px 40px var(--shadow-color),
    0 0 0 1px rgba(0, 255, 204, 0.1);
}

/* Feature Icons - Inspired by Twilio */
.feature-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg,
    rgba(0, 255, 204, 0.1),
    rgba(0, 162, 255, 0.1)
  );
  margin-bottom: 1.5rem;
  position: relative;
}

.feature-icon-wrapper::after {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: inherit;
  padding: 1px;
  background: var(--primary-gradient);
  mask: linear-gradient(#fff 0 0) content-box, 
        linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
}

.feature-icon-wrapper i {
  font-size: 1.5rem;
  color: #00ffcc;
}

/* Feature Titles */
.feature-title,
.card-header {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 1.5rem 0 1rem;
  color: var(--text-primary);
  line-height: 1.3;
}

/* CTA Container */
.cta-container {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-lg {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  font-size: 1.125rem;
  font-weight: 600;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.btn-success {
  background: var(--primary-gradient);
  color: white;
  border: none;
  text-decoration: none;
}

.btn-success:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 255, 204, 0.2);
}

/* Responsive Design */
@media (max-width: 1200px) {
  .hero-title {
    font-size: 3.5rem;
  }
  
  .section-header {
    font-size: 2.5rem;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 80px 0;
  }

  .hero-title {
    font-size: 2.75rem;
  }

  .hero-description {
    font-size: 1.1rem;
  }

  .section-header {
    font-size: 2rem;
  }

  .content-card {
    padding: 2rem;
  }
}
</style> 