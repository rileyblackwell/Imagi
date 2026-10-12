<template>
  <DocsLayout>
    <div class="max-w-5xl mx-auto">
      <DocsPageHeader
        badge-text="PRICING"
        title="Plans & Usage"
        description="Imagi is free. Here's what the one open plan includes and how AI usage works."
      />

      <!-- The plan -->
      <section class="mb-16">
        <h2 class="display display--section">
          One Free Plan
        </h2>
        <p class="lede lede--section">
          There is one plan right now, Free, and it's open to everyone. There are no paid plans and nothing to pay.
        </p>
        <div class="rule-cols rule-cols--2">
          <DocsCard title="Free — $0">
            <ul class="space-y-2 mt-1">
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>No weekly limit on AI usage</span></li>
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>The full AI builder, with every model</span></li>
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>Unlimited projects</span></li>
              <li class="flex items-start gap-2.5"><span class="checklist__tick mt-2" aria-hidden="true"></span><span>Sell, Market and Operate (beta)</span></li>
            </ul>
          </DocsCard>
          <DocsCard title="A ceiling on every run">
            No single run spends more than $10 of AI work without checking in. A run that reaches it stops with its
            progress saved and tells you so—send a message to keep going. Agents keep working on Imagi's servers after you
            close the workspace, and the ceiling applies there too.
          </DocsCard>
        </div>
      </section>

      <!-- How usage works -->
      <section class="mb-16">
        <h2 class="display display--section">
          How Usage Works
        </h2>
        <div class="space-y-4 text-[color:var(--ink-55)] text-lg leading-relaxed mb-8 transition-colors duration-300">
          <p>
            Every run is metered in dollars of AI work, at the AI providers' own list prices with no markup. What a run
            costs depends on the model you pick and how hard you ask it to think. A quick edit on the light model costs a
            fraction of a cent; a long build on the flagship model at high reasoning effort costs far more
            (see <router-link to="/docs/models" class="text-[color:var(--accent)] font-medium hover:underline">Models &amp; Reasoning</router-link>).
          </p>
          <p>
            Follow-up messages in a conversation cost less than the first, because the parts of your project the model has
            already read are billed at the providers' lower cached rate. Besides chatting with the agent, creating a project
            (its automatic first build) and voice dictation are metered too.
          </p>
        </div>
        <div class="callout">
          <h4 class="callout__title">
            The Usage panel
          </h4>
          <p class="callout__body">
            In the Build workspace, the Usage button in the chat toolbar shows your plan. On Free it reads "Unlimited",
            since there's no weekly limit to count down.
          </p>
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
            description="Learn how model and reasoning choices affect what each run costs."
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
