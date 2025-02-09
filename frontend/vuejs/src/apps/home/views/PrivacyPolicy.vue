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
        title: 'Information Collection and Use',
        icon: 'fas fa-database',
        description: 'We collect and process personal information necessary to provide our services. This information is handled with utmost care and in compliance with applicable data protection laws:',
        items: [
          { title: 'Account Information', description: 'Name, email, password (encrypted), profile picture, and registration details' },
          { title: 'Technical Data', description: 'IP address, browser type, device information, operating system, and cookies' },
          { title: 'Usage Information', description: 'Interaction with our services, generated applications, API calls, and feature usage patterns' },
          { title: 'Payment Details', description: 'Billing information, transaction history (stored securely via payment processors)' },
          { title: 'Generated Content', description: 'Applications, code, and configurations created using our services' },
          { title: 'Communication Data', description: 'Support tickets, feedback, and correspondence with our team' }
        ]
      },
      {
        title: 'Data Processing and Storage',
        icon: 'fas fa-microchip',
        description: 'We implement robust security measures to protect your data:',
        items: [
          'End-to-end encryption for sensitive data transmission',
          'Regular security audits and penetration testing',
          'Data backup and disaster recovery protocols',
          'Access controls and authentication mechanisms',
          'Regular updates to security infrastructure',
          'Compliance with industry security standards'
        ]
      },
      {
        title: 'Use of Information',
        icon: 'fas fa-cog',
        description: 'Your information is used for the following purposes:',
        items: [
          { title: 'Service Provision', description: 'Delivering and maintaining our AI-powered development platform' },
          { title: 'Personalization', description: 'Customizing and optimizing your experience' },
          { title: 'Analytics', description: 'Improving our services and understanding user needs' },
          { title: 'Security', description: 'Protecting against fraud and unauthorized access' },
          { title: 'Communication', description: 'Sending service updates, notifications, and support responses' },
          { title: 'Legal Compliance', description: 'Meeting regulatory requirements and enforcing our terms' }
        ]
      },
      {
        title: 'Data Sharing and Third Parties',
        icon: 'fas fa-share-nodes',
        description: 'We may share your information with:',
        items: [
          { title: 'Service Providers', description: 'Cloud hosting, analytics, payment processing, and security services' },
          { title: 'Legal Requirements', description: 'Court orders, law enforcement requests, or regulatory obligations' },
          { title: 'Business Transfers', description: 'Mergers, acquisitions, or asset sales (with user notification)' },
          { title: 'Aggregated Data', description: 'Anonymous, statistical data for research and analysis' }
        ]
      },
      {
        title: 'Your Privacy Rights',
        icon: 'fas fa-user-shield',
        description: 'You have the following rights regarding your personal data:',
        items: [
          { title: 'Access', description: 'Request copies of your personal data' },
          { title: 'Rectification', description: 'Correct inaccurate or incomplete information' },
          { title: 'Deletion', description: 'Request erasure of your personal data' },
          { title: 'Portability', description: 'Receive and transfer your data to another controller' },
          { title: 'Restriction', description: 'Limit how we process your data' },
          { title: 'Objection', description: 'Object to certain types of processing' }
        ]
      },
      {
        title: 'Data Retention',
        icon: 'fas fa-clock',
        description: 'We retain your information according to these principles:',
        items: [
          'Active accounts: Data retained while account is active',
          'Deleted accounts: Data removed within 30 days of deletion request',
          'Backup retention: Up to 90 days for disaster recovery',
          'Legal requirements: As required by applicable laws',
          'Anonymous data: May be retained indefinitely'
        ]
      },
      {
        title: 'International Data Transfers',
        icon: 'fas fa-globe',
        description: 'For users outside our primary operating region:',
        items: [
          'Data may be processed in different jurisdictions',
          'We ensure appropriate safeguards for international transfers',
          'EU-US Privacy Shield compliance where applicable',
          'Standard contractual clauses with service providers',
          'Regular audits of international data protection measures'
        ]
      },
      {
        title: 'Children\'s Privacy',
        icon: 'fas fa-child',
        description: 'Regarding users under 16 years of age:',
        items: [
          'Services not intended for children under 16',
          'We do not knowingly collect children\'s data',
          'Immediate deletion upon discovery of minor\'s data',
          'Parental consent required for legitimate minor users',
          'Special protections for authorized minor accounts'
        ]
      },
      {
        title: 'Changes to Privacy Policy',
        icon: 'fas fa-file-contract',
        description: 'Our policy update procedures:',
        items: [
          'Regular reviews and updates as needed',
          'Notice of material changes via email',
          '30-day advance notice for significant changes',
          'Continued use constitutes acceptance',
          'Previous versions available upon request'
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