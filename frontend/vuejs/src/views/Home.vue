<template>
  <div class="home">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <h1>Welcome to Imagi</h1>
        <p>Build your web applications with natural language</p>
        <div class="hero-buttons">
          <router-link to="/auth/register" class="btn btn-primary btn-lg">Get Started</router-link>
          <router-link to="/about" class="btn btn-outline btn-lg">Learn More</router-link>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features">
      <div class="container">
        <h2>Why Choose Imagi?</h2>
        <div class="feature-grid">
          <div class="feature-card">
            <div class="feature-icon">
              <i class="fas fa-magic"></i>
            </div>
            <h3>AI-Powered Development</h3>
            <p>Transform your ideas into code using natural language. Let AI handle the technical details.</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <i class="fas fa-bolt"></i>
            </div>
            <h3>Lightning Fast</h3>
            <p>Build and deploy web applications in minutes, not days or weeks.</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <i class="fas fa-code"></i>
            </div>
            <h3>Clean Code</h3>
            <p>Generate high-quality, maintainable code that follows best practices.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works -->
    <section class="how-it-works">
      <div class="container">
        <h2>How It Works</h2>
        <div class="steps">
          <div class="step">
            <div class="step-number">1</div>
            <h3>Describe Your Vision</h3>
            <p>Tell us what you want to build using natural language.</p>
          </div>
          <div class="step">
            <div class="step-number">2</div>
            <h3>AI Generation</h3>
            <p>Our AI transforms your description into working code.</p>
          </div>
          <div class="step">
            <div class="step-number">3</div>
            <h3>Customize & Deploy</h3>
            <p>Fine-tune your application and deploy it to the world.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta">
      <div class="container">
        <h2>Ready to Start Building?</h2>
        <p>Join thousands of developers who are already building with Imagi.</p>
        <router-link to="/auth/register" class="btn btn-primary btn-lg">Create Free Account</router-link>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'HomePage'
}
</script>

<style scoped>
.home {
  background-color: var(--bg-secondary);
}

.hero {
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  color: white;
  padding: 6rem 2rem;
  text-align: center;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.hero h1 {
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  line-height: 1.2;
}

.hero p {
  font-size: 1.5rem;
  opacity: 0.9;
  margin-bottom: 2rem;
}

.hero-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn-lg {
  padding: 0.75rem 2rem;
  font-size: 1.125rem;
}

.btn-outline {
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  color: white;
}

.btn-outline:hover {
  background: rgba(255, 255, 255, 0.2);
}

section {
  padding: 6rem 2rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

section h2 {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 3rem;
  color: var(--text-primary);
}

.features {
  background-color: white;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.feature-card {
  padding: 2rem;
  border-radius: 1rem;
  background-color: var(--bg-secondary);
  text-align: center;
  transition: transform 0.2s;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  width: 4rem;
  height: 4rem;
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
}

.feature-icon i {
  font-size: 1.5rem;
  color: white;
}

.feature-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.feature-card p {
  color: var(--text-secondary);
  line-height: 1.6;
}

.how-it-works {
  background-color: var(--bg-secondary);
}

.steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  text-align: center;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.step-number {
  width: 3rem;
  height: 3rem;
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1.5rem;
}

.step h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.step p {
  color: var(--text-secondary);
}

.cta {
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  color: white;
  text-align: center;
}

.cta h2 {
  color: white;
}

.cta p {
  font-size: 1.25rem;
  opacity: 0.9;
  margin-bottom: 2rem;
}

@media (max-width: 768px) {
  .hero h1 {
    font-size: 2.5rem;
  }

  .hero p {
    font-size: 1.25rem;
  }

  section {
    padding: 4rem 1.5rem;
  }

  section h2 {
    font-size: 2rem;
  }

  .hero-buttons {
    flex-direction: column;
    gap: 1rem;
  }

  .btn-lg {
    width: 100%;
  }
}
</style> 