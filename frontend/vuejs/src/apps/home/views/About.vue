<!-- About page -->
<template>
  <DefaultLayout>
    <div>
      <!-- Hero Section -->
      <hero-section
        title="About Imagi"
        description="Transforming natural language into powerful web applications"
      />

      <div class="max-w-4xl mx-auto px-4 py-16">
        <div class="space-y-16">
          <!-- Mission Section -->
          <section>
            <h2 class="text-3xl font-bold text-white mb-8">Our Mission</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
                <div class="text-primary-400 mb-4">
                  <i class="fas fa-bullseye text-2xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Democratizing Web Development</h3>
                <p class="text-gray-300">Our mission is to make web development accessible to everyone by transforming natural language into professional code.</p>
              </div>
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
                <div class="text-primary-400 mb-4">
                  <i class="fas fa-star text-2xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">AI-Powered Innovation</h3>
                <p class="text-gray-300">By combining cutting-edge AI with intuitive design, we're revolutionizing how websites and applications are built.</p>
              </div>
            </div>
          </section>

          <!-- Story Section -->
          <section>
            <h2 class="text-3xl font-bold text-white mb-8">Our Story</h2>
            <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
              <div class="prose prose-invert max-w-none">
                <p>Founded in 2024, Imagi was born from a simple observation: while the world is full of innovative ideas, many remain unrealized due to the technical complexity of web development.</p>
                <p>This insight led to the creation of Imagi's natural language processing platform, which transforms plain English descriptions into functional code.</p>
              </div>
            </div>
          </section>

          <!-- Technology Section -->
          <section>
            <h2 class="text-3xl font-bold text-white mb-8">Our Technology</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
                <div class="text-primary-400 mb-4">
                  <i class="fas fa-robot text-2xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">AI Understanding</h3>
                <p class="text-gray-300">Advanced natural language processing to understand context, requirements, and user intent.</p>
              </div>
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
                <div class="text-primary-400 mb-4">
                  <i class="fas fa-code-branch text-2xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Clean Code</h3>
                <p class="text-gray-300">Generate maintainable code following industry best practices.</p>
              </div>
            </div>
          </section>

          <!-- Vision Section -->
          <section>
            <h2 class="text-3xl font-bold text-white mb-8">Our Vision</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
                <div class="text-primary-400 mb-4">
                  <i class="fas fa-rocket text-2xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Future of Development</h3>
                <p class="text-gray-300">We envision a future where creating web applications is as simple as describing your idea.</p>
              </div>
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
                <div class="text-primary-400 mb-4">
                  <i class="fas fa-users text-2xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Community Impact</h3>
                <p class="text-gray-300">Empowering entrepreneurs, businesses, and creators to bring their digital ideas to life.</p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script>
import { DefaultLayout } from '../../../shared/layouts'
import { HeroSection } from '../components'

export default {
  name: 'About',
  components: {
    DefaultLayout,
    HeroSection
  }
}
</script> 