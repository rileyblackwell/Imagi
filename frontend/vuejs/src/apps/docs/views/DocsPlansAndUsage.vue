<template>
  <DocsLayout>
    <div class="max-w-5xl mx-auto">
      <DocsPageHeader
        badge-text="PRICING"
        title="Plans & Usage"
        description="Start free, then upgrade as you grow. Here's how plans, usage allowances, and billing work."
      />

      <!-- How usage works -->
      <section class="mb-16">
        <h2 class="font-display text-3xl sm:text-4xl font-semibold text-blue-950 dark:text-white mb-6 tracking-[-0.015em] transition-colors duration-300">
          How Usage Works
        </h2>
        <div class="space-y-4 text-blue-950/70 dark:text-blue-100/70 text-lg leading-relaxed mb-8 transition-colors duration-300">
          <p>
            Every plan includes a monthly <strong class="font-semibold text-blue-950 dark:text-white">usage allowance</strong>,
            quoted in dollars of AI work—$5 a month on Free, $20 on Pro. Nothing is charged per run: each run's cost is
            simply metered against two rolling windows, a
            <strong class="font-semibold text-blue-950 dark:text-white">5-hour session</strong> and a
            <strong class="font-semibold text-blue-950 dark:text-white">weekly</strong> window. Those windows are how the
            monthly amount is delivered, and they are the only two limits you'll ever see—there is no separate monthly
            counter running in the background.
          </p>
          <p>
            Because the allowance is measured in dollars rather than messages, what you spend depends on the model you pick
            and how hard you ask it to think. A quick edit on the light model costs a fraction of a cent; a long build on the
            flagship model at high reasoning effort costs far more
            (see <router-link to="/docs/models" class="text-blue-700 dark:text-blue-300 font-medium hover:underline">Models &amp; Reasoning</router-link>).
          </p>
          <p>
            Because the windows roll, allowance frees up gradually as older activity ages out—rather than resetting all at once.
          </p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <DocsCard title="The Usage panel">
            In the Build workspace, the Usage panel shows both windows as dollars spent against their allowance, with a meter
            and a "resets" time, so you always know where you stand. It refreshes automatically after each agent run.
          </DocsCard>
          <DocsCard title="Running out">
            If you use up a window's allowance, the agent tells you clearly and when it resets. You can wait for it to free up
            as the window rolls, switch to a lighter model or lower reasoning effort, or upgrade your plan.
          </DocsCard>
        </div>
      </section>

      <!-- Plans -->
      <section class="mb-16">
        <h2 class="font-display text-3xl sm:text-4xl font-semibold text-blue-950 dark:text-white mb-6 tracking-[-0.015em] transition-colors duration-300">
          Plans
        </h2>
        <p class="text-blue-950/70 dark:text-blue-100/70 text-lg leading-relaxed mb-8 transition-colors duration-300">
          Every plan uses the same rolling 5-hour and weekly windows—higher plans simply give you a bigger allowance in each.
          A week's allowance is spread over five 5-hour sessions, so one long sitting can't drain the whole week, and the
          weekly figures below are set generously against the monthly amount rather than dividing it thinly.
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <DocsCard title="Free — $0">
            <ul class="space-y-2 mt-1">
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>$5 of AI usage per month</span></li>
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>Metered as $2.50 per week, $0.50 per 5-hour session</span></li>
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>1 active project</span></li>
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>Community support</span></li>
            </ul>
          </DocsCard>
          <DocsCard title="Pro — $20 / month">
            <ul class="space-y-2 mt-1">
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>$20 of AI usage per month</span></li>
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>Metered as $10 per week, $2 per 5-hour session</span></li>
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>Unlimited projects</span></li>
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>Priority support</span></li>
            </ul>
          </DocsCard>
          <DocsCard title="Max (5×) — $100 / month">
            <ul class="space-y-2 mt-1">
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>$100 of AI usage per month — 5× Pro</span></li>
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>Metered as $50 per week, $10 per 5-hour session</span></li>
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>Everything in Pro</span></li>
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>Early access to new features</span></li>
            </ul>
          </DocsCard>
          <DocsCard title="Max (20×) — $200 / month">
            <ul class="space-y-2 mt-1">
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>$400 of AI usage per month — 20× Pro</span></li>
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>Metered as $200 per week, $40 per 5-hour session</span></li>
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>Everything in Pro</span></li>
              <li class="flex items-start gap-2.5"><span class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2 flex-shrink-0" aria-hidden="true"></span><span>Priority access at peak times</span></li>
            </ul>
          </DocsCard>
        </div>
      </section>

      <!-- Making your allowance go further -->
      <section class="mb-16">
        <h2 class="font-display text-3xl sm:text-4xl font-semibold text-blue-950 dark:text-white mb-6 tracking-[-0.015em] transition-colors duration-300">
          Making Your Allowance Go Further
        </h2>
        <p class="text-blue-950/70 dark:text-blue-100/70 text-lg leading-relaxed mb-8 transition-colors duration-300">
          Since usage is metered by what each run actually costs, the two dials you control are the model and the reasoning
          effort. Reach for GPT 5.6 Sol at high effort when a task genuinely needs it, and drop to Terra or Luna at a lower
          effort for routine edits, copy tweaks, and questions—it costs a fraction as much and is usually faster too.
        </p>
        <div class="bg-blue-50/70 dark:bg-blue-400/[0.08] border border-blue-200/70 dark:border-blue-300/[0.14] rounded-xl p-6 transition-colors duration-300">
          <h4 class="text-xs font-semibold uppercase tracking-[0.18em] text-blue-700 dark:text-blue-300 mt-0 mb-3 transition-colors duration-300">
            Keeping an eye on it
          </h4>
          <p class="text-lg text-blue-950/70 dark:text-blue-100/70 mb-0 leading-relaxed">
            The Build workspace shows how much of your 5-hour allowance is left right in the toolbar, and the Usage panel
            breaks out both windows in dollars. Both refresh shortly after each AI run.
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
            Subscriptions are handled through Stripe—secure and encrypted. Your card details are managed by Stripe, never
            stored by Imagi.
          </DocsCard>
          <DocsCard title="Manage your plan">
            Upgrade, downgrade, or cancel any time through the billing portal. Changes take effect on your account right
            away, adjusting your usage allowance accordingly.
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
