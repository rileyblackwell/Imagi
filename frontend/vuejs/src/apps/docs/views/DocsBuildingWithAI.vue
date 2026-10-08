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
            with the coordinator; the <strong class="ink-strong">Threads</strong> switch in its header swaps it for the
            Threads pane, which lists the work the coordinator has handed out. On the right is a
            <strong class="ink-strong">live, interactive preview</strong> of your actual running app that updates as the
            agents work. On a phone you see one half at a time: tap <strong class="ink-strong">Preview</strong> in the
            chat header to see your app, and <strong class="ink-strong">Coordinator</strong> in the preview's dock to
            come back.
          </p>
        </div>
        <div class="rule-cols">
          <DocsCard title="AI agents">
            Chat with agents that read and edit your project's files directly—not just suggestions, but real changes built into your app.
          </DocsCard>
          <DocsCard title="Works without you">
            Agents run on Imagi's servers, not in your browser. Close the tab and the work carries on; open the
            workspace again and you pick up right where it is.
          </DocsCard>
          <DocsCard title="Instant preview">
            See your product as a running app you can click through—no build step, no server setup, no waiting.
          </DocsCard>
        </div>
        <div class="callout mt-8">
          <h4 class="callout__title">
            Sign-in comes built in
          </h4>
          <p class="callout__body">
            Every new project ships with sign-in and register pages that Imagi maintains and tests, so your customers'
            accounts are secure from day one. They start as a simple centered card with your business name, and once
            the home page is built they're restyled in the background to match it. The agents can change how these
            pages look and what they say, but not the sign-in code itself—so asking for a different look or wording
            works, while the security underneath stays as Imagi built it.
          </p>
        </div>
      </section>

      <!-- Getting started steps -->
      <section class="mb-16">
        <h2 class="display display--section">
          Getting Started
        </h2>

        <DocsStepCard :number="1" title="Create a Project">
          <p class="text-lg leading-relaxed mb-6">
            From your Projects page, brief the agent in four steps: <strong class="ink-strong">Name it</strong>,
            <strong class="ink-strong">Describe the business</strong>, and, optionally,
            <strong class="ink-strong">How should the app work?</strong> and <strong class="ink-strong">Set the
            look</strong>. The description matters most: Imagi's AI uses it to build the very first version of your app,
            so in a few sentences say what you offer, who it's for, and how people find you and pay (it needs at least
            20 characters). Under How should the app work?, say in everyday words what people can do on it, what it
            needs to keep track of, and anything that matters to you; starters like "People can…" and "It keeps track
            of…" help you begin, and Imagi turns your answer into the plan for your app. Under Set the look, describe the
            feel, colours, or fonts you want, or tap a mood such as Friendly or Calm; skip it and Imagi picks a look that
            fits. Then choose <strong class="ink-strong">Create project</strong>.
          </p>
          <div class="callout">
            <h4 class="callout__title">
              Behind the scenes
            </h4>
            <p class="callout__body">
              As soon as you create a project, Imagi runs an AI build in the background to generate a tailored first
              version from your brief, including how you said the app should work. Its Home, About, and Contact pages are built at the same time, so it takes
              about half a minute. While it runs, the Build card on your project hub reads "Imagi is writing your first
              version"; it unlocks the moment the build finishes—click it to open the workspace.
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
            box so you can read them over before sending. Right-click the button to pick which microphone to use. Once
            there's text in the box, the same button sends it.
          </p>
          <p class="text-lg leading-relaxed">
            Before you send, you can choose which AI <strong class="ink-strong">model</strong>
            and how much <strong class="ink-strong">reasoning effort</strong> to use from the chip in the message box.
            See <router-link to="/docs/models" class="text-[color:var(--accent)] font-medium hover:underline">Models &amp; Reasoning</router-link>
            for how to pick.
          </p>
        </DocsStepCard>

        <DocsStepCard :number="3" title="Watch the Agents Work">
          <p class="text-lg leading-relaxed mb-6">
            The coordinator answers questions itself, and hands every change you ask for to a
            <strong class="ink-strong">thread</strong>. A card appears in your chat naming the job, with its state on
            top—"Thread starting", "Thread working", "Needs an answer from you", "Thread complete", or "Stopped before
            finishing"—and a <strong class="ink-strong">Go to thread</strong> button to follow along. You don't have to
            wait: while threads work in the background, go ahead and send your next message.
          </p>
          <p class="text-lg leading-relaxed mb-6">
            Inside a thread you'll see a live status line (<em class="font-display italic">"Planning…," "Reading project
            files…," "Editing project files…"</em>) and an <strong class="ink-strong">activity feed</strong> that checks
            off each step it takes in plain language. For bigger requests it posts a <strong class="ink-strong">plan
            checklist</strong> and ticks items off as it goes. When it finishes, a small chip shows how many files were
            updated.
          </p>
          <p class="text-lg leading-relaxed">
            You stay in control the whole time. While the coordinator is working, the send button becomes
            <strong class="ink-strong">Stop</strong>: stop a run at any point and keep what was already done. Or press
            Enter to queue a follow-up that sends automatically when the current run finishes—you can queue one message
            at a time, and sending another replaces it. Messages you type into a busy thread wait for it instead, and the
            thread reads them all when its current step finishes.
          </p>
        </DocsStepCard>

        <DocsStepCard :number="4" title="Preview It Live">
          <p class="text-lg leading-relaxed">
            Your app runs live in the preview pane on the right—a real, interactive browser you can click, type, and scroll
            through, not a static mockup. It updates as the agents make changes. A small dock floats above it with back,
            forward, refresh, and home buttons, plus the name of the page you're on: click it to see every page in your
            app and jump to one. If something in your app ever throws an error, a "Something broke in your app" banner
            appears with a <strong class="ink-strong">Fix it</strong> button that hands the details straight to the
            coordinator. If the preview sits idle for a while it dozes off—choose "Wake it up" to bring it back.
          </p>
        </DocsStepCard>
      </section>

      <!-- How the agent works -->
      <section class="mb-16">
        <h2 class="display display--section">
          How the AI Agents Work
        </h2>
        <p class="lede lede--section">
          Behind a simple chat box, each agent works like a capable teammate—reading your project to understand it, making
          a plan, editing files, and checking the result. You see all of it in plain language, without needing to read code.
        </p>
        <div class="rule-cols rule-cols--2">
          <DocsCard title="Activity feed">
            A running checklist of what a thread actually did—read a file, created a page, searched the project or the
            web—each step marked in progress or complete, then folded to a one-line summary when the run ends.
          </DocsCard>
          <DocsCard title="Plan checklist">
            For larger tasks, the agent lays out a to-do list up front and ticks each item off as it works, so you can follow
            the plan as it happens.
          </DocsCard>
          <DocsCard title="Files updated">
            After each run, a chip such as "3 files updated" shows exactly what changed—hover to see the list of files.
          </DocsCard>
          <DocsCard title="Graceful limits">
            Threads keep going on big jobs by themselves. If one still isn't done after several long rounds, it saves its
            work and asks you on its card—say "keep going" and it picks up where it left off. The coordinator stops
            cleanly after a long run and suggests sending "Continue". Any single run that spends $10 stops and checks in
            with you first, with its progress saved.
          </DocsCard>
        </div>
      </section>

      <!-- Coordinator and threads -->
      <section class="mb-16">
        <h2 class="display display--section">
          The Coordinator and Threads
        </h2>
        <p class="lede lede--section">
          You direct the whole build from one conversation. The <strong class="ink-strong">coordinator</strong> works out
          what you're asking for and puts <strong class="ink-strong">threads</strong> to work on the building—each in its
          own isolated copy of your app, so several can run at once without colliding.
        </p>
        <div class="rule-cols rule-cols--2">
          <DocsCard title="The coordinator">
            Your primary conversation—tell it what you want, one thing after another. It answers simple questions itself
            and hands each separate request to its own thread; ask for several things and they're built in parallel (up
            to five at a time—the rest wait their turn as "Thread starting").
          </DocsCard>
          <DocsCard title="Threads">
            The <strong class="ink-strong">Threads</strong> switch in the chat header opens a pane that lists every
            thread under Waiting on you, Working, and Finished. Open any thread to read it, and type into it to steer it
            directly—a change, an answer, or "keep going". Each card's dot tells you its state at a glance: blue while
            it's working, amber when it needs you, green when it's done, red if it stopped.
          </DocsCard>
          <DocsCard title="Questions">
            When a thread or the coordinator needs a decision, it asks right in your chat, often with a few one-tap
            answers—tap one, or type your own. You can also answer inside the thread. A thread waiting on you pops up a
            notice and shows a count in the browser tab's title, so you notice even from another tab.
          </DocsCard>
          <DocsCard title="Applied automatically">
            When a thread finishes, its work goes into your app on its own—you don't need to approve it. Each update
            appears above the message box: "Got it" to clear it, or "See the work" to open its thread. If a thread
            stops before finishing, choose <strong class="ink-strong">Try again</strong> on its card or inside it.
          </DocsCard>
          <DocsCard title="Alternatives to compare">
            Ask for alternatives—"show me two versions of the homepage"—and up to three threads build independent takes on
            the same request. Those wait for you: pick "Use this one" on the version you want, and "Discard" the rest.
          </DocsCard>
          <DocsCard title="Workspace settings">
            The gear in the chat header (and in the Threads pane) opens workspace settings. Under Models, pick the model
            the coordinator uses and the one new threads start on, and switch every existing thread to it in one click.
          </DocsCard>
        </div>
      </section>

      <!-- Checkpoints -->
      <section class="mb-16">
        <h2 class="display display--section">
          Never Lose Your Work
        </h2>
        <p class="lede lede--section">
          Imagi saves your app's state before the coordinator starts working on a message, so you never have to think
          about saving—and you can always go back.
        </p>
        <div class="rule-cols rule-cols--2">
          <DocsCard title="Checkpoints in the chat">
            Your restore points live right in your conversation with the coordinator: messages you sent mark the moment
            before the agents acted on them, so the chat itself is your app's history.
          </DocsCard>
          <DocsCard title="Restore a checkpoint">
            Hover an earlier message and choose "Restore checkpoint" to roll both your app and the conversation back to the
            moment before that message. After you confirm, the messages that came after it are removed and your original
            message is put back in the message box, ready to edit and resend—handy for trying a different direction.
            Restoring isn't available while the coordinator is working.
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
            description="Once your app is built, sell, market, and operate your business from the same project."
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
