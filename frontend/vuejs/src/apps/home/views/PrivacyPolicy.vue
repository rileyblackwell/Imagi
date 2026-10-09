<!--
  Privacy policy.

  Long-form legal text on the Spotlight stage: a lit opener, then the
  editorial prose measure (a hairline before each section, no cards), re-lit
  by the bridge in shared/styles/spotlight.css.
-->
<template>
  <div class="spotlight legal-page">
  <DefaultLayout>
    <div class="editorial relative min-h-screen">
      <main class="relative">

        <!-- Opener -->
        <section class="sl-opener legal-opener">
          <div class="sl-spot" aria-hidden="true"></div>
          <div class="sl-dots" aria-hidden="true"></div>
          <div class="sl-wrap sl-opener__inner">
            <p class="sl-eyebrow sl-pill legal-rise"><span class="sl-pip" aria-hidden="true"></span>Legal</p>
            <h1 class="sl-display sl-h1 legal-title legal-rise">Privacy Policy</h1>
            <p class="sl-lede legal-rise">
              How Imagi handles your data — what we collect, how it is stored, who it is shared with, and the control you have over it.
            </p>
            <p class="legal-updated legal-rise">Last updated: October 9, 2026</p>
          </div>
        </section>

        <!-- Sections -->
        <section class="relative pt-2 pb-20 md:pb-28">
          <div class="prose-shell prose">
            <template v-for="section in sections" :key="section.badge">
              <h2>
                <span class="sec-num">{{ parseBadge(section.badge).eyebrow }}</span>
                {{ parseBadge(section.badge).title }}
              </h2>
              <p v-if="section.description">{{ section.description }}</p>

              <template v-if="section.items">
                <template v-for="item in section.items" :key="item.title">
                  <h3>{{ item.title }}</h3>
                  <p>{{ item.text }}</p>
                </template>
              </template>
            </template>
          </div>
        </section>

        <ClosingSection
          title="Ready to start?"
          description="Your data stays yours. Describe what you want to build, and have a working web app the same afternoon."
          primary-button-text="Start building"
          secondary-button-text="Terms of Service"
          secondary-button-to="/terms"
        />
      </main>
    </div>
  </DefaultLayout>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { DefaultLayout } from '@/shared/layouts'
import { ClosingSection } from '@/apps/home/components/organisms/sections'

export default defineComponent({
  name: 'PrivacyPolicy',
  components: {
    DefaultLayout,
    ClosingSection
  },
  setup() {
    // Split a badge like "1. Introduction" into an eyebrow label and a title.
    const parseBadge = (badge) => {
      const match = badge.match(/^(\d+)\.\s*(.+)$/)
      if (match) {
        return {
          eyebrow: `Section ${match[1].padStart(2, '0')}`,
          title: match[2]
        }
      }
      return { eyebrow: 'Additional Terms', title: badge }
    }

    const sections = [
      {
        badge: '1. About This Policy',
        description: 'This policy explains what information Imagi collects when you use imagi.up.railway.app and the Imagi product, how we use it, and who we share it with. Imagi is a platform where you build a web app by chatting with AI agents, then use business tools (Sell, Market and Operate) alongside it. By using Imagi you agree to this policy and to our Terms of Service.'
      },
      {
        badge: '2. What We Collect',
        items: [
          {
            title: '2.1 Your Account',
            text: 'Your name, email address, username and password. Passwords are stored hashed, never in plain text.'
          },
          {
            title: '2.2 Your Projects',
            text: 'What you tell us about each project (its name, description and look), your conversations with Imagi\'s agents, any voice recordings you dictate, and the code, pages and files the agents write for you.'
          },
          {
            title: '2.3 Billing',
            text: 'Your plan, your usage against its weekly allowance, and payment records. Card details are collected and held by Stripe, our payment processor; we do not store your full card number.'
          },
          {
            title: '2.4 Business Tools',
            text: 'If you use Sell, Market or Operate, we store what you add there: products, prices, customers and orders; contacts, campaigns and messages; income, expenses and your app\'s live address. If you connect an outside account (such as Stripe, Twilio, Google Ads or Meta), we store the identifiers and access keys needed to use it, encrypted.'
          },
          {
            title: '2.5 Usage and Technical Data',
            text: 'Server logs such as IP address, browser type, the pages and requests you make, and errors, which we use to run, secure and fix the service.'
          },
          {
            title: '2.6 Cookies and Browser Storage',
            text: 'We use your browser\'s storage and a small number of essential cookies to keep you signed in and remember settings like your theme. We do not use advertising cookies or third-party analytics trackers on Imagi.'
          }
        ]
      },
      {
        badge: '3. How We Use It',
        description: 'We use your information to provide Imagi: to sign you in, run the AI agents that build and edit your app, show your app in a live preview, operate the business tools you use, bill you, enforce usage limits, keep the service secure, fix problems, and contact you about your account or changes to Imagi. We do not sell your personal information, and we do not use your projects to train AI models.'
      },
      {
        badge: '4. Who We Share It With',
        description: 'We share information only with the services that help us run Imagi, with services you choose to connect, or when the law requires it.',
        items: [
          {
            title: '4.1 AI Providers',
            text: 'Your prompts, project content and code are sent to Anthropic, whose Claude models power Imagi\'s agents and web search. If you use dictation, your audio is sent to OpenAI to turn it into text.'
          },
          {
            title: '4.2 Infrastructure and Payments',
            text: 'Imagi and its database are hosted on Railway. Payments for Imagi plans are processed by Stripe.'
          },
          {
            title: '4.3 Services You Connect',
            text: 'When you connect Stripe (through Sell), Twilio, Google Ads or Meta, we send those services what is needed to do what you ask, such as creating a price, sending a text, or pausing an ad campaign. Their own terms and privacy policies apply to what they receive.'
          },
          {
            title: '4.4 Legal and Business Reasons',
            text: 'We may disclose information if required by law, to protect the rights or safety of Imagi, our users or others, or as part of a merger, sale or similar transaction involving Imagi.'
          }
        ]
      },
      {
        badge: '5. Your Customers and Visitors',
        description: 'When you use the business tools, you may give Imagi information about other people, such as your customers, contacts, or the visitors to your app. We process it only to provide the tools to you. You are responsible for having the right to collect and use it, including getting consent before sending anyone text messages. Operate\'s visitor tag counts visits without cookies: it records the page path and referring site, and turns the visitor\'s IP address and browser into a daily-changing code that cannot be traced back to them, rather than storing the IP address itself.'
      },
      {
        badge: '6. Security',
        description: 'We use reasonable measures to protect your information, including encrypted connections, hashed passwords, and encryption for the access keys of accounts you connect. No online service is perfectly secure, and we cannot guarantee that your information will never be accessed without authorization.'
      },
      {
        badge: '7. Keeping and Deleting Data',
        description: 'We keep your information while your account is open. You can delete projects at any time. To delete your account and its data, contact us and we will delete it, except for what we must keep for legal, billing or security reasons. Copies may remain in logs or backups for a limited time.'
      },
      {
        badge: '8. Your Choices',
        description: 'You can ask us for a copy of your information, to correct it, or to delete it. Depending on where you live, you may have additional rights under local law, and we will respond to requests as those laws require.'
      },
      {
        badge: '9. Children',
        description: 'Imagi is not meant for children under 13, and we do not knowingly collect their information. If you believe a child has given us information, contact us and we will delete it.'
      },
      {
        badge: '10. Changes and Contact',
        description: 'We may update this policy as Imagi changes. When we do, we will change the date at the top of this page, and for significant changes we will let you know in the product or by email. Questions or requests about your data can be sent to support@imagi.com.'
      }
    ]

    return {
      sections,
      parseBadge
    }
  }
})
</script>

<style scoped>
.sl-opener .legal-title {
  font-size: clamp(44px, 7.4vw, 96px);
}

.sl-opener.legal-opener {
  padding-bottom: clamp(40px, 6vw, 72px);
}

.legal-updated {
  margin: 4px 0 0;
  padding: 6px 12px;
  border: 1px solid var(--sl-line);
  border-radius: 999px;
  color: var(--sl-faint);
  font-size: 13px;
}

.legal-rise {
  animation: legal-rise 0.8s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.legal-rise:nth-child(2) { animation-delay: 60ms; }
.legal-rise:nth-child(3) { animation-delay: 120ms; }
.legal-rise:nth-child(4) { animation-delay: 180ms; }

@keyframes legal-rise {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: none; }
}

@media (prefers-reduced-motion: reduce) {
  .legal-rise { animation: none; }
}
</style>
