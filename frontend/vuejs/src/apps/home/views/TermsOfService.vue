<!-- Terms of Service Page - Premium Design matching Home -->
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
        <section class="relative min-h-[50vh] flex items-center justify-center overflow-hidden pt-28 pb-16 sm:pt-32 sm:pb-20 md:pt-36 md:pb-24">
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
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-amber-400"></span>
                  </span>
                  <span class="text-sm font-medium text-white/70 tracking-wide">Legal & Agreements</span>
                </div>
              </div>

              <!-- Hero title -->
              <h1 class="text-4xl sm:text-5xl md:text-6xl lg:text-[3.5rem] font-semibold tracking-tight mb-8 leading-[1.1] animate-fade-in-up" style="animation-delay: 100ms">
                <span class="block text-white/90">Terms of Service</span>
                <span class="block mt-3">
                  <span class="relative inline-block">
                    <span class="bg-gradient-to-r from-violet-400 via-fuchsia-400 to-violet-400 bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient-x">
                      Our Agreement
                    </span>
                    <span class="absolute -bottom-2 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-400/50 to-transparent"></span>
                  </span>
                </span>
              </h1>

              <!-- Description -->
              <p class="text-lg sm:text-xl text-white/50 mb-6 max-w-2xl mx-auto leading-relaxed animate-fade-in-up" style="animation-delay: 200ms">
                Please read these terms carefully before using our services. By accessing our platform, you agree to be bound by these terms.
              </p>
              
              <p class="text-sm text-white/40 animate-fade-in-up" style="animation-delay: 300ms">
                Last updated: July 15, 2023
              </p>
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

        <!-- Content Sections -->
        <div class="py-20 md:py-32 px-6 sm:px-8 lg:px-12">
          <div class="max-w-4xl mx-auto space-y-16">
            
            <!-- Sections -->
            <section v-for="(section, index) in sections" :key="index" class="group relative">
              <div class="relative p-6 md:p-8 rounded-2xl border border-white/[0.06] bg-white/[0.02] backdrop-blur-sm hover:bg-white/[0.04] hover:border-white/[0.1] transition-all duration-500 overflow-hidden">
                <!-- Subtle hover glow -->
                <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                  <div class="absolute inset-0 bg-gradient-to-br opacity-[0.03]" :class="getGradientClass(section.color)"></div>
                </div>
                
                <!-- Header -->
                <div class="relative flex items-start gap-4 mb-6">
                  <div 
                    class="flex-shrink-0 inline-flex items-center justify-center w-12 h-12 rounded-xl border transition-all duration-300"
                    :class="getIconContainerClass(section.color)"
                  >
                    <i :class="[section.icon, 'text-lg', getIconClass(section.color)]"></i>
                  </div>
                  <div class="flex-1">
                    <div class="inline-flex items-center gap-2 px-3 py-1 bg-white/[0.03] rounded-full border border-white/[0.08] mb-3">
                      <div class="w-1.5 h-1.5 rounded-full animate-pulse" :class="getDotClass(section.color)"></div>
                      <span class="text-xs font-medium text-white/60 uppercase tracking-wider">{{ section.badge }}</span>
                    </div>
                    <h2 class="text-xl md:text-2xl font-semibold text-white/90">{{ section.title }}</h2>
                  </div>
                </div>
                
                <!-- Content -->
                <div class="relative space-y-4">
                  <p v-if="section.description" class="text-white/50 leading-relaxed">{{ section.description }}</p>
                  
                  <!-- List items if present -->
                  <div v-if="section.items" class="space-y-3 mt-6">
                    <div v-for="(item, itemIndex) in section.items" :key="itemIndex" 
                         class="flex items-start gap-3 p-4 bg-white/[0.03] rounded-xl border border-white/[0.06]">
                      <div class="w-2 h-2 rounded-full mt-2 flex-shrink-0" :class="getDotClass(section.color)"></div>
                      <div class="flex-1">
                        <span v-if="item.title" class="text-white/90 font-medium">{{ item.title }}: </span>
                        <span class="text-white/50">{{ item.text }}</span>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Simple list if present -->
                  <div v-if="section.simpleItems" class="space-y-3 mt-6">
                    <div v-for="(item, itemIndex) in section.simpleItems" :key="itemIndex" 
                         class="flex items-start gap-3 p-4 bg-white/[0.03] rounded-xl border border-white/[0.06]">
                      <div class="w-2 h-2 rounded-full mt-1.5 flex-shrink-0" :class="getDotClass(section.color)"></div>
                      <span class="text-white/50">{{ item }}</span>
                    </div>
                  </div>
                  
                  <!-- Grid items if present -->
                  <div v-if="section.gridItems" class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-6">
                    <div v-for="(item, itemIndex) in section.gridItems" :key="itemIndex" 
                         class="flex items-start gap-3 p-4 bg-white/[0.03] rounded-xl border border-white/[0.06]">
                      <div class="w-2 h-2 rounded-full mt-1.5 flex-shrink-0" :class="getDotClass(section.color)"></div>
                      <span class="text-white/50 text-sm">{{ item }}</span>
                    </div>
                  </div>
                </div>

                <!-- Bottom accent line on hover -->
                <div 
                  class="absolute bottom-0 left-0 right-0 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                  :class="getAccentLineClass(section.color)"
                ></div>
              </div>
            </section>

            <!-- CTA Section -->
            <section class="py-8">
              <div class="group relative">
                <!-- Background glow -->
                <div class="absolute -inset-1 bg-gradient-to-r from-violet-600/20 via-fuchsia-600/20 to-violet-600/20 rounded-3xl blur-xl opacity-50 group-hover:opacity-70 transition-opacity duration-500"></div>
                
                <div class="relative p-8 md:p-10 rounded-2xl border border-white/[0.08] bg-[#0a0a0f]/80 backdrop-blur-xl overflow-hidden text-center">
                  <!-- Accent line -->
                  <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-500/50 to-transparent"></div>
                  
                  <div class="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 border border-violet-500/20 mb-6">
                    <i class="fas fa-file-contract text-violet-400 text-xl"></i>
                  </div>
                  
                  <h2 class="text-2xl md:text-3xl font-semibold text-white/90 mb-4">
                    Questions About Our Terms?
                  </h2>
                  <p class="text-white/50 mb-8 max-w-xl mx-auto">
                    We're here to help you understand our terms and conditions. Reach out with any questions.
                  </p>
                  
                  <router-link 
                    to="/contact"
                    class="group/btn inline-flex items-center justify-center gap-2 px-7 py-3.5 bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-xl text-white font-medium shadow-lg shadow-violet-500/25 hover:shadow-xl hover:shadow-violet-500/30 transition-all duration-300 hover:-translate-y-0.5"
                  >
                    <i class="fas fa-envelope"></i>
                    <span>Contact Us</span>
                    <i class="fas fa-arrow-right text-sm transform group-hover/btn:translate-x-1 transition-transform duration-300"></i>
                  </router-link>
                  
                  <!-- Decorative elements -->
                  <div class="absolute -bottom-20 -right-20 w-40 h-40 bg-violet-500/5 rounded-full blur-3xl"></div>
                  <div class="absolute -top-20 -left-20 w-32 h-32 bg-fuchsia-500/5 rounded-full blur-3xl"></div>
                </div>
              </div>
            </section>
          </div>
        </div>
      </main>
    </div>
  </DefaultLayout>
</template>

<script>
import { defineComponent } from 'vue'
import { DefaultLayout } from '@/shared/layouts'

export default defineComponent({
  name: 'TermsOfService',
  components: {
    DefaultLayout
  },
  setup() {
    const sections = [
      {
        badge: 'Introduction',
        title: 'Welcome to Imagi Oasis',
        icon: 'fas fa-handshake',
        color: 'violet',
        description: 'Welcome to Imagi Oasis. Our Terms of Service govern your use of our platform and services. By using Imagi Oasis, you agree to these terms in their entirety. These terms were last updated on July 15, 2023. We may update these terms from time to time, so please check this page occasionally to ensure you\'re aware of any changes.'
      },
      {
        badge: 'Acceptance',
        title: 'Acceptance of Terms',
        icon: 'fas fa-check-circle',
        color: 'blue',
        description: 'By accessing or using Imagi\'s services, including our AI-powered website builder ("Imagi Oasis"), you acknowledge that you have read, understood, and agree to be bound by these Terms of Service. If you do not agree to these terms, you must not access or use our services. By using our services, you represent that you have the legal capacity to enter into a binding agreement.'
      },
      {
        badge: 'Prohibited Uses',
        title: 'Prohibited Activities',
        icon: 'fas fa-ban',
        color: 'rose',
        description: 'You are strictly prohibited from using Imagi\'s services for any unlawful or unauthorized purposes.',
        simpleItems: [
          'Creating any illegal products, services, applications, or content that violates applicable laws',
          'Developing applications that promote, facilitate, or enable illegal activities',
          'Building systems designed to harm, defraud, exploit, or harass others',
          'Attempting to reverse engineer, decompile, or access non-public parts of our services',
          'Using our services to spread malware, viruses, or other harmful code'
        ]
      },
      {
        badge: 'Service',
        title: 'Service Description & Limitations',
        icon: 'fas fa-cube',
        color: 'emerald',
        description: 'Imagi provides an AI-powered platform for generating code and websites. Please be aware of the following service limitations.',
        gridItems: [
          'Our services are provided "as is" without warranties',
          'We may modify, suspend, or discontinue services',
          'Generated code requires review and testing',
          'Usage limits may apply to maintain quality'
        ]
      },
      {
        badge: 'Responsibilities',
        title: 'User Responsibilities',
        icon: 'fas fa-user-shield',
        color: 'amber',
        description: 'Users must adhere to our conduct guidelines and maintain responsible use of our platform.',
        items: [
          { title: 'Account Security', text: 'Maintain security and confidentiality of credentials' },
          { title: 'Accurate Information', text: 'Provide complete and up-to-date information' },
          { title: 'Legal Compliance', text: 'Comply with all applicable laws and regulations' },
          { title: 'Security Measures', text: 'Implement appropriate security for your applications' }
        ]
      },
      {
        badge: 'Intellectual Property',
        title: 'Intellectual Property Rights',
        icon: 'fas fa-copyright',
        color: 'fuchsia',
        description: 'Understanding ownership and usage rights for content created on our platform.',
        items: [
          { title: 'Your Content', text: 'You retain ownership of the content and applications you create' },
          { title: 'Our Platform', text: 'Imagi retains all rights to our platform, technology, and branding' },
          { title: 'Generated Code', text: 'Code generated through our AI tools is licensed for your use' },
          { title: 'Feedback', text: 'Any feedback you provide may be used to improve our services' }
        ]
      }
    ]
    
    const getGradientClass = (color) => {
      const gradients = {
        violet: 'from-violet-500 to-purple-500',
        blue: 'from-blue-500 to-cyan-500',
        emerald: 'from-emerald-500 to-teal-500',
        amber: 'from-amber-500 to-orange-500',
        fuchsia: 'from-fuchsia-500 to-pink-500',
        rose: 'from-rose-500 to-red-500'
      }
      return gradients[color] || gradients.violet
    }
    
    const getIconContainerClass = (color) => {
      const classes = {
        violet: 'bg-violet-500/10 border-violet-500/20 group-hover:bg-violet-500/15 group-hover:border-violet-500/30',
        blue: 'bg-blue-500/10 border-blue-500/20 group-hover:bg-blue-500/15 group-hover:border-blue-500/30',
        emerald: 'bg-emerald-500/10 border-emerald-500/20 group-hover:bg-emerald-500/15 group-hover:border-emerald-500/30',
        amber: 'bg-amber-500/10 border-amber-500/20 group-hover:bg-amber-500/15 group-hover:border-amber-500/30',
        fuchsia: 'bg-fuchsia-500/10 border-fuchsia-500/20 group-hover:bg-fuchsia-500/15 group-hover:border-fuchsia-500/30',
        rose: 'bg-rose-500/10 border-rose-500/20 group-hover:bg-rose-500/15 group-hover:border-rose-500/30'
      }
      return classes[color] || classes.violet
    }
    
    const getIconClass = (color) => {
      const classes = {
        violet: 'text-violet-400',
        blue: 'text-blue-400',
        emerald: 'text-emerald-400',
        amber: 'text-amber-400',
        fuchsia: 'text-fuchsia-400',
        rose: 'text-rose-400'
      }
      return classes[color] || classes.violet
    }
    
    const getDotClass = (color) => {
      const classes = {
        violet: 'bg-violet-400',
        blue: 'bg-blue-400',
        emerald: 'bg-emerald-400',
        amber: 'bg-amber-400',
        fuchsia: 'bg-fuchsia-400',
        rose: 'bg-rose-400'
      }
      return classes[color] || classes.violet
    }
    
    const getAccentLineClass = (color) => {
      const classes = {
        violet: 'bg-gradient-to-r from-transparent via-violet-500/50 to-transparent',
        blue: 'bg-gradient-to-r from-transparent via-blue-500/50 to-transparent',
        emerald: 'bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent',
        amber: 'bg-gradient-to-r from-transparent via-amber-500/50 to-transparent',
        fuchsia: 'bg-gradient-to-r from-transparent via-fuchsia-500/50 to-transparent',
        rose: 'bg-gradient-to-r from-transparent via-rose-500/50 to-transparent'
      }
      return classes[color] || classes.violet
    }
    
    return {
      sections,
      getGradientClass,
      getIconContainerClass,
      getIconClass,
      getDotClass,
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
