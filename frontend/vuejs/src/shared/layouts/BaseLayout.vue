<!-- Base layout for all pages -->
<template>
  <div class="min-h-screen flex flex-col bg-dark-950">
    <!-- Header -->
    <header class="bg-dark-900/80 backdrop-blur-sm border-b border-dark-800 sticky top-0 z-50">
      <nav class="container mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <!-- Logo -->
          <router-link to="/" class="flex items-center gap-3">
            <img src="@/shared/assets/images/logo.webp" alt="Imagi Logo" class="h-8 w-auto" />
            <span class="text-xl font-bold bg-gradient-to-r from-primary-300 to-primary-500 text-transparent bg-clip-text">
              Imagi
            </span>
          </router-link>

          <!-- Auth Button -->
          <router-link 
            to="/auth/login" 
            class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Login
          </router-link>
        </div>
      </nav>
    </header>

    <!-- Main Content -->
    <main class="flex-grow">
      <slot></slot>
    </main>

    <!-- Footer -->
    <footer class="bg-dark-900 border-t border-dark-700">
      <div class="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <!-- Navigation Links -->
        <div class="flex justify-center space-x-8">
          <router-link to="/about" class="text-gray-400 hover:text-primary-400">About</router-link>
          <router-link to="/privacy" class="text-gray-400 hover:text-primary-400">Privacy Policy</router-link>
          <router-link to="/terms" class="text-gray-400 hover:text-primary-400">Terms of Service</router-link>
          <router-link to="/contact" class="text-gray-400 hover:text-primary-400">Contact</router-link>
        </div>

        <!-- Copyright -->
        <div class="mt-8 pt-8 border-t border-dark-700">
          <p class="text-center text-gray-400">&copy; {{ currentYear }} Imagi. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'BaseLayout',
  computed: {
    currentYear() {
      return new Date().getFullYear()
    }
  }
}
</script>

<style>
:root {
  --color-dark-950: #0a0b0f;
  --color-dark-900: #111318;
  --color-dark-800: #1a1d24;
  --color-dark-700: #282c35;
  --color-primary-400: #60a5fa;
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;
}

.bg-dark-950 {
  background-color: var(--color-dark-950);
}

.shadow-glow {
  box-shadow: 0 0 25px -5px var(--color-primary-500);
}
</style> 