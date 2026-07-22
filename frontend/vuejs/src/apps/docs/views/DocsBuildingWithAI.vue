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
        <h2 class="font-display text-3xl sm:text-4xl font-semibold text-blue-950 dark:text-white mb-6 tracking-[-0.015em] transition-colors duration-300">
          The Build Workspace
        </h2>
        <div class="space-y-4 text-blue-950/70 dark:text-blue-100/70 text-lg leading-relaxed mb-8 transition-colors duration-300">
          <p>
            <strong class="font-semibold text-blue-950 dark:text-white">Build</strong> is where you turn an idea into a
            working web application. Instead of writing code, you describe what you want in plain language and Imagi's
            AI agents generate the pages, styling, and logic for you—then refine them as you give feedback.
          </p>
          <p>
            The workspace has two halves. On the left is your <strong class="font-semibold text-blue-950 dark:text-white">conversation</strong>
            with the agent (and the Agent Manager, for running several agents at once). On the right is a
            <strong class="font-semibold text-blue-950 dark:text-white">live, interactive preview</strong> of your actual
            running app that updates as the agent works.
          </p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
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
        <h2 class="font-display text-3xl sm:text-4xl font-semibold text-blue-950 dark:text-white mb-6 tracking-[-0.015em] transition-colors duration-300">
          Getting Started
        </h2>

        <DocsStepCard :number="1" title="Create a Project">
          <p class="text-lg leading-relaxed mb-6">
            From your Projects page, give your project a <strong class="font-semibold text-blue-950 dark:text-white">Business Name</strong>
            and a <strong class="font-semibold text-blue-950 dark:text-white">Business Description</strong>. The description matters:
            Imagi's AI uses it to build the very first version of your app, so describe what your business does, who its
            customers are, and how you'll sell.
          </p>
          <div class="bg-blue-50/70 dark:bg-blue-400/[0.08] border border-blue-200/70 dark:border-blue-300/[0.14] rounded-xl p-6 transition-colors duration-300">
            <h4 class="text-xs font-semibold uppercase tracking-[0.18em] text-blue-700 dark:text-blue-300 mt-0 mb-3 transition-colors duration-300">
              Behind the scenes
            </h4>
            <p class="text-lg text-blue-950/70 dark:text-blue-100/70 mb-0 leading-relaxed">
              As soon as you create a project, Imagi runs an AI build in the background to generate a tailored first
              version from your description. Your project hub shows a "Building your app" state, and the Build workspace
              opens automatically the moment that first build is ready.
            </p>
          </div>
          <div class="w-full h-px bg-blue-950/[0.08] dark:bg-white/[0.14] my-6" aria-hidden="true"></div>
          <router-link
            to="/imagi/projects"
            class="group inline-flex items-center justify-center gap-3 px-8 py-4 rounded-full font-medium text-lg bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0 shadow-[0_1px_2px_rgba(23,37,84,0.25),0_8px_20px_-6px_rgba(23,37,84,0.35),inset_0_1px_0_rgba(255,255,255,0.12)] hover:shadow-[0_2px_3px_rgba(23,37,84,0.22),0_14px_28px_-8px_rgba(23,37,84,0.4),inset_0_1px_0_rgba(255,255,255,0.12)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.5),0_10px_24px_-8px_rgba(0,0,0,0.55)] dark:hover:shadow-[0_2px_3px_rgba(0,0,0,0.5),0_14px_30px_-8px_rgba(0,0,0,0.6)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
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
              <div class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2.5 flex-shrink-0" aria-hidden="true"></div>
              <span class="text-lg leading-relaxed">"Add a contact page with a form"</span>
            </li>
            <li class="flex items-start gap-3">
              <div class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2.5 flex-shrink-0" aria-hidden="true"></div>
              <span class="text-lg leading-relaxed">"Change the homepage headline and colors"</span>
            </li>
            <li class="flex items-start gap-3">
              <div class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2.5 flex-shrink-0" aria-hidden="true"></div>
              <span class="text-lg leading-relaxed">"Add an About page that tells my story"</span>
            </li>
            <li class="flex items-start gap-3">
              <div class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2.5 flex-shrink-0" aria-hidden="true"></div>
              <span class="text-lg leading-relaxed">"Make the site look great on phones"</span>
            </li>
          </ul>
          <p class="text-lg leading-relaxed">
            Before you send, you can choose which AI <strong class="font-semibold text-blue-950 dark:text-white">model</strong>
            and how much <strong class="font-semibold text-blue-950 dark:text-white">reasoning effort</strong> to use for the
            task. See <router-link to="/docs/models" class="text-blue-700 dark:text-blue-300 font-medium hover:underline">Models &amp; Reasoning</router-link>
            for how to pick.
          </p>
        </DocsStepCard>

        <DocsStepCard :number="3" title="Watch the Agent Work">
          <p class="text-lg leading-relaxed mb-6">
            The agent doesn't just reply—it builds. As it works you'll see a live status line
            (<em class="font-display italic">"Planning…," "Reading project files…," "Editing project files…"</em>)
            and an <strong class="font-semibold text-blue-950 dark:text-white">activity feed</strong> that checks off each
            step it takes in plain language. For bigger requests it posts a <strong class="font-semibold text-blue-950 dark:text-white">plan
            checklist</strong> and ticks items off as it goes. When it finishes, a small chip shows how many files were updated.
          </p>
          <p class="text-lg leading-relaxed">
            You stay in control the whole time: you can <strong class="font-semibold text-blue-950 dark:text-white">stop</strong>
            a run at any point and keep what was already done, or queue a follow-up message that sends automatically when the
            current run finishes.
          </p>
        </DocsStepCard>

        <DocsStepCard :number="4" title="Preview It Live">
          <p class="text-lg leading-relaxed">
            Your app runs live in the preview pane on the right—a real, interactive browser you can click, type, and scroll
            through, not a static mockup. It updates as the agent makes changes, and a built-in page selector lets you jump
            to any page in your app. If something in your app ever throws an error, a
            <strong class="font-semibold text-blue-950 dark:text-white">"Fix it"</strong> button hands the details straight
            to the agent to investigate.
          </p>
        </DocsStepCard>
      </section>

      <!-- How the agent works -->
      <section class="mb-16">
        <h2 class="font-display text-3xl sm:text-4xl font-semibold text-blue-950 dark:text-white mb-6 tracking-[-0.015em] transition-colors duration-300">
          How the AI Agent Works
        </h2>
        <p class="text-blue-950/70 dark:text-blue-100/70 text-lg leading-relaxed mb-8 transition-colors duration-300">
          Behind a simple chat box, the agent works like a capable teammate—reading your project to understand it, making
          a plan, editing files, and checking the result. You see all of it in plain language, without needing to read code.
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
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
        <h2 class="font-display text-3xl sm:text-4xl font-semibold text-blue-950 dark:text-white mb-6 tracking-[-0.015em] transition-colors duration-300">
          The Agent Manager
        </h2>
        <p class="text-blue-950/70 dark:text-blue-100/70 text-lg leading-relaxed mb-8 transition-colors duration-300">
          For bigger builds, the <strong class="font-semibold text-blue-950 dark:text-white">Agent Manager</strong> turns the
          workspace into a small team of agents you direct. You steer the build from one main thread while dispatching
          side-jobs that run in parallel—each in its own isolated copy of your app, so nothing collides.
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
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
            Finished tasks wait for your decision. Review what each one changed, then <strong class="font-semibold text-blue-950 dark:text-white">Accept</strong>
            to merge it into your app or <strong class="font-semibold text-blue-950 dark:text-white">Dismiss</strong> to
            discard it—nothing touches your app until you say so.
          </DocsCard>
        </div>
      </section>

      <!-- Checkpoints -->
      <section class="mb-16">
        <h2 class="font-display text-3xl sm:text-4xl font-semibold text-blue-950 dark:text-white mb-6 tracking-[-0.015em] transition-colors duration-300">
          Never Lose Your Work
        </h2>
        <p class="text-blue-950/70 dark:text-blue-100/70 text-lg leading-relaxed mb-8 transition-colors duration-300">
          Every message you send is a checkpoint. Imagi saves your app's state before the agent starts working, so you never
          have to think about saving—and you can always go back.
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
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
        <h2 class="font-display text-3xl sm:text-4xl font-semibold text-blue-950 dark:text-white mb-6 tracking-[-0.015em] transition-colors duration-300">
          Next Steps
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
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
