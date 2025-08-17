<template>
  <DefaultLayout :isHomeNav="true">
    <div class="min-h-screen bg-dark-950 relative overflow-hidden">
      <!-- Enhanced Background Effects matching dashboard pages -->
      <div class="absolute inset-0 pointer-events-none">
        <!-- Enhanced Pattern Overlay -->
        <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
        <div class="absolute inset-0 bg-noise opacity-[0.015]"></div>
        <div class="absolute inset-0 bg-gradient-to-br from-primary-950/10 via-dark-900 to-violet-950/10"></div>
        
        <!-- Enhanced Glowing Orbs Animation -->
        <div class="absolute -top-[10%] right-[15%] w-[800px] h-[800px] rounded-full bg-indigo-600/5 blur-[150px] animate-float"></div>
        <div class="absolute bottom-[5%] left-[20%] w-[600px] h-[600px] rounded-full bg-fuchsia-600/5 blur-[120px] animate-float-delay"></div>
        
        <!-- Animated Lines and Particles -->
        <div class="absolute left-0 right-0 top-1/3 h-px bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent animate-pulse-slow"></div>
        <div class="absolute left-0 right-0 bottom-1/3 h-px bg-gradient-to-r from-transparent via-violet-500/20 to-transparent animate-pulse-slow delay-700"></div>
      </div>

      <!-- Enhanced Content Container -->
      <div class="relative z-10">
        <!-- Modern Welcome Header Section -->
        <div class="pt-32 pb-12 px-6 sm:px-8 lg:px-12">
          <div class="max-w-7xl mx-auto">
            <div class="flex flex-col md:flex-row md:items-end md:justify-between gap-8">
              <div class="space-y-6 md:max-w-3xl">
                <!-- Enhanced Badge -->
                <div class="inline-flex items-center px-4 py-1.5 bg-gradient-to-r from-indigo-500/10 to-violet-500/10 rounded-full">
                  <span class="text-indigo-400 font-semibold text-sm tracking-wider">OUR COMPANY</span>
                </div>
                
                <!-- Modern Title with Gradient Enhancement -->
                <h1 class="text-4xl md:text-5xl font-bold text-white leading-tight">
                  <span class="inline-block bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent pb-1">About</span> 
                  <br class="hidden sm:block" />Our Story
                </h1>
                
                <!-- Enhanced Description -->
                <p class="text-xl text-gray-300 max-w-2xl">
                  Imagi empowers anyone—no coding skills required—to turn ideas into real, professional web applications. Our mission is to make building full-stack web apps as easy as having a conversation.
                </p>
              </div>
              
              <!-- Stats Overview Cards -->
              <div class="grid grid-cols-2 gap-4 justify-end">
                <div v-for="(stat, index) in stats" :key="index"
                     class="group relative transform transition-all duration-300">
                  <!-- Modern glassmorphism container -->
                  <div class="relative rounded-xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-lg shadow-black/20 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/30">
                    <!-- Sleek gradient header -->
                    <div class="h-0.5 w-full bg-gradient-to-r from-indigo-400 via-violet-400 to-indigo-400 opacity-80"></div>
                    
                    <div class="p-4 text-center">
                      <div class="text-lg font-bold bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent mb-1">
                        {{ stat.value }}
                      </div>
                      <div class="text-xs text-gray-400">{{ stat.label }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Animated Divider Line -->
            <div class="w-full h-px bg-gradient-to-r from-transparent via-primary-500/30 to-transparent my-12 animate-pulse-slow"></div>
          </div>
        </div>

        <!-- Main Content with Modern Layout -->
        <div class="px-6 sm:px-8 lg:px-12 pb-24">
          <div class="max-w-7xl mx-auto">
            <div class="space-y-16">
              <!-- Mission Section -->
              <section>
                <div class="text-center mb-12">
                  <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-indigo-500/15 to-violet-500/15 border border-indigo-400/20 rounded-full mb-6 backdrop-blur-sm">
                    <div class="w-1.5 h-1.5 bg-indigo-400 rounded-full mr-2 animate-pulse"></div>
                    <span class="text-indigo-300 font-medium text-xs tracking-wide uppercase">Our Mission</span>
                  </div>
                  <h2 class="text-3xl md:text-4xl font-bold text-white mb-4">
                    <span class="inline-block bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">Web Creation for Everyone</span>
                  </h2>
                  <p class="text-gray-300 max-w-3xl mx-auto">Imagi is on a mission to make web development accessible to everyone, not just programmers. We believe anyone should be able to build a powerful web app—no technical background needed.</p>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
                    <!-- Modern glassmorphism container -->
                    <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                      <!-- Sleek gradient header -->
                      <div class="h-1 w-full bg-gradient-to-r from-cyan-400 via-blue-400 to-cyan-400 opacity-80"></div>
                      
                      <!-- Subtle background effects -->
                      <div class="absolute -top-32 -right-32 w-64 h-64 bg-gradient-to-br from-cyan-400/4 to-blue-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                      
                      <div class="relative z-10 p-8">
                        <!-- Icon and Content -->
                        <div class="flex items-start gap-4 mb-6">
                          <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-400/20 to-blue-400/20 flex items-center justify-center border border-cyan-400/20 flex-shrink-0">
                            <i class="fas fa-bullseye text-cyan-300 text-lg"></i>
                          </div>
                          <div class="flex-1">
                            <h3 class="text-xl font-semibold text-white mb-3 leading-tight">No Coding? No Problem!</h3>
                          </div>
                        </div>
                        
                        <p class="text-gray-300 leading-relaxed">
                          Imagi is designed for non-technical creators, entrepreneurs, and business owners. Just describe your idea in plain English, and our AI turns it into a real web application—no code, no jargon, no barriers.
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
                    <!-- Modern glassmorphism container -->
                    <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                      <!-- Sleek gradient header -->
                      <div class="h-1 w-full bg-gradient-to-r from-emerald-400 via-teal-400 to-emerald-400 opacity-80"></div>
                      
                      <!-- Subtle background effects -->
                      <div class="absolute -top-32 -left-32 w-64 h-64 bg-gradient-to-br from-emerald-400/4 to-teal-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                      
                      <div class="relative z-10 p-8">
                        <!-- Icon and Content -->
                        <div class="flex items-start gap-4 mb-6">
                          <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-400/20 to-teal-400/20 flex items-center justify-center border border-emerald-400/20 flex-shrink-0">
                            <i class="fas fa-lightbulb text-emerald-300 text-lg"></i>
                          </div>
                          <div class="flex-1">
                            <h3 class="text-xl font-semibold text-white mb-3 leading-tight">AI That Works for You</h3>
                          </div>
                        </div>
                        
                        <p class="text-gray-300 leading-relaxed">
                          Our platform uses advanced AI to handle all the technical details. You focus on your vision—we handle the rest, building both the user interface and the backend logic for you.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <!-- What We Do Section -->
              <section>
                <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
                  <!-- Modern glassmorphism container -->
                  <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                    <!-- Sleek gradient header -->
                    <div class="h-1 w-full bg-gradient-to-r from-amber-400 via-orange-400 to-amber-400 opacity-80"></div>
                    
                    <!-- Subtle background effects -->
                    <div class="absolute -top-32 -right-32 w-64 h-64 bg-gradient-to-br from-amber-400/4 to-orange-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                    
                    <div class="relative z-10 p-8">
                      <!-- Modern pill badge -->
                      <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-amber-500/15 to-orange-500/15 border border-amber-400/20 rounded-full mb-6 backdrop-blur-sm">
                        <div class="w-1.5 h-1.5 bg-amber-400 rounded-full mr-2 animate-pulse"></div>
                        <span class="text-amber-300 font-medium text-xs tracking-wide uppercase">What We Do</span>
                      </div>
                      
                      <!-- Main Description -->
                      <div class="mb-8">
                        <h2 class="text-2xl font-semibold text-white mb-4 leading-tight">What Makes Imagi Unique?</h2>
                        <p class="text-gray-300 leading-relaxed mb-6">
                          Imagi Oasis is the only platform that lets you create full-stack web applications (with a Vue.js frontend and Django backend) just by describing what you want. No coding, no hiring developers, no waiting months—just your idea, brought to life in minutes.
                        </p>
                      </div>
                      
                      <!-- Modern separator -->
                      <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-8"></div>
                      
                      <!-- Key Features -->
                      <div class="space-y-6">
                        <h3 class="text-xl font-semibold text-white mb-6 flex items-center gap-3">
                          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-400/20 to-orange-400/20 flex items-center justify-center border border-amber-400/20">
                            <i class="fas fa-star text-amber-400 text-sm"></i>
                          </div>
                          Key Features
                        </h3>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div class="flex items-start gap-4 p-4 bg-white/5 rounded-xl border border-white/10">
                            <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-400/20 to-orange-400/20 flex items-center justify-center mt-1 flex-shrink-0 border border-amber-400/20">
                              <i class="fas fa-wand-magic-sparkles text-xs text-amber-400"></i>
                            </div>
                            <div class="flex-1">
                              <span class="text-white font-semibold block mb-1">Plain English to Web App</span>
                              <span class="text-gray-300 text-sm">Describe your vision in your own words. Imagi’s AI builds your app for you—no technical terms needed.</span>
                            </div>
                          </div>
                          
                          <div class="flex items-start gap-4 p-4 bg-white/5 rounded-xl border border-white/10">
                            <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-400/20 to-orange-400/20 flex items-center justify-center mt-1 flex-shrink-0 border border-amber-400/20">
                              <i class="fas fa-code text-xs text-amber-400"></i>
                            </div>
                            <div class="flex-1">
                              <span class="text-white font-semibold block mb-1">Full-Stack, Instantly</span>
                              <span class="text-gray-300 text-sm">Get a complete web app with a beautiful Vue.js interface and a powerful Django backend, ready to use and grow.</span>
                            </div>
                          </div>
                          
                          <div class="flex items-start gap-4 p-4 bg-white/5 rounded-xl border border-white/10">
                            <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-400/20 to-orange-400/20 flex items-center justify-center mt-1 flex-shrink-0 border border-amber-400/20">
                              <i class="fas fa-arrows-rotate text-xs text-amber-400"></i>
                            </div>
                            <div class="flex-1">
                              <span class="text-white font-semibold block mb-1">Easy Changes, Anytime</span>
                              <span class="text-gray-300 text-sm">Want to update your app? Just ask! Imagi’s AI makes changes for you, instantly—no need to touch code.</span>
                            </div>
                          </div>
                          
                          <div class="flex items-start gap-4 p-4 bg-white/5 rounded-xl border border-white/10">
                            <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-400/20 to-orange-400/20 flex items-center justify-center mt-1 flex-shrink-0 border border-amber-400/20">
                              <i class="fas fa-shield-halved text-xs text-amber-400"></i>
                            </div>
                            <div class="flex-1">
                              <span class="text-white font-semibold block mb-1">Best Practices, Built In</span>
                              <span class="text-gray-300 text-sm">Every app follows modern standards for security, speed, and reliability—so you can focus on your idea, not the tech.</span>
                            </div>
                          </div>
                          
                          <div class="flex items-start gap-4 p-4 bg-white/5 rounded-xl border border-white/10 md:col-span-2">
                            <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-400/20 to-orange-400/20 flex items-center justify-center mt-1 flex-shrink-0 border border-amber-400/20">
                              <i class="fas fa-coins text-xs text-amber-400"></i>
                            </div>
                            <div class="flex-1">
                              <span class="text-white font-semibold block mb-1">Affordable for All</span>
                              <span class="text-gray-300 text-sm">Build your app for just a few dollars. No expensive developer fees, no hidden costs—just pay for what you use.</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <!-- Vision Section -->
              <section>
                <div class="text-center mb-12">
                  <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-violet-500/15 to-fuchsia-500/15 border border-violet-400/20 rounded-full mb-6 backdrop-blur-sm">
                    <div class="w-1.5 h-1.5 bg-violet-400 rounded-full mr-2 animate-pulse"></div>
                    <span class="text-violet-300 font-medium text-xs tracking-wide uppercase">Our Vision</span>
                  </div>
                  <h2 class="text-3xl md:text-4xl font-bold text-white mb-4">
                    <span class="inline-block bg-gradient-to-r from-violet-400 to-fuchsia-400 bg-clip-text text-transparent">A Future Where Anyone Can Build</span>
                  </h2>
                  <p class="text-gray-300 max-w-3xl mx-auto">Imagi is building a world where anyone can create technology, no matter their background. We’re removing barriers so your creativity can shine.</p>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                  <div v-for="(item, index) in visionItems" :key="index"
                       class="group relative transform transition-all duration-300 hover:-translate-y-1">
                    <!-- Modern glassmorphism container -->
                    <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                      <!-- Sleek gradient header -->
                      <div class="h-1 w-full bg-gradient-to-r from-violet-400 via-fuchsia-400 to-violet-400 opacity-80"></div>
                      
                      <!-- Subtle background effects -->
                      <div class="absolute -top-32 -right-32 w-64 h-64 bg-gradient-to-br from-violet-400/4 to-fuchsia-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                      
                      <div class="relative z-10 p-8">
                        <!-- Icon and Content -->
                        <div class="flex items-start gap-4 mb-6">
                          <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-400/20 to-fuchsia-400/20 flex items-center justify-center border border-violet-400/20 flex-shrink-0">
                            <i :class="['text-violet-300 text-lg', item.icon]"></i>
                          </div>
                          <div class="flex-1">
                            <h3 class="text-xl font-semibold text-white mb-3 leading-tight">{{ item.title }}</h3>
                          </div>
                        </div>
                        
                        <p class="text-gray-300 leading-relaxed">{{ item.description }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <!-- Technology Section -->
              <section>
                <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
                  <!-- Modern glassmorphism container -->
                  <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                    <!-- Sleek gradient header -->
                    <div class="h-1 w-full bg-gradient-to-r from-cyan-400 via-blue-400 to-cyan-400 opacity-80"></div>
                    
                    <!-- Subtle background effects -->
                    <div class="absolute -top-32 -left-32 w-64 h-64 bg-gradient-to-br from-cyan-400/4 to-blue-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                    
                    <div class="relative z-10 p-8">
                      <!-- Modern pill badge -->
                      <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-cyan-500/15 to-blue-500/15 border border-cyan-400/20 rounded-full mb-6 backdrop-blur-sm">
                        <div class="w-1.5 h-1.5 bg-cyan-400 rounded-full mr-2 animate-pulse"></div>
                        <span class="text-cyan-300 font-medium text-xs tracking-wide uppercase">Our Technology</span>
                      </div>
                      
                      <div class="text-center mb-8">
                        <h2 class="text-2xl font-semibold text-white mb-4 leading-tight">Modern Technology, Simple for You</h2>
                        <p class="text-gray-300 leading-relaxed max-w-3xl mx-auto">
                          Imagi uses the same powerful technologies trusted by top companies—like Python, Django, and Vue.js—but you never have to see a line of code. Everything is handled for you, behind the scenes.
                        </p>
                      </div>
                      
                      <!-- Modern separator -->
                      <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-8"></div>
                      
                      <!-- Technology Grid -->
                      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div v-for="(tech, index) in technologies" :key="index"
                             class="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4 text-center hover:border-cyan-400/30 transition-all duration-300">
                          <div class="h-12 flex items-center justify-center mb-3">
                            <i :class="['text-2xl', getTechIcon(tech)]"></i>
                          </div>
                          <h4 class="text-sm font-medium text-gray-200">{{ tech }}</h4>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>
              
              <!-- CTA Section -->
              <section>
                <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
                  <!-- Modern glassmorphism container -->
                  <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                    <!-- Sleek gradient header -->
                    <div class="h-1 w-full bg-gradient-to-r from-rose-400 via-pink-400 to-rose-400 opacity-80"></div>
                    
                    <!-- Subtle background effects -->
                    <div class="absolute -top-32 -right-32 w-64 h-64 bg-gradient-to-br from-rose-400/4 to-pink-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                    
                    <div class="relative z-10 p-8">
                      <!-- Modern pill badge -->
                      <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-rose-500/15 to-pink-500/15 border border-rose-400/20 rounded-full mb-6 backdrop-blur-sm mx-auto">
                        <div class="w-1.5 h-1.5 bg-rose-400 rounded-full mr-2 animate-pulse"></div>
                        <span class="text-rose-300 font-medium text-xs tracking-wide uppercase">Get Started</span>
                      </div>
                      
                      <div class="text-center">
                        <h2 class="text-3xl font-semibold text-white mb-4 leading-tight">
                          Ready to Build Your App?
                          <span class="inline-block bg-gradient-to-r from-rose-400 to-pink-400 bg-clip-text text-transparent">No Coding Required!</span>
                        </h2>
                        <p class="text-gray-300 text-lg leading-relaxed mb-8 max-w-2xl mx-auto">
                          Start building your own web application today. Just describe your idea, and let Imagi do the rest.
                        </p>
                        
                        <!-- CTA Buttons -->
                        <div class="flex flex-col sm:flex-row gap-4 justify-center">
                          <router-link 
                            to="/products/oasis/builder/dashboard"
                            class="inline-flex items-center justify-center px-8 py-3 bg-gradient-to-r from-rose-500 to-pink-500 hover:from-rose-400 hover:to-pink-400 text-white font-medium rounded-xl shadow-lg shadow-rose-500/25 transition-all duration-200 transform hover:-translate-y-1"
                          >
                            <i class="fas fa-wand-magic-sparkles mr-2"></i>
                            Start Building
                          </router-link>
                          
                          <router-link 
                            to="/docs"
                            class="inline-flex items-center justify-center px-8 py-3 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-rose-400/30 text-white font-medium rounded-xl transition-all duration-200"
                          >
                            <i class="fas fa-book mr-2"></i>
                            Learn More
                          </router-link>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script>
import { defineComponent } from 'vue'
import { DefaultLayout } from '@/shared/layouts'

export default defineComponent({
  name: 'About',
  components: {
    DefaultLayout
  },
  setup() {
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
    
    const technologies = ['Python', 'Django', 'Vue.js', 'TailwindCSS', 'PostgreSQL', 'Docker', 'OpenAI', 'Anthropic']
    
    // Function to get icon for technology stack items
    const getTechIcon = (tech) => {
      const iconMap = {
        'Python': 'fab fa-python text-blue-400',
        'Django': 'fas fa-server text-green-400',
        'Vue.js': 'fab fa-vuejs text-green-500',
        'TailwindCSS': 'fab fa-css3 text-blue-500',
        'PostgreSQL': 'fas fa-database text-blue-400',
        'Docker': 'fab fa-docker text-blue-500',
        'OpenAI': 'fas fa-brain text-indigo-400',
        'Anthropic': 'fas fa-robot text-violet-400'
      }
      return iconMap[tech] || 'fas fa-code text-gray-400'
    }
    
    return {
      stats,
      visionItems,
      technologies,
      getTechIcon
    }
  }
})
</script>

<style scoped>
/* Completely remove any browser default styling for form inputs */
input, textarea {
  outline: none !important;
  box-shadow: none !important;
  -webkit-appearance: none !important;
  -moz-appearance: none !important;
  appearance: none !important;
}

input:focus, textarea:focus {
  outline: none !important;
  box-shadow: none !important;
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

.delay-700 {
  animation-delay: 700ms;
}
</style>