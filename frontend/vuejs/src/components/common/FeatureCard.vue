<template>
  <div class="content-card">
    <div v-if="icon" class="feature-icon-wrapper">
      <i :class="['fas', icon]"></i>
    </div>
    <slot name="icon"></slot>
    
    <h3 class="feature-title">{{ title }}</h3>
    <p class="feature-description"><slot></slot></p>
    
    <slot name="footer"></slot>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.content-card {
  background-color: var(--color-background);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-md);
  transition: transform 0.2s, box-shadow 0.2s;
}

.content-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.feature-icon-wrapper {
  width: 48px;
  height: 48px;
  background-color: var(--color-primary-light);
  border-radius: var(--border-radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--spacing-md);
}

.feature-icon-wrapper i {
  font-size: var(--font-size-xl);
  color: var(--color-primary);
}

.feature-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-sm);
  color: var(--color-text);
}

.feature-description {
  color: var(--color-text-muted);
  line-height: 1.6;
}

@media (max-width: 768px) {
  .content-card {
    padding: var(--spacing-lg);
  }

  .feature-icon-wrapper {
    width: 40px;
    height: 40px;
  }

  .feature-icon-wrapper i {
    font-size: var(--font-size-lg);
  }
}
</style> 