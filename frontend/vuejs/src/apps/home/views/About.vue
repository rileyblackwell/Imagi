<template>
  <base-layout>
    <!-- Hero Section -->
    <template #hero>
      <div class="absolute inset-0 bg-gradient-radial from-primary-500/10 via-transparent to-transparent"></div>
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        <div class="text-center max-w-3xl mx-auto">
          <h1 class="text-5xl md:text-6xl font-extrabold tracking-tight text-white">
            About Imagi
          </h1>
          <p class="mt-6 text-xl text-gray-300">
            Transforming natural language into powerful web applications
          </p>
        </div>
      </div>
    </template>

    <!-- Main Content -->
    <template #default>
      <!-- Mission Section -->
      <section class="py-24">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 class="text-3xl font-bold text-white text-center">Our Mission</h2>
          <div class="mt-20 grid grid-cols-1 gap-12 sm:grid-cols-2">
            <div class="relative group">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-bullseye text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Democratizing Web Development</h3>
                <p class="text-gray-300">Our mission is to make web development accessible to everyone by transforming natural language into professional code.</p>
              </div>
            </div>
            <div class="relative group">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-star text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">AI-Powered Innovation</h3>
                <p class="text-gray-300">By combining cutting-edge AI with intuitive design, we're revolutionizing how websites and applications are built.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Story Section -->
      <section class="py-24 bg-dark-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 class="text-3xl font-bold text-white text-center">Our Story</h2>
          <div class="mt-12 max-w-3xl mx-auto bg-dark-900/50 rounded-2xl p-8 border border-dark-700">
            <p class="text-gray-300 mb-6">Founded in 2024, Imagi was born from a simple observation: while the world is full of innovative ideas, many remain unrealized due to the technical complexity of web development.</p>
            <p class="text-gray-300">This insight led to the creation of Imagi's natural language processing platform, which transforms plain English descriptions into functional code.</p>
          </div>
        </div>
      </section>

      <!-- Technology Section -->
      <section class="py-24">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 class="text-3xl font-bold text-white text-center">Our Technology</h2>
          <div class="mt-20 grid grid-cols-1 gap-12 sm:grid-cols-2">
            <div class="relative group">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-robot text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">AI Understanding</h3>
                <p class="text-gray-300">Advanced natural language processing to understand context, requirements, and user intent.</p>
              </div>
            </div>
            <div class="relative group">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-code-branch text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Clean Code</h3>
                <p class="text-gray-300">Generate maintainable code following industry best practices.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Vision Section -->
      <section class="py-24 bg-dark-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 class="text-3xl font-bold text-white text-center">Our Vision</h2>
          <div class="mt-20 grid grid-cols-1 gap-12 sm:grid-cols-2">
            <div class="relative group">
              <div class="bg-dark-900/50 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-rocket text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Future of Development</h3>
                <p class="text-gray-300">We envision a future where creating web applications is as simple as describing your idea.</p>
              </div>
            </div>
            <div class="relative group">
              <div class="bg-dark-900/50 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-users text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Community Impact</h3>
                <p class="text-gray-300">Empowering entrepreneurs, businesses, and creators to bring their digital ideas to life.</p>
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
  name: 'About',
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