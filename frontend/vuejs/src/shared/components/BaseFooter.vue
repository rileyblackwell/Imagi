<!-- BaseFooter component -->
<template>
  <footer class="bg-dark-900 border-t border-dark-700">
    <div class="max-w-7xl mx-auto py-16 px-4 sm:px-6 lg:px-8">
      <!-- Main Footer Content -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-12">
        <!-- Company Info -->
        <div class="col-span-1 md:col-span-2 space-y-6">
          <div>
            <router-link to="/" class="text-2xl font-bold text-white hover:text-primary-400 transition-colors">
              Imagi
            </router-link>
            <p class="mt-4 text-gray-400 leading-relaxed">
              Transform your ideas into powerful web applications using natural language with Imagi's AI technology. Build faster, smarter, and more efficiently.
            </p>
          </div>
          
          <!-- Social Links -->
          <div class="space-y-4">
            <h4 class="text-sm font-semibold text-gray-300 uppercase tracking-wider">Connect With Us</h4>
            <div class="flex space-x-5">
              <a 
                href="https://twitter.com/imagiai" 
                target="_blank" 
                rel="noopener noreferrer" 
                class="text-gray-400 hover:text-primary-400 transition-colors transform hover:-translate-y-1 duration-200"
              >
                <i class="fab fa-twitter text-xl"></i>
              </a>
              <a 
                href="https://github.com/imagiai" 
                target="_blank" 
                rel="noopener noreferrer" 
                class="text-gray-400 hover:text-primary-400 transition-colors transform hover:-translate-y-1 duration-200"
              >
                <i class="fab fa-github text-xl"></i>
              </a>
              <a 
                href="https://linkedin.com/company/imagiai" 
                target="_blank" 
                rel="noopener noreferrer" 
                class="text-gray-400 hover:text-primary-400 transition-colors transform hover:-translate-y-1 duration-200"
              >
                <i class="fab fa-linkedin text-xl"></i>
              </a>
              <a 
                href="https://discord.gg/imagiai" 
                target="_blank" 
                rel="noopener noreferrer" 
                class="text-gray-400 hover:text-primary-400 transition-colors transform hover:-translate-y-1 duration-200"
              >
                <i class="fab fa-discord text-xl"></i>
              </a>
            </div>
          </div>
        </div>

        <!-- Quick Links -->
        <div class="space-y-6">
          <h4 class="text-sm font-semibold text-gray-300 uppercase tracking-wider">Company</h4>
          <ul class="space-y-4">
            <li>
              <router-link 
                to="/about" 
                class="text-gray-400 hover:text-primary-400 transition-colors flex items-center group"
              >
                <i class="fas fa-chevron-right text-xs mr-2 opacity-0 group-hover:opacity-100 transition-opacity"></i>
                About Us
              </router-link>
            </li>
            <li>
              <router-link 
                to="/contact" 
                class="text-gray-400 hover:text-primary-400 transition-colors flex items-center group"
              >
                <i class="fas fa-chevron-right text-xs mr-2 opacity-0 group-hover:opacity-100 transition-opacity"></i>
                Contact
              </router-link>
            </li>
            <li>
              <router-link 
                to="/careers" 
                class="text-gray-400 hover:text-primary-400 transition-colors flex items-center group"
              >
                <i class="fas fa-chevron-right text-xs mr-2 opacity-0 group-hover:opacity-100 transition-opacity"></i>
                Careers
              </router-link>
            </li>
            <li>
              <router-link 
                to="/blog" 
                class="text-gray-400 hover:text-primary-400 transition-colors flex items-center group"
              >
                <i class="fas fa-chevron-right text-xs mr-2 opacity-0 group-hover:opacity-100 transition-opacity"></i>
                Blog
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Legal Links -->
        <div class="space-y-6">
          <h4 class="text-sm font-semibold text-gray-300 uppercase tracking-wider">Legal</h4>
          <ul class="space-y-4">
            <li>
              <router-link 
                to="/privacy" 
                class="text-gray-400 hover:text-primary-400 transition-colors flex items-center group"
              >
                <i class="fas fa-chevron-right text-xs mr-2 opacity-0 group-hover:opacity-100 transition-opacity"></i>
                Privacy Policy
              </router-link>
            </li>
            <li>
              <router-link 
                to="/terms" 
                class="text-gray-400 hover:text-primary-400 transition-colors flex items-center group"
              >
                <i class="fas fa-chevron-right text-xs mr-2 opacity-0 group-hover:opacity-100 transition-opacity"></i>
                Terms of Service
              </router-link>
            </li>
            <li>
              <router-link 
                to="/security" 
                class="text-gray-400 hover:text-primary-400 transition-colors flex items-center group"
              >
                <i class="fas fa-chevron-right text-xs mr-2 opacity-0 group-hover:opacity-100 transition-opacity"></i>
                Security
              </router-link>
            </li>
            <li>
              <router-link 
                to="/cookie-policy" 
                class="text-gray-400 hover:text-primary-400 transition-colors flex items-center group"
              >
                <i class="fas fa-chevron-right text-xs mr-2 opacity-0 group-hover:opacity-100 transition-opacity"></i>
                Cookie Policy
              </router-link>
            </li>
          </ul>
        </div>
      </div>

      <!-- Bottom Bar -->
      <div class="mt-12 pt-8 border-t border-dark-700">
        <div class="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          <!-- Copyright -->
          <p class="text-gray-400 text-sm">
            &copy; {{ currentYear }} Imagi. All rights reserved.
          </p>
          
          <!-- Additional Links -->
          <div class="flex space-x-6">
            <a 
              href="#" 
              class="text-gray-400 hover:text-primary-400 transition-colors text-sm"
            >
              Status
            </a>
            <a 
              href="#" 
              class="text-gray-400 hover:text-primary-400 transition-colors text-sm"
            >
              Support
            </a>
            <a 
              href="#" 
              class="text-gray-400 hover:text-primary-400 transition-colors text-sm"
            >
              API
            </a>
          </div>
        </div>
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

<style scoped>
/* Hover animations */
.group:hover .fa-chevron-right {
  transform: translateX(2px);
}

.fa-chevron-right {
  transition: transform 0.2s ease-in-out;
}

/* Social icons hover effect */
.fab {
  transition: transform 0.2s ease-in-out;
}
</style> 