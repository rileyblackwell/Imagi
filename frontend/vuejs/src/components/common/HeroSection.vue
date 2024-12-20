<template>
  <section :class="['hero-section', heroClass]">
    <div class="hero-container">
      <div class="hero-content">
        <h1 class="hero-title">{{ title }}</h1>
        <p class="hero-description">{{ description }}</p>
        <slot></slot>
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  heroClass: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.hero-section {
  background-color: var(--color-background-alt);
  padding: var(--spacing-2xl) 0;
  text-align: center;
}

.hero-container {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 0 var(--spacing-md);
}

.hero-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-md);
  color: var(--color-text);
}

.hero-description {
  font-size: var(--font-size-lg);
  color: var(--color-text-muted);
  margin-bottom: var(--spacing-lg);
}

@media (max-width: 768px) {
  .hero-section {
    padding: var(--spacing-xl) 0;
  }

  .hero-title {
    font-size: var(--font-size-2xl);
  }

  .hero-description {
    font-size: var(--font-size-md);
  }
}
</style> 