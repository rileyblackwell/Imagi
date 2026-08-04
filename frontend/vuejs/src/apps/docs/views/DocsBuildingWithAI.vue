<template>
  <DocsLayout>
    <div class="max-w-5xl mx-auto">
      <DocsPageHeader
        badge-text="BUILD"
        title="Building with AI"
        description="Create a project, describe what you want in plain language, and watch Imagi's AI agents build your app in a live workspace."
      />

      <!-- Overview -->
      <section class="mb-16">
        <h2 class="display display--section">
          The Build Workspace
        </h2>
        <div class="space-y-4 text-[color:var(--ink-55)] text-lg leading-relaxed mb-8 transition-colors duration-300">
          <p>
            <strong class="ink-strong">Build</strong> is where you turn an idea into a
            working web application. Instead of writing code, you describe what you want in plain language and Imagi's
            AI agents generate the pages, styling, and logic for you—then refine them as you give feedback.
          </p>
          <p>
            The workspace has two halves. On the left is your <strong class="ink-strong">conversation</strong>
            with the agent (and the Agent Manager, for running several agents at once). On the right is a
            <strong class="ink-strong">live, interactive preview</strong> of your actual
            running app that updates as the agent works.
          </p>
        </div>
        <div class="rule-cols">
          <DocsCard title="AI agents">
            Chat with agents that read and edit your project's files directly—not just suggestions, but real changes built into your app.
          </DocsCard>
          <DocsCard title="Live workspace">
            Generate and refine pages in real time. Every change the agent makes shows up in your project immediately.
          </DocsCard>
          <DocsCard title="Instant preview">
            See your product as a running app you can click through—no build step, no deploy button, no waiting.
          </DocsCard>
        </div>
      </section>

      <!-- Getting started steps -->
      <section class="mb-16">
        <h2 class="display display--section">
          Getting Started
        </h2>

        <DocsStepCard :number="1" title="Create a Project">
          <p class="text-lg leading-relaxed mb-6">
            From your Projects page, give your project a <strong class="ink-strong">Business Name</strong>
            and a <strong class="ink-strong">Business Description</strong>. The description matters:
            Imagi's AI uses it to build the very first version of your app, so describe what your business does, who its
            customers are, and how you'll sell.
          </p>
          <div class="callout">
            <h4 class="callout__title">
              Behind the scenes
            </h4>
            <p class="callout__body">
              As soon as you create a project, Imagi runs an AI build in the background to generate a tailored first
              version from your description. Your project hub shows a "Building your app" state, and the Build workspace
              opens automatically the moment that first build is ready.
            </p>
          </div>
          <div class="section-rule my-6" aria-hidden="true"></div>
          <router-link
            to="/imagi/projects"
            class="btn-primary group"
          >
            <span>Create a Project</span>
            <svg class="w-5 h-5 ml-1 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </router-link>
        </DocsStepCard>

        <DocsStepCard :number="2" title="Describe What You Want">
          <p class="text-lg leading-relaxed mb-6">
            In the workspace, type a request in plain language—describe a page, a feature, or a change. The more specific
            you are, the better the result. You can ask for anything from a whole new section to a single tweak:
          </p>
          <ul class="space-y-3 mb-6">
            <li class="flex items-start gap-3">
              <div class="checklist__tick mt-2.5" aria-hidden="true"></div>
              <span class="text-lg leading-relaxed">"Add a contact page with a form"</span>
            </li>
            <li class="flex items-start gap-3">
              <div class="checklist__tick mt-2.5" aria-hidden="true"></div>
              <span class="text-lg leading-relaxed">"Change the homepage headline and colors"</span>
            </li>
            <li class="flex items-start gap-3">
              <div class="checklist__tick mt-2.5" aria-hidden="true"></div>
              <span class="text-lg leading-relaxed">"Add an About page that tells my story"</span>
            </li>
            <li class="flex items-start gap-3">
              <div class="checklist__tick mt-2.5" aria-hidden="true"></div>
              <span class="text-lg leading-relaxed">"Make the site look great on phones"</span>
            </li>
          </ul>
          <p class="text-lg leading-relaxed">
            Before you send, you can choose which AI <strong class="ink-strong">model</strong>
            and how much <strong class="ink-strong">reasoning effort</strong> to use for the
            task. See <router-link to="/docs/models" class="text-[color:var(--accent)] font-medium hover:underline">Models &amp; Reasoning</router-link>
            for how to pick.
          </p>
        </DocsStepCard>

        <DocsStepCard :number="3" title="Watch the Agent Work">
          <p class="text-lg leading-relaxed mb-6">
            The agent doesn't just reply—it builds. As it works you'll see a live status line
            (<em class="font-display italic">"Planning…," "Reading project files…," "Editing project files…"</em>)
            and an <strong class="ink-strong">activity feed</strong> that checks off each
            step it takes in plain language. For bigger requests it posts a <strong class="ink-strong">plan
            checklist</strong> and ticks items off as it goes. When it finishes, a small chip shows how many files were updated.
          </p>
          <p class="text-lg leading-relaxed">
            You stay in control the whole time: you can <strong class="ink-strong">stop</strong>
            a run at any point and keep what was already done, or queue a follow-up message that sends automatically when the
            current run finishes.
          </p>
        </DocsStepCard>

        <DocsStepCard :number="4" title="Preview It Live">
          <p class="text-lg leading-relaxed">
            Your app runs live in the preview pane on the right—a real, interactive browser you can click, type, and scroll
            through, not a static mockup. It updates as the agent makes changes, and a built-in page selector lets you jump
            to any page in your app. If something in your app ever throws an error, a
            <strong class="ink-strong">"Fix it"</strong> button hands the details straight
            to the agent to investigate.
          </p>
        </DocsStepCard>
      </section>

      <!-- How the agent works -->
      <section class="mb-16">
        <h2 class="display display--section">
          How the AI Agent Works
        </h2>
        <p class="lede lede--section">
          Behind a simple chat box, the agent works like a capable teammate—reading your project to understand it, making
          a plan, editing files, and checking the result. You see all of it in plain language, without needing to read code.
        </p>
        <div class="rule-cols rule-cols--2">
          <DocsCard title="Activity feed">
            A running checklist of what the agent actually did—read a file, created a page, searched the project or the web—each
            step marked in progress or complete, then collapsed to a one-line summary when the run ends.
          </DocsCard>
          <DocsCard title="Plan checklist">
            For larger tasks, the agent lays out a to-do list up front and ticks each item off as it works, so you can follow
            the plan as it happens.
          </DocsCard>
          <DocsCard title="Files updated">
            After each run, a chip such as "3 files updated" shows exactly what changed—hover to see the list of files.
          </DocsCard>
          <DocsCard title="Graceful limits">
            If you reach a usage limit or a task is too big for one run, the agent tells you clearly and suggests the next
            step—like sending "Continue" to pick up where it left off.
          </DocsCard>
        </div>
      </section>

      <!-- Agent Manager -->
      <section class="mb-16">
        <h2 class="display display--section">
          The Agent Manager
        </h2>
        <p class="lede lede--section">
          For bigger builds, the <strong class="ink-strong">Agent Manager</strong> turns the
          workspace into a small team of agents you direct. You steer the build from one main thread while dispatching
          side-jobs that run in parallel—each in its own isolated copy of your app, so nothing collides.
        </p>
        <div class="rule-cols rule-cols--2">
          <DocsCard title="Lead thread">
            Your primary conversation—the one place you direct the build from. Its changes go straight into your project's
            main timeline.
          </DocsCard>
          <DocsCard title="Tasks">
            Dispatch a side-job with the "+" button and it runs in parallel without disturbing your lead thread. Run several
            at once to get more done at the same time.
          </DocsCard>
          <DocsCard title="Parallel drafts">
            When you dispatch a task, choose how many drafts to build—1, 2, or 3. Imagi builds each as an independent attempt
            at the same request, so you can compare and pick the best.
          </DocsCard>
          <DocsCard title="Review &amp; accept">
            Finished tasks wait for your decision. Review what each one changed, then <strong class="ink-strong">Accept</strong>
            to merge it into your app or <strong class="ink-strong">Dismiss</strong> to
            discard it—nothing touches your app until you say so.
          </DocsCard>
        </div>
      </section>

      <!-- Checkpoints -->
      <section class="mb-16">
        <h2 class="display display--section">
          Never Lose Your Work
        </h2>
        <p class="lede lede--section">
          Every message you send is a checkpoint. Imagi saves your app's state before the agent starts working, so you never
          have to think about saving—and you can always go back.
        </p>
        <div class="rule-cols rule-cols--2">
          <DocsCard title="Checkpoints in the chat">
            Your restore points live right in the conversation: each message you sent marks the moment before the agent
            acted on it, so the chat itself is your app's history.
          </DocsCard>
          <DocsCard title="Restore a checkpoint">
            Hover any earlier message and choose "Restore checkpoint" to roll both your app and the conversation back to the
            moment before that message—handy for trying a different direction.
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
            to="/docs/running-your-business"
            title="Running Your Business"
            description="Once your app is built, sell, market, and operate your business from the same workspace."
          />
          <DocsNavigationCard
            to="/docs/models"
            title="Models & Reasoning"
            description="Learn how to pick the right model and reasoning effort for each build task."
          />
        </div>
      </section>
    </div>
  </DocsLayout>
</template>

<script setup>
import DocsLayout from '../layouts/DocsLayout.vue';
import { DocsCard, DocsNavigationCard, DocsPageHeader, DocsStepCard } from '../components';
</script>
