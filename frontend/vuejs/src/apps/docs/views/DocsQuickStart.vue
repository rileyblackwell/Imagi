<template>
  <DocsLayout>
    <div class="max-w-5xl mx-auto">
      <DocsPageHeader
        badge-text="QUICK START"
        title="Quick Start Guide"
        description="Get up and running with Imagi in minutes with this step-by-step guide."
      />

      <DocsStepCard :number="1" title="Create a Project">
        <p class="text-lg leading-relaxed mb-6">
          Navigate to the Builder Dashboard to get started. Click the "New Project" button to create your first project.
          Give it a name and description that reflects what you want to build.
        </p>
        <div class="w-full h-px bg-blue-950/[0.08] dark:bg-white/[0.14] mb-6" aria-hidden="true"></div>
        <router-link
          to="/imagi/projects"
          class="group inline-flex items-center justify-center gap-3 px-8 py-4 rounded-full font-medium text-lg bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0 shadow-[0_1px_2px_rgba(23,37,84,0.25),0_8px_20px_-6px_rgba(23,37,84,0.35),inset_0_1px_0_rgba(255,255,255,0.12)] hover:shadow-[0_2px_3px_rgba(23,37,84,0.22),0_14px_28px_-8px_rgba(23,37,84,0.4),inset_0_1px_0_rgba(255,255,255,0.12)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.5),0_10px_24px_-8px_rgba(0,0,0,0.55)] dark:hover:shadow-[0_2px_3px_rgba(0,0,0,0.5),0_14px_30px_-8px_rgba(0,0,0,0.6)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
        >
          <span>Create New Project</span>
          <svg
            class="w-5 h-5 ml-1 transition-transform duration-300 group-hover:translate-x-1"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
        </router-link>
      </DocsStepCard>

      <DocsStepCard :number="2" title="Build Your Project">
        <p class="text-lg leading-relaxed mb-6">
          Once your project is created, you'll be taken to the AI agent interface. Here's where the magic happens—simply
          prompt the AI agent with what you want your project to be. The more specific you are, the better results you'll get.
        </p>

        <ul class="space-y-3 mb-6">
          <li class="flex items-start gap-3">
            <div class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2.5 flex-shrink-0" aria-hidden="true"></div>
            <span class="text-lg leading-relaxed">Describe the <strong class="font-semibold text-blue-950 dark:text-white">purpose</strong> and functionality you need</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2.5 flex-shrink-0" aria-hidden="true"></div>
            <span class="text-lg leading-relaxed">Specify key <strong class="font-semibold text-blue-950 dark:text-white">features</strong> and user interactions</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2.5 flex-shrink-0" aria-hidden="true"></div>
            <span class="text-lg leading-relaxed">Mention any <strong class="font-semibold text-blue-950 dark:text-white">data models</strong> or structure requirements</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2.5 flex-shrink-0" aria-hidden="true"></div>
            <span class="text-lg leading-relaxed">Share <strong class="font-semibold text-blue-950 dark:text-white">design preferences</strong> or style inspiration</span>
          </li>
        </ul>

        <div class="bg-blue-50/70 dark:bg-blue-400/[0.08] border border-blue-200/70 dark:border-blue-300/[0.14] rounded-xl p-6 transition-colors duration-300">
          <h4 class="text-xs font-semibold uppercase tracking-[0.18em] text-blue-700 dark:text-blue-300 mt-0 mb-3 transition-colors duration-300">
            Example Prompt
          </h4>
          <p class="font-display italic text-lg text-blue-950/70 dark:text-blue-100/70 mb-0 leading-relaxed">
            "I need a task management application with user authentication. Users should be able to create projects,
            add tasks to projects, and mark tasks as complete. Each task should have a title, description, due date,
            and priority level. The app should have a dashboard showing task statistics and upcoming deadlines.
            The design should be minimal and modern, similar to Asana but with a darker theme."
          </p>
        </div>

        <p class="text-lg leading-relaxed mt-6">
          The AI agent will work with you to build out your application, generating code, creating views, and setting up
          your backend—all through natural conversation.
        </p>
      </DocsStepCard>

      <DocsStepCard :number="3" title="Deploy Your Project">
        <p class="text-lg leading-relaxed mb-6">
          When you're happy with your application, it's time to share it with the world. Imagi makes deployment simple—just
          click the "Deploy" button in your project dashboard.
        </p>

        <ul class="space-y-3 mb-6">
          <li class="flex items-start gap-3">
            <div class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2.5 flex-shrink-0" aria-hidden="true"></div>
            <span class="text-lg leading-relaxed">Review your application to ensure everything works as expected</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2.5 flex-shrink-0" aria-hidden="true"></div>
            <span class="text-lg leading-relaxed">Click the <strong class="font-semibold text-blue-950 dark:text-white">"Deploy"</strong> button in your project dashboard</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2.5 flex-shrink-0" aria-hidden="true"></div>
            <span class="text-lg leading-relaxed">Your app will be built and deployed to a live URL automatically</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="w-1.5 h-1.5 rotate-45 bg-orange-500/80 dark:bg-orange-400/80 mt-2.5 flex-shrink-0" aria-hidden="true"></div>
            <span class="text-lg leading-relaxed">Share your URL with users and start gathering feedback</span>
          </li>
        </ul>

        <p class="text-lg leading-relaxed">
          Your application will be live on the web, ready for users to access. You can continue to iterate and redeploy
          as your project evolves.
        </p>
      </DocsStepCard>

      <section class="mb-16">
        <h2 class="font-display text-3xl sm:text-4xl font-semibold text-blue-950 dark:text-white mb-6 tracking-[-0.015em] transition-colors duration-300">
          Next Steps
        </h2>
        <p class="text-blue-950/70 dark:text-blue-100/70 text-lg leading-relaxed mb-8 transition-colors duration-300">
          Now that you've completed the quick start, continue learning with these guides:
        </p>
        <div class="grid grid-cols-1 gap-6">
          <DocsNavigationCard
            to="/docs/creating-projects"
            title="Creating Projects"
            description="Learn more about project creation options and best practices."
          />
        </div>
      </section>
    </div>
  </DocsLayout>
</template>

<script setup>
import DocsLayout from '../layouts/DocsLayout.vue';
import { DocsPageHeader, DocsStepCard, DocsNavigationCard } from '../components';
</script>
