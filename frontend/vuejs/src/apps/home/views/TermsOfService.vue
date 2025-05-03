<template>
  <DefaultLayout :isHomeNav="true">
    <div class="min-h-screen bg-dark-950 relative overflow-hidden">
      <!-- Enhanced Background Effects matching other pages -->
      <div class="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <!-- Gradient orbs -->
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
          <!-- Enhanced section header to match other pages -->
          <div class="inline-block px-4 py-1.5 bg-primary-500/10 rounded-full mb-3">
            <span class="text-primary-400 font-semibold text-sm tracking-wider">LEGAL & AGREEMENTS</span>
          </div>
          
          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
            <span class="text-white block mb-2 sm:mb-3">Terms of Service</span>
            <GradientText variant="primary" class="font-bold block text-5xl sm:text-6xl lg:text-7xl">
              Our Agreement
            </GradientText>
          </h1>
          
          <p class="text-xl text-gray-300 mb-12 sm:mb-16 max-w-3xl mx-auto leading-relaxed">
            Please read these terms carefully before using our services.
          </p>
        </div>
      </section>

      <!-- Divider with animated line matching other pages -->
      <div class="relative h-16 max-w-7xl mx-auto">
        <div class="absolute inset-x-0 h-px mx-auto w-2/3 sm:w-1/2 bg-gradient-to-r from-transparent via-primary-500/30 to-transparent animate-pulse-slow"></div>
      </div>

      <!-- Main Content -->
      <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24 relative">
        <!-- Introduction -->
        <div class="relative mb-16">
          <div class="group relative transform transition-all duration-300 hover:-translate-y-2">
            <!-- Enhanced glass morphism effect with glow -->
            <div class="absolute -inset-0.5 bg-gradient-to-r from-indigo-500/50 to-blue-500/50 rounded-2xl opacity-0 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"></div>
            
            <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden h-full flex flex-col border border-dark-800/50 group-hover:border-primary-500/30 transition-all duration-300">
              <!-- Card header with gradient -->
              <div class="h-2 w-full bg-gradient-to-r from-indigo-500 to-blue-500"></div>
              <div class="p-8">
                <p class="text-lg text-gray-300 mb-4">
                  Welcome to Imagi Oasis. Our Terms of Service govern your use of our platform and services. By using Imagi Oasis, you agree to these terms in their entirety.
                </p>
                <p class="text-lg text-gray-300">
                  These terms were last updated on July 15, 2023. We may update these terms from time to time, so please check this page occasionally to ensure you're aware of any changes.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Terms Content -->
        <div class="space-y-12 relative z-10">
          <SectionHeader 
            title="Terms of Service" 
            subtitle="Please familiarize yourself with our terms before using Imagi Oasis."
          />
          
          <!-- Terms Sections -->
          <div class="space-y-12">
            <!-- Acceptance of Terms Section -->
            <div class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl border border-dark-700/40 transition-all duration-300 hover:border-primary-500/30 hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)]">
              <div class="p-7">
                <div class="flex items-center gap-4 mb-5">
                  <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-indigo-500 flex items-center justify-center shadow-md">
                    <i class="fas fa-check-circle text-white text-xl"></i>
                  </div>
                  <h2 class="text-2xl font-bold text-white">Acceptance of Terms</h2>
                </div>
                <p class="text-gray-300 mb-5">{{ termsSection[0].description }}</p>
              </div>
            </div>

            <!-- Prohibited Uses Section -->
            <div class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl border border-dark-700/40 transition-all duration-300 hover:border-violet-500/30 hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)]">
              <div class="p-7">
                <div class="flex items-center gap-4 mb-5">
                  <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500 to-purple-500 flex items-center justify-center shadow-md">
                    <i class="fas fa-ban text-white text-xl"></i>
                  </div>
                  <h2 class="text-2xl font-bold text-white">Prohibited Uses</h2>
                </div>
                <p class="text-gray-300 mb-5">{{ termsSection[1].description }}</p>
              </div>
              
              <div class="px-7 pb-7">
                <div class="bg-dark-900/50 backdrop-blur-sm rounded-xl p-5 border border-dark-800">
                  <ul class="space-y-4">
                    <li v-for="(item, index) in termsSection[1].items" :key="index" class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-violet-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>{{ item }}</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Service Description Section -->
            <div class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl border border-dark-700/40 transition-all duration-300 hover:border-indigo-500/30 hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)]">
              <div class="p-7">
                <div class="flex items-center gap-4 mb-5">
                  <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-blue-500 flex items-center justify-center shadow-md">
                    <i class="fas fa-cube text-white text-xl"></i>
                  </div>
                  <h2 class="text-2xl font-bold text-white">Service Description and Limitations</h2>
                </div>
                <p class="text-gray-300 mb-5">{{ termsSection[2].description }}</p>
              </div>
              
              <div class="px-7 pb-7">
                <div class="bg-dark-900/50 backdrop-blur-sm rounded-xl p-5 border border-dark-800">
                  <ul class="space-y-4">
                    <li v-for="(item, index) in termsSection[2].items" :key="index" class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-indigo-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>{{ item }}</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- User Responsibilities Section -->
            <div class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl border border-dark-700/40 transition-all duration-300 hover:border-purple-500/30 hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)]">
              <div class="p-7">
                <div class="flex items-center gap-4 mb-5">
                  <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-fuchsia-500 flex items-center justify-center shadow-md">
                    <i class="fas fa-user-shield text-white text-xl"></i>
                  </div>
                  <h2 class="text-2xl font-bold text-white">User Responsibilities and Conduct</h2>
                </div>
                <p class="text-gray-300 mb-5">{{ termsSection[3].description }}</p>
              </div>
              
              <div class="px-7 pb-7">
                <div class="bg-dark-900/50 backdrop-blur-sm rounded-xl p-5 border border-dark-800">
                  <ul class="space-y-4">
                    <li v-for="(item, index) in termsSection[3].items" :key="index" class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-purple-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>{{ item }}</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <!-- Divider -->
          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-dark-700"></div>
            </div>
            <div class="relative flex justify-center">
              <span class="bg-dark-900 px-4 text-sm text-gray-400">Additional Information</span>
            </div>
          </div>

          <!-- Additional Information -->
          <SectionHeader 
            title="Additional Terms" 
            subtitle="Further important information about using our services."
          />

          <!-- Additional sections -->
          <div class="space-y-12">
            <!-- Payment Terms Section -->
            <div class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl border border-dark-700/40 transition-all duration-300 hover:border-green-500/30 hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)]">
              <div class="p-7">
                <div class="flex items-center gap-4 mb-5">
                  <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-teal-500 flex items-center justify-center shadow-md">
                    <i class="fas fa-credit-card text-white text-xl"></i>
                  </div>
                  <h2 class="text-2xl font-bold text-white">Payment Terms and Billing</h2>
                </div>
              </div>
              
              <div class="px-7 pb-7">
                <div class="bg-dark-900/50 backdrop-blur-sm rounded-xl p-5 border border-dark-800">
                  <ul class="space-y-4">
                    <li v-for="(item, index) in termsSection[4].items" :key="index" class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-green-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>
                        <strong class="text-white">{{ item.title }}:</strong> {{ item.description }}
                      </span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Intellectual Property Rights -->
            <div class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl border border-dark-700/40 transition-all duration-300 hover:border-primary-500/30 hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)]">
              <div class="p-7">
                <div class="flex items-center gap-4 mb-5">
                  <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-indigo-500 flex items-center justify-center shadow-md">
                    <i class="fas fa-copyright text-white text-xl"></i>
                  </div>
                  <h2 class="text-2xl font-bold text-white">Intellectual Property Rights</h2>
                </div>
                <p class="text-gray-300 mb-5">{{ termsSection[5].description }}</p>
              </div>
              
              <div class="px-7 pb-7">
                <div class="bg-dark-900/50 backdrop-blur-sm rounded-xl p-5 border border-dark-800">
                  <ul class="space-y-4">
                    <li v-for="(item, index) in termsSection[5].items" :key="index" class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-primary-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>
                        <strong class="text-white">{{ item.title }}:</strong> {{ item.description }}
                      </span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Limitation of Liability and Termination (2 column) -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <!-- Limitation of Liability -->
              <div class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl border border-dark-700/40 transition-all duration-300 hover:border-violet-500/30 hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)]">
                <div class="p-7">
                  <div class="flex items-center gap-4 mb-5">
                    <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500 to-purple-500 flex items-center justify-center shadow-md">
                      <i class="fas fa-shield-halved text-white text-xl"></i>
                    </div>
                    <h2 class="text-2xl font-bold text-white">Limitation of Liability</h2>
                  </div>
                  <p class="text-gray-300 mb-5">{{ termsSection[6].description }}</p>
                </div>
                
                <div class="px-7 pb-7">
                  <div class="bg-dark-900/50 backdrop-blur-sm rounded-xl p-5 border border-dark-800">
                    <ul class="space-y-4">
                      <li v-for="(item, index) in termsSection[6].items" :key="index" class="flex items-start">
                        <div class="w-2 h-2 rounded-full bg-violet-400 mt-2.5 mr-3 flex-shrink-0"></div>
                        <span>{{ item }}</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
              
              <!-- Termination -->
              <div class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl border border-dark-700/40 transition-all duration-300 hover:border-indigo-500/30 hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)]">
                <div class="p-7">
                  <div class="flex items-center gap-4 mb-5">
                    <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-blue-500 flex items-center justify-center shadow-md">
                      <i class="fas fa-door-closed text-white text-xl"></i>
                    </div>
                    <h2 class="text-2xl font-bold text-white">Termination</h2>
                  </div>
                  <p class="text-gray-300 mb-5">{{ termsSection[7].description }}</p>
                </div>
                
                <div class="px-7 pb-7">
                  <div class="bg-dark-900/50 backdrop-blur-sm rounded-xl p-5 border border-dark-800">
                    <ul class="space-y-4">
                      <li v-for="(item, index) in termsSection[7].items" :key="index" class="flex items-start">
                        <div class="w-2 h-2 rounded-full bg-indigo-400 mt-2.5 mr-3 flex-shrink-0"></div>
                        <span>{{ item }}</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Enhanced CTA Section -->
          <section>
            <div class="group relative transform transition-all duration-300 hover:-translate-y-2">
              <!-- Enhanced glass morphism effect with stronger gradient glow -->
              <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500/70 to-violet-500/70 rounded-2xl opacity-70 group-hover:opacity-90 blur group-hover:blur-md transition-all duration-300"></div>
              
              <div class="relative bg-dark-900/70 backdrop-blur-xl rounded-xl overflow-hidden border border-primary-500/30 group-hover:border-primary-500/50 transition-all duration-300">
                <div class="h-3 w-full bg-gradient-to-r from-primary-500 to-violet-500"></div>
                <!-- Decorative Elements -->
                <div class="absolute inset-0 pointer-events-none">
                  <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-10"></div>
                </div>

                <!-- Content -->
                <div class="relative z-10 px-6 py-12 md:px-12 text-center">
                  <h2 class="text-3xl md:text-4xl font-bold text-white mb-4">
                    Questions About
                    <span class="bg-gradient-to-r from-primary-300 to-violet-300 bg-clip-text text-transparent">
                      Our Terms?
                    </span>
                  </h2>

                  <p class="text-lg text-white/90 mb-8 max-w-xl mx-auto">
                    We're here to help you understand our terms and conditions. Reach out with any questions.
                  </p>

                  <!-- Action Buttons -->
                  <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
                    <HomeNavbarButton
                      to="/contact"
                      class="group relative w-full sm:w-auto min-w-[200px] !h-12 px-6 rounded-xl bg-white/10 hover:bg-white/20 border border-white/30 hover:border-white/50 transition-all duration-300 transform hover:-translate-y-1"
                    >
                      <span class="relative z-10 flex items-center justify-center text-lg font-bold text-white">
                        Contact Us
                      </span>
                    </HomeNavbarButton>
                  </div>
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
import { defineComponent } from 'vue'
import { DefaultLayout } from '@/shared/layouts'
import { 
  GradientText,
  HeroBadge,
  HomeNavbarButton,
  CardContainer,
  SectionHeader 
} from '@/apps/home/components'

export default defineComponent({
  name: 'Terms',
  components: {
    DefaultLayout,
    GradientText,
    HeroBadge,
    HomeNavbarButton,
    CardContainer,
    SectionHeader
  },
  setup() {
    const termsSection = [
      {
        title: 'Acceptance of Terms',
        icon: 'fas fa-check-circle',
        description: 'By accessing or using Imagi\'s services, including our AI-powered website builder ("Imagi Oasis"), you acknowledge that you have read, understood, and agree to be bound by these Terms of Service. If you do not agree to these terms, you must not access or use our services. By using our services, you represent that you have the legal capacity to enter into a binding agreement.'
      },
      {
        title: 'Prohibited Uses',
        icon: 'fas fa-ban',
        description: 'You are strictly prohibited from using Imagi\'s services for any unlawful or unauthorized purposes. Violations may result in immediate account termination and potential legal action. Prohibited activities include:',
        items: [
          'Creating any illegal products, services, applications, or content that violates applicable laws',
          'Developing applications that promote, facilitate, or enable illegal activities, including but not limited to fraud, terrorism, or trafficking',
          'Generating content that violates laws, regulations, or third-party rights',
          'Building systems designed to harm, defraud, exploit, or harass others',
          'Any activities that violate intellectual property rights, export control laws, or data protection regulations',
          'Attempting to reverse engineer, decompile, or access non-public parts of our services',
          'Using our services to spread malware, viruses, or other harmful code',
          'Engaging in activities that could damage Imagi\'s reputation or infrastructure'
        ]
      },
      {
        title: 'Service Description and Limitations',
        icon: 'fas fa-cube',
        description: 'Imagi provides an AI-powered platform for generating code and websites. While we strive for excellence, you acknowledge that:',
        items: [
          'Our services are provided "as is" without warranties of any kind',
          'We may modify, suspend, or discontinue services at any time',
          'We do not guarantee uninterrupted or error-free service',
          'Generated code and applications require review and testing',
          'You are responsible for compliance with applicable laws and regulations',
          'We may impose usage limits or restrictions to maintain service quality'
        ]
      },
      {
        title: 'User Responsibilities and Conduct',
        icon: 'fas fa-user-shield',
        description: 'Users of Imagi\'s services have specific responsibilities and must adhere to our conduct guidelines:',
        items: [
          'Maintain account security and confidentiality of credentials',
          'Provide accurate, complete, and up-to-date information',
          'Comply with all applicable laws, regulations, and industry standards',
          'Report any security vulnerabilities or suspicious activities',
          'Take responsibility for all activities under your account',
          'Implement appropriate security measures for your applications',
          'Regularly backup your data and code',
          'Respect the intellectual property rights of others'
        ]
      },
      {
        title: 'Payment Terms and Billing',
        icon: 'fas fa-credit-card',
        items: [
          { title: 'Non-Refundable Payments', description: 'All payments are final and non-refundable unless explicitly required by law or stated otherwise' },
          { title: 'Subscription Terms', description: 'Recurring fees are automatically charged at the start of each billing cycle until cancellation' },
          { title: 'Price Changes', description: 'We reserve the right to modify pricing with 30 days notice for existing subscribers' },
          { title: 'Payment Processing', description: 'You must provide valid payment information and authorize us to charge your payment method' },
          { title: 'Failed Payments', description: 'Service access may be suspended or terminated for failed payments or chargebacks' },
          { title: 'Taxes', description: 'You are responsible for all applicable taxes and governmental charges' }
        ]
      },
      {
        title: 'Intellectual Property Rights',
        icon: 'fas fa-copyright',
        description: 'Our intellectual property rights are fundamental to our business:',
        items: [
          { title: 'Ownership', description: 'All service-related intellectual property belongs to Imagi, including systems, code, and designs' },
          { title: 'User Content', description: 'You retain rights to your content while granting us necessary licenses to provide services' },
          { title: 'Restrictions', description: 'No right to copy, modify, or create derivative works without explicit permission' },
          { title: 'Feedback', description: 'Any feedback or suggestions you provide may be used without obligation or compensation' }
        ]
      },
      {
        title: 'Limitation of Liability',
        icon: 'fas fa-shield-halved',
        description: 'To the maximum extent permitted by law:',
        items: [
          'We are not liable for indirect, incidental, special, or consequential damages',
          'Our total liability is limited to the amount paid for services in the past 12 months',
          'We do not warrant the accuracy, completeness, or reliability of generated code',
          'You agree to indemnify us against claims arising from your use of services',
          'We are not responsible for third-party services or content'
        ]
      },
      {
        title: 'Termination',
        icon: 'fas fa-door-closed',
        description: 'We reserve the right to terminate or suspend access to our services:',
        items: [
          'For violations of these terms or applicable laws',
          'Without prior notice if necessary to protect our services or other users',
          'For extended periods of account inactivity',
          'When required by law or regulation',
          'Upon account deletion, certain data may be permanently deleted'
        ]
      }
    ]

    return {
      termsSection
    }
  }
})
</script>

<style scoped>
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

/* Simple list styling without generated bullets */
ul {
  @apply pl-0 mb-4;
  list-style: none;
}

ul li {
  @apply mb-3 text-gray-300;
}

/* Remove any generated bullets */
ul li::before, 
ul li::marker {
  content: none;
}

/* Styling for circular bullet points (handled in markup) */
.w-2.h-2.rounded-full {
  @apply bg-gradient-to-r from-primary-400 to-violet-400;
  box-shadow: 0 0 6px rgba(139, 92, 246, 0.5);
}

h3 {
  @apply text-xl font-bold text-white mb-4;
}

h4 {
  @apply text-lg font-semibold text-white mb-3;
}

p {
  @apply mb-4 text-gray-300;
}

p:last-child {
  @apply mb-0;
}
</style>