<template>
  <footer class="app-footer">
    <div class="container">
      <div class="footer-content">
        <!-- Brand -->
        <div class="footer-brand">
          <router-link to="/" class="logo">
            <img src="@/assets/images/logo-full.svg" alt="Imagi Logo" class="logo-full" />
          </router-link>
          <p class="brand-description">
            Transform your ideas into reality with AI-powered web development.
          </p>
          <div class="social-links">
            <a href="https://twitter.com/imagi" target="_blank" rel="noopener" class="social-link">
              <i class="fab fa-twitter"></i>
            </a>
            <a href="https://github.com/imagi" target="_blank" rel="noopener" class="social-link">
              <i class="fab fa-github"></i>
            </a>
            <a href="https://discord.gg/imagi" target="_blank" rel="noopener" class="social-link">
              <i class="fab fa-discord"></i>
            </a>
          </div>
        </div>

        <!-- Navigation -->
        <div class="footer-navigation">
          <div class="footer-section">
            <h3 class="section-title">Product</h3>
            <ul class="section-links">
              <li><router-link to="/features">Features</router-link></li>
              <li><router-link to="/pricing">Pricing</router-link></li>
              <li><router-link to="/docs">Documentation</router-link></li>
              <li><router-link to="/changelog">Changelog</router-link></li>
            </ul>
          </div>

          <div class="footer-section">
            <h3 class="section-title">Company</h3>
            <ul class="section-links">
              <li><router-link to="/about">About</router-link></li>
              <li><router-link to="/blog">Blog</router-link></li>
              <li><router-link to="/careers">Careers</router-link></li>
              <li><router-link to="/contact">Contact</router-link></li>
            </ul>
          </div>

          <div class="footer-section">
            <h3 class="section-title">Resources</h3>
            <ul class="section-links">
              <li><router-link to="/templates">Templates</router-link></li>
              <li><router-link to="/examples">Examples</router-link></li>
              <li><router-link to="/community">Community</router-link></li>
              <li><router-link to="/support">Support</router-link></li>
            </ul>
          </div>

          <div class="footer-section">
            <h3 class="section-title">Legal</h3>
            <ul class="section-links">
              <li><router-link to="/privacy">Privacy Policy</router-link></li>
              <li><router-link to="/terms">Terms of Service</router-link></li>
              <li><router-link to="/security">Security</router-link></li>
              <li><router-link to="/cookies">Cookie Policy</router-link></li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Bottom bar -->
      <div class="footer-bottom">
        <p class="copyright">
          &copy; {{ currentYear }} Imagi. All rights reserved.
        </p>
        <div class="language-selector">
          <select v-model="currentLanguage" class="language-select">
            <option value="en">English</option>
            <option value="es">Español</option>
            <option value="fr">Français</option>
            <option value="de">Deutsch</option>
            <option value="ja">日本語</option>
          </select>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { ref, computed } from 'vue';

const currentLanguage = ref('en');
const currentYear = computed(() => new Date().getFullYear());
</script>

<style scoped>
.app-footer {
  background-color: var(--bg-primary);
  border-top: 1px solid var(--border-color);
  padding: var(--spacing-12) 0 var(--spacing-6);
}

.footer-content {
  display: grid;
  grid-template-columns: 2fr 3fr;
  gap: var(--spacing-16);
  margin-bottom: var(--spacing-12);
}

/* Brand section */
.footer-brand {
  max-width: 320px;
}

.logo {
  display: inline-block;
  margin-bottom: var(--spacing-4);
}

.logo-full {
  height: 32px;
  width: auto;
}

.brand-description {
  color: var(--text-secondary);
  margin-bottom: var(--spacing-6);
  font-size: var(--font-size-sm);
  line-height: 1.6;
}

.social-links {
  display: flex;
  gap: var(--spacing-4);
}

.social-link {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--border-radius-full);
  background-color: var(--bg-secondary);
  color: var(--text-secondary);
  transition: var(--transition-base);
}

.social-link:hover {
  background-color: var(--primary-color);
  color: white;
}

/* Navigation */
.footer-navigation {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-8);
}

.section-title {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-4);
}

.section-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.section-links li {
  margin-bottom: var(--spacing-3);
}

.section-links a {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: var(--font-size-sm);
  transition: var(--transition-base);
}

.section-links a:hover {
  color: var(--text-primary);
}

/* Bottom bar */
.footer-bottom {
  padding-top: var(--spacing-6);
  border-top: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.copyright {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

.language-select {
  padding: var(--spacing-2) var(--spacing-3);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  background-color: var(--bg-primary);
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: var(--transition-base);
}

.language-select:hover {
  border-color: var(--primary-color);
}

/* Responsive */
@media (max-width: 1024px) {
  .footer-content {
    grid-template-columns: 1fr;
    gap: var(--spacing-8);
  }

  .footer-brand {
    max-width: none;
    text-align: center;
  }

  .social-links {
    justify-content: center;
  }

  .footer-navigation {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .app-footer {
    padding: var(--spacing-8) 0 var(--spacing-4);
  }

  .footer-navigation {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .footer-bottom {
    flex-direction: column;
    gap: var(--spacing-4);
    text-align: center;
  }
}
</style> 