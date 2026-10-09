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
            where they sit under "Run the business", next to Build under "Build the product". The Build card also
            shows when your app's first build is still being written.
          </p>
          <p>
            Sell and Market connect to your own third-party accounts—Stripe for payments, Twilio for messaging—so money and
            messages flow through accounts you control. Operate needs no connection; it is one dashboard for your live app
            and your business's money.
          </p>
          <p>
            All three are in <strong class="ink-strong">beta</strong>. They work today, and they are still in development,
            so expect them to grow and change. Each one carries a Beta label in your project hub and on its own page.
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
          checkout links or prebuilt payment pages, and track the orders and customers that result. An Overview tab sums
          it all up. Payments run through
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
        <div class="bg-ink/[0.03] dark:bg-blue-400/[0.08] border border-[color:var(--rule)] rounded-xl p-6 mt-6 transition-colors duration-300">
          <h4 class="callout__title">
            Connecting Stripe
          </h4>
          <p class="callout__body">
            In Sell's Settings, paste your Stripe keys and pick a currency (USD, EUR, GBP, CAD, or AUD). Your secret key is
            stored encrypted and never shown again. A "Test connection" check confirms your account is ready to take
            charges, and a "Connected" badge appears once you're set up. Optionally, add a webhook signing secret—Settings
            shows the endpoint URL to give Stripe—so orders update to paid on their own; without it, use "Refresh status" on
            a pending order. Settings also lists the storefront API your app can call to list products and start a
            checkout.
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
            Compose a campaign, pick a channel—text blast or automated voice broadcast in the voice you choose—and send it
            now. Text campaigns can also be scheduled from 15 minutes to 35 days ahead (this needs a Twilio Messaging Service
            SID in Settings), and a scheduled campaign can be canceled. Personalize messages with
            <code v-pre>{{first_name}}</code>, <code v-pre>{{last_name}}</code>, or
            <code v-pre>{{name}}</code>, and watch a live character and SMS-segment count as you write.
          </DocsCard>
          <DocsCard title="Two-way inbox">
            Read and reply to customer texts in an inbox, one conversation per contact. Each campaign reports how many
            messages were delivered, pending, or failed, and the Overview tracks replies across all your messaging.
          </DocsCard>
          <DocsCard title="Audience">
            Manage your contacts as a searchable list with tags and consent front and center. Add people one at a time or
            bulk-import a batch by pasting one contact per line, and segment campaigns by tag.
          </DocsCard>
          <DocsCard title="Ads">
            Connect Google Ads and Meta Ads in Market's Settings by pasting your API credentials, then monitor spend,
            impressions, clicks, and conversions in one dashboard—sync on demand, filter by platform, and pause or resume
            campaigns without leaving Imagi.
          </DocsCard>
        </div>
        <div class="bg-ink/[0.03] dark:bg-blue-400/[0.08] border border-[color:var(--rule)] rounded-xl p-6 mt-6 transition-colors duration-300">
          <h4 class="callout__title">
            Messaging responsibly
          </h4>
          <p class="callout__body">
            Campaigns only go to subscribed contacts. New contacts—added by hand or imported—start out subscribed, so only
            add people who've agreed to hear from you. Replies of "STOP" unsubscribe someone automatically, and "START"
            re-subscribes them, keeping your audience consent-based.
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
          Operate is a dashboard with two halves. One side watches your app: is it up, is it fast, and who is visiting.
          The other watches your business: revenue, expenses, and profit. No third-party connection required.
        </p>
        <div class="rule-cols rule-cols--2">
          <DocsCard title="Your app">
            Add the address your app lives at and Imagi checks it for uptime and response time, whenever you open
            Operate or press "Check now". To count visitors, paste the page-view tag Operate gives you into your app (or
            ask Build to add it). The tag sets no cookies and only counts visits to your live address, never the preview.
          </DocsCard>
          <DocsCard title="Your business">
            Revenue, expenses, and profit for the last 30 days, plus a month-by-month chart. Revenue counts payments
            taken through Sell plus any income you record; expenses come from the ledger. Record either from the Ledger
            tab, each with a category, amount, and date.
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
