<template>
  <DefaultLayout :isHomeNav="true">
    <div class="min-h-screen bg-dark-950 relative overflow-hidden">
      <!-- Enhanced Background Effects matching Projects page -->
      <div class="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <!-- Gradient orbs matching Projects page -->
        <div class="absolute top-[10%] left-[5%] w-[300px] sm:w-[500px] md:w-[800px] h-[300px] sm:h-[500px] md:h-[800px] rounded-full bg-primary-500/5 blur-[80px] sm:blur-[120px] animate-float"></div>
        <div class="absolute bottom-[20%] right-[10%] w-[200px] sm:w-[400px] md:w-[600px] h-[200px] sm:h-[400px] md:h-[600px] rounded-full bg-violet-500/5 blur-[60px] sm:blur-[100px] animate-float-delay"></div>
        <!-- Grid pattern overlay -->
        <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
        <!-- Subtle noise texture -->
        <div class="absolute inset-0 bg-noise opacity-[0.015]"></div>
      </div>

      <!-- Hero Section with improved styling -->
      <section class="relative min-h-[60vh] flex items-center justify-center overflow-hidden pt-32 pb-16 sm:pt-36 sm:pb-20">
        <!-- Content -->
        <div class="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <!-- Enhanced section header to match projects page -->
          <div class="inline-block px-4 py-1.5 bg-primary-500/10 rounded-full mb-3">
            <span class="text-primary-400 font-semibold text-sm tracking-wider">OUR COMPANY</span>
          </div>
          
          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
            <span class="text-white block mb-2 sm:mb-3">About</span>
            <GradientText variant="primary" class="font-bold block text-5xl sm:text-6xl lg:text-7xl">
              Our Story
            </GradientText>
          </h1>
          
          <p class="text-xl text-gray-300 mb-12 sm:mb-16 max-w-3xl mx-auto leading-relaxed">
            We're pioneering the future of web development through AI-powered innovation and human-centric design.
          </p>

          <!-- Stats Grid - Enhanced styling with glass morphism -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6 max-w-4xl mx-auto">
            <div v-for="(stat, index) in stats" :key="index"
                 class="group relative transform transition-all duration-300 hover:-translate-y-2"
            >
              <!-- Enhanced glass morphism effect with glow -->
              <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500/50 to-violet-500/50 rounded-2xl opacity-0 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"></div>
              
              <!-- Card content with enhanced styling -->
              <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden h-full flex flex-col border border-dark-800/50 group-hover:border-primary-500/30 transition-all duration-300">
                <!-- Card header with gradient -->
                <div class="h-2 w-full bg-gradient-to-r from-primary-500 to-violet-500"></div>
                <div class="p-4">
                  <div class="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-primary-300 to-violet-300 bg-clip-text text-transparent mb-1">
                    {{ stat.value }}
                  </div>
                  <div class="text-sm text-gray-400">{{ stat.label }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Divider with animated line matching Projects page -->
      <div class="relative h-16 max-w-7xl mx-auto">
        <div class="absolute inset-x-0 h-px mx-auto w-2/3 sm:w-1/2 bg-gradient-to-r from-transparent via-primary-500/30 to-transparent animate-pulse-slow"></div>
      </div>

      <!-- Main Content -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24 relative">
        <div class="space-y-24 relative z-10">
          <!-- Mission Section -->
          <section>
            <SectionHeader 
              title="Our Mission" 
              subtitle="We're transforming the world of web development through innovative AI solutions."
            />
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div class="group relative transform transition-all duration-300 hover:-translate-y-2">
                <!-- Enhanced glass morphism effect with glow -->
                <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500/50 to-violet-500/50 rounded-2xl opacity-0 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"></div>
                
                <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden h-full flex flex-col border border-dark-800/50 group-hover:border-primary-500/30 transition-all duration-300">
                  <!-- Card header with gradient -->
                  <div class="h-2 w-full bg-gradient-to-r from-primary-500 to-violet-500"></div>
                  <div class="p-7">
                    <div class="flex items-center gap-4 mb-5">
                      <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500/20 to-violet-500/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-primary-500/20 shadow-lg shadow-primary-500/5">
                        <i class="fas fa-bullseye text-primary-400 text-xl"></i>
                      </div>
                      <h3 class="text-xl font-bold text-white">Democratizing Web Development</h3>
                    </div>
                    <p class="text-gray-300">We're on a mission to make web development accessible to everyone. By bridging the gap between human ideas and technical implementation, we're empowering creators, entrepreneurs, and businesses to bring their digital visions to life without the traditional barriers of coding.</p>
                  </div>
                </div>
              </div>
              
              <div class="group relative transform transition-all duration-300 hover:-translate-y-2">
                <!-- Enhanced glass morphism effect with glow -->
                <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500/50 to-violet-500/50 rounded-2xl opacity-0 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"></div>
                
                <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden h-full flex flex-col border border-dark-800/50 group-hover:border-primary-500/30 transition-all duration-300">
                  <!-- Card header with gradient -->
                  <div class="h-2 w-full bg-gradient-to-r from-primary-500 to-violet-500"></div>
                  <div class="p-7">
                    <div class="flex items-center gap-4 mb-5">
                      <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500/20 to-violet-500/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-primary-500/20 shadow-lg shadow-primary-500/5">
                        <i class="fas fa-lightbulb text-primary-400 text-xl"></i>
                      </div>
                      <h3 class="text-xl font-bold text-white">Innovation Through AI</h3>
                    </div>
                    <p class="text-gray-300">We believe in harnessing the power of artificial intelligence to transform how web applications are built. Our platform combines cutting-edge AI with intuitive design to create a revolutionary development experience.</p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- What We Do Section -->
          <section>
            <SectionHeader 
              title="What We Do" 
              subtitle="Our innovative platform transforms how web applications are built, deployed, and maintained."
            />
            
            <div class="group relative transform transition-all duration-300 hover:-translate-y-2">
              <!-- Enhanced glass morphism effect with glow -->
              <div class="absolute -inset-0.5 bg-gradient-to-r from-indigo-500/50 to-blue-500/50 rounded-2xl opacity-0 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"></div>
              
              <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden h-full flex flex-col border border-dark-800/50 group-hover:border-primary-500/30 transition-all duration-300">
                <!-- Card header with gradient -->
                <div class="h-2 w-full bg-gradient-to-r from-indigo-500 to-blue-500"></div>
                <div class="p-7">
                  <p class="text-lg text-gray-300 mb-10">Imagi is pioneering the future of web development with our flagship product, <span class="text-primary-400">Imagi Oasis</span>. Our platform transforms natural language descriptions into fully functional Django web applications, making the development process more intuitive and efficient than ever before.</p>
                  
                  <h3 class="text-xl font-bold text-white mb-8 flex items-center gap-3">
                    <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500/20 to-violet-500/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-primary-500/20">
                      <i class="fas fa-star text-primary-400"></i>
                    </div>
                    Key Features
                  </h3>
                  
                  <div class="space-y-8">
                    <div class="flex items-start gap-6">
                      <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500/15 to-violet-500/15 flex items-center justify-center mt-1 flex-shrink-0 group-hover:scale-110 transition-all duration-300 border border-primary-500/20">
                        <i class="fas fa-wand-magic-sparkles text-sm text-primary-400"></i>
                      </div>
                      <div class="flex-1">
                        <strong class="text-white block mb-2">Natural Language Generation</strong>
                        <span class="text-gray-300">Simply describe your vision in plain English, and watch as our AI transforms it into clean, professional code.</span>
                      </div>
                    </div>
                    <div class="flex items-start gap-6">
                      <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500/15 to-violet-500/15 flex items-center justify-center mt-1 flex-shrink-0 group-hover:scale-110 transition-all duration-300 border border-primary-500/20">
                        <i class="fas fa-code text-sm text-primary-400"></i>
                      </div>
                      <div class="flex-1">
                        <strong class="text-white block mb-2">Full-Stack Development</strong>
                        <span class="text-gray-300">Generate both frontend and backend code, complete with database structures, API endpoints, and user interfaces.</span>
                      </div>
                    </div>
                    <div class="flex items-start gap-6">
                      <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500/15 to-violet-500/15 flex items-center justify-center mt-1 flex-shrink-0 group-hover:scale-110 transition-all duration-300 border border-primary-500/20">
                        <i class="fas fa-arrows-rotate text-sm text-primary-400"></i>
                      </div>
                      <div class="flex-1">
                        <strong class="text-white block mb-2">Iterative Refinement</strong>
                        <span class="text-gray-300">Continuously refine and enhance your application through natural conversation with our AI.</span>
                      </div>
                    </div>
                    <div class="flex items-start gap-6">
                      <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500/15 to-violet-500/15 flex items-center justify-center mt-1 flex-shrink-0 group-hover:scale-110 transition-all duration-300 border border-primary-500/20">
                        <i class="fas fa-shield-halved text-sm text-primary-400"></i>
                      </div>
                      <div class="flex-1">
                        <strong class="text-white block mb-2">Best Practices Built-in</strong>
                        <span class="text-gray-300">Every generated application follows industry standards for security, performance, and maintainability.</span>
                      </div>
                    </div>
                    <div class="flex items-start gap-6">
                      <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500/15 to-violet-500/15 flex items-center justify-center mt-1 flex-shrink-0 group-hover:scale-110 transition-all duration-300 border border-primary-500/20">
                        <i class="fas fa-coins text-sm text-primary-400"></i>
                      </div>
                      <div class="flex-1">
                        <strong class="text-white block mb-2">Affordable Pricing</strong>
                        <span class="text-gray-300">Pay only for what you use with our credit-based system. Build complete web apps for just a few dollars instead of thousands.</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- Vision Section -->
          <section>
            <SectionHeader 
              title="Our Vision" 
              subtitle="We're creating a future where technology enables creativity without barriers."
            />
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div v-for="(item, index) in visionItems" :key="index"
                   class="group relative transform transition-all duration-300 hover:-translate-y-2"
              >
                <!-- Enhanced glass morphism effect with glow -->
                <div class="absolute -inset-0.5 bg-gradient-to-r from-violet-500/50 to-fuchsia-500/50 rounded-2xl opacity-0 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"></div>
                
                <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden h-full flex flex-col border border-dark-800/50 group-hover:border-primary-500/30 transition-all duration-300">
                  <!-- Card header with gradient -->
                  <div class="h-2 w-full bg-gradient-to-r from-violet-500 to-fuchsia-500"></div>
                  <div class="p-7">
                    <div class="flex items-center gap-4 mb-5">
                      <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-violet-500/20 shadow-lg shadow-violet-500/5">
                        <i :class="['text-violet-400 text-xl', item.icon]"></i>
                      </div>
                      <h3 class="text-xl font-bold text-white">{{ item.title }}</h3>
                    </div>
                    <p class="text-gray-300">{{ item.description }}</p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- Technology Section -->
          <section>
            <SectionHeader 
              title="Our Technology" 
              subtitle="Powered by cutting-edge AI and a modern technology stack."
            />
            
            <div class="group relative transform transition-all duration-300 hover:-translate-y-2">
              <!-- Enhanced glass morphism effect with glow -->
              <div class="absolute -inset-0.5 bg-gradient-to-r from-cyan-500/50 to-blue-500/50 rounded-2xl opacity-0 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"></div>
              
              <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden h-full flex flex-col border border-dark-800/50 group-hover:border-primary-500/30 transition-all duration-300">
                <!-- Card header with gradient -->
                <div class="h-2 w-full bg-gradient-to-r from-cyan-500 to-blue-500"></div>
                <!-- Content -->
                <div class="p-7">
                  <div class="text-center md:text-left">
                    <h3 class="text-xl font-bold text-white mb-4">AI-Powered Development Platform</h3>
                    <p class="text-gray-300 mb-6">
                      Our technology stack combines the latest advancements in AI with robust, industry-standard web development frameworks and tools.
                    </p>
                  </div>
                  
                  <div class="grid grid-cols-2 md:grid-cols-4 gap-5 mt-8">
                    <div v-for="(tech, index) in ['Python', 'Django', 'Vue.js', 'TailwindCSS', 'PostgreSQL', 'Docker', 'OpenAI', 'Anthropic']" :key="index"
                         class="bg-dark-800/50 backdrop-blur-sm border border-dark-700 rounded-lg p-4 text-center group-hover:border-primary-500/20 transition-all duration-300"
                    >
                      <div class="h-14 flex items-center justify-center mb-3">
                        <i :class="['text-3xl', getTechIcon(tech)]"></i>
                      </div>
                      <h4 class="text-sm font-medium text-gray-200">{{ tech }}</h4>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
          
          <!-- CTA Section -->
          <CTASection
            title="Ready to Transform Your"
            highlightedText="Development Process?"
            description="Create beautiful web apps in minutes for just a few dollars - not thousands. No coding required."
            primaryButtonText="Start Building"
            primaryButtonTo="/products/oasis/builder/dashboard"
            icon="fas fa-wand-magic-sparkles"
            :showSecondaryButton="true"
            secondaryButtonText="Learn More" 
            secondaryButtonTo="/docs"
          />
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script>
import { defineComponent, computed } from 'vue'
import { useAuthStore } from '@/apps/auth/stores'
import { DefaultLayout } from '@/shared/layouts'
import { GradientText, HeroBadge, SectionHeader } from '@/apps/home/components'
import { CTASection } from '@/apps/home/components/organisms/sections'

export default defineComponent({
  name: 'About',
  components: {
    DefaultLayout,
    GradientText,
    HeroBadge,
    SectionHeader,
    CTASection
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
        description: 'We envision a world where the barrier between idea and implementation disappears, where creating sophisticated Django web applications is as natural as having a conversation.',
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
    
    // Function to get icon for technology stack items
    const getTechIcon = (tech) => {
      const iconMap = {
        'Python': 'fab fa-python text-blue-400',
        'Django': 'fas fa-server text-green-400',
        'Vue.js': 'fab fa-vuejs text-green-500',
        'TailwindCSS': 'fab fa-css3 text-blue-500',
        'PostgreSQL': 'fas fa-database text-blue-400',
        'Docker': 'fab fa-docker text-blue-500',
        'OpenAI': 'fas fa-brain text-primary-400',
        'Anthropic': 'fas fa-robot text-violet-400',
        'Google Cloud': 'fab fa-google text-blue-400',
      }
      return iconMap[tech] || 'fas fa-code text-gray-400'
    }
    
    return {
      isAuthenticated: computed(() => authStore.isAuthenticated),
      stats,
      visionItems,
      getTechIcon
    }
  }
})
</script>

<style scoped>
/* Remove all animation styles */

/* Reset list styles */
.prose ul {
  padding-left: 0;
  margin: 0;
  list-style: none;
}

.prose li {
  padding-left: 0;
  margin: 0;
}

/* Remove default bullet points */
.prose li::before {
  display: none !important;
}

/* Ensure proper spacing for flex items */
.prose li.flex {
  padding: 0;
  margin: 0;
}

/* Extra spacing for nested content */
.prose li > div {
  margin-top: 0;
  margin-bottom: 0;
}

/* Float animation for background orbs */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.animate-float {
  animation: float 15s ease-in-out infinite;
}

.animate-float-delay {
  animation: float 18s ease-in-out infinite reverse;
}

/* Add subtle animation for loading state */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.animate-pulse-slow {
  animation: pulse 3s ease-in-out infinite;
}
</style>