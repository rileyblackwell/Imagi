<script setup>
const features = [
  {
    icon: 'comments',
    title: 'Natural Language Interface',
    description: 'Describe your web app in plain English. Our AI understands context, requirements, and user experience needs.'
  },
  {
    icon: 'layer-group',
    title: 'Full-Stack Generation',
    description: 'From beautiful UIs to robust backends, we generate complete, production-ready applications.'
  },
  {
    icon: 'wand-magic-sparkles',
    title: 'Real-time Preview',
    description: 'See your app come to life instantly. Make adjustments and watch them update in real-time.'
  }
]
</script>

<template>
  <section class="feature-section">
    <div class="container">
      <h2 class="section-title">Why Choose Imagi</h2>
      <p class="section-subtitle">
        The intelligent platform that understands your vision
      </p>
      
      <div class="feature-grid">
        <div 
          v-for="feature in features" 
          :key="feature.title"
          class="feature-card"
        >
          <div class="feature-icon">
            <i :class="'fas fa-' + feature.icon"></i>
          </div>
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-description">{{ feature.description }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.feature-section {
  @apply py-24 bg-gray-900/50;
}

.container {
  @apply max-w-7xl mx-auto px-4;
}

.section-title {
  @apply text-4xl font-bold text-center mb-4;
  background: linear-gradient(135deg, #22d3ee 0%, #3b82f6 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.section-subtitle {
  @apply text-xl text-gray-300 text-center mb-16;
}

.feature-grid {
  @apply grid md:grid-cols-3 gap-8;
}

.feature-card {
  @apply p-8 rounded-xl bg-gray-800/50 border border-gray-700/50 
         hover:border-cyan-500/50 transition-all transform hover:scale-105;
}

.feature-icon {
  @apply w-12 h-12 flex items-center justify-center text-2xl text-cyan-400 mb-6 
         bg-gray-800 rounded-lg;
}

.feature-title {
  @apply text-xl font-bold mb-4 text-white;
}

.feature-description {
  @apply text-gray-300 leading-relaxed;
}
</style> 