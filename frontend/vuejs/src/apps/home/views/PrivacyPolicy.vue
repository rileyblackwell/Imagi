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
              <span class="text-white block mb-2 sm:mb-3">Privacy Policy</span>
              <GradientText variant="primary" class="font-bold block text-5xl sm:text-6xl lg:text-7xl">
                Your Privacy Matters
              </GradientText>
            </h1>
            <p class="text-lg sm:text-xl text-gray-300 max-w-2xl mx-auto">
              We are committed to protecting your privacy and ensuring the security of your personal information.
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

        <!-- Privacy Content -->
        <div class="space-y-12 relative">
          <!-- Information Section -->
          <section v-for="(section, index) in privacySections" :key="index"
            class="group bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/30 transition-all duration-500"
          >
            <div class="flex items-center mb-8">
              <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mr-4 group-hover:scale-110 transition-transform duration-500">
                <i :class="['text-2xl text-primary-400', section.icon]"></i>
              </div>
              <h2 class="text-2xl sm:text-3xl font-bold text-white group-hover:text-primary-300 transition-colors duration-300">
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
                If you have any questions or concerns about this Privacy Policy, please 
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
  name: 'PrivacyPolicy',
  components: {
    DefaultLayout,
    GradientText
  },
  setup() {
    const privacySections = [
      {
        title: 'Information We Collect',
        icon: 'fas fa-database',
        description: 'We collect the following types of information to provide and improve our services:',
        items: [
          'Account Information: Your name, email address, password, and other details provided during account registration.',
          'Profile Information: Details you provide to customize your user profile.',
          'Payment Information: Billing details and transaction data processed securely via third-party payment providers.',
          'Usage Data: Information about your interactions with our services.'
        ]
      },
      {
        title: 'How We Use Your Information',
        icon: 'fas fa-cog',
        description: 'We use the collected information for the following purposes:',
        items: [
          'To provide, maintain, and improve our services',
          'To process payments securely and efficiently',
          'To send technical notices and support messages',
          'To analyze usage trends and enhance user experience',
          'To detect, prevent, and address technical issues'
        ]
      },
      {
        title: 'Information Sharing',
        icon: 'fas fa-share-nodes',
        description: 'Your personal information is not sold. However, we may share your data in the following situations:',
        items: [
          { title: 'Service Providers', description: 'Trusted third-party providers that support our operations.' },
          { title: 'Legal Obligations', description: 'To comply with laws, regulations, or legal requests.' },
          { title: 'Professional Advisors', description: 'Consultants, auditors, or legal counsel for business purposes.' },
          { title: 'Business Transfers', description: 'In the event of a merger, sale, or acquisition.' }
        ]
      },
      {
        title: 'Data Security',
        icon: 'fas fa-shield-halved',
        description: 'We prioritize the security of your personal information by implementing industry-standard measures, including:',
        items: [
          'Encryption of sensitive data during transmission and storage',
          'Secure server infrastructure with access controls',
          'Regular security audits and monitoring for vulnerabilities',
          'Employee training on security best practices'
        ]
      },
      {
        title: 'Your Rights',
        icon: 'fas fa-user-shield',
        description: 'You have certain rights regarding your personal information:',
        items: [
          { title: 'Access', description: 'Request access to your personal data.' },
          { title: 'Correction', description: 'Update or correct inaccurate data.' },
          { title: 'Deletion', description: 'Request deletion of your personal data.' },
          { title: 'Portability', description: 'Receive your data in a structured, commonly used format.' }
        ]
      }
    ]

    return {
      privacySections
    }
  }
})
</script>

<style scoped>
/* Remove default list styles */
.prose ul {
  padding-left: 0;
  margin: 0;
}

.prose li {
  padding-left: 0;
}

.prose li::before {
  display: none;
}
</style>