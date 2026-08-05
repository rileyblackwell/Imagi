<template>
  <DocsLayout>
    <div class="max-w-5xl mx-auto">
      <DocsPageHeader
        badge-text="RUN"
        title="Running Your Business"
        description="Once your app is built, sell to customers, reach your audience, and run the day-to-day—all from the same project."
      />

      <!-- Overview -->
      <section class="mb-16">
        <div class="lede space-y-4 text-lg">
          <p>
            Building your product is only half the job. Every Imagi project comes with three more workspaces for actually
            running the business: <strong class="ink-strong">Sell</strong>,
            <strong class="ink-strong">Market</strong>, and
            <strong class="ink-strong">Operate</strong>. You open them from your project hub,
            right alongside Build.
          </p>
          <p>
            Sell and Market connect to your own third-party accounts—Stripe for payments, Twilio for messaging—so money and
            messages flow through accounts you control. Operate needs no connection; it ties everything together with
            finances, invoicing, and tasks.
          </p>
        </div>
      </section>

      <!-- SELL -->
      <section class="mb-16">
        <h2 class="display text-3xl sm:text-4xl mb-2">
          Sell
        </h2>
        <p class="text-emerald-700 dark:text-emerald-300 text-sm font-semibold uppercase tracking-[0.14em] mb-6 transition-colors duration-300">
          Turn visitors into customers
        </p>
        <p class="lede lede--section">
          Sell is your storefront and payments back office. You build a product catalog, collect money through shareable
          checkout links or prebuilt payment pages, and track the orders and customers that result. Payments run through
          <strong class="ink-strong">your own Stripe account</strong>—Imagi never holds your funds.
        </p>
        <div class="rule-cols rule-cols--2">
          <DocsCard title="Products & checkout">
            Create products with a name, price, image, and billing interval—one-time, monthly, or yearly. Copy a payment
            link for any product and share it anywhere; it opens a secure Stripe checkout page.
          </DocsCard>
          <DocsCard title="Payment pages">
            Install prebuilt, secure payment pages into your app with one click. Card details never touch your app—Stripe
            handles the card, and prices can't be tampered with.
          </DocsCard>
          <DocsCard title="Orders">
            Track every order by status—pending, paid, fulfilled, canceled, or refunded—and mark orders fulfilled as you ship.
          </DocsCard>
          <DocsCard title="Customers">
            A lightweight CRM. Buyers appear automatically after checkout, and you can add contacts by hand—each with total
            spent, order history, and notes.
          </DocsCard>
        </div>
        <div class="bg-blue-50/70 dark:bg-blue-400/[0.08] border border-[color:var(--rule)] rounded-xl p-6 mt-6 transition-colors duration-300">
          <h4 class="callout__title">
            Connecting Stripe
          </h4>
          <p class="callout__body">
            In Sell's Settings, paste your Stripe keys and pick a currency. Your secret key is stored encrypted and never
            shown again. A "Test connection" check confirms your account is ready to take charges, and a "Connected" badge
            appears once you're set up.
          </p>
        </div>
      </section>

      <!-- MARKET -->
      <section class="mb-16">
        <h2 class="display text-3xl sm:text-4xl mb-2">
          Market
        </h2>
        <p class="text-violet-700 dark:text-violet-300 text-sm font-semibold uppercase tracking-[0.14em] mb-6 transition-colors duration-300">
          Grow your audience
        </p>
        <p class="lede lede--section">
          Market is your outbound-messaging and advertising hub. Connect your own <strong class="ink-strong">Twilio</strong>
          account to send text and voice campaigns to an opt-in contact list, hold two-way conversations in an inbox, and
          keep an eye on your Google and Meta ad campaigns—all in one place.
        </p>
        <div class="rule-cols rule-cols--2">
          <DocsCard title="SMS & voice campaigns">
            Compose a campaign, pick a channel—text blast or automated voice broadcast—and send it now or schedule it for later.
            Personalize each message with the contact's name, and see a live character count as you write.
          </DocsCard>
          <DocsCard title="Two-way inbox">
            Read and reply to customer texts in a shared inbox, one conversation per contact. Delivery and reply tracking
            let you see exactly how a campaign landed.
          </DocsCard>
          <DocsCard title="Audience">
            Manage your contacts as a searchable list with tags and consent front and center. Add people one at a time or
            bulk-import a batch, and segment campaigns by tag.
          </DocsCard>
          <DocsCard title="Ads">
            Connect Google Ads and Meta Ads to monitor spend, impressions, clicks, and conversions in one dashboard—and
            pause or resume campaigns without leaving Imagi.
          </DocsCard>
        </div>
        <div class="bg-blue-50/70 dark:bg-blue-400/[0.08] border border-[color:var(--rule)] rounded-xl p-6 mt-6 transition-colors duration-300">
          <h4 class="callout__title">
            Messaging responsibly
          </h4>
          <p class="callout__body">
            Market only sends to contacts who've opted in. Replies of "STOP" unsubscribe someone automatically, and "START"
            re-subscribes them—so your audience stays consent-based and compliant.
          </p>
        </div>
      </section>

      <!-- OPERATE -->
      <section class="mb-16">
        <h2 class="display text-3xl sm:text-4xl mb-2">
          Operate
        </h2>
        <p class="text-amber-700 dark:text-amber-300 text-sm font-semibold uppercase tracking-[0.14em] mb-6 transition-colors duration-300">
          Run the business
        </p>
        <p class="lede lede--section">
          Operate is your command center. It brings together a financial ledger, invoicing, and a task list, and its
          dashboard even pulls in a pulse from Sell and Market—so you can see how the whole business is doing at a glance.
          No third-party connection required.
        </p>
        <div class="rule-cols rule-cols--2">
          <DocsCard title="Business dashboard">
            Income, expenses, and net over the last 30 days, plus a cash-flow chart, what's awaiting payment, and what's up
            next. An "Across your business" view surfaces sales and messaging activity from Sell and Market.
          </DocsCard>
          <DocsCard title="Finance">
            Record income and expenses in a simple ledger, each with a category, amount, and date. Marking an invoice paid
            records the income for you automatically.
          </DocsCard>
          <DocsCard title="Invoices">
            Create invoices with line items, issue and due dates, and notes. Move each from draft to sent to paid, and
            overdue invoices are flagged so nothing slips.
          </DocsCard>
          <DocsCard title="Tasks">
            Keep the day-to-day organized with a task list—priorities, due dates, and simple open / in-progress / done
            states so the work stays on track.
          </DocsCard>
        </div>
      </section>

      <!-- Next steps -->
      <section class="mb-16">
        <h2 class="display display--section">
          Next Steps
        </h2>
        <div class="rule-cols rule-cols--2">
          <DocsNavigationCard
            to="/docs/building"
            title="Building with AI"
            description="Build and refine the app your business runs on with Imagi's AI agents."
          />
          <DocsNavigationCard
            to="/docs/plans"
            title="Plans & Usage"
            description="See how plans, usage limits, and billing work as your business grows."
          />
        </div>
      </section>
    </div>
  </DocsLayout>
</template>

<script setup>
import DocsLayout from '../layouts/DocsLayout.vue';
import { DocsCard, DocsNavigationCard, DocsPageHeader } from '../components';
</script>
