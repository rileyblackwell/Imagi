<template>
  <footer class="app-footer">
    <div class="max-w-7xl mx-auto px-4 py-12">
      <div class="grid md:grid-cols-4 gap-8">
        <!-- Logo and Description -->
        <div class="col-span-2">
          <img src="@/assets/images/logo.webp" alt="Imagi" class="h-10 w-auto mb-4" />
          <p class="text-gray-400 max-w-md">
            Transform your ideas into full-stack web applications using natural language. 
            Powered by advanced AI technology.
          </p>
        </div>

        <!-- Quick Links -->
        <div>
          <h3 class="text-white font-semibold mb-4">Quick Links</h3>
          <ul class="space-y-2">
            <li v-for="link in quickLinks" :key="link.path">
              <router-link 
                :to="link.path"
                class="text-gray-400 hover:text-white transition-colors"
              >
                {{ link.name }}
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Contact -->
        <div>
          <h3 class="text-white font-semibold mb-4">Contact</h3>
          <ul class="space-y-2 text-gray-400">
            <li>
              <a href="mailto:support@imagi.ai" class="hover:text-white transition-colors">
                support@imagi.ai
              </a>
            </li>
          </ul>
        </div>
      </div>

      <!-- Copyright -->
      <div class="mt-12 pt-8 border-t border-gray-800">
        <p class="text-center text-gray-500">
          © {{ new Date().getFullYear() }} Imagi. All rights reserved.
        </p>
      </div>
    </div>
  </footer>
</template>

<script setup>
const quickLinks = [
  { name: 'Home', path: '/' },
  { name: 'About', path: '/about' },
  { name: 'Start Building', path: '/builder' },
]
</script>

<style>
.app-footer {
  @apply bg-gray-900 border-t border-gray-800;
}
</style>
