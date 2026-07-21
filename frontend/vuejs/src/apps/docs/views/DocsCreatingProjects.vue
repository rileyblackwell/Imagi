<template>
  <DocsLayout>
    <div class="max-w-5xl mx-auto">
      <DocsPageHeader
        badge-text="PROJECTS"
        title="Creating Projects"
        description="Learn how to create and configure new projects in Imagi."
      />

      <DocsCard title="Project Creation Process">
        <p class="text-lg leading-relaxed">
          Creating a new project in Imagi is simple, intuitive, and designed to get you from idea to working application quickly.
          Here's a detailed guide on how to create and configure your projects.
        </p>
      </DocsCard>

      <DocsStepCard :number="1" title="Starting a New Project">
        <p class="text-lg leading-relaxed mb-6">
          To create a new project, navigate to the Imagi dashboard and follow these steps:
        </p>

        <ol class="space-y-4 mb-6">
          <li class="flex items-start gap-4">
            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-[#dbeeff] to-[#9ecdf3] dark:from-blue-400/[0.18] dark:to-blue-500/[0.22] ring-1 ring-blue-900/[0.08] dark:ring-blue-300/[0.18] text-blue-700 dark:text-blue-200 font-semibold text-sm flex items-center justify-center flex-shrink-0 transition-all duration-300">1</div>
            <div class="text-lg leading-relaxed">
              <strong class="text-blue-950 dark:text-white font-semibold">Click the "New Project" button</strong> on your dashboard homepage or from the projects list.
            </div>
          </li>
          <li class="flex items-start gap-4">
            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-[#dbeeff] to-[#9ecdf3] dark:from-blue-400/[0.18] dark:to-blue-500/[0.22] ring-1 ring-blue-900/[0.08] dark:ring-blue-300/[0.18] text-blue-700 dark:text-blue-200 font-semibold text-sm flex items-center justify-center flex-shrink-0 transition-all duration-300">2</div>
            <div class="text-lg leading-relaxed">
              <strong class="text-blue-950 dark:text-white font-semibold">Enter a project name</strong> — choose something descriptive that reflects the purpose of your application.
            </div>
          </li>
          <li class="flex items-start gap-4">
            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-[#dbeeff] to-[#9ecdf3] dark:from-blue-400/[0.18] dark:to-blue-500/[0.22] ring-1 ring-blue-900/[0.08] dark:ring-blue-300/[0.18] text-blue-700 dark:text-blue-200 font-semibold text-sm flex items-center justify-center flex-shrink-0 transition-all duration-300">3</div>
            <div class="text-lg leading-relaxed">
              <strong class="text-blue-950 dark:text-white font-semibold">Select a project template</strong> (optional) — start from scratch or choose from pre-configured templates.
            </div>
          </li>
        </ol>

        <div class="bg-blue-50/70 dark:bg-blue-400/[0.08] border border-blue-200/70 dark:border-blue-300/[0.14] rounded-xl p-6 transition-colors duration-300">
          <h4 class="text-xs font-semibold uppercase tracking-[0.18em] text-blue-700 dark:text-blue-300 mt-0 mb-3 transition-colors duration-300">Pro Tip</h4>
          <p class="text-lg text-blue-950/70 dark:text-blue-100/70 mb-0 leading-relaxed">
            Starting with a template can save time, but creating from scratch gives you more control over the architecture.
            Choose based on your specific needs and timeline.
          </p>
        </div>
      </DocsStepCard>
    </div>
  </DocsLayout>
</template>

<script setup>
import DocsLayout from '../layouts/DocsLayout.vue';
import { DocsCard, DocsPageHeader, DocsStepCard } from '../components';
</script>
