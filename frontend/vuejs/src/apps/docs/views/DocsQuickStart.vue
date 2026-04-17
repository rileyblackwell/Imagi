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
        <div class="w-full h-px bg-gray-200 dark:bg-gray-300 mb-6"></div>
        <router-link
          to="/products/imagi/projects"
          class="btn-3d group relative inline-flex items-center justify-center gap-3 px-8 py-4 bg-gradient-to-b from-gray-800 via-gray-900 to-gray-950 text-white rounded-full font-medium text-lg transition-all duration-300 overflow-hidden border border-gray-700/50"
        >
          <span class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/30 to-transparent"></span>
          <span class="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-black/30 to-transparent"></span>
          <span class="relative">Create New Project</span>
          <svg
            class="relative w-5 h-5 ml-1 transition-transform duration-300 group-hover:translate-x-1"
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
            <div class="w-1.5 h-1.5 rounded-full bg-gray-900 dark:bg-black mt-2 flex-shrink-0"></div>
            <span class="text-lg leading-relaxed">Describe the <strong class="font-semibold text-gray-900 dark:text-black">purpose</strong> and functionality you need</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="w-1.5 h-1.5 rounded-full bg-gray-900 dark:bg-black mt-2 flex-shrink-0"></div>
            <span class="text-lg leading-relaxed">Specify key <strong class="font-semibold text-gray-900 dark:text-black">features</strong> and user interactions</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="w-1.5 h-1.5 rounded-full bg-gray-900 dark:bg-black mt-2 flex-shrink-0"></div>
            <span class="text-lg leading-relaxed">Mention any <strong class="font-semibold text-gray-900 dark:text-black">data models</strong> or structure requirements</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="w-1.5 h-1.5 rounded-full bg-gray-900 dark:bg-black mt-2 flex-shrink-0"></div>
            <span class="text-lg leading-relaxed">Share <strong class="font-semibold text-gray-900 dark:text-black">design preferences</strong> or style inspiration</span>
          </li>
        </ul>

        <div class="bg-gray-50 dark:bg-gray-100 border border-gray-200 dark:border-gray-300 rounded-xl p-6 transition-colors duration-300">
          <h4 class="text-gray-900 dark:text-black mt-0 mb-3 text-lg font-semibold">
            Example Prompt
          </h4>
          <p class="text-lg mb-0 leading-relaxed">
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
            <div class="w-1.5 h-1.5 rounded-full bg-gray-900 dark:bg-black mt-2 flex-shrink-0"></div>
            <span class="text-lg leading-relaxed">Review your application to ensure everything works as expected</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="w-1.5 h-1.5 rounded-full bg-gray-900 dark:bg-black mt-2 flex-shrink-0"></div>
            <span class="text-lg leading-relaxed">Click the <strong class="font-semibold text-gray-900 dark:text-black">"Deploy"</strong> button in your project dashboard</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="w-1.5 h-1.5 rounded-full bg-gray-900 dark:bg-black mt-2 flex-shrink-0"></div>
            <span class="text-lg leading-relaxed">Your app will be built and deployed to a live URL automatically</span>
          </li>
          <li class="flex items-start gap-3">
            <div class="w-1.5 h-1.5 rounded-full bg-gray-900 dark:bg-black mt-2 flex-shrink-0"></div>
            <span class="text-lg leading-relaxed">Share your URL with users and start gathering feedback</span>
          </li>
        </ul>

        <p class="text-lg leading-relaxed">
          Your application will be live on the web, ready for users to access. You can continue to iterate and redeploy
          as your project evolves.
        </p>
      </DocsStepCard>

      <section class="mb-16">
        <h2 class="text-3xl sm:text-4xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight transition-colors duration-300">
          Next Steps
        </h2>
        <p class="text-gray-700 dark:text-white/70 text-lg leading-relaxed mb-8 transition-colors duration-300">
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

<style scoped>
.btn-3d {
  transform: translateZ(0);
  box-shadow:
    0 2px 3px -1px rgba(0, 0, 0, 0.4),
    0 6px 12px -3px rgba(0, 0, 0, 0.35),
    0 16px 32px -8px rgba(0, 0, 0, 0.3),
    0 24px 48px -12px rgba(0, 0, 0, 0.2),
    0 3px 0 -1px rgba(0, 0, 0, 0.5),
    inset 0 2px 4px 0 rgba(255, 255, 255, 0.2),
    inset 0 -4px 8px -2px rgba(0, 0, 0, 0.3);
}
</style>
