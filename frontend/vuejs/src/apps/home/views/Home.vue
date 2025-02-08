<!-- Home landing page -->
<template>
  <DefaultLayout :isHomeNav="true" class="flex-grow">
    <div class="flex flex-col min-h-screen">
      <div class="min-h-screen bg-dark-900">
        <!-- Hero Section -->
        <section class="relative min-h-[90vh] md:min-h-[80vh] flex items-center justify-center overflow-hidden py-24 md:py-20 mt-16 sm:mt-0">
          <!-- Background Effects -->
          <div class="absolute inset-0 bg-dark-900">
            <div class="absolute inset-0 bg-gradient-to-br from-primary-500/10 via-dark-900 to-violet-500/10"></div>
            <div class="absolute top-20 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-gradient-to-r from-primary-500/20 to-violet-500/20 rounded-full blur-[120px] opacity-70"></div>
          </div>

          <!-- Content -->
          <div class="relative w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex flex-col lg:flex-row items-center gap-8 lg:gap-16">
              <!-- Left side - Main content -->
              <div class="flex-1 text-center lg:text-left">
                <div class="inline-block px-4 py-1 bg-dark-800/50 backdrop-blur-sm rounded-full border border-dark-700 mb-6">
                  <span class="text-sm font-medium text-gray-300">
                    <i class="fas fa-sparkles text-primary-500 mr-2"></i>
                    AI-Powered Web Development
                  </span>
                </div>

                <h1 class="text-3xl sm:text-4xl lg:text-6xl font-bold tracking-tight mb-6">
                  <span class="text-white block mb-1">Transform Your</span>
                  <span class="text-white block mb-1">Ideas Into</span>
                  <GradientText variant="primary" class="font-bold block text-4xl sm:text-5xl lg:text-7xl">
                    Web Applications
                  </GradientText>
                </h1>

                <p class="text-lg sm:text-xl text-gray-300 mb-8 max-w-xl">
                  Create professional web applications using natural language. 
                  Describe your vision, and watch as AI brings it to life.
                </p>

                <div class="flex flex-col sm:flex-row items-center gap-4 justify-center lg:justify-start">
                  <HomeNavbarButton
                    :to="{ name: isAuthenticated ? 'builder-dashboard' : 'login' }"
                    gradient-type="primary"
                    size="lg"
                    class="!h-12 px-8"
                  >
                    Start Building
                    <i class="fas fa-arrow-right ml-2"></i>
                  </HomeNavbarButton>

                  <a href="#how-it-works" class="flex items-center gap-2 text-gray-300 hover:text-white transition-colors px-4 py-2">
                    <i class="fas fa-play text-xs bg-dark-800 p-2 rounded-full"></i>
                    <span>How It Works</span>
                  </a>
                </div>
              </div>

              <!-- Right side - Feature highlights -->
              <div class="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-lg w-full">
                <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-6 border border-dark-700">
                  <div class="w-10 h-10 bg-gradient-to-br from-primary-500 to-indigo-500 rounded-lg flex items-center justify-center mb-4">
                    <i class="fas fa-wand-magic-sparkles text-white"></i>
                  </div>
                  <h3 class="text-white font-semibold mb-2">AI Generation</h3>
                  <p class="text-gray-300 text-sm">Instant code generation powered by advanced AI</p>
                </div>

                <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-6 border border-dark-700">
                  <div class="w-10 h-10 bg-gradient-to-br from-indigo-500 to-violet-500 rounded-lg flex items-center justify-center mb-4">
                    <i class="fas fa-bolt text-white"></i>
                  </div>
                  <h3 class="text-white font-semibold mb-2">Rapid Build</h3>
                  <p class="text-gray-300 text-sm">Build in minutes, not months</p>
                </div>

                <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-6 border border-dark-700">
                  <div class="w-10 h-10 bg-gradient-to-br from-violet-500 to-purple-500 rounded-lg flex items-center justify-center mb-4">
                    <i class="fas fa-code text-white"></i>
                  </div>
                  <h3 class="text-white font-semibold mb-2">Clean Code</h3>
                  <p class="text-gray-300 text-sm">Professional, maintainable code</p>
                </div>

                <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-6 border border-dark-700">
                  <div class="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center mb-4">
                    <i class="fas fa-rocket text-white"></i>
                  </div>
                  <h3 class="text-white font-semibold mb-2">Easy Deploy</h3>
                  <p class="text-gray-300 text-sm">One-click deployment</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Features Section -->
        <section class="py-12 md:py-24 px-4 sm:px-6 lg:px-8">
          <div class="max-w-7xl mx-auto">
            <div class="text-center mb-16">
              <h2 class="text-3xl sm:text-4xl font-bold text-white mb-4">Why Choose Imagi</h2>
              <p class="text-xl text-gray-300">Transform your ideas into reality with powerful AI-driven web development</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
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
        <section class="py-12 md:py-24 px-4 sm:px-6 lg:px-8 bg-dark-800/50">
          <div class="max-w-7xl mx-auto">
            <div class="text-center mb-16">
              <h2 class="text-3xl sm:text-4xl font-bold text-white mb-4">How It Works</h2>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8">
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
        <section class="py-12 md:py-24 px-4 sm:px-6 lg:px-8">
          <div class="max-w-7xl mx-auto">
            <div class="text-center mb-16">
              <h2 class="text-3xl sm:text-4xl font-bold text-white mb-4">What You Can Build</h2>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8">
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
    </div>
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