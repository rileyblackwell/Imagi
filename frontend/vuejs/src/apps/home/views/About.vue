<!-- About page -->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="min-h-screen bg-dark-900">
      <!-- Hero Section -->
      <section class="relative min-h-[60vh] md:min-h-[50vh] flex items-center justify-center overflow-hidden py-12 md:py-20">
        <!-- Background Effects -->
        <div class="absolute inset-0 bg-dark-900">
          <div class="absolute inset-0 bg-gradient-to-br from-primary-500/10 via-dark-900 to-violet-500/10"></div>
          <div class="absolute top-20 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-gradient-to-r from-primary-500/20 to-violet-500/20 rounded-full blur-[120px] opacity-70"></div>
        </div>

        <!-- Content -->
        <div class="relative w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 class="text-3xl sm:text-4xl lg:text-6xl font-bold tracking-tight mb-4 md:mb-6">
            <span class="text-white block">About Imagi</span>
            <GradientText variant="primary" class="font-bold block text-3xl sm:text-4xl lg:text-5xl">
              Revolutionizing Web Development
            </GradientText>
          </h1>
          <p class="text-base sm:text-lg lg:text-xl text-gray-300 mb-6 md:mb-8 max-w-2xl mx-auto">
            Transforming the way web applications are built through the power of natural language and AI.
          </p>
        </div>
      </section>

      <div class="max-w-4xl mx-auto px-4 py-8 md:py-16 relative">
        <div class="space-y-8 md:space-y-16">
          <!-- Mission Section -->
          <section>
            <h2 class="text-3xl font-bold text-white mb-8 text-center">Our Mission</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8">
              <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300 hover:-translate-y-1 group">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-bullseye text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Democratizing Web Development</h3>
                <p class="text-gray-300">We're on a mission to make web development accessible to everyone. By bridging the gap between human ideas and technical implementation, we're empowering creators, entrepreneurs, and businesses to bring their digital visions to life without the traditional barriers of coding.</p>
              </div>
              <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300 hover:-translate-y-1 group">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-lightbulb text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Innovation Through AI</h3>
                <p class="text-gray-300">We believe in harnessing the power of artificial intelligence to transform how web applications are built. Our platform combines cutting-edge AI with intuitive design to create a revolutionary development experience.</p>
              </div>
            </div>
          </section>

          <!-- What We Do Section -->
          <section>
            <h2 class="text-3xl font-bold text-white mb-8 text-center">What We Do</h2>
            <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/20 transition-all duration-300">
              <div class="prose prose-invert max-w-none prose-p:text-gray-300 prose-li:text-gray-300 prose-strong:text-white">
                <p class="text-lg">Imagi is pioneering the future of web development with our flagship product, <span class="text-primary-400">Imagi Oasis</span>. Our platform transforms natural language descriptions into fully functional web applications, making the development process more intuitive and efficient than ever before.</p>
                
                <h3 class="text-xl font-semibold mt-8 mb-4">Key Features:</h3>
                <ul class="space-y-4">
                  <li class="flex items-start">
                    <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mr-3 mt-1 flex-shrink-0">
                      <i class="fas fa-wand-magic-sparkles text-sm text-primary-400"></i>
                    </div>
                    <span><strong class="text-white">Natural Language Generation:</strong> Simply describe your vision in plain English, and watch as our AI transforms it into clean, professional code.</span>
                  </li>
                  <li class="flex items-start">
                    <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mr-3 mt-1 flex-shrink-0">
                      <i class="fas fa-code text-sm text-primary-400"></i>
                    </div>
                    <span><strong class="text-white">Full-Stack Development:</strong> Generate both frontend and backend code, complete with database structures, API endpoints, and user interfaces.</span>
                  </li>
                  <li class="flex items-start">
                    <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mr-3 mt-1 flex-shrink-0">
                      <i class="fas fa-arrows-rotate text-sm text-primary-400"></i>
                    </div>
                    <span><strong class="text-white">Iterative Refinement:</strong> Continuously refine and enhance your application through natural conversation with our AI.</span>
                  </li>
                  <li class="flex items-start">
                    <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mr-3 mt-1 flex-shrink-0">
                      <i class="fas fa-shield-halved text-sm text-primary-400"></i>
                    </div>
                    <span><strong class="text-white">Best Practices Built-in:</strong> Every generated application follows industry standards for security, performance, and maintainability.</span>
                  </li>
                </ul>
              </div>
            </div>
          </section>

          <!-- Our Vision Section -->
          <section>
            <h2 class="text-3xl font-bold text-white mb-8 text-center">Our Vision</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300 hover:-translate-y-1 group">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-rocket text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Future of Development</h3>
                <p class="text-gray-300">We envision a world where the barrier between idea and implementation disappears, where creating sophisticated web applications is as natural as having a conversation.</p>
              </div>
              <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300 hover:-translate-y-1 group">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-users text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Empowering Creators</h3>
                <p class="text-gray-300">We're building tools that empower individuals and teams to focus on creativity and innovation, rather than getting bogged down by technical complexities.</p>
              </div>
              <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300 hover:-translate-y-1 group">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-globe text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Global Impact</h3>
                <p class="text-gray-300">By making web development accessible to everyone, we're fostering a more inclusive digital future where anyone can contribute to the web's evolution.</p>
              </div>
            </div>
          </section>

          <!-- Technology Section -->
          <section>
            <h2 class="text-3xl font-bold text-white mb-8 text-center">Our Technology</h2>
            <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/20 transition-all duration-300">
              <div class="prose prose-invert max-w-none prose-p:text-gray-300">
                <p class="text-lg">At the heart of Imagi lies a sophisticated AI system that understands context, requirements, and user intent. Our technology stack combines:</p>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-8 mt-6 md:mt-8">
                  <div class="bg-dark-900/30 backdrop-blur-sm rounded-xl p-6 border border-dark-600">
                    <h4 class="text-lg font-semibold text-white mb-4 flex items-center">
                      <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mr-3 flex-shrink-0">
                        <i class="fas fa-brain text-primary-400"></i>
                      </div>
                      Advanced AI Models
                    </h4>
                    <p class="text-gray-300">State-of-the-art language models trained on vast amounts of code and development patterns to understand and generate high-quality applications.</p>
                  </div>
                  <div class="bg-dark-900/30 backdrop-blur-sm rounded-xl p-6 border border-dark-600">
                    <h4 class="text-lg font-semibold text-white mb-4 flex items-center">
                      <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mr-3 flex-shrink-0">
                        <i class="fas fa-cubes text-primary-400"></i>
                      </div>
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
            <h2 class="text-3xl font-bold text-white mb-8 text-center">Join the Revolution</h2>
            <div class="bg-gradient-to-r from-primary-600 to-primary-400 rounded-2xl p-6 md:p-8 text-center">
              <h3 class="text-xl md:text-2xl font-bold text-white mb-3 md:mb-4">Ready to Transform Your Ideas into Reality?</h3>
              <p class="text-white text-base md:text-lg mb-6 md:mb-8">Join thousands of creators who are already building the future with Imagi.</p>
              <router-link
                :to="{ name: isAuthenticated ? 'builder-dashboard' : 'login' }"
                class="inline-flex items-center px-8 py-3 text-lg font-medium rounded-lg text-primary-600 bg-white hover:bg-gray-100 transition-all duration-300 transform hover:scale-[1.02]"
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
import { DefaultLayout } from '@/shared/layouts'
import { GradientText, HeroSection } from '@/apps/home/components'
import { useAuthStore } from '@/apps/auth/store'
import { computed } from 'vue'

export default {
  name: 'About',
  components: {
    DefaultLayout,
    GradientText,
    HeroSection
  },
  setup() {
    const authStore = useAuthStore()
    
    return {
      isAuthenticated: computed(() => authStore.isAuthenticated)
    }
  }
}
</script>

<style>
/* Reset default prose list styles */
.prose :where(ul):not(:where([class~="not-prose"] *)) {
  padding-left: 0;
  list-style-type: none;
  margin: 0;
}

.prose :where(ul > li):not(:where([class~="not-prose"] *)) {
  position: relative;
  padding-left: 0;
  margin-top: 1em;
  margin-bottom: 1em;
}

/* Custom bullet point styling */
.prose :where(ul > li):not(:where([class~="not-prose"] *))::before {
  display: none;
}

/* Ensure proper spacing for nested content */
.prose :where(ul > li > *):not(:where([class~="not-prose"] *)) {
  margin-top: 0;
  margin-bottom: 0;
}

/* Specific spacing for feature list items */
.prose ul.space-y-4 > li {
  margin: 0;
  padding: 0;
}
</style>