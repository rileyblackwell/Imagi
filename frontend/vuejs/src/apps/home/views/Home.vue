<!-- Home landing page -->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="min-h-screen bg-dark-900">
      <!-- Hero Section -->
      <section class="relative overflow-hidden pt-32 pb-24 px-4 sm:px-6 lg:px-8">
        <!-- Background gradient effect -->
        <div class="absolute inset-0 bg-gradient-to-br from-primary-500/20 via-indigo-500/10 to-violet-500/20 pointer-events-none"></div>
        
        <div class="relative max-w-7xl mx-auto text-center">
          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-8">
            <GradientText variant="primary">Transform Your Ideas</GradientText>
            <br />
            <span class="text-white">Into Web Applications</span>
          </h1>
          <p class="text-xl text-gray-300 max-w-3xl mx-auto mb-12">
            Create powerful, professional web applications using natural language with Imagi's AI technology
          </p>
          <HomeNavbarButton
            :to="isAuthenticated ? '/builder' : '/auth/login'"
            gradient-type="primary"
            size="lg"
            class="text-lg px-8 py-4 !h-14"
          >
            Start Building
            <i class="fas fa-arrow-right ml-2"></i>
          </HomeNavbarButton>
        </div>
      </section>

      <!-- Features Section -->
      <section class="py-24 px-4 sm:px-6 lg:px-8 relative">
        <div class="max-w-7xl mx-auto">
          <div class="text-center mb-16">
            <h2 class="text-3xl sm:text-4xl font-bold text-white mb-4">Why Choose Imagi</h2>
            <p class="text-xl text-gray-300">Transform your ideas into reality with powerful AI-driven web development</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300">
              <div class="w-12 h-12 bg-gradient-to-br from-primary-500 to-indigo-500 rounded-lg flex items-center justify-center mb-6">
                <i class="fas fa-keyboard text-white text-xl"></i>
              </div>
              <h3 class="text-xl font-semibold text-white mb-4">Natural Language Input</h3>
              <p class="text-gray-300">Describe your vision in plain English, and watch as it transforms into reality.</p>
            </div>

            <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300">
              <div class="w-12 h-12 bg-gradient-to-br from-indigo-500 to-violet-500 rounded-lg flex items-center justify-center mb-6">
                <i class="fas fa-bolt text-white text-xl"></i>
              </div>
              <h3 class="text-xl font-semibold text-white mb-4">Rapid Development</h3>
              <p class="text-gray-300">Build websites and applications in minutes, not months.</p>
            </div>

            <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300">
              <div class="w-12 h-12 bg-gradient-to-br from-violet-500 to-purple-500 rounded-lg flex items-center justify-center mb-6">
                <i class="fas fa-code text-white text-xl"></i>
              </div>
              <h3 class="text-xl font-semibold text-white mb-4">Professional Code</h3>
              <p class="text-gray-300">Generate clean, maintainable code that follows industry best practices.</p>
            </div>
          </div>
        </div>
      </section>

      <!-- How It Works -->
      <section class="py-24 px-4 sm:px-6 lg:px-8 bg-dark-800/50">
        <div class="max-w-7xl mx-auto">
          <div class="text-center mb-16">
            <h2 class="text-3xl sm:text-4xl font-bold text-white mb-4">How It Works</h2>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div class="relative">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300">
                <div class="w-12 h-12 bg-gradient-to-br from-primary-500 to-indigo-500 rounded-lg flex items-center justify-center mb-6">
                  <i class="fas fa-pencil-alt text-white text-xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">1. Describe Your Vision</h3>
                <p class="text-gray-300">Tell us what you want to build using natural language. Describe your features, design preferences, and requirements.</p>
              </div>
            </div>

            <div class="relative">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300">
                <div class="w-12 h-12 bg-gradient-to-br from-indigo-500 to-violet-500 rounded-lg flex items-center justify-center mb-6">
                  <i class="fas fa-magic text-white text-xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">2. AI Generation</h3>
                <p class="text-gray-300">Our advanced AI analyzes your description and generates all necessary code, from frontend interfaces to backend logic.</p>
              </div>
            </div>

            <div class="relative">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300">
                <div class="w-12 h-12 bg-gradient-to-br from-violet-500 to-purple-500 rounded-lg flex items-center justify-center mb-6">
                  <i class="fas fa-sliders-h text-white text-xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">3. Customize & Refine</h3>
                <p class="text-gray-300">Review the generated application, make adjustments, and refine details using natural language commands.</p>
              </div>
            </div>

            <div class="relative">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300">
                <div class="w-12 h-12 bg-gradient-to-br from-fuchsia-500 to-pink-500 rounded-lg flex items-center justify-center mb-6">
                  <i class="fas fa-rocket text-white text-xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">4. Launch & Scale</h3>
                <p class="text-gray-300">Deploy your application with confidence, knowing it's built with scalable, secure, and maintainable code.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Use Cases -->
      <section class="py-24 px-4 sm:px-6 lg:px-8">
        <div class="max-w-7xl mx-auto">
          <div class="text-center mb-16">
            <h2 class="text-3xl sm:text-4xl font-bold text-white mb-4">What You Can Build</h2>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300">
              <div class="w-12 h-12 bg-gradient-to-br from-primary-500 to-indigo-500 rounded-lg flex items-center justify-center mb-6">
                <i class="fas fa-store text-white text-xl"></i>
              </div>
              <h3 class="text-xl font-semibold text-white mb-4">E-commerce Sites</h3>
              <p class="text-gray-300">Create full-featured online stores with product catalogs, shopping carts, and secure payment processing.</p>
            </div>

            <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300">
              <div class="w-12 h-12 bg-gradient-to-br from-indigo-500 to-violet-500 rounded-lg flex items-center justify-center mb-6">
                <i class="fas fa-briefcase text-white text-xl"></i>
              </div>
              <h3 class="text-xl font-semibold text-white mb-4">Business Applications</h3>
              <p class="text-gray-300">Build custom CRM systems, inventory management tools, and other business-specific applications.</p>
            </div>

            <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300">
              <div class="w-12 h-12 bg-gradient-to-br from-violet-500 to-purple-500 rounded-lg flex items-center justify-center mb-6">
                <i class="fas fa-users text-white text-xl"></i>
              </div>
              <h3 class="text-xl font-semibold text-white mb-4">Community Platforms</h3>
              <p class="text-gray-300">Develop social networks, forums, and community-driven websites with user management and content sharing.</p>
            </div>

            <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300">
              <div class="w-12 h-12 bg-gradient-to-br from-fuchsia-500 to-pink-500 rounded-lg flex items-center justify-center mb-6">
                <i class="fas fa-chart-line text-white text-xl"></i>
              </div>
              <h3 class="text-xl font-semibold text-white mb-4">Analytics Dashboards</h3>
              <p class="text-gray-300">Create data visualization tools and interactive dashboards for business intelligence and reporting.</p>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Footer -->
    <footer class="bg-dark-800/50 border-t border-dark-700">
      <div class="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <!-- Company Info -->
          <div class="col-span-1 md:col-span-2">
            <GradientText variant="primary" class="text-2xl font-bold mb-4">Imagi</GradientText>
            <p class="text-gray-300 mb-4">Transform your ideas into powerful web applications using natural language with our AI technology.</p>
            <div class="flex space-x-4">
              <a href="#" class="text-gray-400 hover:text-white transition-colors">
                <i class="fab fa-twitter"></i>
              </a>
              <a href="#" class="text-gray-400 hover:text-white transition-colors">
                <i class="fab fa-github"></i>
              </a>
              <a href="#" class="text-gray-400 hover:text-white transition-colors">
                <i class="fab fa-linkedin"></i>
              </a>
            </div>
          </div>

          <!-- Quick Links -->
          <div>
            <h3 class="text-white font-semibold mb-4">Quick Links</h3>
            <ul class="space-y-2">
              <li>
                <router-link to="/about" class="text-gray-300 hover:text-white transition-colors">About</router-link>
              </li>
              <li>
                <router-link to="/features" class="text-gray-300 hover:text-white transition-colors">Features</router-link>
              </li>
              <li>
                <router-link to="/pricing" class="text-gray-300 hover:text-white transition-colors">Pricing</router-link>
              </li>
            </ul>
          </div>

          <!-- Support -->
          <div>
            <h3 class="text-white font-semibold mb-4">Support</h3>
            <ul class="space-y-2">
              <li>
                <router-link to="/docs" class="text-gray-300 hover:text-white transition-colors">Documentation</router-link>
              </li>
              <li>
                <router-link to="/contact" class="text-gray-300 hover:text-white transition-colors">Contact</router-link>
              </li>
              <li>
                <router-link to="/privacy" class="text-gray-300 hover:text-white transition-colors">Privacy Policy</router-link>
              </li>
            </ul>
          </div>
        </div>

        <div class="mt-8 pt-8 border-t border-dark-700">
          <p class="text-center text-gray-400">
            © {{ new Date().getFullYear() }} Imagi. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  </DefaultLayout>
</template>

<script>
import { defineComponent, computed } from 'vue'
import { useAuthStore } from '@/apps/auth/store'
import { DefaultLayout } from '@/shared/layouts'
import GradientText from '../components/shared/GradientText.vue'
import HomeNavbarButton from '../components/shared/HomeNavbarButton.vue'

export default defineComponent({
  name: 'Home',
  components: {
    DefaultLayout,
    GradientText,
    HomeNavbarButton
  },
  setup() {
    const authStore = useAuthStore()
    
    return {
      isAuthenticated: computed(() => authStore.isAuthenticated)
    }
  }
})
</script> 