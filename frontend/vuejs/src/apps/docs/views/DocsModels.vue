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
            <strong class="ink-strong">reasoning effort</strong>—picked from one menu that lists every option in
            <em class="font-display italic">Faster → Smarter</em> order, with a line on what each one is for.
          </p>
          <p>
            Both settings are per conversation, so different threads can use different settings. The model you pick is saved
            with the conversation; reasoning effort applies while the workspace is open and goes back to Medium when you
            reload the page. The general rule: smarter models and more reasoning give better results on hard tasks, but
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
          Imagi offers four Claude models, ordered from fastest to smartest. Every one has a large context window, so
          it can hold a lot of your project in mind at once.
        </p>
        <div class="rule-cols rule-cols--2">
          <DocsCard title="Haiku 5.5">
            <p class="mb-3"><span class="text-xs font-semibold uppercase tracking-[0.14em] text-[color:var(--accent)]">Fast</span></p>
            Fast and inexpensive, yet capable at most tasks—not just small edits and quick questions. Turn up the effort
            and it handles harder work too, while stretching your usage further than the other models.
          </DocsCard>
          <DocsCard title="Sonnet 5.5">
            <p class="mb-3"><span class="text-xs font-semibold uppercase tracking-[0.14em] text-[color:var(--accent)]">Quick</span></p>
            Quick and capable, a strong everyday builder at a modest price—a good step up from Haiku when a change
            spans a few pages.
          </DocsCard>
          <DocsCard title="Opus 5.5">
            <p class="mb-3"><span class="text-xs font-semibold uppercase tracking-[0.14em] text-[color:var(--accent)]">Balanced · default</span></p>
            Thoughtful and dependable, with strong judgment on code and design—pages, features, fixes and questions
            alike. It's the default: start here, and switch only when a task calls for it. A new project's first build
            runs on Opus 5.5, with the home page in fast mode, and opens as soon as that page is ready.
          </DocsCard>
          <DocsCard title="Fable 5.1">
            <p class="mb-3"><span class="text-xs font-semibold uppercase tracking-[0.14em] text-[color:var(--accent)]">Frontier</span></p>
            Frontier intelligence for the hardest, most complex work, where you want the best possible result and don't
            mind that it uses much more of your usage.
          </DocsCard>
        </div>
        <div class="bg-ink/[0.03] dark:bg-blue-400/[0.08] border border-[color:var(--rule)] rounded-xl p-6 mt-6 transition-colors duration-300">
          <h4 class="callout__title">
            How the model picker works
          </h4>
          <p class="callout__body">
            Click the model chip in the chat toolbar (it shows the current model and reasoning, like "Opus 5.5 · Medium").
            A menu opens with Haiku 5.5, Sonnet 5.5, Opus 5.5 and Fable 5.1, each with a short description, and a check next to the one in
            use—click another to switch. You can also use the arrow keys, and Escape closes the menu. Smarter models
            consume your usage faster.
          </p>
        </div>
        <div class="bg-ink/[0.03] dark:bg-blue-400/[0.08] border border-[color:var(--rule)] rounded-xl p-6 mt-6 transition-colors duration-300">
          <h4 class="callout__title">
            Fast mode
          </h4>
          <p class="callout__body">
            On Opus 5.5 the same menu has a Fast mode switch under Speed. Turn it on for noticeably quicker replies, at
            twice the price, so it uses your plan's usage twice as fast. The chip adds "· Fast" while it's on, and threads
            the coordinator starts follow its setting. Like the model, it's saved with the conversation. The other models don't offer it, so the switch is greyed out for them.
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
          under the model list in the same menu as a row of five rising bars, from
          <em class="font-display italic">Low → Max</em>—click a bar to set the level, and hover to see what
          each one means before you pick it. More reasoning
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
            <span class="text-lg leading-relaxed"><strong class="ink-strong">Extra High</strong> — thorough work on the hardest tasks</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="checklist__tick mt-2.5" aria-hidden="true"></div>
            <span class="text-lg leading-relaxed"><strong class="ink-strong">Max</strong> — everything the model has, whatever it takes</span>
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
            Switch to Haiku 5.5 at Low or Medium effort. You'll get fast results and stretch your usage further—and
            nudging the effort up lets Haiku take on bigger jobs too.
          </DocsCard>
          <DocsCard title="Everyday building">
            Stick with the defaults—Opus 5.5 at Medium reasoning. It handles most pages, features, and changes comfortably.
          </DocsCard>
          <DocsCard title="Complex features">
            Move up to Fable 5.1 and High, Extra High or Max effort when a task is large or intricate and getting it right matters most.
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
