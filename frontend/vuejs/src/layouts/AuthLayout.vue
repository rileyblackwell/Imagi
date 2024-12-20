<template>
  <MainLayout>
    <div class="auth-layout">
      <router-view />
    </div>
  </MainLayout>
</template>

<script setup>
import MainLayout from './MainLayout.vue'
</script>

<style scoped>
.auth-layout {
  min-height: calc(100vh - var(--header-height) - var(--footer-height));
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-lg);
  background: var(--color-background-alt);
}
</style> 