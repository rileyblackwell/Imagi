<template>
  <div class="about">
    <!-- Hero Section -->
    <section class="hero about-hero">
      <div class="hero-content">
        <h1 class="hero-title">About Imagi</h1>
        <p class="hero-lead">Transforming natural language into powerful web applications</p>
      </div>
    </section>

    <!-- Mission Section -->
    <section class="content-section">
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
    </section>

    <!-- Story Section -->
    <section class="content-section">
      <h2 class="section-header">Our Story</h2>
      <div class="text-content">
        <p>Founded in 2024, Imagi was born from a simple observation: while the world is full of innovative ideas, many remain unrealized due to the technical complexity of web development.</p>
        <p>This insight led to the creation of Imagi's natural language processing platform, which transforms plain English descriptions into functional code.</p>
      </div>
    </section>

    <!-- Technology Section -->
    <section class="content-section">
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
    </section>

    <!-- Vision Section -->
    <section class="content-section">
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
    </section>
  </div>
</template>

<script>
export default {
  name: 'AboutView'
}
</script>

<style scoped>
.about {
  flex: 1;
}

/* Hero Section */
.about-hero {
  min-height: 60vh;
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
  text-align: center;
}

.text-content p {
  color: var(--global-muted-text-color);
  font-size: 1.125rem;
  line-height: 1.8;
  margin-bottom: 1.5rem;
}

.text-content p:last-child {
  margin-bottom: 0;
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
  text-align: center;
}

.section-header {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 3rem;
  color: var(--global-text-color);
}

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

/* Mobile styles */
@media screen and (max-width: 768px) {
  .about-hero {
    min-height: 40vh;
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
  }

  .content-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .text-content {
    text-align: left;
  }

  .text-content p {
    font-size: 1rem;
  }
}
</style> 