<template>
  <base-layout>
    <!-- Hero Section -->
    <template #hero>
      <div class="absolute inset-0 bg-gradient-radial from-primary-500/10 via-transparent to-transparent"></div>
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        <div class="text-center max-w-3xl mx-auto">
          <h1 class="text-5xl md:text-6xl font-extrabold tracking-tight">
            <span class="block text-white">Transform Your Ideas Into</span>
            <span class="block bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">
              Web Applications
            </span>
          </h1>
          <p class="mt-6 text-xl text-gray-300">
            Create powerful, professional web applications using natural language with Imagi's AI technology
          </p>
          <div class="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
            <router-link
              to="/auth/register"
              class="inline-flex items-center justify-center px-8 py-3 text-base font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 transition-all transform hover:-translate-y-0.5"
            >
              <span>Start Building</span>
              <i class="fas fa-arrow-right ml-2"></i>
            </router-link>
          </div>
        </div>
      </div>
    </template>

    <!-- Main Content -->
    <template #default>
      <!-- Why Choose Imagi Section -->
      <section class="py-24">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="text-center">
            <h2 class="text-3xl font-bold text-white">Why Choose Imagi</h2>
            <p class="mt-4 text-xl text-gray-300 max-w-2xl mx-auto">
              Transform your ideas into reality with powerful AI-driven web development
            </p>
          </div>

          <div class="mt-20 grid grid-cols-1 gap-12 sm:grid-cols-2 lg:grid-cols-3">
            <!-- Natural Language Input -->
            <div class="relative group">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-keyboard text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Natural Language Input</h3>
                <p class="text-gray-300">Describe your vision in plain English, and watch as it transforms into reality.</p>
              </div>
            </div>

            <!-- Rapid Development -->
            <div class="relative group">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-bolt text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Rapid Development</h3>
                <p class="text-gray-300">Build websites and applications in minutes, not months.</p>
              </div>
            </div>

            <!-- Professional Code -->
            <div class="relative group">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-code text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Professional Code</h3>
                <p class="text-gray-300">Generate clean, maintainable code that follows industry best practices.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- How It Works Section -->
      <section class="py-24 bg-dark-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="text-center">
            <h2 class="text-3xl font-bold text-white">How It Works</h2>
          </div>

          <div class="mt-20 grid grid-cols-1 gap-12 sm:grid-cols-2 lg:grid-cols-4">
            <!-- Step 1 -->
            <div class="relative group">
              <div class="bg-dark-900/50 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-pencil-alt text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">1. Describe Your Vision</h3>
                <p class="text-gray-300">Tell us what you want to build using natural language. Describe your features, design preferences, and requirements.</p>
              </div>
            </div>

            <!-- Step 2 -->
            <div class="relative group">
              <div class="bg-dark-900/50 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-magic text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">2. AI Generation</h3>
                <p class="text-gray-300">Our advanced AI analyzes your description and generates all necessary code, from frontend interfaces to backend logic.</p>
              </div>
            </div>

            <!-- Step 3 -->
            <div class="relative group">
              <div class="bg-dark-900/50 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-sliders-h text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">3. Customize & Refine</h3>
                <p class="text-gray-300">Review the generated application, make adjustments, and refine details using natural language commands.</p>
              </div>
            </div>

            <!-- Step 4 -->
            <div class="relative group">
              <div class="bg-dark-900/50 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-rocket text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">4. Launch & Scale</h3>
                <p class="text-gray-300">Deploy your application with confidence, knowing it's built with scalable, secure, and maintainable code.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- What You Can Build Section -->
      <section class="py-24">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="text-center">
            <h2 class="text-3xl font-bold text-white">What You Can Build</h2>
          </div>

          <div class="mt-20 grid grid-cols-1 gap-12 sm:grid-cols-2">
            <!-- E-commerce Sites -->
            <div class="relative group">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-store text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">E-commerce Sites</h3>
                <p class="text-gray-300">Create full-featured online stores with product catalogs, shopping carts, and secure payment processing.</p>
              </div>
            </div>

            <!-- Business Applications -->
            <div class="relative group">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-briefcase text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Business Applications</h3>
                <p class="text-gray-300">Build custom CRM systems, inventory management tools, and other business-specific applications.</p>
              </div>
            </div>

            <!-- Community Platforms -->
            <div class="relative group">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-users text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Community Platforms</h3>
                <p class="text-gray-300">Develop social networks, forums, and community-driven websites with user management and content sharing.</p>
              </div>
            </div>

            <!-- Analytics Dashboards -->
            <div class="relative group">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-chart-line text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Analytics Dashboards</h3>
                <p class="text-gray-300">Create data visualization tools and interactive dashboards for business intelligence and reporting.</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </template>
  </base-layout>
</template>

<script>
import BaseLayout from '@/shared/layouts/BaseLayout.vue'

export default {
  name: 'Home',
  components: {
    BaseLayout
  }
}
</script>

<style>
.shadow-glow {
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(0, 255, 204, 0.1);
}

.bg-gradient-radial {
  background: radial-gradient(circle at top right, var(--tw-gradient-from), var(--tw-gradient-to));
}
</style> 