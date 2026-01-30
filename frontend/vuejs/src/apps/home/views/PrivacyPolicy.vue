<!-- Privacy Policy Page - Clean minimal design matching Home -->
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
              Privacy Policy
            </h1>
              
            <!-- Description -->
            <p class="text-lg sm:text-xl text-gray-600 dark:text-white/70 max-w-3xl mx-auto leading-relaxed mb-6 transition-colors duration-300">
              We are committed to protecting your privacy and ensuring the security of your personal information.
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
  name: 'PrivacyPolicy',
  components: {
    DefaultLayout
  },
  setup() {
    const sections = [
      {
        badge: '1. Introduction',
        description: 'At Imagi, we understand that privacy is fundamental to building trust with our users. This Privacy Policy is designed to help you understand what information we collect, why we collect it, and how we use and protect it. We are committed to transparency in our data practices and to complying with applicable data protection laws including GDPR, CCPA, and other privacy regulations. This policy applies to all users of our platform, whether you are creating applications, managing projects, or simply exploring our services. We may update this policy periodically to reflect changes in our practices or legal requirements, and we will notify you of any material changes. By continuing to use our services after changes are made, you acknowledge and accept the updated policy.'
      },
      {
        badge: '2. Information We Collect',
        description: 'We collect various types of information to provide, maintain, and improve our services. The data we collect falls into several categories, each serving specific purposes in delivering our AI-powered development platform. All information is collected with your consent and is handled in accordance with applicable privacy laws.',
        items: [
          { 
            title: '2.1 Account Information', 
            text: 'When you create an account with Imagi, we collect your full name, email address, and authentication credentials. Your password is encrypted using industry-standard bcrypt hashing and is never stored in plain text. If you choose to add a profile picture, we store this image securely. We also maintain records of your account creation date, last login time, and account verification status. This information is essential for providing you access to our platform and personalizing your experience.' 
          },
          { 
            title: '2.2 Technical Data', 
            text: 'To ensure platform security and optimize performance, we automatically collect technical information about your device and connection. This includes your IP address, which helps us prevent fraud and unauthorized access. We collect browser type and version, operating system, device identifiers, screen resolution, and time zone settings. We also use cookies and similar tracking technologies to maintain your session, remember your preferences, and analyze how you interact with our platform. You can control cookie preferences through your browser settings, though some features may not function properly without certain cookies.' 
          },
          { 
            title: '2.3 Usage Information', 
            text: 'We track how you interact with our services to improve functionality and user experience. This includes the pages you visit, features you use, time spent on different sections of the platform, and the sequence of your actions. For our AI-powered tools, we log API requests, generation attempts, error messages, and performance metrics. We also collect information about the projects you create, including project names, descriptions, configurations, and the technologies you choose to use. This data helps us understand usage patterns, identify bugs, and develop new features that meet user needs.' 
          },
          { 
            title: '2.4 Payment Information', 
            text: 'When you make a purchase or subscribe to our services, we collect billing information necessary to process payments. This includes your name, billing address, and payment method details. However, sensitive payment card information is never stored on our servers. Instead, we use trusted third-party payment processors (such as Stripe) that are PCI DSS compliant. We only retain transaction IDs, purchase dates, amounts, and subscription status. You can view your payment history and manage payment methods through your account settings.' 
          },
          { 
            title: '2.5 Generated Content', 
            text: 'All applications, code, and configurations you create using our platform are stored in our systems. This includes your project files, database schemas, UI components, API endpoints, and any custom code you write or generate through our AI tools. We store this content to provide you continuous access to your work and to enable collaboration features. Your generated content is private by default and is only accessible to you and any collaborators you explicitly grant access to. We may analyze aggregated, anonymized patterns from generated content to improve our AI models, but we never use your specific projects for training without explicit permission.' 
          },
          { 
            title: '2.6 Communication Data', 
            text: 'When you contact our support team, submit feedback, participate in surveys, or communicate with us through any channel, we collect and store this information. This includes the content of your messages, attachments you send, and metadata such as timestamps. We use this information to respond to your inquiries, resolve issues, improve our services, and ensure we are meeting your needs. If you participate in user research or provide testimonials, we will ask for explicit consent before using your feedback publicly.' 
          }
        ]
      },
      {
        badge: '3. How We Protect Your Data',
        description: 'Security is a top priority at Imagi. We implement multiple layers of protection to safeguard your personal information against unauthorized access, alteration, disclosure, or destruction. Our security practices meet or exceed industry standards and are regularly updated to address emerging threats.',
        items: [
          { 
            title: '3.1 Encryption Standards', 
            text: 'All data transmitted between your device and our servers is protected using TLS 1.3 encryption, ensuring that your information cannot be intercepted during transmission. At rest, sensitive data is encrypted using AES-256 encryption. Your passwords are hashed using bcrypt with individual salts, making them computationally infeasible to reverse. API keys and access tokens are encrypted and rotated regularly. We also implement secure key management practices, with encryption keys stored separately from the encrypted data.' 
          },
          { 
            title: '3.2 Regular Security Audits', 
            text: 'We conduct comprehensive security audits quarterly, including both automated vulnerability scanning and manual penetration testing by certified security professionals. Our code undergoes security reviews before deployment, and we maintain a responsible disclosure program for security researchers. Any vulnerabilities identified are prioritized and remediated promptly according to their severity. We also monitor security advisories for all third-party dependencies and update them as needed.' 
          },
          { 
            title: '3.3 Data Backup and Recovery', 
            text: 'Your data is automatically backed up daily to geographically distributed locations to ensure continuity in case of hardware failure or disaster. Backups are encrypted and retained for 90 days. We regularly test our disaster recovery procedures to ensure we can restore services quickly if needed. Our backup systems are designed to enable point-in-time recovery, minimizing potential data loss. In the unlikely event of data loss, we will notify affected users promptly and work to recover the data.' 
          },
          { 
            title: '3.4 Access Controls and Authentication', 
            text: 'Access to user data within our organization is strictly controlled on a need-to-know basis. All employees with data access undergo background checks and security training. We implement role-based access controls, requiring multi-factor authentication for administrative access. All access to production systems is logged and monitored for suspicious activity. Employee access is reviewed quarterly and immediately revoked upon termination. We also enforce strong password policies and session management practices.' 
          },
          { 
            title: '3.5 Infrastructure Security', 
            text: 'Our infrastructure is hosted on secure, SOC 2 compliant cloud platforms with built-in DDoS protection and network isolation. We use firewalls, intrusion detection systems, and security groups to protect our services. Our systems are regularly patched and updated to address known vulnerabilities. We employ automated monitoring to detect and respond to security incidents in real-time. Infrastructure changes undergo security review before implementation.' 
          },
          { 
            title: '3.6 Compliance and Certifications', 
            text: 'We maintain compliance with industry security standards including GDPR for European users and CCPA for California residents. Our privacy practices are designed to meet OWASP security guidelines and follow the principle of privacy by design. We are committed to achieving SOC 2 Type II certification and regularly assess our compliance posture. Our privacy policy and security practices are reviewed annually by legal counsel to ensure ongoing compliance with evolving regulations.' 
          }
        ]
      },
      {
        badge: '4. How We Use Your Information',
        description: 'The information we collect serves specific purposes that directly benefit your experience with our platform. We are committed to using your data responsibly and only for the purposes described in this policy. We never sell your personal information to third parties.',
        items: [
          { 
            title: '4.1 Service Delivery and Maintenance', 
            text: 'Your information is essential for providing access to our AI-powered development platform. We use your account details to authenticate you, maintain your session, and provide access to your projects and settings. Technical data helps us ensure the platform operates smoothly across different devices and browsers. Usage information allows us to identify and fix bugs, optimize performance, and ensure reliability. We monitor system health and performance metrics to prevent downtime and address issues proactively.' 
          },
          { 
            title: '4.2 Personalization and Enhancement', 
            text: 'We analyze your usage patterns and preferences to customize your experience on our platform. This includes remembering your settings, suggesting relevant features, recommending project templates, and providing contextual help. Our AI tools learn from your interactions to provide more accurate code generation and better suggestions. We may also use your project history to offer relevant tutorials or documentation that matches your skill level and interests.' 
          },
          { 
            title: '4.3 Analytics and Improvement', 
            text: 'We use aggregated, anonymized data to understand how users interact with our platform and identify areas for improvement. This helps us prioritize feature development, improve our AI models, and optimize user workflows. We analyze conversion rates, feature adoption, error rates, and user feedback to make data-driven decisions about product development. These insights help us create a better experience for all users while maintaining individual privacy.' 
          },
          { 
            title: '4.4 Security and Fraud Prevention', 
            text: 'We monitor account activity and system access patterns to detect and prevent unauthorized access, fraud, and abuse. This includes analyzing login attempts, identifying suspicious behavior, and enforcing rate limits to prevent service abuse. We use your IP address and device information to recognize trusted devices and flag unusual activity. If we detect potential security issues with your account, we may temporarily restrict access and notify you to verify your identity.' 
          },
          { 
            title: '4.5 Communication and Support', 
            text: 'We use your contact information to send important service notifications, such as security alerts, system maintenance schedules, and changes to our terms or policies. If you opt in, we may also send product updates, feature announcements, and educational content. When you contact support, we use your communication history to provide better assistance and resolve issues more efficiently. You can control your communication preferences in your account settings.' 
          },
          { 
            title: '4.6 Legal Compliance and Protection', 
            text: 'We may use your information to comply with legal obligations, respond to legal requests, enforce our Terms of Service, and protect our rights and those of our users. This includes investigating violations of our policies, preventing illegal activities, and responding to valid legal processes such as subpoenas or court orders. We will only disclose information when legally required or when necessary to protect safety and security.' 
          }
        ]
      },
      {
        badge: '5. Data Sharing and Disclosure',
        description: 'We understand that trust is built on transparency about who has access to your information. We do not sell your personal data to anyone. We only share your information in limited circumstances with trusted partners who help us provide our services, and only to the extent necessary.',
        items: [
          { 
            title: '5.1 Service Providers and Partners', 
            text: 'We work with carefully vetted third-party service providers to help operate our platform. This includes cloud hosting providers (such as Railway and AWS), payment processors (such as Stripe), analytics services, email delivery services, and customer support tools. These partners are contractually obligated to protect your data and may only use it to provide services on our behalf. They are not permitted to use your information for their own purposes. We regularly review our service providers to ensure they maintain appropriate security and privacy standards.' 
          },
          { 
            title: '5.2 Legal Requirements and Requests', 
            text: 'We may disclose your information when required by law or in response to valid legal processes, including subpoenas, court orders, or regulatory requests. We carefully review all such requests to ensure they are legally valid and appropriately scoped. Where possible, we will notify you before disclosing your information unless prohibited by law or if notification would undermine the purpose of the request. We maintain transparency reports to document the number and nature of legal requests we receive.' 
          },
          { 
            title: '5.3 Business Transfers and Changes', 
            text: 'If Imagi is involved in a merger, acquisition, asset sale, or bankruptcy, your information may be transferred as part of that transaction. In such cases, we will notify you via email and prominent notice on our website at least 30 days before your information is transferred and becomes subject to a different privacy policy. You will have the opportunity to delete your account before the transfer if you do not agree to the new privacy practices.' 
          },
          { 
            title: '5.4 Aggregated and Anonymized Data', 
            text: 'We may share aggregated, anonymized data that cannot be used to identify you personally. This includes usage statistics, platform trends, and industry benchmarks. For example, we might share that "X% of users created projects using React" without revealing any individual user information. This data helps us participate in industry research, provide transparency to stakeholders, and improve our services. Anonymized data is stripped of all personally identifiable information before sharing.' 
          }
        ]
      },
      {
        badge: '6. Your Privacy Rights',
        description: 'You have significant control over your personal information. We respect your privacy rights and provide tools to exercise them easily. The specific rights available to you may vary depending on your location, but we generally extend broad privacy protections to all users regardless of jurisdiction.',
        items: [
          { 
            title: '6.1 Right to Access', 
            text: 'You have the right to request a copy of all personal information we hold about you. This includes your account details, usage history, generated content, and any other data associated with your account. You can access most of this information directly through your account dashboard. For a comprehensive data export, you can submit a request through our support system, and we will provide your data in a structured, commonly used format within 30 days.' 
          },
          { 
            title: '6.2 Right to Rectification', 
            text: 'If you discover that any information we hold about you is inaccurate or incomplete, you have the right to correct it. You can update most information directly through your account settings, including your name, email address, and profile details. If you need help correcting information you cannot edit yourself, contact our support team and we will make the corrections promptly.' 
          },
          { 
            title: '6.3 Right to Deletion', 
            text: 'You can request deletion of your account and associated personal information at any time. When you delete your account, we will permanently remove your personal information, including your profile, projects, and usage history, within 30 days. Some information may be retained in backups for up to 90 days for disaster recovery purposes, after which it will be permanently deleted. Note that we may retain certain information if required by law or necessary to resolve disputes or enforce our agreements.' 
          },
          { 
            title: '6.4 Right to Data Portability', 
            text: 'You have the right to receive your personal information in a portable format and to transmit it to another service provider. We provide data export functionality that allows you to download your projects, code, and account information in standard formats like JSON and ZIP archives. This enables you to easily move your work to other platforms if you choose.' 
          },
          { 
            title: '6.5 Right to Restriction', 
            text: 'You can request that we limit how we process your personal information in certain circumstances. For example, if you contest the accuracy of your data, you can request that we restrict processing while we verify accuracy. You can also request restriction if you believe processing is unlawful but prefer restriction over deletion. During any restriction period, we will only store your data and process it with your consent or for legal purposes.' 
          },
          { 
            title: '6.6 Right to Object', 
            text: 'You have the right to object to certain types of processing, particularly for marketing purposes. You can opt out of marketing communications at any time by clicking the unsubscribe link in any marketing email or adjusting your preferences in account settings. You can also object to automated decision-making, including profiling. If you object, we will stop the processing unless we have compelling legitimate grounds that override your interests or need to process the data for legal claims.' 
          },
          {
            title: '6.7 How to Exercise Your Rights',
            text: 'To exercise any of these rights, you can access your account settings, contact our support team at support@imagi.com, or submit a request through our privacy portal. We will respond to all requests within 30 days and will verify your identity before processing requests that involve accessing or deleting personal information. There is no fee for exercising these rights unless your request is clearly unfounded or excessive, in which case we may charge a reasonable fee or refuse the request.'
          }
        ]
      },
      {
        badge: '7. Data Retention',
        description: 'We retain your personal information only for as long as necessary to provide our services and fulfill the purposes outlined in this privacy policy. When data is no longer needed, we securely delete or anonymize it.',
        items: [
          {
            title: '7.1 Active Account Data',
            text: 'While your account is active, we retain all associated information to provide continuous service. This includes your profile, projects, usage history, and preferences. You have full access to and control over this data at all times through your account dashboard.'
          },
          {
            title: '7.2 Closed Account Data',
            text: 'When you close your account, we begin the deletion process immediately. Most personal information is deleted within 30 days. Some data may persist in backup systems for up to 90 days before final deletion. We may retain certain non-personal information in anonymized form for analytics purposes.'
          },
          {
            title: '7.3 Legal and Compliance Requirements',
            text: 'In some cases, we may be required to retain certain information longer to comply with legal obligations, such as tax records (typically 7 years) or to resolve disputes. When legal retention is required, we will securely isolate the data and restrict access until the retention period expires.'
          }
        ]
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
