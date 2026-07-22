<template>
  <DocsLayout>
    <div class="max-w-5xl mx-auto">
      <DocsPageHeader
        badge-text="DOCUMENTATION"
        title="Welcome to Imagi"
        description="The all-in-one platform to build and run your business."
      />

      <!-- What is Imagi -->
      <section class="mb-16">
        <h2 class="font-display text-3xl sm:text-4xl font-semibold text-blue-950 dark:text-white mb-6 tracking-[-0.015em] transition-colors duration-300">
          What is Imagi?
        </h2>
        <div class="space-y-4 text-blue-950/70 dark:text-blue-100/70 text-lg leading-relaxed transition-colors duration-300">
          <p>
            Imagi is an all-in-one platform for building and running a business. First, you build your
            web application with AI-powered tools: design visually, chat with AI to plan and write code,
            and launch to the web—all designed to be fast, affordable, and approachable.
          </p>
          <p>
            Then you run your business with built-in tools for marketing, sales, and finance. Whether you're
            launching a startup or growing a small business, Imagi takes you from idea to a running business
            without requiring a technical team.
          </p>
        </div>
      </section>

      <!-- Who is it for -->
      <section class="mb-16">
        <h2 class="font-display text-3xl sm:text-4xl font-semibold text-blue-950 dark:text-white mb-8 tracking-[-0.015em] transition-colors duration-300">
          Who is it for?
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <DocsCard title="Startup Founders">
            Go from idea to a running business without hiring a team—build your product, then find customers and grow revenue.
          </DocsCard>
          <DocsCard title="Small Business Owners">
            Get your business online and manage marketing, sales, and finances in one place instead of juggling separate tools.
          </DocsCard>
          <DocsCard title="Creators & Side Hustlers">
            Turn a project or passion into a real business—build the app, market it, take payments, and track the money.
          </DocsCard>
        </div>
      </section>

      <!-- How Does Imagi Work -->
      <section class="mb-16">
        <h2 class="font-display text-3xl sm:text-4xl font-semibold text-blue-950 dark:text-white mb-6 tracking-[-0.015em] transition-colors duration-300">
          How Does Imagi Work?
        </h2>
        <p class="text-blue-950/70 dark:text-blue-100/70 text-lg leading-relaxed mb-8 transition-colors duration-300">
          Imagi brings everything you need to build and run a business into one seamless platform. You start by
          building your web app, then use built-in tools to operate and grow your business:
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <DocsCard title="Build">
            Describe what you want in plain language and Imagi's AI agents generate the pages, styling, and logic
            for your product—refining it live in an interactive preview, with no coding or server setup required.
          </DocsCard>
          <DocsCard title="Sell">
            Turn visitors into paying customers. Create a product catalog, share checkout links, and track orders
            and customer relationships—payments powered by your own Stripe account.
          </DocsCard>
          <DocsCard title="Market">
            Reach and engage your audience over text and voice with Twilio-powered campaigns, hold two-way
            conversations in a shared inbox, and keep an eye on your Google and Meta ad campaigns in one place.
          </DocsCard>
          <DocsCard title="Operate">
            Run the day-to-day from a single command center—record income and expenses, send invoices and get
            paid, and track your tasks, with dashboards that show the health of your business at a glance.
          </DocsCard>
        </div>
      </section>

      <!-- Why Choose Imagi -->
      <section class="mb-16">
        <h2 class="font-display text-3xl sm:text-4xl font-semibold text-blue-950 dark:text-white mb-6 tracking-[-0.015em] transition-colors duration-300">
          Why Choose Imagi?
        </h2>
        <p class="text-blue-950/70 dark:text-blue-100/70 text-lg leading-relaxed mb-8 transition-colors duration-300">
          Imagi is built on the principle that starting and running a business should be accessible to everyone,
          not just those with technical teams and big budgets. Here's what sets us apart:
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <DocsCard title="Everything in One Place">
            Build your product and run marketing, sales, and finance from a single platform. No more stitching
            together a dozen separate subscriptions to keep your business running.
          </DocsCard>
          <DocsCard title="Affordable & Transparent">
            Get started for a fraction of the cost of hiring developers or a full software stack. No hidden fees,
            no vendor lock-in—just straightforward pricing that scales with your needs.
          </DocsCard>
          <DocsCard title="Built to Move Fast">
            Go from idea to a live product and paying customers quickly. Every feature is designed to help you
            launch, find traction, and grow without technical roadblocks.
          </DocsCard>
          <DocsCard title="Room to Grow">
            As your business scales, your app grows with you. Imagi generates standard Vue.js and Django code
            that any developer can pick up and extend when you're ready.
          </DocsCard>
        </div>
      </section>

      <!-- Learn More Section -->
      <section class="mb-16">
        <h2 class="font-display text-3xl sm:text-4xl font-semibold text-blue-950 dark:text-white mb-6 tracking-[-0.015em] transition-colors duration-300">
          Learn More
        </h2>
        <p class="text-blue-950/70 dark:text-blue-100/70 text-lg leading-relaxed mb-8 transition-colors duration-300">
          Ready to dive deeper? Explore these guides to learn more about using Imagi:
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <DocsNavigationCard
            to="/docs/building"
            title="Building with AI"
            description="Create a project and build your app by chatting with Imagi's AI agents."
          />
          <DocsNavigationCard
            to="/docs/running-your-business"
            title="Running Your Business"
            description="Sell, market, and operate your business with the built-in workspaces."
          />
          <DocsNavigationCard
            to="/docs/models"
            title="Models & Reasoning"
            description="Choose the right AI model and reasoning effort for each task."
          />
          <DocsNavigationCard
            to="/docs/plans"
            title="Plans & Usage"
            description="Understand plans, usage limits, credits, and billing."
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
