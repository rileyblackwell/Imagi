<!-- About Page - Premium Design matching Home -->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="min-h-screen bg-[#050509] relative overflow-hidden">
      <!-- Ultra Premium Background System (match Home) -->
      <div class="fixed inset-0 pointer-events-none">
        <!-- Deep space base with richer gradients -->
        <div class="absolute inset-0 bg-gradient-to-b from-[#08081a] via-[#050509] to-[#020204]"></div>

        <!-- Animated mesh gradient layer -->
        <div class="absolute inset-0 opacity-95">
          <div class="absolute inset-0 bg-[radial-gradient(ellipse_120%_80%_at_50%_-20%,rgba(124,58,237,0.22),transparent_50%)] animate-pulse-slow"></div>
          <div class="absolute inset-0 bg-[radial-gradient(ellipse_90%_70%_at_90%_20%,rgba(139,92,246,0.15),transparent_45%)] animate-drift"></div>
          <div class="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_5%_60%,rgba(217,70,239,0.10),transparent_40%)] animate-drift-reverse"></div>
          <div class="absolute inset-0 bg-[radial-gradient(ellipse_60%_50%_at_50%_100%,rgba(79,70,229,0.12),transparent_50%)]"></div>
        </div>

        <!-- Refined grid pattern -->
        <div class="absolute inset-0 opacity-[0.025]" style="background-image: linear-gradient(rgba(139,92,246,0.4) 1px, transparent 1px), linear-gradient(90deg, rgba(139,92,246,0.4) 1px, transparent 1px); background-size: 80px 80px;"></div>

        <!-- Premium noise texture -->
        <div class="absolute inset-0 opacity-[0.015]" style="background-image: url('data:image/svg+xml,%3Csvg viewBox=%220 0 512 512%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noise%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.7%22 numOctaves=%224%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noise)%22/%3E%3C/svg%3E');"></div>

        <!-- Northern lights aurora -->
        <div class="absolute top-0 left-0 right-0 h-[800px] overflow-hidden">
          <div class="absolute inset-x-[5%] top-0 h-full opacity-45 animate-aurora">
            <div class="absolute inset-0 bg-gradient-to-b from-violet-500/30 via-fuchsia-500/15 to-transparent blur-[140px] transform rotate-[-2deg]"></div>
          </div>
          <div class="absolute inset-x-[15%] top-0 h-[600px] opacity-30 animate-aurora-delayed">
            <div class="absolute inset-0 bg-gradient-to-b from-cyan-400/15 via-violet-400/10 to-transparent blur-[120px] transform rotate-[1deg]"></div>
          </div>
        </div>

        <!-- Floating luminous orbs -->
        <div class="absolute top-[10%] right-[5%] w-[700px] h-[700px] rounded-full bg-gradient-to-br from-violet-600/10 via-indigo-600/6 to-transparent blur-[180px] animate-float-slow"></div>
        <div class="absolute bottom-[10%] left-[0%] w-[600px] h-[600px] rounded-full bg-gradient-to-tr from-fuchsia-600/8 via-purple-600/5 to-transparent blur-[160px] animate-float-delayed"></div>
        <div class="absolute top-[50%] right-[20%] w-[400px] h-[400px] rounded-full bg-gradient-to-bl from-amber-500/6 via-rose-500/4 to-transparent blur-[120px] animate-float-reverse"></div>
        <div class="absolute top-[30%] left-[10%] w-[350px] h-[350px] rounded-full bg-gradient-to-br from-cyan-500/5 to-transparent blur-[100px] animate-float-gentle"></div>

        <!-- Additional subtle accent orb -->
        <div class="absolute top-[70%] left-[40%] w-[300px] h-[300px] rounded-full bg-gradient-to-br from-emerald-500/4 to-transparent blur-[100px] animate-float-slow" style="animation-delay: -10s;"></div>
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

        <!-- Elegant Divider with Glow (match Home) -->
        <div class="relative py-12 md:py-16 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
          <div class="relative flex items-center justify-center">
            <div class="flex-1 h-px bg-gradient-to-r from-transparent via-white/[0.12] to-transparent"></div>
            <div class="mx-10 flex items-center gap-4">
              <div class="w-1.5 h-1.5 rounded-full bg-violet-400/40 animate-pulse"></div>
              <div class="relative w-2.5 h-2.5">
                <div class="absolute inset-0 rounded-full bg-gradient-to-br from-violet-400 to-fuchsia-400 opacity-70 animate-pulse"></div>
                <div class="absolute -inset-1.5 rounded-full bg-violet-400/25 blur-md"></div>
              </div>
              <div class="w-1.5 h-1.5 rounded-full bg-violet-400/40 animate-pulse"></div>
            </div>
            <div class="flex-1 h-px bg-gradient-to-r from-transparent via-white/[0.12] to-transparent"></div>
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
        <div class="relative py-12 md:py-16 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
          <div class="relative h-px">
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/[0.10] to-transparent"></div>
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-violet-500/12 to-transparent blur-sm"></div>
          </div>
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
        <div class="relative py-12 md:py-16 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
          <div class="relative h-px">
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/[0.10] to-transparent"></div>
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-violet-500/12 to-transparent blur-sm"></div>
          </div>
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
        <div class="relative py-12 md:py-16 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
          <div class="relative h-px">
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/[0.10] to-transparent"></div>
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-violet-500/12 to-transparent blur-sm"></div>
          </div>
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
        <div class="relative py-12 md:py-16 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
          <div class="relative h-px">
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/[0.10] to-transparent"></div>
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-violet-500/12 to-transparent blur-sm"></div>
          </div>
        </div>
              
              <!-- CTA Section (reuse Home component) -->
        <CTASection 
          icon="fas fa-rocket"
          title="Ready to Build Your App?"
          highlightedText="No Coding Required!"
          description="Start building your own web application today. Just describe your idea, and let Imagi do the rest."
          highlightedStat=""
          descriptionSuffix=""
          primaryButtonText="Start Building"
          primaryButtonTo="/products/oasis/builder/dashboard"
          :showSecondaryButton="true"
          secondaryButtonText="Learn More"
          secondaryButtonTo="/docs"
          secondaryButtonIcon="fas fa-book"
        />
      </main>
    </div>
  </DefaultLayout>
</template>

<script>
import { defineComponent } from 'vue'
import { DefaultLayout } from '@/shared/layouts'
import { CTASection } from '@/apps/home/components/organisms/sections'

export default defineComponent({
  name: 'About',
  components: {
    DefaultLayout,
    CTASection
  },
  setup() {
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
