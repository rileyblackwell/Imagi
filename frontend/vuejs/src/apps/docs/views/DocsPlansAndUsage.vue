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
        <h2 class="display display--section">
          How Usage Works
        </h2>
        <div class="space-y-4 text-[color:var(--ink-55)] text-lg leading-relaxed mb-8 transition-colors duration-300">
          <p>
            Every plan includes a <strong class="ink-strong">weekly usage allowance</strong>,
            quoted in dollars of AI work—$10 a week on Free, $20 on Pro. Nothing is charged per run: each run's cost is
            simply metered against one
            <strong class="ink-strong">rolling weekly window</strong>. That window is the only
            limit you'll ever see—there is no session cap and no separate monthly counter running in the background.
          </p>
          <p>
            Because the allowance is measured in dollars rather than messages, what you spend depends on the model you pick
            and how hard you ask it to think. A quick edit on the light model costs a fraction of a cent; a long build on the
            flagship model at high reasoning effort costs far more
            (see <router-link to="/docs/models" class="text-[color:var(--accent)] font-medium hover:underline">Models &amp; Reasoning</router-link>).
          </p>
          <p>
            Because the window rolls, allowance frees up gradually as older activity ages out—rather than resetting all at once.
          </p>
        </div>
        <div class="rule-cols rule-cols--2">
          <DocsCard title="The Usage panel">
            In the Build workspace, the Usage panel shows the week's spend against your allowance, with a meter
            and a "resets" time, so you always know where you stand. It refreshes automatically after each agent run.
          </DocsCard>
          <DocsCard title="Running out">
            If you use up the week's allowance, the agent tells you clearly and when it resets. You can wait for it to free up
            as the window rolls, switch to a lighter model or lower reasoning effort, or upgrade your plan.
          </DocsCard>
        </div>
      </section>

      <!-- Plans -->
      <section class="mb-16">
        <h2 class="display display--section">
          Plans
        </h2>
        <p class="lede lede--section">
          Every plan uses the same rolling weekly window—higher plans simply give you a bigger allowance in it. There is no
          session limit on top, so a single long sitting can use as much of the week's allowance as you want it to.
        </p>
        <div class="rule-cols rule-cols--2">
          <DocsCard title="Free — $0">
            <ul class="space-y-2 mt-1">
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>$10 of AI usage per week</span></li>
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>1 active project</span></li>
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>Community support</span></li>
            </ul>
          </DocsCard>
          <DocsCard title="Pro — $25 / month">
            <ul class="space-y-2 mt-1">
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>$20 of AI usage per week</span></li>
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>Unlimited projects</span></li>
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>Priority support</span></li>
            </ul>
          </DocsCard>
          <DocsCard title="Max (5×) — $100 / month">
            <ul class="space-y-2 mt-1">
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>$100 of AI usage per week — 5× Pro</span></li>
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>Everything in Pro</span></li>
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>Early access to new features</span></li>
            </ul>
          </DocsCard>
          <DocsCard title="Max (10×) — $200 / month">
            <ul class="space-y-2 mt-1">
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>$200 of AI usage per week — 10× Pro</span></li>
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>Everything in Pro</span></li>
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>Priority access at peak times</span></li>
            </ul>
          </DocsCard>
        </div>
      </section>

      <!-- Making your allowance go further -->
      <section class="mb-16">
        <h2 class="display display--section">
          Making Your Allowance Go Further
        </h2>
        <p class="lede lede--section">
          Since usage is metered by what each run actually costs, the two dials you control are the model and the reasoning
          effort. Reach for GPT 5.6 Sol at high effort when a task genuinely needs it, and drop to Terra or Luna at a lower
          effort for routine edits, copy tweaks, and questions—it costs a fraction as much and is usually faster too.
        </p>
        <div class="callout">
          <h4 class="callout__title">
            Keeping an eye on it
          </h4>
          <p class="callout__body">
            The Build workspace shows how much of your weekly allowance is left right in the toolbar, and the Usage panel
            shows the same figure in dollars. Both refresh shortly after each AI run.
          </p>
        </div>
      </section>

      <!-- Billing -->
      <section class="mb-16">
        <h2 class="display display--section">
          Billing
        </h2>
        <div class="rule-cols rule-cols--2">
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
        <h2 class="display display--section">
          Next Steps
        </h2>
        <div class="rule-cols rule-cols--2">
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
