<!-- Home landing page -->
<template>
  <DefaultLayout :isHomeNav="true" class="flex-grow">
    <div class="flex flex-col min-h-screen">
      <div class="min-h-screen bg-dark-900">
        <!-- Hero Section -->
        <section class="relative min-h-[90vh] md:min-h-[80vh] flex items-center justify-center overflow-hidden py-24 md:py-20 mt-16 sm:mt-0">
          <!-- Enhanced Background Effects -->
          <div class="absolute inset-0 bg-dark-900">
            <div class="absolute inset-0 bg-gradient-to-br from-primary-500/10 via-dark-900 to-violet-500/10"></div>
            <div class="absolute top-20 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-gradient-to-r from-primary-500/20 to-violet-500/20 rounded-full blur-[120px] opacity-70"></div>
            <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.02]"></div>
          </div>

          <!-- Content -->
          <div class="relative w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex flex-col lg:flex-row items-center gap-8 lg:gap-16">
              <!-- Left side - Main content -->
              <div class="flex-1 text-center lg:text-left">
                <div class="inline-block px-4 py-1 bg-dark-800/50 backdrop-blur-sm rounded-full border border-primary-500/50 mb-6">
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

                <!-- Buttons -->
                <div class="flex flex-col sm:flex-row items-center gap-4 justify-center lg:justify-start">
                  <HomeNavbarButton
                    :to="{ name: isAuthenticated ? 'builder-dashboard' : 'login' }"
                    class="group relative w-full sm:w-auto !h-14 px-8 rounded-xl border border-primary-500/30 hover:border-primary-500/50 bg-gradient-to-r from-primary-500/20 to-violet-500/20 hover:from-primary-500/30 hover:to-violet-500/30 backdrop-blur-sm transition-all duration-500"
                  >
                    <span class="relative z-10 flex items-center justify-center text-lg font-medium text-white group-hover:text-white/90">
                      Start Building
                      <i class="fas fa-arrow-right ml-2 transform group-hover:translate-x-1 transition-transform duration-500"></i>
                    </span>
                  </HomeNavbarButton>

                  <a 
                    href="#how-it-works" 
                    class="group flex items-center gap-3 text-gray-300 hover:text-white transition-all duration-300 px-6 py-3 rounded-xl border border-dark-700 hover:border-primary-500/30 bg-dark-800/50 hover:bg-dark-800/80 backdrop-blur-sm"
                  >
                    <div class="w-8 h-8 rounded-full bg-dark-700 group-hover:bg-primary-500/20 flex items-center justify-center transition-all duration-300">
                      <i class="fas fa-play text-xs text-primary-400"></i>
                    </div>
                    <span class="font-medium">How It Works</span>
                  </a>
                </div>
              </div>

              <!-- Right side - Interactive Demo -->
              <div class="flex-1">
                <AnimatedTerminal />
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

        <!-- Stats Section -->
        <section class="py-12 md:py-24 px-4 sm:px-6 lg:px-8 bg-dark-800/50">
          <div class="max-w-7xl mx-auto">
            <div class="grid grid-cols-2 lg:grid-cols-4 gap-8">
              <div class="text-center">
                <div class="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-primary-400 to-violet-400 bg-clip-text text-transparent mb-2">10K+</div>
                <p class="text-gray-300">Active Users</p>
              </div>
              <div class="text-center">
                <div class="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-primary-400 to-violet-400 bg-clip-text text-transparent mb-2">50K+</div>
                <p class="text-gray-300">Apps Generated</p>
              </div>
              <div class="text-center">
                <div class="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-primary-400 to-violet-400 bg-clip-text text-transparent mb-2">99%</div>
                <p class="text-gray-300">Success Rate</p>
              </div>
              <div class="text-center">
                <div class="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-primary-400 to-violet-400 bg-clip-text text-transparent mb-2">24/7</div>
                <p class="text-gray-300">AI Support</p>
              </div>
            </div>
          </div>
        </section>

        <!-- Testimonials Section -->
        <section class="py-12 md:py-24 px-4 sm:px-6 lg:px-8">
          <div class="max-w-7xl mx-auto">
            <div class="text-center mb-16">
              <h2 class="text-3xl sm:text-4xl font-bold text-white mb-4">What Developers Say</h2>
              <p class="text-xl text-gray-300">Join thousands of satisfied developers who trust Imagi</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700">
                <div class="flex items-center mb-6">
                  <div class="flex text-primary-400">
                    <i class="fas fa-star"></i>
                    <i class="fas fa-star"></i>
                    <i class="fas fa-star"></i>
                    <i class="fas fa-star"></i>
                    <i class="fas fa-star"></i>
                  </div>
                </div>
                <p class="text-gray-300 mb-6">"Imagi has revolutionized how I build web applications. What used to take weeks now takes hours. The AI understands exactly what I need."</p>
                <div class="flex items-center">
                  <div class="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-violet-500 flex items-center justify-center">
                    <span class="text-white font-semibold">JS</span>
                  </div>
                  <div class="ml-3">
                    <div class="text-white font-semibold">John Smith</div>
                    <div class="text-gray-400 text-sm">Senior Developer</div>
                  </div>
                </div>
              </div>

              <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700">
                <div class="flex items-center mb-6">
                  <div class="flex text-primary-400">
                    <i class="fas fa-star"></i>
                    <i class="fas fa-star"></i>
                    <i class="fas fa-star"></i>
                    <i class="fas fa-star"></i>
                    <i class="fas fa-star"></i>
                  </div>
                </div>
                <p class="text-gray-300 mb-6">"The code quality is impressive. It's not just about speed - Imagi generates clean, maintainable code that follows best practices."</p>
                <div class="flex items-center">
                  <div class="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-violet-500 flex items-center justify-center">
                    <span class="text-white font-semibold">AD</span>
                  </div>
                  <div class="ml-3">
                    <div class="text-white font-semibold">Alice Davis</div>
                    <div class="text-gray-400 text-sm">Tech Lead</div>
                  </div>
                </div>
              </div>

              <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700">
                <div class="flex items-center mb-6">
                  <div class="flex text-primary-400">
                    <i class="fas fa-star"></i>
                    <i class="fas fa-star"></i>
                    <i class="fas fa-star"></i>
                    <i class="fas fa-star"></i>
                    <i class="fas fa-star"></i>
                  </div>
                </div>
                <p class="text-gray-300 mb-6">"Perfect for startups and MVPs. We've cut our development time by 80% and can iterate much faster with customer feedback."</p>
                <div class="flex items-center">
                  <div class="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-violet-500 flex items-center justify-center">
                    <span class="text-white font-semibold">MR</span>
                  </div>
                  <div class="ml-3">
                    <div class="text-white font-semibold">Mike Ross</div>
                    <div class="text-gray-400 text-sm">Startup Founder</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- CTA Section -->
        <section class="py-12 px-4 sm:px-6 lg:px-8">
          <div class="max-w-4xl mx-auto relative">
            <!-- Main CTA Card -->
            <div class="relative rounded-2xl overflow-hidden">
              <!-- Gradient Background -->
              <div class="absolute inset-0 bg-gradient-to-br from-primary-600 via-violet-600 to-purple-600"></div>
              
              <!-- Decorative Elements -->
              <div class="absolute inset-0">
                <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-10"></div>
                <div class="absolute -top-40 -right-40 w-80 h-80 bg-primary-400 rounded-full blur-[100px] opacity-30"></div>
              </div>

              <!-- Content Container -->
              <div class="relative z-10 px-6 py-12 md:px-12">
                <div class="max-w-2xl mx-auto text-center">
                  <!-- Main Text -->
                  <h2 class="text-3xl md:text-4xl font-bold text-white mb-4 leading-tight">
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
                    <!-- Start Building Button -->
                    <HomeNavbarButton
                      :to="{ name: isAuthenticated ? 'builder-dashboard' : 'login' }"
                      class="group relative w-full sm:w-auto min-w-[200px] !h-12 px-6 rounded-xl border-2 border-primary-300 hover:border-primary-200 bg-transparent hover:bg-white/10 transition-all duration-300 transform hover:-translate-y-0.5"
                    >
                      <span class="relative z-10 flex items-center justify-center text-lg font-bold text-white">
                        Start Building Free
                        <i class="fas fa-arrow-right ml-2 transform group-hover:translate-x-1 transition-transform"></i>
                      </span>
                    </HomeNavbarButton>

                    <!-- Contact Sales Button -->
                    <HomeNavbarButton
                      to="/contact"
                      class="group relative w-full sm:w-auto min-w-[200px] !h-12 px-6 rounded-xl border-2 border-white hover:border-white/90 bg-transparent hover:bg-white/10 transition-all duration-300 transform hover:-translate-y-0.5"
                    >
                      <span class="relative z-10 flex items-center justify-center text-lg font-bold text-white">
                        Contact Sales
                        <i class="fas fa-arrow-up-right-from-square ml-2 transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform"></i>
                      </span>
                    </HomeNavbarButton>
                  </div>
                </div>
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
import { 
  GradientText, 
  HomeNavbarButton, 
  HeroSection,
  AnimatedTerminal 
} from '@/apps/home/components'

export default defineComponent({
  name: 'Home',
  components: {
    DefaultLayout,
    GradientText,
    HomeNavbarButton,
    HeroSection,
    AnimatedTerminal
  },
  setup() {
    const authStore = useAuthStore()
    
    return {
      isAuthenticated: computed(() => authStore.isAuthenticated)
    }
  }
})
</script>