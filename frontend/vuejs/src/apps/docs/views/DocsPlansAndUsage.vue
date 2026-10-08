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
            quoted in dollars of AI work—$3 a week on Free, $10 on Pro. Nothing is charged per run: each run's cost is
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
            Usage is metered at the AI providers' own list prices, with no markup. Follow-up messages in a conversation cost
            less than the first, because the parts of your project the model has already read are billed at the providers'
            lower cached rate. Besides chatting with the agent, creating a project (its automatic first build) and voice
            dictation also count toward your allowance.
          </p>
          <p>
            Because the window rolls, allowance frees up gradually as older activity ages out—rather than resetting all at once.
          </p>
        </div>
        <div class="rule-cols rule-cols--2">
          <DocsCard title="The Usage panel">
            In the Build workspace, the Usage button in the chat toolbar opens a panel showing how much of the week's
            allowance you've used, as a percentage with a meter, and when usage next frees up. It refreshes after each agent
            run and whenever you open it.
          </DocsCard>
          <DocsCard title="Running out">
            If you use up the week's allowance, the agent tells you clearly and when usage frees up. You can wait for it to
            free up as the window rolls, switch to a lighter model or lower reasoning effort, or upgrade your plan. The check
            happens before each run starts, so a run already underway always finishes—which can take you slightly past the
            allowance.
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
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>$3 of AI usage per week</span></li>
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>1 active project</span></li>
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>Community support</span></li>
            </ul>
          </DocsCard>
          <DocsCard title="Pro — $25 / month">
            <ul class="space-y-2 mt-1">
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>$10 of AI usage per week</span></li>
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>Unlimited projects</span></li>
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>Priority support</span></li>
            </ul>
          </DocsCard>
          <DocsCard title="Max (5×) — $100 / month">
            <ul class="space-y-2 mt-1">
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>$50 of AI usage per week — 5× Pro</span></li>
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>Everything in Pro</span></li>
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>Early access to new features</span></li>
            </ul>
          </DocsCard>
          <DocsCard title="Max (10×) — $200 / month">
            <ul class="space-y-2 mt-1">
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>$100 of AI usage per week — 10× Pro</span></li>
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
          effort. Reach for Fable 5.1 at high effort when a task genuinely needs it, and drop to Sonnet 5.5 or Haiku 5.5 at a lower
          effort for routine edits, copy tweaks, and questions—it costs a fraction as much and is usually faster too.
        </p>
        <div class="callout">
          <h4 class="callout__title">
            Keeping an eye on it
          </h4>
          <p class="callout__body">
            Open the Usage panel from the Build workspace's chat toolbar to see how much of your weekly allowance you've
            used. It refreshes shortly after each AI run.
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
            Switch between paid plans from the Pricing page: your existing subscription is changed, never duplicated, and the
            difference is prorated—charged right away when you move up, credited to future invoices when you move down. The
            new allowance applies as soon as the change goes through. To update your card or cancel, choose "Manage billing"
            on the Pricing page to open Stripe's billing portal; a cancelled plan stays active until the end of the current
            billing period, then moves to Free.
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
