<!--
  Terms of service.

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
            <h1 class="sl-display sl-h1 legal-title legal-rise">Terms of Service</h1>
            <p class="sl-lede legal-rise">
              The agreement between you and Imagi covering accounts, acceptable use, payment, and the limits of the service.
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
          description="Describe what you want to build, and have a working web app the same afternoon — with the tools to market, sell and run it in the same project."
          primary-button-text="Start building"
          secondary-button-text="Privacy Policy"
          secondary-button-to="/privacy"
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
  name: 'TermsOfService',
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
        badge: '1. Agreement',
        description: 'These terms are an agreement between you and Imagi for your use of the Imagi website and product. By creating an account or using Imagi, you agree to these terms and to our Privacy Policy. You must be at least 18, or the age of majority where you live. If you use Imagi for a business, you agree to these terms on its behalf and confirm you are allowed to.'
      },
      {
        badge: '2. The Service',
        description: 'Imagi lets you build a web app by chatting with AI agents that write its code and show it in a live preview, and offers business tools, Sell, Market and Operate, to help run what you build. Sell, Market and Operate are in beta, and publishing your app to the internet from Imagi is not available yet. We are actively developing Imagi, so features may change, be added or be removed at any time.'
      },
      {
        badge: '3. Your Account',
        description: 'Give us accurate information and keep your password safe. You are responsible for everything done through your account. Tell us promptly if you think someone else has accessed it.'
      },
      {
        badge: '4. Your Content and AI Output',
        items: [
          {
            title: '4.1 What You Own',
            text: 'You keep ownership of what you bring to Imagi and, as between you and Imagi, of the code and content the agents create for your projects. You give Imagi permission to store, process and display that content only as needed to run the service for you, including sending it to the providers described in our Privacy Policy.'
          },
          {
            title: '4.2 AI Can Make Mistakes',
            text: 'Imagi\'s agents use AI, and their output can be wrong, incomplete, insecure, or similar to content made for others. Review and test what Imagi produces before you rely on it. You are responsible for your app, how you use it, and making sure it follows the laws that apply to you.'
          },
          {
            title: '4.3 Imagi\'s Platform',
            text: 'Imagi\'s own software, design and brand belong to Imagi. Prebuilt pieces Imagi adds to your project, such as sign-in and payment pages, are yours to use in that project. If you send us feedback, we may use it freely.'
          }
        ]
      },
      {
        badge: '5. Acceptable Use',
        description: 'Do not use Imagi to break the law; to build or host malware, scams, phishing or deceptive apps; to send spam or texts to people who have not agreed to receive them; to infringe anyone\'s rights; to harass or harm others; to attack, overload or get around the limits of Imagi or its providers; or to access other users\' accounts or data. You must also follow the usage policies of the AI providers Imagi relies on. We may remove content or limit accounts that break these rules.'
      },
      {
        badge: '6. Connected Services',
        description: 'Some features work through outside services you connect, such as Stripe for taking payments in Sell, Twilio for texts, and Google Ads or Meta for advertising. Your use of those services is governed by their own terms. You are responsible for any fees they charge, including ad spend on accounts you connect, and for your dealings with your own customers. Imagi is not a party to sales you make.'
      },
      {
        badge: '7. Plans and Payment',
        items: [
          {
            title: '7.1 Plans and Usage',
            text: 'Imagi offers a Free plan and paid plans. Each plan includes a weekly allowance of AI usage; when it runs out, AI work pauses until the allowance resets or you change plans. Current plans and prices are shown on our pricing page.'
          },
          {
            title: '7.2 Billing',
            text: 'Paid plans are billed monthly in advance through Stripe and renew automatically until you cancel. Plan changes may be prorated as shown when you make them. Prices exclude taxes unless stated. We may change prices, and a change applies to you from your next billing period after we tell you about it.'
          },
          {
            title: '7.3 Cancelling and Refunds',
            text: 'You can cancel anytime from the billing portal. Your plan stays active until the end of the period you paid for. Payments are non-refundable except where the law requires otherwise.'
          }
        ]
      },
      {
        badge: '8. Disclaimers',
        description: 'Imagi is provided "as is" and "as available". To the fullest extent the law allows, we make no warranties of any kind, including that the service will be uninterrupted, error-free or secure, that AI output will be accurate, or that your data will never be lost. Keep your own copies of anything important.'
      },
      {
        badge: '9. Limitation of Liability',
        description: 'To the fullest extent the law allows, Imagi will not be liable for indirect, incidental, special, consequential or punitive damages, or for lost profits, revenue, data or goodwill. Imagi\'s total liability for any claim relating to the service is limited to the greater of what you paid Imagi in the 12 months before the claim, or $100.'
      },
      {
        badge: '10. Indemnity',
        description: 'You agree to cover Imagi\'s losses and costs, including reasonable legal fees, from claims arising out of your content, your app, your use of Imagi, or your breach of these terms.'
      },
      {
        badge: '11. Ending Your Use',
        description: 'You can stop using Imagi and ask us to close your account at any time. We may suspend or close an account that breaks these terms, puts Imagi or others at risk, or goes unpaid. Sections 4 and 8 through 12 continue to apply after your account closes.'
      },
      {
        badge: '12. Governing Law',
        description: 'Imagi is based in Grand Rapids, Michigan. These terms are governed by the laws of the State of Michigan, United States, without regard to conflict-of-law rules. Disputes will be handled in the state or federal courts serving Kent County, Michigan, except where the law gives you the right to bring a claim elsewhere.'
      },
      {
        badge: '13. Changes and Contact',
        description: 'We may update these terms as Imagi changes. When we do, we will change the date at the top of this page, and for significant changes we will let you know in the product or by email. Continuing to use Imagi after a change means you accept the updated terms.'
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
