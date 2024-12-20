<template>
  <div id="app">
    <nav class="header-navbar navbar navbar-expand-lg" v-if="!hideNavbar">
      <div class="global-container">
        <div class="navbar-header">
          <router-link class="header-brand" to="/">
            <div class="header-logo-placeholder"></div>
            <span class="header-brand-highlight">Imagi</span>
          </router-link>
        </div>
        <slot name="navbar-links"></slot>
      </div>
    </nav>

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
    
    const hideNavbar = computed(() => {
      return route.meta.hideNavbar || false
    })
    
    const hideFooter = computed(() => {
      return route.meta.hideFooter || false
    })
    
    return {
      hideNavbar,
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

/* Header styles */
.header-navbar {
  background: var(--global-background-dark);
  backdrop-filter: blur(var(--global-blur-intensity));
  -webkit-backdrop-filter: blur(var(--global-blur-intensity));
  padding: 20px 0;
  border-bottom: 1px solid var(--global-border-light);
  position: relative;
  z-index: 1000;
  transition: background 0.3s ease;
}

.header-navbar:hover {
  background: var(--global-background-dark);
}

.global-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--global-container-padding);
  width: 100%;
  display: flex;
  align-items: center;
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--global-text-color);
  font-weight: 700;
  font-size: 1.5rem;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  text-decoration: none;
  padding-left: 0;
}

.header-brand:hover {
  text-decoration: none;
  color: var(--global-text-color);
}

.header-logo-placeholder {
  width: 30px;
  height: 30px;
  position: relative;
  display: inline-block;
  transform: rotate(45deg);
  border-radius: 50% / 30%;
  overflow: hidden;
}

.header-logo-placeholder::before,
.header-logo-placeholder::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border: 2px solid white;
  border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;
  box-shadow: 0 0 15px rgba(0, 162, 255, 0.5);
}

.header-logo-placeholder::before {
  transform: rotate(45deg);
}

.header-logo-placeholder::after {
  transform: rotate(-45deg);
}

.header-brand-highlight {
  background: var(--global-highlight-gradient);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 1.8rem;
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
  .header-navbar {
    padding: 15px 0;
  }

  .header-navbar .navbar-container {
    padding: 0 15px;
  }

  .site-footer-content {
    gap: 12px;
  }

  .site-footer-copyright {
    font-size: 0.8rem;
  }

  .header-brand {
    font-size: 1.3rem;
  }

  .header-logo-placeholder {
    width: 25px;
    height: 25px;
  }

  .header-brand-highlight {
    font-size: 1.5rem;
  }
}
</style>
