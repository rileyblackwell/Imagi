<template>
  <div class="auth-layout">
    <nav class="auth-nav">
      <router-link to="/" class="logo">
        <img src="@/assets/images/logo.svg" alt="Imagi Logo" />
      </router-link>
    </nav>

    <main class="auth-content">
      <div class="auth-container">
        <div class="auth-card">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>

        <div class="auth-footer">
          <p class="text-center text-secondary">
            &copy; {{ currentYear }} Imagi. All rights reserved.
          </p>
          <div class="auth-links">
            <router-link to="/privacy" class="text-secondary">Privacy Policy</router-link>
            <span class="separator">•</span>
            <router-link to="/terms" class="text-secondary">Terms of Service</router-link>
          </div>
        </div>
      </div>
    </main>

    <!-- Background decoration -->
    <div class="auth-background">
      <div class="gradient-circle gradient-circle-1"></div>
      <div class="gradient-circle gradient-circle-2"></div>
      <div class="gradient-circle gradient-circle-3"></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const currentYear = computed(() => new Date().getFullYear());
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  background-color: var(--bg-secondary);
}

.auth-nav {
  padding: var(--spacing-4) var(--spacing-6);
  background-color: var(--bg-primary);
  box-shadow: var(--shadow-sm);
  position: relative;
  z-index: var(--z-sticky);
}

.logo {
  display: inline-block;
}

.logo img {
  height: 32px;
  width: auto;
}

.auth-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-8) var(--spacing-4);
  position: relative;
  z-index: var(--z-elevate);
}

.auth-container {
  width: 100%;
  max-width: 480px;
  margin: 0 auto;
}

.auth-card {
  background-color: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lg);
  padding: var(--spacing-8);
  margin-bottom: var(--spacing-8);
}

.auth-footer {
  text-align: center;
}

.auth-links {
  margin-top: var(--spacing-2);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-3);
}

.separator {
  color: var(--text-tertiary);
}

/* Background decoration */
.auth-background {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: var(--z-negative);
}

.gradient-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
}

.gradient-circle-1 {
  top: -200px;
  left: -200px;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0) 70%);
}

.gradient-circle-2 {
  top: 40%;
  right: -200px;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(79, 70, 229, 0.15) 0%, rgba(79, 70, 229, 0) 70%);
}

.gradient-circle-3 {
  bottom: -150px;
  left: 30%;
  width: 250px;
  height: 250px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.1) 0%, rgba(99, 102, 241, 0) 70%);
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 640px) {
  .auth-card {
    padding: var(--spacing-6);
  }

  .auth-content {
    padding: var(--spacing-4);
  }
}
</style> 