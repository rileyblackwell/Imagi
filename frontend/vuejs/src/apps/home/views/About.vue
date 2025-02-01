<!-- About page -->
<template>
  <DefaultLayout :isHomeNav="true">
    <div>
      <!-- Hero Section -->
      <hero-section
        title="About Imagi"
        description="Revolutionizing web development through the power of natural language and AI"
      />

      <div class="max-w-4xl mx-auto px-4 py-16">
        <div class="space-y-24">
          <!-- Mission Section -->
          <section>
            <h2 class="text-3xl font-bold text-white mb-8">Our Mission</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
                <div class="text-primary-400 mb-4">
                  <i class="fas fa-bullseye text-2xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Democratizing Web Development</h3>
                <p class="text-gray-300">We're on a mission to make web development accessible to everyone. By bridging the gap between human ideas and technical implementation, we're empowering creators, entrepreneurs, and businesses to bring their digital visions to life without the traditional barriers of coding.</p>
              </div>
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
                <div class="text-primary-400 mb-4">
                  <i class="fas fa-lightbulb text-2xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Innovation Through AI</h3>
                <p class="text-gray-300">We believe in harnessing the power of artificial intelligence to transform how web applications are built. Our platform combines cutting-edge AI with intuitive design to create a revolutionary development experience.</p>
              </div>
            </div>
          </section>

          <!-- What We Do Section -->
          <section>
            <h2 class="text-3xl font-bold text-white mb-8">What We Do</h2>
            <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 space-y-6">
              <div class="prose prose-invert max-w-none">
                <p class="text-lg">Imagi is pioneering the future of web development with our flagship product, <span class="text-primary-400">Imagi Oasis</span>. Our platform transforms natural language descriptions into fully functional web applications, making the development process more intuitive and efficient than ever before.</p>
                
                <h3 class="text-xl font-semibold mt-8 mb-4">Key Features:</h3>
                <ul class="space-y-4">
                  <li class="flex items-start">
                    <i class="fas fa-wand-magic-sparkles text-primary-400 mt-1 mr-3"></i>
                    <span><strong class="text-white">Natural Language Generation:</strong> Simply describe your vision in plain English, and watch as our AI transforms it into clean, professional code.</span>
                  </li>
                  <li class="flex items-start">
                    <i class="fas fa-code text-primary-400 mt-1 mr-3"></i>
                    <span><strong class="text-white">Full-Stack Development:</strong> Generate both frontend and backend code, complete with database structures, API endpoints, and user interfaces.</span>
                  </li>
                  <li class="flex items-start">
                    <i class="fas fa-arrows-rotate text-primary-400 mt-1 mr-3"></i>
                    <span><strong class="text-white">Iterative Refinement:</strong> Continuously refine and enhance your application through natural conversation with our AI.</span>
                  </li>
                  <li class="flex items-start">
                    <i class="fas fa-shield-halved text-primary-400 mt-1 mr-3"></i>
                    <span><strong class="text-white">Best Practices Built-in:</strong> Every generated application follows industry standards for security, performance, and maintainability.</span>
                  </li>
                </ul>
              </div>
            </div>
          </section>

          <!-- Our Vision Section -->
          <section>
            <h2 class="text-3xl font-bold text-white mb-8">Our Vision</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
                <div class="text-primary-400 mb-4">
                  <i class="fas fa-rocket text-2xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Future of Development</h3>
                <p class="text-gray-300">We envision a world where the barrier between idea and implementation disappears, where creating sophisticated web applications is as natural as having a conversation.</p>
              </div>
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
                <div class="text-primary-400 mb-4">
                  <i class="fas fa-users text-2xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Empowering Creators</h3>
                <p class="text-gray-300">We're building tools that empower individuals and teams to focus on creativity and innovation, rather than getting bogged down by technical complexities.</p>
              </div>
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
                <div class="text-primary-400 mb-4">
                  <i class="fas fa-globe text-2xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Global Impact</h3>
                <p class="text-gray-300">By making web development accessible to everyone, we're fostering a more inclusive digital future where anyone can contribute to the web's evolution.</p>
              </div>
            </div>
          </section>

          <!-- Technology Section -->
          <section>
            <h2 class="text-3xl font-bold text-white mb-8">Our Technology</h2>
            <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
              <div class="prose prose-invert max-w-none">
                <p class="text-lg">At the heart of Imagi lies a sophisticated AI system that understands context, requirements, and user intent. Our technology stack combines:</p>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8">
                  <div>
                    <h4 class="text-lg font-semibold text-white mb-4 flex items-center">
                      <i class="fas fa-brain text-primary-400 mr-3"></i>
                      Advanced AI Models
                    </h4>
                    <p class="text-gray-300">State-of-the-art language models trained on vast amounts of code and development patterns to understand and generate high-quality applications.</p>
                  </div>
                  <div>
                    <h4 class="text-lg font-semibold text-white mb-4 flex items-center">
                      <i class="fas fa-cubes text-primary-400 mr-3"></i>
                      Modern Architecture
                    </h4>
                    <p class="text-gray-300">A robust, scalable infrastructure built on cutting-edge technologies to ensure reliability, security, and performance.</p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- Join Us Section -->
          <section>
            <h2 class="text-3xl font-bold text-white mb-8">Join the Revolution</h2>
            <div class="bg-gradient-to-r from-primary-600 to-primary-400 rounded-2xl p-8 text-center">
              <h3 class="text-2xl font-bold text-white mb-4">Ready to Transform Your Ideas into Reality?</h3>
              <p class="text-white text-lg mb-8">Join thousands of creators who are already building the future with Imagi.</p>
              <router-link
                to="/auth/register"
                class="inline-flex items-center px-8 py-3 text-lg font-medium rounded-lg text-primary-600 bg-white hover:bg-gray-100 transition-colors"
              >
                Start Building Today
                <i class="fas fa-arrow-right ml-2"></i>
              </router-link>
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

<style scoped>
.prose {
  color: #94a3b8;
}

.prose strong {
  color: #f8fafc;
}

.prose h3 {
  color: #f8fafc;
}
</style> 