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
            with your main agent (and the Subagents pane, which shows the agents it has put to work). On the right is a
            <strong class="ink-strong">live, interactive preview</strong> of your actual
            running app that updates as the agents work. On a phone, the two share the screen—use the Preview switch in the
            chat header to flip to your app.
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
            See your product as a running app you can click through—no build step, no server setup, no waiting.
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
            From your Projects page, give your project a <strong class="ink-strong">Business name</strong>
            and fill in <strong class="ink-strong">What the business does</strong>. The description matters:
            Imagi's AI uses it to build the very first version of your app, so describe what your business does, who its
            customers are, and how you'll sell. An optional <strong class="ink-strong">Design direction</strong> field lets
            you describe the look you want.
          </p>
          <div class="callout">
            <h4 class="callout__title">
              Behind the scenes
            </h4>
            <p class="callout__body">
              As soon as you create a project, Imagi runs an AI build in the background to generate a tailored first
              version from your description—several agents build its pages at the same time, so it takes about half a
              minute. Your project hub shows the build's progress, and the Build card unlocks as soon as it's ready: click
              it to open the workspace.
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
          <p class="text-lg leading-relaxed mb-6">
            Press <strong class="ink-strong">Enter</strong> to send and
            <strong class="ink-strong">Shift+Enter</strong> for a new line. Rather talk? Hold the microphone button (or hold
            <strong class="ink-strong">⌘D</strong>, Ctrl+D on Windows) and speak—your words are transcribed into the message
            box so you can read them over before sending. Right-click the button to pick which microphone to use.
          </p>
          <p class="text-lg leading-relaxed">
            Before you send, you can choose which AI <strong class="ink-strong">model</strong>
            and how much <strong class="ink-strong">reasoning effort</strong> to use for the
            task. See <router-link to="/docs/models" class="text-[color:var(--accent)] font-medium hover:underline">Models &amp; Reasoning</router-link>
            for how to pick.
          </p>
        </DocsStepCard>

        <DocsStepCard :number="3" title="Watch the Agent Work">
          <p class="text-lg leading-relaxed mb-6">
            Your main agent answers questions itself, and hands every change you ask for to a
            <strong class="ink-strong">subagent</strong>—a card appears in your chat naming the job, and you can open it to
            follow along. The subagent doesn't just reply—it builds. As it works you'll see a live status line
            (<em class="font-display italic">"Planning…," "Reading project files…," "Editing project files…"</em>)
            and an <strong class="ink-strong">activity feed</strong> that checks off each
            step it takes in plain language. For bigger requests it posts a <strong class="ink-strong">plan
            checklist</strong> and ticks items off as it goes. When it finishes, a small chip shows how many files were updated.
          </p>
          <p class="text-lg leading-relaxed">
            You stay in control the whole time: you can <strong class="ink-strong">stop</strong>
            a run at any point and keep what was already done, or queue a follow-up message that sends automatically when the
            current run finishes. You can queue one message at a time—sending another replaces it.
          </p>
        </DocsStepCard>

        <DocsStepCard :number="4" title="Preview It Live">
          <p class="text-lg leading-relaxed">
            Your app runs live in the preview pane on the right—a real, interactive browser you can click, type, and scroll
            through, not a static mockup. It updates as the agents make changes. The preview's toolbar has back, forward,
            refresh, and home buttons, plus a page selector that lets you jump to any page in your app. If something in your
            app ever throws an error, a <strong class="ink-strong">"Fix it"</strong> button
            hands the details straight to the agent to investigate.
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
            If a task is too big for one run, the agent stops cleanly and suggests sending "Continue" to pick up where it left
            off. If you've used up your weekly allowance, it tells you when usage frees up and suggests a lighter model, less
            reasoning, or upgrading your plan.
          </DocsCard>
        </div>
      </section>

      <!-- Subagents -->
      <section class="mb-16">
        <h2 class="display display--section">
          Your Main Agent and Subagents
        </h2>
        <p class="lede lede--section">
          You direct the whole build from one conversation. Your <strong class="ink-strong">main agent</strong> works out
          what you're asking for and puts <strong class="ink-strong">subagents</strong> to work on the building—each in its
          own isolated copy of your app, so several can run at once without colliding.
        </p>
        <div class="rule-cols rule-cols--2">
          <DocsCard title="Main thread">
            Your primary conversation—the one place you direct the build from. Ask for changes here and your main agent hands
            each separate request to its own subagent; ask several things at once and they're built in parallel.
          </DocsCard>
          <DocsCard title="Subagents">
            Each job appears as a card in your chat that turns into "Subagent complete" when it's done, with a summary of
            what changed. The <strong class="ink-strong">Subagents</strong> switch in the chat header shows how many are
            working and opens a list of active and past subagents; open any one to read its thread, then "Back to main
            thread".
          </DocsCard>
          <DocsCard title="Applied automatically">
            When a subagent finishes, its work goes into your app on its own—you don't need to approve it. Updates collect
            under "From your subagents" above the message box: "Got it" to clear one, or "See the work" to open its thread.
            If a subagent needs a decision from you, it asks there and waits for your answer.
          </DocsCard>
          <DocsCard title="Alternatives to compare">
            Ask for alternatives—"show me two versions of the homepage"—and up to three subagents build independent takes on
            the same request. Those wait for you: pick "Use this one" on the version you want, and "Discard" the rest.
          </DocsCard>
        </div>
      </section>

      <!-- Checkpoints -->
      <section class="mb-16">
        <h2 class="display display--section">
          Never Lose Your Work
        </h2>
        <p class="lede lede--section">
          Imagi saves your app's state before the agent starts working on a message, so you never have to think about
          saving—and you can always go back.
        </p>
        <div class="rule-cols rule-cols--2">
          <DocsCard title="Checkpoints in the chat">
            Your restore points live right in your main conversation: messages you sent mark the moment before the agent
            acted on them, so the chat itself is your app's history.
          </DocsCard>
          <DocsCard title="Restore a checkpoint">
            Hover an earlier message and choose "Restore checkpoint" to roll both your app and the conversation back to the
            moment before that message. After you confirm, the messages that came after it are removed and your original
            message is put back in the message box, ready to edit and resend—handy for trying a different direction.
            Restoring isn't available while the agent is working.
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
