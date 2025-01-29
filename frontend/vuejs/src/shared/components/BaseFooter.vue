<!-- BaseFooter component -->
<template>
  <footer class="bg-dark-900 border-t border-dark-700">
    <div class="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <!-- Company Info -->
        <div class="col-span-1 md:col-span-2">
          <h3 class="text-lg font-semibold text-white mb-4">Imagi</h3>
          <p class="text-gray-400 mb-4">Transform your ideas into powerful web applications using natural language with Imagi's AI technology.</p>
          <div class="flex space-x-4">
            <a href="https://twitter.com/imagiai" target="_blank" rel="noopener noreferrer" class="text-gray-400 hover:text-primary-400 transition-colors">
              <font-awesome-icon :icon="['fab', 'twitter']" size="lg" />
            </a>
            <a href="https://github.com/imagiai" target="_blank" rel="noopener noreferrer" class="text-gray-400 hover:text-primary-400 transition-colors">
              <font-awesome-icon :icon="['fab', 'github']" size="lg" />
            </a>
          </div>
        </div>

        <!-- Quick Links -->
        <div>
          <h3 class="text-lg font-semibold text-white mb-4">Links</h3>
          <ul class="space-y-3">
            <li>
              <router-link to="/about" class="text-gray-400 hover:text-primary-400 transition-colors">About Us</router-link>
            </li>
            <li>
              <router-link to="/contact" class="text-gray-400 hover:text-primary-400 transition-colors">Contact</router-link>
            </li>
            <li>
              <router-link to="/privacy" class="text-gray-400 hover:text-primary-400 transition-colors">Privacy Policy</router-link>
            </li>
            <li>
              <router-link to="/terms" class="text-gray-400 hover:text-primary-400 transition-colors">Terms of Service</router-link>
            </li>
          </ul>
        </div>
      </div>

      <!-- Copyright -->
      <div class="mt-8 pt-8 border-t border-dark-700">
        <p class="text-center text-gray-400">&copy; {{ currentYear }} Imagi. All rights reserved.</p>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'BaseFooter',
  computed: {
    currentYear() {
      return new Date().getFullYear()
    }
  }
}
</script> 