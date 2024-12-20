<template>
  <footer class="site-footer">
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
        &copy; 2024 Imagi. All rights reserved.
      </p>
    </div>
  </footer>
</template>

<style scoped>
.site-footer {
  background: var(--bg-primary);
  border-top: 1px solid var(--border-color);
  padding: 2rem 0;
}

.site-footer-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.footer-brand-text {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
}

.site-footer-links {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.link {
  text-decoration: none;
  transition: all 0.2s;
}

.link-muted {
  color: var(--text-secondary);
}

.link-muted:hover {
  color: var(--text-primary);
}

.site-footer-divider {
  color: var(--text-muted);
}

.site-footer-copyright {
  color: var(--text-muted);
  font-size: 0.875rem;
  margin: 0;
}

@media (max-width: 768px) {
  .site-footer-content {
    gap: 0.75rem;
  }

  .site-footer-links {
    gap: 0.75rem;
  }
}
</style> 