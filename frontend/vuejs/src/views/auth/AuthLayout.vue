<template>
  <div class="auth-layout">
    <nav class="auth-nav">
      <div class="container">
        <router-link to="/" class="brand">
          <span class="brand-highlight">Imagi</span>
        </router-link>
      </div>
    </nav>

    <main class="auth-main">
      <router-view></router-view>
    </main>

    <footer class="auth-footer">
      <div class="container">
        <div class="footer-links">
          <router-link to="/about" class="link">About</router-link>
          <span class="divider">•</span>
          <router-link to="/contact" class="link">Contact</router-link>
          <span class="divider">•</span>
          <router-link to="/privacy" class="link">Privacy</router-link>
          <span class="divider">•</span>
          <router-link to="/terms" class="link">Terms</router-link>
        </div>
        <p class="copyright">
          &copy; {{ new Date().getFullYear() }} Imagi. All rights reserved.
        </p>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'AuthLayout'
}
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f8fafc;
}

.auth-nav {
  background: white;
  padding: 1rem 0;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.brand {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2d3748;
  text-decoration: none;
}

.brand-highlight {
  color: #6366f1;
}

.auth-main {
  flex: 1;
  padding: 2rem 0;
}

.auth-footer {
  background: white;
  padding: 1.5rem 0;
  border-top: 1px solid #e2e8f0;
}

.footer-links {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 1rem;
}

.link {
  color: #718096;
  text-decoration: none;
  transition: color 0.2s;
}

.link:hover {
  color: #4a5568;
}

.divider {
  color: #cbd5e0;
  margin: 0 0.75rem;
}

.copyright {
  text-align: center;
  color: #a0aec0;
  font-size: 0.875rem;
  margin: 0;
}

@media (max-width: 640px) {
  .auth-main {
    padding: 1rem 0;
  }

  .footer-links {
    flex-direction: column;
    gap: 0.5rem;
  }

  .divider {
    display: none;
  }
}
</style> 