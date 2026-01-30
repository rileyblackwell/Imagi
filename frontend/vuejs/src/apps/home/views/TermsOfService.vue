<!-- Terms of Service Page - Clean minimal design matching Home -->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="min-h-screen bg-white dark:bg-[#0a0a0a] relative overflow-hidden transition-colors duration-500">
      <!-- Enhanced minimal background with subtle noise texture effect -->
      <div class="fixed inset-0 pointer-events-none">
        <!-- Subtle gradient - very minimal -->
        <div class="absolute inset-0 bg-gradient-to-b from-gray-50/50 via-white to-white dark:from-[#0a0a0a] dark:via-[#0a0a0a] dark:to-[#0a0a0a] transition-colors duration-500"></div>
        
        <!-- Very subtle grid pattern for texture (dark mode only) -->
        <div class="absolute inset-0 opacity-[0.015] dark:opacity-[0.02]" 
             style="background-image: linear-gradient(rgba(128,128,128,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(128,128,128,0.1) 1px, transparent 1px); background-size: 64px 64px;"></div>
      </div>

      <!-- Main Content -->
      <main class="relative z-10">
        <!-- Hero Section -->
        <section class="relative pt-32 sm:pt-40 md:pt-48 pb-16 sm:pb-20 md:pb-24 px-6 sm:px-8 lg:px-12 bg-white dark:bg-[#0a0a0a] transition-colors duration-500 overflow-hidden">
          <div class="relative max-w-4xl mx-auto text-center">
            <!-- Hero title -->
            <h1 class="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight leading-[1.1] transition-colors duration-300">
              Terms of Service
            </h1>
              
            <!-- Description -->
            <p class="text-lg sm:text-xl text-gray-600 dark:text-white/70 max-w-3xl mx-auto leading-relaxed mb-6 transition-colors duration-300">
              Please read these terms carefully before using our services. By accessing our platform, you agree to be bound by these terms.
            </p>
            
            <p class="text-base text-gray-500 dark:text-white/50 transition-colors duration-300">
              Last updated: July 15, 2023
            </p>
          </div>
        </section>

        <!-- Content Sections -->
        <section v-for="(section, index) in sections" :key="index" 
                 :class="[
                   'relative px-6 sm:px-8 lg:px-12 bg-white dark:bg-[#0a0a0a] transition-colors duration-500 overflow-hidden',
                   index === sections.length - 1 ? 'pt-6 md:pt-8 pb-24 md:pb-32' : 
                   index === 0 ? 'pt-6 md:pt-8 pb-2 md:pb-3' : 'pt-2 md:pt-3 pb-6 md:pb-8'
                 ]">
          <!-- Subtle ambient background -->
          <div class="absolute inset-0 pointer-events-none">
            <div class="absolute top-1/2 left-1/2 w-[800px] h-[400px] bg-gradient-radial from-gray-200/30 dark:from-white/[0.02] via-transparent to-transparent rounded-full blur-3xl transform -translate-x-1/2 -translate-y-1/2"></div>
          </div>

          <div class="relative max-w-3xl mx-auto">
            <!-- Section header -->
            <div class="mb-12">
              <h2 class="text-3xl sm:text-4xl font-semibold text-gray-900 dark:text-white mb-4 transition-colors duration-300">
                {{ section.badge }}
              </h2>
              <p v-if="section.description" class="text-lg text-gray-600 dark:text-white/70 leading-relaxed transition-colors duration-300 mb-8">
                {{ section.description }}
              </p>
            </div>
            
            <!-- Content as paragraphs -->
            <div v-if="section.items" class="space-y-8">
              <div v-for="(item, itemIndex) in section.items" :key="itemIndex">
                <h3 class="text-xl font-semibold text-gray-900 dark:text-white transition-colors duration-300 mb-3">
                  {{ item.title }}
                </h3>
                <p class="text-gray-600 dark:text-white/70 leading-relaxed transition-colors duration-300">
                  {{ item.text }}
                </p>
              </div>
            </div>
          </div>
        </section>
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
        badge: '1. Introduction',
        description: 'Welcome to Imagi Oasis, an AI-powered platform designed to help you build, deploy, and manage web applications. These Terms of Service constitute a legally binding agreement between you and Imagi regarding your use of our platform and services. By creating an account, accessing our website, or using any of our features, you acknowledge that you have read, understood, and agree to be bound by these terms in their entirety. If you do not agree with any part of these terms, you must immediately discontinue use of our services. These terms were last updated on July 15, 2023. We reserve the right to modify these terms at any time, and we will notify you of material changes via email or through prominent notices on our platform. Your continued use of our services following such modifications constitutes acceptance of the updated terms.'
      },
      {
        badge: '2. Acceptance and Eligibility',
        description: 'By accessing or using Imagi Oasis, you represent and warrant that you meet all eligibility requirements and have the legal capacity to enter into this binding agreement. You must be at least 18 years old or have reached the age of majority in your jurisdiction to use our services. If you are using our services on behalf of an organization, you represent that you have the authority to bind that organization to these terms. You also agree that all registration information you submit is truthful, accurate, and complete, and you will maintain the accuracy of this information. We reserve the right to refuse service, terminate accounts, or remove content at our sole discretion if we believe you have violated these terms or engaged in conduct we deem inappropriate or harmful to our platform or other users.'
      },
      {
        badge: '3. Account Responsibilities',
        description: 'When you create an account with Imagi Oasis, you assume certain responsibilities to ensure the security and proper use of our platform.',
        items: [
          { 
            title: '3.1 Account Security and Credentials', 
            text: 'You are solely responsible for maintaining the confidentiality of your account credentials, including your username and password. You must use a strong, unique password and enable multi-factor authentication when available. You agree not to share your account credentials with any third party or allow others to access your account. You are responsible for all activities that occur under your account, whether authorized by you or not. If you suspect any unauthorized access to your account, you must immediately notify us at security@imagi.com and change your password. We will not be liable for any loss or damage arising from your failure to maintain account security.' 
          },
          { 
            title: '3.2 Accurate Information', 
            text: 'You agree to provide complete, accurate, and up-to-date information when creating your account and using our services. This includes your name, email address, billing information, and any other details required for service provision. You must promptly update your account information if it changes. Providing false or misleading information, or impersonating another person or entity, is strictly prohibited and may result in immediate account termination.' 
          },
          { 
            title: '3.3 Lawful Use and Compliance', 
            text: 'You agree to use Imagi Oasis only for lawful purposes and in compliance with all applicable laws, regulations, and ordinances in your jurisdiction. This includes export control laws, data protection regulations, intellectual property laws, and any industry-specific regulations that apply to your use case. You are solely responsible for ensuring that your use of our platform and any applications you create comply with all applicable laws. We reserve the right to report any suspected illegal activity to law enforcement authorities.' 
          },
          { 
            title: '3.4 Application Security', 
            text: 'While we provide tools to help you build secure applications, you are ultimately responsible for implementing appropriate security measures in the applications you create and deploy through our platform. This includes protecting sensitive data, implementing access controls, validating user inputs, and following security best practices. You agree to conduct security testing and code reviews before deploying applications to production. We recommend following OWASP guidelines and conducting regular security audits of your applications.' 
          },
          {
            title: '3.5 Professional Conduct',
            text: 'You agree to conduct yourself professionally when using our platform and interacting with our support team or other users. Harassment, abuse, threats, discrimination, or any form of harmful behavior toward Imagi staff or other users is strictly prohibited. We maintain a zero-tolerance policy for such conduct and will terminate accounts that violate this requirement without prior warning.'
          }
        ]
      },
      {
        badge: '4. Prohibited Uses and Activities',
        description: 'To maintain a safe, secure, and legal platform for all users, certain uses of our services are strictly prohibited. Engaging in any of the following activities may result in immediate account suspension or termination, legal action, and reporting to appropriate authorities.',
        items: [
          { 
            title: '4.1 Illegal Content and Activities', 
            text: 'You are strictly prohibited from using our platform to create, host, distribute, or promote any content, products, services, or applications that violate applicable laws. This includes but is not limited to content related to illegal drugs, weapons trafficking, human trafficking, child exploitation, terrorism, fraud, money laundering, or any other criminal activity. You may not use our services to facilitate, promote, or engage in any illegal activity. Any applications created for illegal purposes will be immediately removed, and the account will be terminated and reported to law enforcement.' 
          },
          { 
            title: '4.2 Harmful and Malicious Applications', 
            text: 'You may not create or deploy applications that are designed to harm, defraud, exploit, or harass others. This includes applications that spread malware, viruses, ransomware, spyware, or any other harmful code. You may not create phishing applications, scam websites, or applications designed to deceive users or steal personal information. Applications that facilitate cyberbullying, doxxing, stalking, or harassment are strictly prohibited. Any application that poses a security risk to our platform, other users, or the general public will be immediately removed.' 
          },
          { 
            title: '4.3 Unauthorized Access and Exploitation', 
            text: 'You are prohibited from attempting to gain unauthorized access to our systems, servers, networks, or other users\' accounts. This includes attempting to bypass security measures, conducting penetration testing without explicit written permission, exploiting vulnerabilities, or using automated tools to scrape our platform. You may not reverse engineer, decompile, disassemble, or attempt to discover the source code of any non-public parts of our services. If you discover a security vulnerability, you must report it immediately through our responsible disclosure program rather than exploiting it.' 
          },
          { 
            title: '4.4 Service Abuse and Resource Manipulation', 
            text: 'You may not abuse our services by creating multiple accounts to circumvent usage limits, engaging in activity that degrades service performance, conducting denial-of-service attacks, or consuming excessive resources that impact other users. You may not use our platform for cryptocurrency mining, sending spam, operating bot networks, or any other activity that violates our acceptable use policy. We monitor resource usage and reserve the right to throttle or terminate accounts that abuse our infrastructure.' 
          },
          { 
            title: '4.5 Intellectual Property Infringement', 
            text: 'You may not use our platform to create applications that infringe on the intellectual property rights of others. This includes unauthorized use of copyrighted material, trademarks, patents, trade secrets, or other proprietary information. You may not create applications that facilitate piracy, copyright infringement, or trademark counterfeiting. If we receive a valid DMCA takedown notice or other intellectual property complaint regarding your content, we will remove the infringing material and may terminate repeat offenders.' 
          },
          {
            title: '4.6 Manipulation and Deceptive Practices',
            text: 'You may not engage in deceptive practices such as creating fake reviews, manipulating rankings or metrics, impersonating others, or misrepresenting your affiliation with any person or organization. You may not use our platform to conduct astroturfing, create sock puppet accounts, or engage in any form of manipulation designed to deceive users or our systems.'
          }
        ]
      },
      {
        badge: '5. Service Provision and Availability',
        description: 'Imagi Oasis provides an AI-powered platform for code generation, application building, and deployment. While we strive to provide reliable and high-quality services, there are important limitations and considerations you should understand.',
        items: [
          { 
            title: '5.1 As-Is Basis and No Warranties', 
            text: 'Our services are provided on an "as is" and "as available" basis without any warranties of any kind, whether express or implied. This includes but is not limited to warranties of merchantability, fitness for a particular purpose, non-infringement, or that our services will be error-free, uninterrupted, secure, or free from viruses or other harmful components. While we use advanced AI technologies, we do not warrant that code generated by our platform will be bug-free, secure, or suitable for your specific needs. All generated code should be reviewed, tested, and validated before deployment to production environments.' 
          },
          { 
            title: '5.2 Service Modifications and Discontinuation', 
            text: 'We reserve the right to modify, suspend, or discontinue any aspect of our services at any time, with or without notice, and without liability to you. This includes adding or removing features, changing pricing structures, implementing usage limits, or terminating the service entirely. We may also perform scheduled or emergency maintenance that temporarily interrupts service availability. While we will make reasonable efforts to provide advance notice of significant changes or planned downtime, such notice is not guaranteed. We recommend maintaining backups of your projects and not relying solely on our platform for critical business operations.' 
          },
          { 
            title: '5.3 Code Review and Testing Requirements', 
            text: 'All code generated through our AI-powered tools must be thoroughly reviewed and tested before deployment. Our AI generates code based on patterns and training data, but it cannot guarantee that the generated code will meet your specific requirements, be free of bugs, or implement best practices for your particular use case. You are solely responsible for reviewing generated code for security vulnerabilities, performance issues, accessibility compliance, and functional correctness. We strongly recommend conducting code reviews, implementing automated testing, and performing security audits before deploying any applications to production.' 
          },
          { 
            title: '5.4 Usage Limits and Fair Use', 
            text: 'We may impose usage limits on our services to maintain quality, performance, and availability for all users. This includes limits on API requests, project size, storage capacity, bandwidth, and generation frequency. Usage limits vary by subscription tier and may change over time. We reserve the right to throttle or temporarily suspend accounts that exceed fair use thresholds or engage in activity that degrades service quality for other users. If your usage needs exceed standard limits, contact our sales team about enterprise plans with higher capacity.' 
          },
          {
            title: '5.5 Third-Party Dependencies',
            text: 'Our platform integrates with various third-party services and technologies. While we carefully select reliable partners, we cannot guarantee the availability, performance, or security of third-party services. Changes or disruptions to third-party services may impact functionality on our platform. We are not responsible for issues arising from third-party service failures or changes to their terms of service.'
          },
          {
            title: '5.6 Beta Features and Experimental Tools',
            text: 'We may offer beta, experimental, or preview features that are still in development. These features are provided for testing and feedback purposes and may be unstable, incomplete, or subject to significant changes. Beta features are provided without warranties and may be discontinued at any time. You use beta features at your own risk and should not rely on them for production workloads.'
          }
        ]
      },
      {
        badge: '6. Intellectual Property Rights',
        description: 'Understanding ownership and usage rights for content created on our platform is essential. This section clarifies what you own, what we own, and how intellectual property is handled.',
        items: [
          { 
            title: '6.1 Your Content and Applications', 
            text: 'You retain all ownership rights to the content and applications you create using our platform. This includes your project files, custom code, database schemas, UI designs, documentation, and any other original work you produce. By using our services, you grant us a limited, non-exclusive, worldwide license to host, store, and process your content solely for the purpose of providing our services to you. This license terminates when you delete your content or close your account, except for content that has been shared publicly or where retention is required by law. You represent and warrant that you have all necessary rights to the content you upload and that your content does not infringe on the intellectual property rights of any third party.' 
          },
          { 
            title: '6.2 Our Platform and Technology', 
            text: 'Imagi retains all rights, title, and interest in our platform, technology, branding, trademarks, service marks, logos, and any proprietary algorithms, models, or processes used to provide our services. This includes our website, software, API, documentation, user interface, AI models, and any improvements or derivatives thereof. These terms do not grant you any ownership rights or licenses to our intellectual property except as expressly stated. You may not copy, modify, distribute, sell, or lease any part of our services or included software, nor may you reverse engineer or attempt to extract the source code of our proprietary technology.' 
          },
          { 
            title: '6.3 Generated Code and AI Output', 
            text: 'Code generated through our AI tools is licensed to you for your use in accordance with these terms. You may use, modify, and distribute generated code in your applications without restriction, including for commercial purposes. However, we retain ownership of the underlying AI models, algorithms, and generation processes. While we grant you broad rights to use generated code, we cannot guarantee that generated code is entirely original or does not inadvertently replicate patterns from publicly available code. You are responsible for reviewing generated code for potential intellectual property issues before use.' 
          },
          { 
            title: '6.4 Feedback and Suggestions', 
            text: 'If you provide us with feedback, suggestions, ideas, or recommendations regarding our platform ("Feedback"), you grant us a perpetual, irrevocable, worldwide, royalty-free license to use, modify, and incorporate that Feedback into our services without compensation or attribution to you. This enables us to improve our platform based on user insights without legal complications. By providing Feedback, you represent that you have the right to grant this license and that the Feedback does not violate any third-party rights.' 
          },
          {
            title: '6.5 Open Source and Third-Party Components',
            text: 'Our platform may incorporate or generate code that uses open source libraries or third-party components. These components remain subject to their original licenses. When generating code that includes open source dependencies, you are responsible for complying with the applicable open source licenses. We provide information about included dependencies where possible, but you should verify license compliance independently.'
          },
          {
            title: '6.6 Copyright Infringement and DMCA',
            text: 'We respect intellectual property rights and expect our users to do the same. If you believe your copyrighted work has been infringed by content on our platform, you may submit a DMCA takedown notice to dmca@imagi.com. We will investigate valid claims and take appropriate action, which may include removing the infringing content and terminating repeat offenders. If you believe your content was removed in error, you may submit a counter-notice.'
          }
        ]
      },
      {
        badge: '7. Payment Terms and Billing',
        description: 'If you subscribe to paid services or make purchases through our platform, the following payment terms apply. Please review these carefully to understand your financial obligations.',
        items: [
          {
            title: '7.1 Subscription Plans and Pricing',
            text: 'We offer various subscription plans with different features and usage limits. Current pricing is available on our website and may change over time. We will provide at least 30 days notice before implementing price increases for existing subscribers. Any price changes will take effect at the start of your next billing cycle. You can view your current subscription, usage, and billing information in your account dashboard.'
          },
          {
            title: '7.2 Billing and Payment Processing',
            text: 'Subscription fees are billed in advance on a recurring basis (monthly or annually, depending on your plan). You authorize us to charge your payment method on file for all applicable fees. We use third-party payment processors (such as Stripe) to handle payment processing securely. If a payment fails, we will notify you and attempt to process the payment again. Your service may be suspended if payment issues are not resolved within a reasonable timeframe.'
          },
          {
            title: '7.3 Refunds and Cancellation',
            text: 'You may cancel your subscription at any time through your account settings. Cancellation takes effect at the end of your current billing period, and you will retain access to paid features until that time. We do not provide refunds for partial subscription periods, except as required by law or in cases of service failure on our part. If you believe you are entitled to a refund due to service issues, contact our support team within 30 days of the charge.'
          },
          {
            title: '7.4 Taxes',
            text: 'All fees are exclusive of applicable taxes unless otherwise stated. You are responsible for paying any sales tax, VAT, GST, or other taxes associated with your purchase. We will collect and remit taxes where required by law. Tax rates and requirements vary by jurisdiction and may change over time.'
          }
        ]
      },
      {
        badge: '8. Limitation of Liability',
        description: 'To the maximum extent permitted by law, Imagi Oasis and its affiliates, officers, employees, agents, and licensors shall not be liable for any indirect, incidental, special, consequential, or punitive damages, or any loss of profits, revenue, data, or goodwill arising from your use or inability to use our services. This includes damages resulting from errors in generated code, security vulnerabilities, data loss, service interruptions, or any other service failures. Our total aggregate liability for all claims relating to these terms or our services shall not exceed the amount you paid us in the twelve months preceding the claim, or $100, whichever is greater. Some jurisdictions do not allow certain limitations of liability, so these limitations may not apply to you.'
      },
      {
        badge: '9. Indemnification',
        description: 'You agree to indemnify, defend, and hold harmless Imagi Oasis, its affiliates, officers, directors, employees, agents, and licensors from and against any claims, liabilities, damages, losses, costs, or expenses (including reasonable attorney fees) arising from your use of our services, your violation of these terms, your infringement of any third-party rights, or any applications you create or deploy through our platform. This indemnification obligation survives termination of your account and these terms.'
      },
      {
        badge: '10. Termination',
        description: 'Either party may terminate this agreement at any time. You may close your account through your account settings or by contacting support. We may suspend or terminate your account immediately, without prior notice, if we believe you have violated these terms, engaged in fraudulent activity, or for any other reason at our sole discretion. Upon termination, your right to use our services ceases immediately. We will provide you with a reasonable opportunity to export your data following termination, but we are not obligated to retain your data indefinitely. Provisions of these terms that by their nature should survive termination will survive, including intellectual property rights, limitation of liability, indemnification, and dispute resolution.'
      },
      {
        badge: '11. Dispute Resolution and Governing Law',
        description: 'These terms are governed by and construed in accordance with the laws of the State of California, United States, without regard to its conflict of law provisions. Any disputes arising from these terms or your use of our services shall first be addressed through good faith negotiations. If a dispute cannot be resolved through negotiation, you agree to submit to the exclusive jurisdiction of the state and federal courts located in San Francisco County, California. Some jurisdictions provide legal rights that cannot be waived, and nothing in these terms limits such mandatory rights. If you are a consumer in the European Union, you may also have the right to use online dispute resolution platforms provided by the European Commission.'
      },
      {
        badge: 'Changes to Terms',
        description: 'We reserve the right to modify these Terms of Service at any time. When we make material changes, we will notify you via email to the address associated with your account and display a prominent notice on our platform. The updated terms will become effective 30 days after we provide notice, giving you time to review the changes. If you do not agree to the modified terms, you must discontinue use of our services and close your account before the effective date. Your continued use of our services after the effective date constitutes acceptance of the updated terms. We recommend reviewing these terms periodically to stay informed of any changes.'
      }
    ]
    
    return {
      sections
    }
  }
})
</script>

<style scoped>
/* Refined minimal scrollbar */
:deep(::-webkit-scrollbar) {
  width: 8px;
}

:deep(::-webkit-scrollbar-track) {
  background: transparent;
}

:deep(::-webkit-scrollbar-thumb) {
  background: rgba(0, 0, 0, 0.12);
  border-radius: 4px;
  transition: background 0.2s ease;
}

:deep(::-webkit-scrollbar-thumb:hover) {
  background: rgba(0, 0, 0, 0.2);
}

:root.dark :deep(::-webkit-scrollbar-thumb) {
  background: rgba(255, 255, 255, 0.12);
}

:root.dark :deep(::-webkit-scrollbar-thumb:hover) {
  background: rgba(255, 255, 255, 0.2);
}

/* Smooth scroll behavior */
:deep(html) {
  scroll-behavior: smooth;
}
</style>
