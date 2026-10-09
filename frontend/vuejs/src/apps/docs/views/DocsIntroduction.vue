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
        <h2 class="display display--section">
          What is Imagi?
        </h2>
        <div class="lede space-y-4 text-lg">
          <p>
            Imagi is an all-in-one platform for building and running a business. Each business is a
            <strong class="ink-strong">project</strong>. First, you build its web application with AI: describe what you
            want in chat, and Imagi's agents plan and write the code while you watch it take shape in a live preview—all
            designed to be fast, affordable, and approachable.
          </p>
          <p>
            Then you run your business from the same project with built-in tools for marketing, sales, and day-to-day
            operations. Whether you're
            launching a startup or growing a small business, Imagi takes you from idea to a running business
            without requiring a technical team.
          </p>
        </div>
      </section>

      <!-- Who is it for -->
      <section class="mb-16">
        <h2 class="display text-3xl sm:text-4xl mb-8">
          Who is it for?
        </h2>
        <div class="rule-cols">
          <DocsCard title="Startup Founders">
            Go from idea to a running business without hiring a team—build your product, then find customers and grow revenue.
          </DocsCard>
          <DocsCard title="Small Business Owners">
            Build your business's web app and manage marketing, sales, and finances in one place instead of juggling separate tools.
          </DocsCard>
          <DocsCard title="Creators & Side Hustlers">
            Turn a project or passion into a real business—build the app, market it, take payments, and track the money.
          </DocsCard>
        </div>
      </section>

      <!-- Getting started -->
      <section class="mb-16">
        <h2 class="display display--section">
          Getting Started
        </h2>
        <ul class="space-y-3">
          <li class="flex items-start gap-3">
            <div class="checklist__tick mt-2.5" aria-hidden="true"></div>
            <span class="text-lg leading-relaxed"><strong class="ink-strong">Create a project</strong> — give your business a
              name, describe what it does, and optionally say how the app should work and the look you want.</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="checklist__tick mt-2.5" aria-hidden="true"></div>
            <span class="text-lg leading-relaxed"><strong class="ink-strong">Get a first build automatically</strong> — Imagi
              builds your home page first, in about a minute, then adds the other pages your business needs as AI agents
              finish them, on top of a working foundation with sign-in built in.</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="checklist__tick mt-2.5" aria-hidden="true"></div>
            <span class="text-lg leading-relaxed"><strong class="ink-strong">Keep building by chatting</strong> — open the
              Build workspace and ask for changes; the preview updates as the agents work.</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="checklist__tick mt-2.5" aria-hidden="true"></div>
            <span class="text-lg leading-relaxed"><strong class="ink-strong">Run the business</strong> — the project's hub
              links to Build and to the Sell, Market, and Operate workspaces, which are in beta.</span>
          </li>
        </ul>
      </section>

      <!-- How Does Imagi Work -->
      <section class="mb-16">
        <h2 class="display display--section">
          How Does Imagi Work?
        </h2>
        <p class="lede lede--section">
          Imagi brings everything you need to build and run a business into one seamless platform. You start by
          building your web app, then use built-in tools to operate and grow your business:
        </p>
        <div class="rule-cols rule-cols--2">
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
            conversations in an inbox, and keep an eye on your Google and Meta ad campaigns in one place.
          </DocsCard>
          <DocsCard title="Operate">
            One dashboard for running the business: whether your app is up and fast, who is visiting, and your
            revenue, expenses, and profit.
          </DocsCard>
        </div>
      </section>

      <!-- Why Choose Imagi -->
      <section class="mb-16">
        <h2 class="display display--section">
          Why Choose Imagi?
        </h2>
        <p class="lede lede--section">
          Imagi is built on the principle that starting and running a business should be accessible to everyone,
          not just those with technical teams and big budgets. Here's what sets us apart:
        </p>
        <div class="rule-cols rule-cols--2">
          <DocsCard title="Everything in One Place">
            Build your product and run marketing, sales, and operations from a single platform. No more stitching
            together a dozen separate subscriptions to keep your business running.
          </DocsCard>
          <DocsCard title="Affordable & Transparent">
            Get started for a fraction of the cost of hiring developers or a full software stack. AI usage is metered
            at the AI providers' own list prices with no markup, and a free plan lets you try everything first.
          </DocsCard>
          <DocsCard title="Built to Move Fast">
            Go from idea to a working app and paying customers quickly. Every feature is designed to help you
            launch, find traction, and grow without technical roadblocks.
          </DocsCard>
          <DocsCard title="Room to Grow">
            As your business scales, your app grows with you. Imagi builds it with Vue.js and Django—standard,
            widely used open-source frameworks, not a proprietary format.
          </DocsCard>
        </div>
      </section>

      <!-- Learn More Section -->
      <section class="mb-16">
        <h2 class="display display--section">
          Learn More
        </h2>
        <p class="lede lede--section">
          Ready to dive deeper? Explore these guides to learn more about using Imagi:
        </p>
        <div class="rule-cols rule-cols--2">
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
            description="Understand plans, usage allowances, and billing."
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
