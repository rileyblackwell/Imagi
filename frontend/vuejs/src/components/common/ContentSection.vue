<template>
  <section class="content-section">
    <div class="text-content">
      <section v-if="title || $slots.header" class="section-header-wrapper">
        <h2 v-if="title" class="section-header">{{ title }}</h2>
        <slot name="header"></slot>
      </section>
      
      <div :class="['content-text', { 'content-grid': isGrid }]">
        <slot></slot>
      </div>

      <slot name="footer"></slot>
    </div>
  </section>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: ''
  },
  isGrid: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.content-section {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: var(--spacing-2xl) var(--spacing-md);
}

.text-content section {
  margin-bottom: var(--spacing-2xl);
}

.section-header {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-lg);
  color: var(--color-text);
}

.content-text {
  color: var(--color-text);
  line-height: 1.6;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-xl);
  margin-bottom: var(--spacing-xl);
}

:deep(.content-text p) {
  margin-bottom: var(--spacing-md);
}

:deep(.content-text ul) {
  list-style-type: disc;
  margin-left: var(--spacing-xl);
  margin-bottom: var(--spacing-md);
}

:deep(.content-text li) {
  margin-bottom: var(--spacing-sm);
}

:deep(.content-text strong) {
  font-weight: var(--font-weight-bold);
}

:deep(.link) {
  color: var(--color-primary);
  text-decoration: none;
  transition: color 0.2s;
}

:deep(.link:hover) {
  color: var(--color-primary-dark);
  text-decoration: underline;
}

@media (max-width: 768px) {
  .content-section {
    padding: var(--spacing-xl) var(--spacing-md);
  }

  .section-header {
    font-size: var(--font-size-lg);
  }

  .content-grid {
    grid-template-columns: 1fr;
  }
}
</style> 