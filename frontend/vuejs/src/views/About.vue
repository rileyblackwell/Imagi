<template>
  <div class="about-page">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-container">
        <h1 class="hero-title">About Imagi</h1>
        <p class="hero-description">
          Transforming natural language into powerful web applications
        </p>
      </div>
    </section>

    <!-- Mission Section -->
    <section class="content-section">
      <div class="section-container">
        <h2 class="section-header">Our Mission</h2>
        <div class="content-grid">
          <div class="content-card">
            <div class="feature-icon-wrapper">
              <i class="fas fa-bullseye"></i>
            </div>
            <h3 class="feature-title">Democratizing Web Development</h3>
            <p>Our mission is to make web development accessible to everyone by transforming natural language into professional code.</p>
          </div>
          <div class="content-card">
            <div class="feature-icon-wrapper">
              <i class="fas fa-star"></i>
            </div>
            <h3 class="feature-title">AI-Powered Innovation</h3>
            <p>By combining cutting-edge AI with intuitive design, we're revolutionizing how websites and applications are built.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Story Section -->
    <section class="content-section bg-alt">
      <div class="section-container">
        <h2 class="section-header">Our Story</h2>
        <div class="text-content">
          <p>Founded in 2024, Imagi was born from a simple observation: while the world is full of innovative ideas, many remain unrealized due to the technical complexity of web development.</p>
          <p>This insight led to the creation of Imagi's natural language processing platform, which transforms plain English descriptions into functional code.</p>
        </div>
      </div>
    </section>

    <!-- Technology Section -->
    <section class="content-section">
      <div class="section-container">
        <h2 class="section-header">Our Technology</h2>
        <div class="content-grid">
          <div class="content-card">
            <div class="feature-icon-wrapper">
              <i class="fas fa-robot"></i>
            </div>
            <h3 class="feature-title">AI Understanding</h3>
            <p>Advanced natural language processing to understand context, requirements, and user intent.</p>
          </div>
          <div class="content-card">
            <div class="feature-icon-wrapper">
              <i class="fas fa-code-branch"></i>
            </div>
            <h3 class="feature-title">Clean Code</h3>
            <p>Generate maintainable code following industry best practices.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Vision Section -->
    <section class="content-section bg-alt">
      <div class="section-container">
        <h2 class="section-header">Our Vision</h2>
        <div class="content-grid">
          <div class="content-card">
            <div class="feature-icon-wrapper">
              <i class="fas fa-rocket"></i>
            </div>
            <h3 class="feature-title">Future of Development</h3>
            <p>We envision a future where creating web applications is as simple as describing your idea.</p>
          </div>
          <div class="content-card">
            <div class="feature-icon-wrapper">
              <i class="fas fa-users"></i>
            </div>
            <h3 class="feature-title">Community Impact</h3>
            <p>Empowering entrepreneurs, businesses, and creators to bring their digital ideas to life.</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.about-page {
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

/* Content Sections */
.content-section {
  padding: 80px 0;
}

.bg-alt {
  background: var(--bg-secondary);
}

.section-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.section-header {
  font-size: 2.5rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 3rem;
  color: var(--text-primary);
}

/* Grid Layout */
.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

/* Cards */
.content-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 2rem;
  transition: all 0.3s ease;
}

.content-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.feature-icon-wrapper {
  width: 48px;
  height: 48px;
  background: var(--primary-gradient);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.feature-icon-wrapper i {
  font-size: 1.5rem;
  color: white;
}

.feature-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

/* Text Content */
.text-content {
  max-width: 800px;
  margin: 0 auto;
  font-size: 1.125rem;
  line-height: 1.7;
  color: var(--text-secondary);
}

.text-content p + p {
  margin-top: 1.5rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }

  .hero-description {
    font-size: 1.125rem;
  }

  .section-header {
    font-size: 2rem;
  }

  .content-section {
    padding: 60px 0;
  }

  .content-card {
    padding: 1.5rem;
  }
}
</style> 