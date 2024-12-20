<template>
  <section class="hero-section">
    <div class="hero-container">
      <div class="hero-logo">
        <img src="@/assets/images/logo.webp" alt="Imagi" class="logo-image" />
      </div>
      <h1 class="hero-title">
        Transform Ideas into Web Apps
        <span class="hero-subtitle">Using Natural Language</span>
      </h1>
      <p class="hero-description">
        Experience the future of web development with Imagi. Simply describe your vision,
        and our AI transforms it into a fully functional web application. No coding required.
      </p>
      <div class="cta-container">
        <router-link to="/builder" class="cta-button primary">
          Start Building
          <i class="fas fa-wand-magic-sparkles"></i>
        </router-link>
        <router-link to="/about" class="cta-button secondary">
          Learn More
          <i class="fas fa-arrow-right"></i>
        </router-link>
      </div>
    </div>
    <div class="hero-background">
      <div class="gradient-sphere"></div>
    </div>
  </section>
</template>

<style scoped>
.hero-section {
  @apply relative min-h-[90vh] flex items-center justify-center overflow-hidden;
  background: linear-gradient(180deg, rgba(18,18,18,0.95) 0%, rgba(26,26,26,0.95) 100%);
}

.hero-container {
  @apply max-w-7xl mx-auto px-4 py-24 text-center relative z-10;
}

.hero-logo {
  @apply mb-12 animate-float;
}

.logo-image {
  @apply h-32 mx-auto filter drop-shadow-glow;
}

.hero-title {
  @apply text-6xl font-bold mb-4;
  background: linear-gradient(135deg, #22d3ee 0%, #3b82f6 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-subtitle {
  @apply block text-4xl mt-2 opacity-90;
}

.hero-description {
  @apply text-xl text-gray-300 mb-12 max-w-2xl mx-auto leading-relaxed;
}

.cta-container {
  @apply flex flex-col sm:flex-row gap-6 justify-center items-center;
}

.cta-button {
  @apply px-8 py-3 rounded-lg font-semibold flex items-center gap-2 transition-all transform hover:scale-105;
}

.cta-button.primary {
  @apply bg-gradient-to-r from-cyan-500 to-blue-500 text-white 
         hover:from-cyan-600 hover:to-blue-600 shadow-lg hover:shadow-cyan-500/25;
}

.cta-button.secondary {
  @apply border border-gray-700 text-gray-300 hover:bg-gray-800/50;
}

.hero-background {
  @apply absolute inset-0 overflow-hidden;
}

.gradient-sphere {
  @apply absolute w-[800px] h-[800px] rounded-full opacity-30 blur-3xl;
  background: radial-gradient(circle, rgba(34,211,238,0.15) 0%, rgba(59,130,246,0.15) 100%);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
    filter: drop-shadow(0 0 20px rgba(34,211,238,0.35));
  }
  50% {
    transform: translateY(-10px);
    filter: drop-shadow(0 0 30px rgba(34,211,238,0.45));
  }
}

.animate-float {
  animation: float 3s ease-in-out infinite;
}
</style> 