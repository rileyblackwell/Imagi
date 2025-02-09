<template>
  <DefaultLayout :isHomeNav="true">
    <div class="min-h-screen bg-dark-900">
      <!-- Hero Section - Updated spacing -->
      <section class="relative min-h-[60vh] flex items-center justify-center overflow-hidden pt-32 pb-16 sm:pt-36 sm:pb-20">
        <!-- Background Effects -->
        <div class="absolute inset-0 bg-dark-900">
          <div class="absolute inset-0 bg-gradient-to-br from-primary-500/10 via-dark-900 to-violet-500/10"></div>
          <div class="absolute top-20 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-gradient-to-r from-primary-500/20 to-violet-500/20 rounded-full blur-[120px] opacity-70"></div>
        </div>

        <!-- Content - Added responsive padding -->
        <div class="relative w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <!-- Title section - Adjusted spacing -->
          <div class="mb-8 sm:mb-10">
            <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
              <span class="text-white block mb-2 sm:mb-3">About</span>
              <GradientText variant="primary" class="font-bold block text-5xl sm:text-6xl lg:text-7xl">
                Our Story
              </GradientText>
            </h1>
            <p class="text-lg sm:text-xl text-gray-300 mb-12 sm:mb-16 max-w-2xl mx-auto">
              We're pioneering the future of web development through AI-powered innovation and human-centric design.
            </p>
          </div>

          <!-- Stats Grid - Added responsive gaps -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6 max-w-4xl mx-auto">
            <div v-for="(stat, index) in stats" :key="index"
                 class="bg-dark-800/50 backdrop-blur-sm rounded-xl p-4 border border-dark-700/50"
            >
              <div class="text-2xl sm:text-3xl font-bold text-white mb-1">
                {{ stat.value }}
              </div>
              <div class="text-sm text-gray-400">{{ stat.label }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- Main Content -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24 relative">
        <!-- Decorative background elements -->
        <div class="absolute inset-0 overflow-hidden pointer-events-none">
          <div class="absolute -top-40 -right-40 w-80 h-80 bg-primary-500 rounded-full blur-[100px] opacity-20 transform rotate-45"></div>
          <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-violet-500 rounded-full blur-[100px] opacity-20 transform -rotate-45"></div>
        </div>

        <div class="space-y-24 relative">
          <!-- Mission Section -->
          <section>
            <div class="text-center mb-16">
              <GradientText variant="primary" class="text-3xl sm:text-4xl font-bold mb-4">Our Mission</GradientText>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div class="group bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-500 hover:-translate-y-1">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-500">
                  <i class="fas fa-bullseye text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4 group-hover:text-primary-400 transition-colors">Democratizing Web Development</h3>
                <p class="text-gray-300">We're on a mission to make web development accessible to everyone. By bridging the gap between human ideas and technical implementation, we're empowering creators, entrepreneurs, and businesses to bring their digital visions to life without the traditional barriers of coding.</p>
              </div>
              
              <div class="group bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-500 hover:-translate-y-1">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-500">
                  <i class="fas fa-lightbulb text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4 group-hover:text-primary-400 transition-colors">Innovation Through AI</h3>
                <p class="text-gray-300">We believe in harnessing the power of artificial intelligence to transform how web applications are built. Our platform combines cutting-edge AI with intuitive design to create a revolutionary development experience.</p>
              </div>
            </div>
          </section>

          <!-- What We Do Section -->
          <section>
            <div class="text-center mb-16">
              <GradientText variant="primary" class="text-3xl sm:text-4xl font-bold mb-4">What We Do</GradientText>
            </div>
            <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/20 transition-all duration-500">
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

          <!-- Vision Section -->
          <section>
            <div class="text-center mb-16">
              <GradientText variant="primary" class="text-3xl sm:text-4xl font-bold mb-4">Our Vision</GradientText>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
              <!-- Vision cards with enhanced styling -->
              <div v-for="(item, index) in visionItems" :key="index"
                   class="group bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-500 hover:-translate-y-1">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-500">
                  <i :class="['text-2xl text-primary-400', item.icon]"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4 group-hover:text-primary-400 transition-colors">{{ item.title }}</h3>
                <p class="text-gray-300">{{ item.description }}</p>
              </div>
            </div>
          </section>

          <!-- Technology Section -->
          <section>
            <div class="text-center mb-16">
              <GradientText variant="primary" class="text-3xl sm:text-4xl font-bold mb-4">Our Technology</GradientText>
            </div>
            <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/20 transition-all duration-500">
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
            <div class="relative rounded-2xl overflow-hidden">
              <!-- Gradient Background -->
              <div class="absolute inset-0 bg-gradient-to-br from-primary-600 via-violet-600 to-purple-600"></div>
              
              <!-- Decorative Elements -->
              <div class="absolute inset-0">
                <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-10"></div>
                <div class="absolute -top-40 -right-40 w-80 h-80 bg-primary-400 rounded-full blur-[100px] opacity-30"></div>
              </div>

              <!-- Content -->
              <div class="relative z-10 px-6 py-12 md:px-12 text-center">
                <h2 class="text-3xl md:text-4xl font-bold text-white mb-4">
                  Ready to Transform Your
                  <span class="bg-gradient-to-r from-primary-300 to-violet-300 bg-clip-text text-transparent">
                    Development Process?
                  </span>
                </h2>

                <p class="text-lg text-white/90 mb-8 max-w-xl mx-auto">
                  Join thousands of developers building amazing applications
                  <span class="font-semibold text-primary-200">10x faster</span> with AI.
                </p>

                <!-- Action Buttons -->
                <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
                  <HomeNavbarButton
                    :to="{ name: isAuthenticated ? 'builder-dashboard' : 'login' }"
                    class="group relative w-full sm:w-auto min-w-[200px] !h-12 px-6 rounded-xl border-2 border-white hover:border-primary-300 bg-white/10 hover:bg-white/20 transition-all duration-300"
                  >
                    <span class="relative z-10 flex items-center justify-center text-lg font-bold text-white">
                      Start Building Free
                      <i class="fas fa-arrow-right ml-2 transform group-hover:translate-x-1 transition-transform"></i>
                    </span>
                  </HomeNavbarButton>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script>
import { defineComponent, computed } from 'vue'
import { useAuthStore } from '@/apps/auth/store'
import { DefaultLayout } from '@/shared/layouts'
import { GradientText, HomeNavbarButton } from '@/apps/home/components'

export default defineComponent({
  name: 'About',
  components: {
    DefaultLayout,
    GradientText,
    HomeNavbarButton
  },
  setup() {
    const authStore = useAuthStore()
    
    const stats = [
      { value: '10K+', label: 'Active Users' },
      { value: '50K+', label: 'Apps Generated' },
      { value: '99%', label: 'Success Rate' },
      { value: '24/7', label: 'AI Support' }
    ]
    
    const visionItems = [
      {
        title: 'Future of Development',
        description: 'We envision a world where the barrier between idea and implementation disappears, where creating sophisticated web applications is as natural as having a conversation.',
        icon: 'fas fa-rocket'
      },
      {
        title: 'Empowering Creators',
        description: "We're building tools that empower individuals and teams to focus on creativity and innovation, rather than getting bogged down by technical complexities.",
        icon: 'fas fa-users'
      },
      {
        title: 'Global Impact',
        description: "By making web development accessible to everyone, we're fostering a more inclusive digital future where anyone can contribute to the web's evolution.",
        icon: 'fas fa-globe'
      }
    ]
    
    return {
      isAuthenticated: computed(() => authStore.isAuthenticated),
      stats,
      visionItems
    }
  }
})
</script>

<style scoped>
/* Remove all animation styles */
</style>