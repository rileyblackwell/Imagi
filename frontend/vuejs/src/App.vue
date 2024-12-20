<template>
  <div id="app">
    <router-view></router-view>

    <footer class="site-footer" v-if="!hideFooter">
      <div class="site-footer-content">
        <div class="footer-brand">
          <span class="footer-brand-text">Imagi</span>
        </div>
        <div class="site-footer-links">
          <router-link to="/about" class="link link-muted">About</router-link>
          <span class="site-footer-divider">•</span>
          <router-link to="/privacy" class="link link-muted">Privacy</router-link>
          <span class="site-footer-divider">•</span>
          <router-link to="/terms" class="link link-muted">Terms</router-link>
        </div>
        <p class="site-footer-copyright">
          &copy; {{ new Date().getFullYear() }} Imagi. All rights reserved.
        </p>
      </div>
    </footer>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

export default {
  name: 'App',
  setup() {
    const route = useRoute()
    
    const hideFooter = computed(() => {
      return route.meta.hideFooter || false
    })
    
    return {
      hideFooter
    }
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css?family=Poppins:400,700');
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css');

:root {
  --global-font-family: 'Poppins', sans-serif;
  --global-text-color: #ffffff;
  --global-muted-text-color: rgba(255, 255, 255, 0.8);
  --global-background-dark: rgba(13, 12, 34, 0.8);
  --global-border-light: rgba(255, 255, 255, 0.1);
  --global-footer-gradient: linear-gradient(to right, rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.6));
  --global-line-height: 1.6;
  --global-container-padding: 25px;
  --global-highlight-gradient: linear-gradient(45deg, #6366f1, #00ffc6);
  --global-button-shadow: rgba(0, 162, 255, 0.3);
  --global-button-shadow-hover: rgba(0, 162, 255, 0.4);
  --global-blur-intensity: 15px;
}

body {
  font-family: var(--global-font-family);
  line-height: var(--global-line-height);
  margin: 0;
  padding: 0;
  color: var(--global-text-color);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--global-background-dark);
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Footer styles */
.site-footer {
  flex-shrink: 0;
  width: 100%;
  background: var(--global-footer-gradient);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 25px 0;
  text-align: center;
  margin-top: auto;
  border-top: 1px solid var(--global-border-light);
}

.site-footer-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 var(--global-container-padding);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.site-footer-links {
  display: flex;
  align-items: center;
  gap: 15px;
}

.site-footer-divider {
  color: var(--global-muted-text-color);
  font-size: 0.8rem;
}

.site-footer-copyright {
  color: var(--global-muted-text-color);
  font-size: 0.85rem;
  font-weight: 400;
  margin: 0;
  text-align: center;
}

/* Mobile styles */
@media screen and (max-width: 991px) {
  .site-footer-content {
    gap: 12px;
  }

  .site-footer-copyright {
    font-size: 0.8rem;
  }
}
</style>
