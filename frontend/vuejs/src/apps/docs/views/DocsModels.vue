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
            Every message you send in the Build workspace is handled by an AI model. Imagi gives you two simple dials in the
            chat toolbar—a <strong class="font-semibold text-[color:var(--ink)]">model</strong> and a
            <strong class="font-semibold text-[color:var(--ink)]">reasoning effort</strong>—each presented as a
            <em class="font-display italic">Faster → Smarter</em> slider rather than a technical menu.
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
        <h2 class="display text-3xl sm:text-4xl mb-6">
          The Models
        </h2>
        <p class="lede text-lg mb-8">
          Imagi's builder runs on the <strong class="font-semibold text-[color:var(--ink)]">GPT 5.6</strong> family—three
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
          <h4 class="text-xs font-semibold uppercase tracking-[0.18em] text-[color:var(--accent)] mt-0 mb-3 transition-colors duration-300">
            How the model dial works
          </h4>
          <p class="text-lg text-[color:var(--ink-55)] mb-0 leading-relaxed">
            Open the model chip in the chat toolbar (it shows the current model, like "Terra") to reveal a single slider from
            <strong class="font-semibold text-[color:var(--ink)]">Faster</strong> (Luna) to
            <strong class="font-semibold text-[color:var(--ink)]">Smarter</strong> (Sol), with Terra in the middle.
            Smarter models consume your usage faster.
          </p>
        </div>
      </section>

      <!-- Reasoning effort -->
      <section class="mb-16">
        <h2 class="display text-3xl sm:text-4xl mb-6">
          Reasoning Effort
        </h2>
        <p class="lede text-lg mb-8">
          Separate from which model you pick, reasoning effort controls how hard the model thinks before it answers. It runs
          along the same <em class="font-display italic">Faster → Smarter</em> slider, across five levels. More reasoning
          helps on complex, multi-step tasks; less is snappier for simple ones. The default is
          <strong class="font-semibold text-[color:var(--ink)]">Medium</strong>.
        </p>
        <ul class="space-y-3 mb-8">
          <li class="flex items-start gap-3">
            <div class="checklist__tick mt-2.5" aria-hidden="true"></div>
            <span class="text-lg leading-relaxed"><strong class="font-semibold text-[color:var(--ink)]">Minimal</strong> — the quickest, for the simplest changes</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="checklist__tick mt-2.5" aria-hidden="true"></div>
            <span class="text-lg leading-relaxed"><strong class="font-semibold text-[color:var(--ink)]">Low</strong> — a little thinking for straightforward tasks</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="checklist__tick mt-2.5" aria-hidden="true"></div>
            <span class="text-lg leading-relaxed"><strong class="font-semibold text-[color:var(--ink)]">Medium</strong> — the balanced default for everyday building</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="checklist__tick mt-2.5" aria-hidden="true"></div>
            <span class="text-lg leading-relaxed"><strong class="font-semibold text-[color:var(--ink)]">High</strong> — deeper thinking for trickier, multi-step work</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="checklist__tick mt-2.5" aria-hidden="true"></div>
            <span class="text-lg leading-relaxed"><strong class="font-semibold text-[color:var(--ink)]">Extra High</strong> — the most thorough, for the hardest tasks</span>
          </li>
        </ul>
        <p class="lede text-lg">
          As with models, more reasoning consumes your usage faster—so match the effort to the task rather than always
          maxing it out.
        </p>
      </section>

      <!-- Choosing -->
      <section class="mb-16">
        <h2 class="display text-3xl sm:text-4xl mb-6">
          Choosing the Right Setting
        </h2>
        <div class="rule-cols rule-cols--2">
          <DocsCard title="Quick edits & small tweaks">
            Lean toward Luna or Terra with Minimal–Low reasoning. You'll get fast results and stretch your usage further.
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
        <h2 class="display text-3xl sm:text-4xl mb-6">
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
