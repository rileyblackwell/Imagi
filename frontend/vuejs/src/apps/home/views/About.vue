<!-- About Page - Premium Design matching Home -->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="min-h-screen bg-[#050508] relative overflow-hidden">
      <!-- Premium Background System -->
      <div class="fixed inset-0 pointer-events-none">
        <!-- Base gradient mesh -->
        <div class="absolute inset-0 bg-[radial-gradient(ellipse_120%_80%_at_50%_-20%,rgba(120,119,198,0.15),transparent_50%)]"></div>
        <div class="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_80%_50%,rgba(78,68,206,0.08),transparent_40%)]"></div>
        <div class="absolute inset-0 bg-[radial-gradient(ellipse_60%_40%_at_10%_80%,rgba(167,139,250,0.06),transparent_35%)]"></div>
        
        <!-- Subtle grain texture -->
        <div class="absolute inset-0 opacity-[0.015]" style="background-image: url('data:image/svg+xml,%3Csvg viewBox=%220 0 256 256%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noise%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.8%22 numOctaves=%224%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noise)%22/%3E%3C/svg%3E');"></div>
        
        <!-- Animated aurora effect -->
        <div class="absolute top-0 left-1/4 right-1/4 h-[600px] opacity-30">
          <div class="absolute inset-0 bg-gradient-to-b from-violet-500/20 via-fuchsia-500/10 to-transparent blur-[100px] animate-aurora"></div>
        </div>
        
        <!-- Floating orbs -->
        <div class="absolute top-[20%] right-[10%] w-[500px] h-[500px] rounded-full bg-gradient-to-br from-indigo-600/8 to-violet-600/4 blur-[120px] animate-float-slow"></div>
        <div class="absolute bottom-[10%] left-[5%] w-[400px] h-[400px] rounded-full bg-gradient-to-tr from-fuchsia-600/6 to-purple-600/3 blur-[100px] animate-float-delayed"></div>
        <div class="absolute top-[60%] right-[30%] w-[300px] h-[300px] rounded-full bg-gradient-to-bl from-amber-500/4 to-orange-500/2 blur-[80px] animate-float-reverse"></div>
      </div>

      <!-- Main Content -->
      <main class="relative z-10">
        <!-- Hero Section -->
        <section class="relative min-h-[60vh] flex items-center justify-center overflow-hidden pt-28 pb-16 sm:pt-32 sm:pb-20 md:pt-36 md:pb-24">
          <!-- Local background effects -->
          <div class="absolute inset-0 pointer-events-none">
            <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[140%] h-[80%] bg-[radial-gradient(ellipse_at_center,rgba(139,92,246,0.08)_0%,transparent_60%)]"></div>
          </div>

          <div class="relative w-full max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
            <div class="text-center">
              <!-- Animated badge -->
              <div class="mb-8 inline-block animate-fade-in">
                <div class="group inline-flex items-center gap-3 px-4 py-2 bg-white/[0.03] rounded-full border border-white/[0.08] backdrop-blur-sm hover:bg-white/[0.05] hover:border-white/[0.12] transition-all duration-300 cursor-default">
                  <span class="relative flex h-2 w-2">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-violet-400 opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-violet-400"></span>
                  </span>
                  <span class="text-sm font-medium text-white/70 tracking-wide">Our Story</span>
                </div>
                </div>
                
              <!-- Hero title -->
              <h1 class="text-4xl sm:text-5xl md:text-6xl lg:text-[3.5rem] font-semibold tracking-tight mb-8 leading-[1.1] animate-fade-in-up" style="animation-delay: 100ms">
                <span class="block text-white/90">Making Web Development</span>
                <span class="block mt-3">
                  <span class="relative inline-block">
                    <span class="bg-gradient-to-r from-violet-400 via-fuchsia-400 to-violet-400 bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient-x">
                      Accessible to Everyone
                    </span>
                    <span class="absolute -bottom-2 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-400/50 to-transparent"></span>
                  </span>
                </span>
                </h1>
                
              <!-- Description -->
              <p class="text-lg sm:text-xl text-white/50 mb-12 max-w-2xl mx-auto leading-relaxed animate-fade-in-up" style="animation-delay: 200ms">
                  Imagi empowers anyone—no coding skills required—to turn ideas into real, professional web applications. Our mission is to make building full-stack web apps as easy as having a conversation.
                </p>

              <!-- Stats row -->
              <div class="flex flex-wrap justify-center gap-6 md:gap-10 animate-fade-in-up" style="animation-delay: 300ms">
                <div v-for="(stat, index) in stats" :key="index" class="flex items-center gap-2 text-white/40">
                  <i :class="[stat.icon, 'text-sm', getStatIconClass(index)]"></i>
                  <span class="text-sm"><span class="font-semibold text-white/70">{{ stat.value }}</span> {{ stat.label }}</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Elegant Divider -->
        <div class="relative py-8 md:py-12 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
          <div class="relative flex items-center justify-center">
            <div class="flex-1 h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent"></div>
            <div class="mx-6 flex items-center gap-2">
              <div class="w-1 h-1 rounded-full bg-violet-400/50"></div>
              <div class="w-1.5 h-1.5 rounded-full bg-violet-400/70"></div>
              <div class="w-1 h-1 rounded-full bg-violet-400/50"></div>
            </div>
            <div class="flex-1 h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent"></div>
          </div>
        </div>

              <!-- Mission Section -->
        <section class="py-20 md:py-32 px-6 sm:px-8 lg:px-12 relative">
          <div class="max-w-7xl mx-auto relative">
            <!-- Section header -->
            <div class="text-center mb-16 md:mb-20">
              <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/[0.03] rounded-full border border-white/[0.08] mb-6">
                <i class="fas fa-bullseye text-xs text-violet-400/80"></i>
                <span class="text-sm font-medium text-white/60">Our Mission</span>
                  </div>
              
              <h2 class="text-3xl sm:text-4xl md:text-5xl font-semibold text-white/90 mb-5 tracking-tight">Web Creation for Everyone</h2>
              <p class="text-lg text-white/50 max-w-2xl mx-auto leading-relaxed">
                We believe anyone should be able to build a powerful web app—no technical background needed.
              </p>
                </div>
                
            <!-- Mission cards -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-5 md:gap-6">
              <div v-for="(card, index) in missionCards" :key="index" class="group relative">
                <div class="relative h-full p-6 md:p-8 rounded-2xl border border-white/[0.06] bg-white/[0.02] backdrop-blur-sm hover:bg-white/[0.04] hover:border-white/[0.1] transition-all duration-500 cursor-default overflow-hidden">
                  <!-- Subtle hover glow -->
                  <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                    <div class="absolute inset-0 bg-gradient-to-br opacity-[0.03]" :class="getGradientClass(card.color)"></div>
                        </div>
                        
                  <!-- Icon -->
                  <div class="relative mb-6">
                    <div 
                      class="inline-flex items-center justify-center w-12 h-12 rounded-xl border transition-all duration-300"
                      :class="getIconContainerClass(card.color)"
                    >
                      <i :class="[card.icon, 'text-lg', getIconClass(card.color)]"></i>
                    </div>
                  </div>
                  
                  <!-- Content -->
                  <h3 class="relative text-lg font-semibold text-white/90 mb-3">{{ card.title }}</h3>
                  <p class="relative text-white/50 text-sm leading-relaxed">{{ card.description }}</p>

                  <!-- Bottom accent line on hover -->
                  <div 
                    class="absolute bottom-0 left-0 right-0 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                    :class="getAccentLineClass(card.color)"
                  ></div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

        <!-- Simple Divider -->
        <div class="relative py-8 md:py-12 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
          <div class="h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent"></div>
        </div>

              <!-- What We Do Section -->
        <section class="py-20 md:py-32 px-6 sm:px-8 lg:px-12 relative">
          <div class="max-w-7xl mx-auto relative">
            <!-- Section header -->
            <div class="text-center mb-16 md:mb-20">
              <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/[0.03] rounded-full border border-white/[0.08] mb-6">
                <i class="fas fa-wand-magic-sparkles text-xs text-amber-400/80"></i>
                <span class="text-sm font-medium text-white/60">What We Do</span>
                      </div>
                      
              <h2 class="text-3xl sm:text-4xl md:text-5xl font-semibold text-white/90 mb-5 tracking-tight">What Makes Imagi Unique?</h2>
              <p class="text-lg text-white/50 max-w-3xl mx-auto leading-relaxed">
                The only platform that lets you create full-stack web applications just by describing what you want. No coding, no hiring developers, no waiting months.
                        </p>
                      </div>
                      
            <!-- Features grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 md:gap-6">
              <div v-for="(feature, index) in features" :key="index" class="group relative">
                <div class="relative h-full p-6 md:p-8 rounded-2xl border border-white/[0.06] bg-white/[0.02] backdrop-blur-sm hover:bg-white/[0.04] hover:border-white/[0.1] transition-all duration-500 cursor-default overflow-hidden">
                  <!-- Subtle hover glow -->
                  <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                    <div class="absolute inset-0 bg-gradient-to-br opacity-[0.03]" :class="getGradientClass(feature.color)"></div>
                          </div>
                          
                  <!-- Icon -->
                  <div class="relative mb-6">
                    <div 
                      class="inline-flex items-center justify-center w-12 h-12 rounded-xl border transition-all duration-300"
                      :class="getIconContainerClass(feature.color)"
                    >
                      <i :class="[feature.icon, 'text-lg', getIconClass(feature.color)]"></i>
                            </div>
                          </div>
                          
                  <!-- Content -->
                  <h3 class="relative text-lg font-semibold text-white/90 mb-3">{{ feature.title }}</h3>
                  <p class="relative text-white/50 text-sm leading-relaxed">{{ feature.description }}</p>

                  <!-- Bottom accent line on hover -->
                  <div 
                    class="absolute bottom-0 left-0 right-0 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                    :class="getAccentLineClass(feature.color)"
                  ></div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

        <!-- Simple Divider -->
        <div class="relative py-8 md:py-12 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
          <div class="h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent"></div>
        </div>

              <!-- Vision Section -->
        <section class="py-20 md:py-32 px-6 sm:px-8 lg:px-12 relative">
          <div class="max-w-7xl mx-auto relative">
            <!-- Section header -->
            <div class="text-center mb-16 md:mb-20">
              <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/[0.03] rounded-full border border-white/[0.08] mb-6">
                <i class="fas fa-eye text-xs text-fuchsia-400/80"></i>
                <span class="text-sm font-medium text-white/60">Our Vision</span>
              </div>
              
              <h2 class="text-3xl sm:text-4xl md:text-5xl font-semibold text-white/90 mb-5 tracking-tight">A Future Where Anyone Can Build</h2>
              <p class="text-lg text-white/50 max-w-2xl mx-auto leading-relaxed">
                We're building a world where anyone can create technology, no matter their background.
              </p>
            </div>

            <!-- Vision cards -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-5 md:gap-6">
              <div v-for="(item, index) in visionItems" :key="index" class="group relative">
                <div class="relative h-full p-6 md:p-8 rounded-2xl border border-white/[0.06] bg-white/[0.02] backdrop-blur-sm hover:bg-white/[0.04] hover:border-white/[0.1] transition-all duration-500 cursor-default overflow-hidden">
                  <!-- Subtle hover glow -->
                  <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                    <div class="absolute inset-0 bg-gradient-to-br from-fuchsia-500 to-violet-500 opacity-[0.03]"></div>
                </div>
                
                  <!-- Icon -->
                  <div class="relative mb-6">
                    <div class="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-fuchsia-500/10 border border-fuchsia-500/20 group-hover:bg-fuchsia-500/15 group-hover:border-fuchsia-500/30 transition-all duration-300">
                      <i :class="[item.icon, 'text-lg text-fuchsia-400']"></i>
                          </div>
                        </div>
                        
                  <!-- Content -->
                  <h3 class="relative text-lg font-semibold text-white/90 mb-3">{{ item.title }}</h3>
                  <p class="relative text-white/50 text-sm leading-relaxed">{{ item.description }}</p>

                  <!-- Bottom accent line on hover -->
                  <div class="absolute bottom-0 left-0 right-0 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-500 bg-gradient-to-r from-transparent via-fuchsia-500/50 to-transparent"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

        <!-- Simple Divider -->
        <div class="relative py-8 md:py-12 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
          <div class="h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent"></div>
        </div>

              <!-- Technology Section -->
        <section class="py-20 md:py-32 px-6 sm:px-8 lg:px-12 relative">
          <div class="max-w-7xl mx-auto relative">
            <!-- Section header -->
            <div class="text-center mb-16 md:mb-20">
              <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/[0.03] rounded-full border border-white/[0.08] mb-6">
                <i class="fas fa-microchip text-xs text-blue-400/80"></i>
                <span class="text-sm font-medium text-white/60">Our Technology</span>
                      </div>
                      
              <h2 class="text-3xl sm:text-4xl md:text-5xl font-semibold text-white/90 mb-5 tracking-tight">Modern Technology, Simple for You</h2>
              <p class="text-lg text-white/50 max-w-3xl mx-auto leading-relaxed">
                Imagi uses the same powerful technologies trusted by top companies—but you never have to see a line of code.
                        </p>
                      </div>
                      
            <!-- Technology grid -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-5 md:gap-6">
              <div v-for="(tech, index) in technologies" :key="index" class="group relative">
                <div class="relative h-full p-6 rounded-2xl border border-white/[0.06] bg-white/[0.02] backdrop-blur-sm hover:bg-white/[0.04] hover:border-white/[0.1] transition-all duration-500 cursor-default overflow-hidden text-center">
                  <!-- Subtle hover glow -->
                  <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                    <div class="absolute inset-0 bg-gradient-to-br from-blue-500 to-cyan-500 opacity-[0.03]"></div>
                  </div>
                  
                  <!-- Icon -->
                  <div class="relative mb-4 h-12 flex items-center justify-center">
                            <i :class="['text-2xl', getTechIcon(tech)]"></i>
                          </div>
                  
                  <!-- Content -->
                  <h4 class="relative text-sm font-medium text-white/80">{{ tech }}</h4>

                  <!-- Bottom accent line on hover -->
                  <div class="absolute bottom-0 left-0 right-0 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-500 bg-gradient-to-r from-transparent via-blue-500/50 to-transparent"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

        <!-- Simple Divider -->
        <div class="relative py-8 md:py-12 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
          <div class="h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent"></div>
        </div>
              
              <!-- CTA Section -->
        <section class="py-16 sm:py-24 px-6 sm:px-8 lg:px-12">
          <div class="max-w-4xl mx-auto">
            <!-- CTA Card -->
            <div class="group relative">
              <!-- Background glow -->
              <div class="absolute -inset-1 bg-gradient-to-r from-violet-600/20 via-fuchsia-600/20 to-violet-600/20 rounded-3xl blur-xl opacity-50 group-hover:opacity-70 transition-opacity duration-500"></div>
              
              <!-- Card content -->
              <div class="relative p-8 md:p-12 rounded-2xl border border-white/[0.08] bg-[#0a0a0f]/80 backdrop-blur-xl overflow-hidden">
                <!-- Accent line -->
                <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-500/50 to-transparent"></div>
                
                <!-- Content layout -->
                <div class="flex flex-col md:flex-row items-start gap-8">
                  <!-- Icon -->
                  <div class="flex-shrink-0">
                    <div class="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 border border-violet-500/20">
                      <i class="fas fa-rocket text-violet-400 text-xl"></i>
                    </div>
                      </div>
                      
                  <!-- Text content -->
                  <div class="flex-1">
                    <h2 class="text-2xl md:text-3xl font-semibold text-white/90 mb-4 leading-tight">
                          Ready to Build Your App?
                      <span class="bg-gradient-to-r from-violet-400 to-fuchsia-400 bg-clip-text text-transparent">No Coding Required!</span>
                        </h2>
                    
                    <p class="text-base md:text-lg text-white/50 mb-8 leading-relaxed max-w-xl">
                          Start building your own web application today. Just describe your idea, and let Imagi do the rest.
                        </p>
                        
                    <!-- Buttons -->
                    <div class="flex flex-col sm:flex-row gap-4">
                      <!-- Primary Button -->
                          <router-link 
                        :to="getAuthenticatedRedirect"
                        class="group/btn inline-flex items-center justify-center gap-2 px-7 py-3.5 bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-xl text-white font-medium shadow-lg shadow-violet-500/25 hover:shadow-xl hover:shadow-violet-500/30 transition-all duration-300 hover:-translate-y-0.5"
                          >
                        <i class="fas fa-rocket"></i>
                        <span>Start Building</span>
                        <i class="fas fa-arrow-right text-sm transform group-hover/btn:translate-x-1 transition-transform duration-300"></i>
                          </router-link>
                          
                      <!-- Secondary Button -->
                          <router-link 
                            to="/docs"
                        class="group/btn inline-flex items-center justify-center gap-2 px-7 py-3.5 bg-white/[0.05] border border-white/[0.1] hover:bg-white/[0.08] hover:border-white/[0.15] rounded-xl text-white font-medium transition-all duration-300"
                          >
                        <i class="fas fa-book text-violet-400/80"></i>
                        <span>Learn More</span>
                          </router-link>
                    </div>
                  </div>
                </div>
                
                <!-- Decorative elements -->
                <div class="absolute -bottom-20 -right-20 w-40 h-40 bg-violet-500/5 rounded-full blur-3xl"></div>
                <div class="absolute -top-20 -left-20 w-32 h-32 bg-fuchsia-500/5 rounded-full blur-3xl"></div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  </DefaultLayout>
</template>

<script>
import { defineComponent, computed } from 'vue'
import { DefaultLayout } from '@/shared/layouts'
import { useAuthStore } from '@/shared/stores/auth'

export default defineComponent({
  name: 'About',
  components: {
    DefaultLayout
  },
  setup() {
    const authStore = useAuthStore()
    const isAuthenticated = computed(() => authStore.isAuthenticated)
    
    const getAuthenticatedRedirect = computed(() => {
      return isAuthenticated.value ? '/products/oasis/builder/dashboard' : '/auth/login'
    })
    
    const stats = [
      { value: '10K+', label: 'Active Users', icon: 'fas fa-users' },
      { value: '50K+', label: 'Apps Generated', icon: 'fas fa-cube' },
      { value: '99%', label: 'Success Rate', icon: 'fas fa-check-circle' },
      { value: '24/7', label: 'AI Support', icon: 'fas fa-robot' }
    ]
    
    const missionCards = [
      {
        title: 'No Coding? No Problem!',
        description: 'Imagi is designed for non-technical creators, entrepreneurs, and business owners. Just describe your idea in plain English, and our AI turns it into a real web application—no code, no jargon, no barriers.',
        icon: 'fas fa-user-friends',
        color: 'violet'
      },
      {
        title: 'AI That Works for You',
        description: 'Our platform uses advanced AI to handle all the technical details. You focus on your vision—we handle the rest, building both the user interface and the backend logic for you.',
        icon: 'fas fa-lightbulb',
        color: 'emerald'
      }
    ]
    
    const features = [
      {
        title: 'Plain English to Web App',
        description: 'Describe your vision in your own words. Imagi\'s AI builds your app for you—no technical terms needed.',
        icon: 'fas fa-wand-magic-sparkles',
        color: 'violet'
      },
      {
        title: 'Full-Stack, Instantly',
        description: 'Get a complete web app with a beautiful Vue.js interface and a powerful Django backend, ready to use and grow.',
        icon: 'fas fa-layer-group',
        color: 'fuchsia'
      },
      {
        title: 'Easy Changes, Anytime',
        description: 'Want to update your app? Just ask! Imagi\'s AI makes changes for you, instantly—no need to touch code.',
        icon: 'fas fa-arrows-rotate',
        color: 'amber'
      },
      {
        title: 'Best Practices, Built In',
        description: 'Every app follows modern standards for security, speed, and reliability—so you can focus on your idea, not the tech.',
        icon: 'fas fa-shield-halved',
        color: 'emerald'
      },
      {
        title: 'Affordable for All',
        description: 'Build your app for just a few dollars. No expensive developer fees, no hidden costs—just pay for what you use.',
        icon: 'fas fa-coins',
        color: 'blue'
      },
      {
        title: 'Production Ready',
        description: 'Get professional web applications with modern interfaces and robust APIs—ready for real users from day one.',
        icon: 'fas fa-rocket',
        color: 'rose'
      }
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
    
    const technologies = ['Python', 'Django', 'Vue.js', 'TailwindCSS', 'PostgreSQL', 'Docker', 'OpenAI', 'Anthropic']
    
    const getTechIcon = (tech) => {
      const iconMap = {
        'Python': 'fab fa-python text-blue-400',
        'Django': 'fas fa-server text-green-400',
        'Vue.js': 'fab fa-vuejs text-emerald-400',
        'TailwindCSS': 'fab fa-css3 text-cyan-400',
        'PostgreSQL': 'fas fa-database text-blue-400',
        'Docker': 'fab fa-docker text-blue-500',
        'OpenAI': 'fas fa-brain text-violet-400',
        'Anthropic': 'fas fa-robot text-fuchsia-400'
      }
      return iconMap[tech] || 'fas fa-code text-white/40'
    }
    
    const getStatIconClass = (index) => {
      const colors = ['text-violet-400/80', 'text-fuchsia-400/80', 'text-emerald-400/80', 'text-blue-400/80']
      return colors[index % colors.length]
    }
    
    const getGradientClass = (color) => {
      const gradients = {
        violet: 'from-violet-500 to-purple-500',
        fuchsia: 'from-fuchsia-500 to-pink-500',
        amber: 'from-amber-500 to-orange-500',
        emerald: 'from-emerald-500 to-teal-500',
        blue: 'from-blue-500 to-cyan-500',
        rose: 'from-rose-500 to-pink-500'
      }
      return gradients[color] || gradients.violet
    }
    
    const getIconContainerClass = (color) => {
      const classes = {
        violet: 'bg-violet-500/10 border-violet-500/20 group-hover:bg-violet-500/15 group-hover:border-violet-500/30',
        fuchsia: 'bg-fuchsia-500/10 border-fuchsia-500/20 group-hover:bg-fuchsia-500/15 group-hover:border-fuchsia-500/30',
        amber: 'bg-amber-500/10 border-amber-500/20 group-hover:bg-amber-500/15 group-hover:border-amber-500/30',
        emerald: 'bg-emerald-500/10 border-emerald-500/20 group-hover:bg-emerald-500/15 group-hover:border-emerald-500/30',
        blue: 'bg-blue-500/10 border-blue-500/20 group-hover:bg-blue-500/15 group-hover:border-blue-500/30',
        rose: 'bg-rose-500/10 border-rose-500/20 group-hover:bg-rose-500/15 group-hover:border-rose-500/30'
      }
      return classes[color] || classes.violet
    }
    
    const getIconClass = (color) => {
      const classes = {
        violet: 'text-violet-400',
        fuchsia: 'text-fuchsia-400',
        amber: 'text-amber-400',
        emerald: 'text-emerald-400',
        blue: 'text-blue-400',
        rose: 'text-rose-400'
      }
      return classes[color] || classes.violet
    }
    
    const getAccentLineClass = (color) => {
      const classes = {
        violet: 'bg-gradient-to-r from-transparent via-violet-500/50 to-transparent',
        fuchsia: 'bg-gradient-to-r from-transparent via-fuchsia-500/50 to-transparent',
        amber: 'bg-gradient-to-r from-transparent via-amber-500/50 to-transparent',
        emerald: 'bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent',
        blue: 'bg-gradient-to-r from-transparent via-blue-500/50 to-transparent',
        rose: 'bg-gradient-to-r from-transparent via-rose-500/50 to-transparent'
      }
      return classes[color] || classes.violet
    }
    
    return {
      stats,
      missionCards,
      features,
      visionItems,
      technologies,
      isAuthenticated,
      getAuthenticatedRedirect,
      getTechIcon,
      getStatIconClass,
      getGradientClass,
      getIconContainerClass,
      getIconClass,
      getAccentLineClass
    }
  }
})
</script>

<style scoped>
/* Aurora animation */
@keyframes aurora {
  0%, 100% {
    transform: translateX(-10%) rotate(-2deg);
    opacity: 0.3;
  }
  50% {
    transform: translateX(10%) rotate(2deg);
    opacity: 0.4;
  }
}

.animate-aurora {
  animation: aurora 20s ease-in-out infinite;
}

/* Float animations */
@keyframes float-slow {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -20px) scale(1.02);
  }
  66% {
    transform: translate(-20px, 10px) scale(0.98);
  }
}

@keyframes float-delayed {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  50% {
    transform: translate(-25px, -30px) scale(1.03);
  }
}

@keyframes float-reverse {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(20px, 15px);
  }
}

.animate-float-slow {
  animation: float-slow 25s ease-in-out infinite;
}

.animate-float-delayed {
  animation: float-delayed 30s ease-in-out infinite;
  animation-delay: -5s;
}

.animate-float-reverse {
  animation: float-reverse 20s ease-in-out infinite;
  animation-delay: -10s;
}

/* Fade in animation */
@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.animate-fade-in {
  animation: fade-in 0.8s ease-out forwards;
}

/* Fade in up animation */
@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-up {
  opacity: 0;
  animation: fade-in-up 0.8s ease-out forwards;
}

/* Gradient animation */
@keyframes gradient-x {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.animate-gradient-x {
  animation: gradient-x 4s ease infinite;
}

/* Custom scrollbar */
:deep(::-webkit-scrollbar) {
  width: 6px;
}

:deep(::-webkit-scrollbar-track) {
  background: rgba(255, 255, 255, 0.02);
}

:deep(::-webkit-scrollbar-thumb) {
  background: rgba(139, 92, 246, 0.3);
  border-radius: 3px;
}

:deep(::-webkit-scrollbar-thumb:hover) {
  background: rgba(139, 92, 246, 0.5);
}
</style>
