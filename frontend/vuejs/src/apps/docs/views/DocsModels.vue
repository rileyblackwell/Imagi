<template>
  <DocsLayout>
    <div class="max-w-5xl mx-auto">
      <DocsPageHeader
        badge-text="MODELS"
        title="Models & Reasoning"
        description="Choose how much horsepower each build task gets. Imagi lets you pick the AI model and how hard it thinks—balancing speed against depth."
      />

      <!-- Overview -->
      <section class="mb-16">
        <div class="lede space-y-4 text-lg">
          <p>
            Every message you send in the Build workspace is handled by an AI model. Imagi gives you two simple settings in
            the chat toolbar—a <strong class="ink-strong">model</strong> and a
            <strong class="ink-strong">reasoning effort</strong>—picked from one panel that lists every option in
            <em class="font-display italic">Faster → Smarter</em> order rather than hiding it in a technical menu.
          </p>
          <p>
            Both settings are per conversation, so different threads can use different settings, and your choice sticks with
            that conversation. The general rule: smarter models and more reasoning give better results on hard tasks, but
            they use your plan's usage faster.
          </p>
        </div>
      </section>

      <!-- The models -->
      <section class="mb-16">
        <h2 class="display display--section">
          The Models
        </h2>
        <p class="lede lede--section">
          Imagi's builder runs on the <strong class="ink-strong">GPT 5.6</strong> family—three
          models tuned for different jobs, ordered from fastest to smartest. Each has a large context window, so it can hold
          a lot of your project in mind at once.
        </p>
        <div class="rule-cols">
          <DocsCard title="Luna">
            <p class="mb-3"><span class="text-xs font-semibold uppercase tracking-[0.14em] text-[color:var(--accent)]">Light &amp; fast</span></p>
            The most economical model—quick and light. Great for small edits, quick questions, and simple changes where you
            want an answer fast and want to stretch your usage.
          </DocsCard>
          <DocsCard title="Terra">
            <p class="mb-3"><span class="text-xs font-semibold uppercase tracking-[0.14em] text-[color:var(--accent)]">Balanced · default</span></p>
            The everyday default—a balance of speed and capability that handles most chat and building work well. Start here,
            and switch only when a task needs it.
          </DocsCard>
          <DocsCard title="Sol">
            <p class="mb-3"><span class="text-xs font-semibold uppercase tracking-[0.14em] text-[color:var(--accent)]">Flagship</span></p>
            The most capable model—reach for it on the most demanding building tasks, where you want the best possible result
            and don't mind that it uses more of your usage.
          </DocsCard>
        </div>
        <div class="bg-blue-50/70 dark:bg-blue-400/[0.08] border border-[color:var(--rule)] rounded-xl p-6 mt-6 transition-colors duration-300">
          <h4 class="callout__title">
            How the model picker works
          </h4>
          <p class="callout__body">
            Open the model chip in the chat toolbar (it shows the current model and reasoning, like "Terra · Medium") to
            reveal a list of models ordered from <strong class="ink-strong">Faster</strong> (Luna) to
            <strong class="ink-strong">Smarter</strong>, each with its relative usage cost beside it and Terra tagged as
            the default. Smarter models consume your usage faster.
          </p>
        </div>
      </section>

      <!-- Reasoning effort -->
      <section class="mb-16">
        <h2 class="display display--section">
          Reasoning Effort
        </h2>
        <p class="lede lede--section">
          Separate from which model you pick, reasoning effort controls how hard the model thinks before it answers. It sits
          under the model list in the same panel as a <em class="font-display italic">Low → Extra High</em> selector, four
          levels ordered <em class="font-display italic">Faster → Smarter</em>. More reasoning
          helps on complex, multi-step tasks; less is snappier for simple ones. The default is
          <strong class="ink-strong">Medium</strong>.
        </p>
        <ul class="space-y-3 mb-8">
          <li class="flex items-start gap-3">
            <div class="checklist__tick mt-2.5" aria-hidden="true"></div>
            <span class="text-lg leading-relaxed"><strong class="ink-strong">Low</strong> — quick answers for small edits</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="checklist__tick mt-2.5" aria-hidden="true"></div>
            <span class="text-lg leading-relaxed"><strong class="ink-strong">Medium</strong> — the balanced default for everyday building</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="checklist__tick mt-2.5" aria-hidden="true"></div>
            <span class="text-lg leading-relaxed"><strong class="ink-strong">High</strong> — deeper thinking for multi-step work</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="checklist__tick mt-2.5" aria-hidden="true"></div>
            <span class="text-lg leading-relaxed"><strong class="ink-strong">Extra High</strong> — the most thorough, for the hardest tasks</span>
          </li>
        </ul>
        <p class="lede text-lg">
          As with models, more reasoning consumes your usage faster—so match the effort to the task rather than always
          maxing it out.
        </p>
      </section>

      <!-- Choosing -->
      <section class="mb-16">
        <h2 class="display display--section">
          Choosing the Right Setting
        </h2>
        <div class="rule-cols rule-cols--2">
          <DocsCard title="Quick edits & small tweaks">
            Lean toward Luna or Terra with Low reasoning. You'll get fast results and stretch your usage further.
          </DocsCard>
          <DocsCard title="Everyday building">
            Stick with the defaults—Terra at Medium reasoning. It handles most pages, features, and changes comfortably.
          </DocsCard>
          <DocsCard title="Complex features">
            Move up to Sol and High or Extra High reasoning when a task is large or intricate and getting it right matters most.
          </DocsCard>
          <DocsCard title="Watch your usage">
            Smarter models and more reasoning use your plan's usage faster. The Usage panel in the workspace shows where you
            stand—see Plans &amp; Usage for details.
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
            to="/docs/plans"
            title="Plans & Usage"
            description="See how usage limits work and what each plan includes."
          />
          <DocsNavigationCard
            to="/docs/building"
            title="Building with AI"
            description="Put your model and reasoning choices to work in the Build workspace."
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
