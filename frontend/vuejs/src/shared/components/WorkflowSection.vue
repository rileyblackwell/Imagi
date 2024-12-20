<script setup>
const steps = [
  {
    number: 1,
    title: 'Describe Your Vision',
    description: 'Tell us about your web app in natural language. Include features, design preferences, and functionality.'
  },
  {
    number: 2,
    title: 'AI Generation',
    description: 'Our AI analyzes your description and generates all necessary code, from frontend to backend.'
  },
  {
    number: 3,
    title: 'Launch & Iterate',
    description: 'Preview your app, make adjustments, and deploy when ready. Continuous updates are just a description away.'
  }
]
</script>

<template>
  <section class="workflow-section">
    <div class="container">
      <h2 class="section-title">How It Works</h2>
      <p class="section-subtitle">
        Three simple steps to transform your idea into reality
      </p>

      <div class="workflow-grid">
        <div 
          v-for="step in steps" 
          :key="step.number"
          class="workflow-card"
        >
          <div class="step-number">{{ step.number }}</div>
          <h3 class="step-title">{{ step.title }}</h3>
          <p class="step-description">{{ step.description }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.workflow-section {
  @apply py-24 bg-gradient-to-b from-gray-900 to-gray-800;
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

.workflow-grid {
  @apply grid md:grid-cols-3 gap-12;
}

.workflow-card {
  @apply text-center relative;
}

.step-number {
  @apply w-12 h-12 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 
         flex items-center justify-center text-xl font-bold text-white mx-auto mb-6;
}

.step-title {
  @apply text-xl font-bold mb-4 text-white;
}

.step-description {
  @apply text-gray-300 leading-relaxed;
}
</style> 