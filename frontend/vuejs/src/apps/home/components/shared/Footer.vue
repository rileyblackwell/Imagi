<!-- Footer component -->
<template>
  <footer class="bg-dark-900 border-t border-dark-700">
    <div class="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
        <!-- Company Info -->
        <div class="col-span-1 md:col-span-2">
          <h3 class="text-lg font-semibold text-white mb-4">Imagi</h3>
          <p class="text-gray-400 mb-4">Transform your ideas into powerful web applications using natural language with Imagi's AI technology.</p>
          <div class="flex space-x-4">
            <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" class="text-gray-400 hover:text-primary-400">
              <font-awesome-icon :icon="['fab', 'twitter']" />
            </a>
            <a href="https://github.com" target="_blank" rel="noopener noreferrer" class="text-gray-400 hover:text-primary-400">
              <font-awesome-icon :icon="['fab', 'github']" />
            </a>
            <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" class="text-gray-400 hover:text-primary-400">
              <font-awesome-icon :icon="['fab', 'linkedin']" />
            </a>
          </div>
        </div>

        <!-- Quick Links -->
        <div>
          <h3 class="text-lg font-semibold text-white mb-4">Company</h3>
          <ul class="space-y-2">
            <li>
              <router-link to="/about" class="text-gray-400 hover:text-primary-400">About Us</router-link>
            </li>
            <li>
              <router-link to="/contact" class="text-gray-400 hover:text-primary-400">Contact</router-link>
            </li>
          </ul>
        </div>

        <!-- Legal -->
        <div>
          <h3 class="text-lg font-semibold text-white mb-4">Legal</h3>
          <ul class="space-y-2">
            <li>
              <router-link to="/privacy" class="text-gray-400 hover:text-primary-400">Privacy Policy</router-link>
            </li>
            <li>
              <router-link to="/terms" class="text-gray-400 hover:text-primary-400">Terms of Service</router-link>
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
  name: 'Footer',
  computed: {
    currentYear() {
      return new Date().getFullYear()
    }
  }
}
</script> 