<template>
  <section class="cta-section">
    <div class="container">
      <h2 class="cta-title">Ready to Build Your Web App?</h2>
      <p class="cta-description">
        Join the future of web development. Start building your application today with Imagi's AI-powered platform.
      </p>
      <div class="cta-buttons">
        <router-link to="/builder" class="cta-button primary">
          Start Building Now
          <i class="fas fa-wand-magic-sparkles"></i>
        </router-link>
        <router-link to="/auth/register" class="cta-button secondary">
          Create Account
          <i class="fas fa-arrow-right"></i>
        </router-link>
      </div>
    </div>
  </section>
</template>

<style scoped>
.cta-section {
  @apply py-24 bg-gradient-to-b from-gray-800 to-gray-900;
}

.container {
  @apply max-w-7xl mx-auto px-4 text-center;
}

.cta-title {
  @apply text-4xl font-bold mb-6;
  background: linear-gradient(135deg, #22d3ee 0%, #3b82f6 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.cta-description {
  @apply text-xl text-gray-300 mb-12 max-w-2xl mx-auto;
}

.cta-buttons {
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
</style> 