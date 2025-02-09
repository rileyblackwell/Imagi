<template>
  <DefaultLayout :isHomeNav="true">
    <div class="min-h-screen bg-dark-900">
      <!-- Hero Section -->
      <section class="relative min-h-[60vh] flex items-center justify-center overflow-hidden pt-32 pb-16 sm:pt-36 sm:pb-20">
        <!-- Background Effects -->
        <div class="absolute inset-0 bg-dark-900">
          <div class="absolute inset-0 bg-gradient-to-br from-primary-500/10 via-dark-900 to-violet-500/10"></div>
          <div class="absolute top-20 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-gradient-to-r from-primary-500/20 to-violet-500/20 rounded-full blur-[120px] opacity-70"></div>
        </div>

        <!-- Content -->
        <div class="relative w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div class="mb-8 sm:mb-10">
            <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
              <span class="text-white block mb-2 sm:mb-3">Terms of Service</span>
              <GradientText variant="primary" class="font-bold block text-5xl sm:text-6xl lg:text-7xl">
                Our Agreement
              </GradientText>
            </h1>
            <p class="text-lg sm:text-xl text-gray-300 max-w-2xl mx-auto">
              Please read these terms carefully before using our services.
            </p>
          </div>
        </div>
      </section>

      <!-- Main Content -->
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24 relative">
        <!-- Decorative background elements -->
        <div class="absolute inset-0 overflow-hidden pointer-events-none">
          <div class="absolute -top-40 -right-40 w-80 h-80 bg-primary-500 rounded-full blur-[100px] opacity-20 transform rotate-45"></div>
          <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-violet-500 rounded-full blur-[100px] opacity-20 transform -rotate-45"></div>
        </div>

        <!-- Terms Content -->
        <div class="space-y-12 relative">
          <section v-for="(section, index) in termsSection" :key="index"
                   class="group bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/30 transition-all duration-500"
          >
            <div class="flex items-center mb-8">
              <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mr-4 group-hover:scale-110 transition-transform duration-500">
                <i :class="['text-2xl text-primary-400', section.icon]"></i>
              </div>
              <h2 class="text-2xl sm:text-3xl font-bold text-white group-hover:text-primary-300 transition-colors">
                {{ section.title }}
              </h2>
            </div>
            
            <div class="prose prose-invert max-w-none prose-p:text-gray-300 prose-li:text-gray-300 prose-strong:text-white">
              <p v-if="section.description" class="text-lg mb-6">{{ section.description }}</p>
              <ul v-if="section.items" class="space-y-4">
                <li v-for="(item, itemIndex) in section.items" :key="itemIndex" class="flex items-start">
                  <div class="w-2 h-2 rounded-full bg-primary-400 mt-2.5 mr-3 flex-shrink-0"></div>
                  <span v-if="typeof item === 'string'">{{ item }}</span>
                  <span v-else>
                    <strong class="text-white">{{ item.title }}:</strong> {{ item.description }}
                  </span>
                </li>
              </ul>
            </div>
          </section>

          <!-- Contact Section -->
          <section class="bg-gradient-to-br from-primary-600/90 via-violet-600/90 to-purple-600/90 rounded-2xl p-8 relative overflow-hidden">
            <div class="absolute inset-0">
              <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-10"></div>
            </div>
            
            <div class="relative z-10">
              <div class="flex items-center mb-6">
                <div class="w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center mr-4">
                  <i class="fas fa-envelope text-xl text-white"></i>
                </div>
                <h2 class="text-2xl sm:text-3xl font-bold text-white">Contact Us</h2>
              </div>
              
              <p class="text-lg text-white/90">
                If you have any questions about these Terms, please 
                <router-link to="/contact" 
                  class="text-white font-semibold hover:text-primary-200 underline decoration-primary-400/30 hover:decoration-primary-200 transition-colors"
                >
                  contact us
                </router-link>.
              </p>
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
import { GradientText } from '@/apps/home/components'

export default defineComponent({
  name: 'Terms',
  components: {
    DefaultLayout,
    GradientText
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
</style>