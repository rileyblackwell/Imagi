<template>
  <DocsLayout>
    <div class="max-w-5xl mx-auto">
      <DocsPageHeader
        badge-text="PRICING"
        title="Plans & Usage"
        description="Start free, then upgrade as you grow. Here's how plans, usage limits, credits, and billing work."
      />

      <!-- How usage works -->
      <section class="mb-16">
        <h2 class="font-display text-3xl sm:text-4xl font-semibold text-blue-950 dark:text-white mb-6 tracking-[-0.015em] transition-colors duration-300">
          How Usage Works
        </h2>
        <div class="space-y-4 text-blue-950/70 dark:text-blue-100/70 text-lg leading-relaxed mb-8 transition-colors duration-300">
          <p>
            Building with AI consumes <strong class="font-semibold text-blue-950 dark:text-white">usage</strong>. Rather than
            charging per message, Imagi meters how much AI work you do against your plan's limits over two rolling windows:
            a <strong class="font-semibold text-blue-950 dark:text-white">5-hour session</strong> and a
            <strong class="font-semibold text-blue-950 dark:text-white">weekly</strong> limit.
          </p>
          <p>
            Because the windows roll, usage frees up gradually as older activity ages out—rather than resetting all at once.
            Your plan sets how much you can do in each window, and smarter models or higher reasoning effort use it faster
            (see <router-link to="/docs/models" class="text-blue-700 dark:text-blue-300 font-medium hover:underline">Models &amp; Reasoning</router-link>).
          </p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <DocsCard title="The Usage panel">
            In the Build workspace, the Usage panel shows both windows as a percent used, with a meter and a "resets" time,
            so you always know where you stand. It refreshes automatically after each agent run.
          </DocsCard>
          <DocsCard title="Reaching a limit">
            If you hit a limit, the agent tells you clearly and when it resets. You can wait for usage to free up as the
            window rolls, or upgrade your plan for a higher limit.
          </DocsCard>
        </div>
      </section>

      <!-- Plans -->
      <section class="mb-16">
        <h2 class="font-display text-3xl sm:text-4xl font-semibold text-blue-950 dark:text-white mb-6 tracking-[-0.015em] transition-colors duration-300">
          Plans
        </h2>
        <p class="text-blue-950/70 dark:text-blue-100/70 text-lg leading-relaxed mb-8 transition-colors duration-300">
          Every plan uses the same rolling 5-hour and weekly windows—higher plans simply give you more usage in each. Paid
          plans are billed monthly.
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <DocsCard title="Free — $0">
            <ul class="space-y-2 mt-1">
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>Access to the core AI builder</span></li>
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>1 active project</span></li>
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>Standard models &amp; basic usage</span></li>
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>Community support</span></li>
            </ul>
          </DocsCard>
          <DocsCard title="Pro — $20 / month">
            <ul class="space-y-2 mt-1">
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>Everything in Free</span></li>
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>Unlimited projects</span></li>
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>Advanced models &amp; more usage</span></li>
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>Priority support</span></li>
            </ul>
          </DocsCard>
          <DocsCard title="Max (5×) — $100 / month">
            <ul class="space-y-2 mt-1">
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>Everything in Pro</span></li>
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>5× more usage than Pro</span></li>
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>Higher output limits</span></li>
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>Early access to new features</span></li>
            </ul>
          </DocsCard>
          <DocsCard title="Max (20×) — $200 / month">
            <ul class="space-y-2 mt-1">
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>Everything in Pro</span></li>
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>20× more usage than Pro</span></li>
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>Highest output limits</span></li>
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>Priority access at peak times</span></li>
            </ul>
          </DocsCard>
        </div>
      </section>

      <!-- On-demand credits -->
      <section class="mb-16">
        <h2 class="font-display text-3xl sm:text-4xl font-semibold text-blue-950 dark:text-white mb-6 tracking-[-0.015em] transition-colors duration-300">
          On-Demand Credits
        </h2>
        <p class="text-blue-950/70 dark:text-blue-100/70 text-lg leading-relaxed mb-8 transition-colors duration-300">
          Hit your session or weekly limit in the middle of a build? You can buy additional usage credits at any time
          without changing your plan. Choose a preset amount—$10, $25, $50, or $100—or enter a custom amount. Credits are
          added to your account instantly, stack on top of your plan, and never expire.
        </p>
        <div class="bg-blue-50/70 dark:bg-blue-400/[0.08] border border-blue-200/70 dark:border-blue-300/[0.14] rounded-xl p-6 transition-colors duration-300">
          <h4 class="text-xs font-semibold uppercase tracking-[0.18em] text-blue-700 dark:text-blue-300 mt-0 mb-3 transition-colors duration-300">
            Your balance
          </h4>
          <p class="text-lg text-blue-950/70 dark:text-blue-100/70 mb-0 leading-relaxed">
            The Build workspace shows your account balance right in the toolbar, so you can keep an eye on it as you work.
            It refreshes shortly after each AI operation.
          </p>
        </div>
      </section>

      <!-- Billing -->
      <section class="mb-16">
        <h2 class="font-display text-3xl sm:text-4xl font-semibold text-blue-950 dark:text-white mb-6 tracking-[-0.015em] transition-colors duration-300">
          Billing
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <DocsCard title="Secure checkout">
            Subscriptions and credit top-ups are handled through Stripe—secure and encrypted. Your card details are managed
            by Stripe, never stored by Imagi.
          </DocsCard>
          <DocsCard title="Manage your plan">
            Upgrade, downgrade, or cancel any time through the billing portal. Changes to your plan take effect on your
            account, adjusting your usage limits accordingly.
          </DocsCard>
        </div>
      </section>

      <!-- Next steps -->
      <section class="mb-16">
        <h2 class="font-display text-3xl sm:text-4xl font-semibold text-blue-950 dark:text-white mb-6 tracking-[-0.015em] transition-colors duration-300">
          Next Steps
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <DocsNavigationCard
            to="/docs/models"
            title="Models & Reasoning"
            description="Learn how model and reasoning choices affect how fast you use your plan."
          />
          <DocsNavigationCard
            to="/docs/building"
            title="Building with AI"
            description="Head back to the workspace and keep building your app."
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
