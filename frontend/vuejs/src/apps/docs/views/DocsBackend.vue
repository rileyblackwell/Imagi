<template>
  <DocsLayout>
    <div class="max-w-4xl mx-auto">
      <!-- Page header with attractive styling -->
      <div class="mb-10">
        <div class="inline-block px-4 py-1.5 bg-primary-500/10 rounded-full mb-4">
          <span class="text-primary-400 font-semibold text-sm tracking-wider">DOCUMENTATION</span>
        </div>
        <h1 class="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
          Backend Basics
        </h1>
        <p class="text-xl text-gray-300 leading-relaxed">
          Understanding how data and business logic work in your Imagi Oasis application.
        </p>
      </div>

      <!-- Attractive divider -->
      <div class="relative h-16 mb-10">
        <div class="absolute inset-x-0 h-px mx-auto w-2/3 sm:w-1/2 bg-gradient-to-r from-transparent via-primary-500/30 to-transparent animate-pulse-slow"></div>
      </div>

      <!-- Main content -->
      <div class="prose prose-invert prose-lg max-w-none">
        <!-- Introduction -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-8 mb-8">
          <h2 class="text-2xl font-bold text-white mb-4">What is a Backend?</h2>
          <p class="text-gray-300">
            Think of your application as having two main parts:
          </p>
          <ul class="space-y-2 mt-4">
            <li class="flex items-start">
              <div class="flex-shrink-0 w-5 h-5 rounded-full bg-primary-500/20 flex items-center justify-center mr-3 mt-1">
                <i class="fas fa-desktop text-primary-400 text-xs"></i>
              </div>
              <div>
                <span><strong>Frontend</strong>: What users see and interact with (buttons, forms, pages)</span>
              </div>
            </li>
            <li class="flex items-start">
              <div class="flex-shrink-0 w-5 h-5 rounded-full bg-primary-500/20 flex items-center justify-center mr-3 mt-1">
                <i class="fas fa-server text-primary-400 text-xs"></i>
              </div>
              <div>
                <span><strong>Backend</strong>: Where data is stored and processed (like the engine under a car's hood)</span>
              </div>
            </li>
          </ul>
          <p class="text-gray-300 mt-4">
            With Imagi Oasis, you don't need to write code for your backend. Instead, you describe what you want your application to do, and Imagi creates both the frontend and backend for you.
          </p>
        </div>

        <!-- Section 1: Data Models -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-8 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-primary-500 to-violet-500"></div>
          <div class="pl-4">
            <h2 class="text-2xl font-bold text-white mb-4">1. Understanding Data Models</h2>
            <p class="text-gray-300">
              Data models are the blueprints for how information is organized in your application. They define what types of information you'll store and how different pieces of data relate to each other.
            </p>
            <div class="mt-6 bg-dark-800/70 p-6 rounded-lg">
              <h4 class="text-primary-400 font-medium mb-4">Example: Task Management App</h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-dark-700/50 p-4 rounded-lg border border-dark-600/50">
                  <h5 class="text-white font-medium mb-2 flex items-center">
                    <div class="w-6 h-6 rounded-full bg-primary-500/20 flex items-center justify-center mr-2">
                      <i class="fas fa-user text-primary-400 text-xs"></i>
                    </div>
                    User Model
                  </h5>
                  <p class="text-sm text-gray-300 mb-2">Stores information about your users</p>
                  <ul class="text-sm text-gray-400 space-y-1">
                    <li>• Name</li>
                    <li>• Email</li>
                    <li>• Password (securely stored)</li>
                    <li>• Profile picture</li>
                  </ul>
                </div>
                <div class="bg-dark-700/50 p-4 rounded-lg border border-dark-600/50">
                  <h5 class="text-white font-medium mb-2 flex items-center">
                    <div class="w-6 h-6 rounded-full bg-blue-500/20 flex items-center justify-center mr-2">
                      <i class="fas fa-th-list text-blue-400 text-xs"></i>
                    </div>
                    Project Model
                  </h5>
                  <p class="text-sm text-gray-300 mb-2">Groups related tasks together</p>
                  <ul class="text-sm text-gray-400 space-y-1">
                    <li>• Title</li>
                    <li>• Description</li>
                    <li>• Created date</li>
                    <li>• Owner (connects to User)</li>
                  </ul>
                </div>
                <div class="bg-dark-700/50 p-4 rounded-lg border border-dark-600/50">
                  <h5 class="text-white font-medium mb-2 flex items-center">
                    <div class="w-6 h-6 rounded-full bg-green-500/20 flex items-center justify-center mr-2">
                      <i class="fas fa-tasks text-green-400 text-xs"></i>
                    </div>
                    Task Model
                  </h5>
                  <p class="text-sm text-gray-300 mb-2">Individual tasks to be completed</p>
                  <ul class="text-sm text-gray-400 space-y-1">
                    <li>• Title</li>
                    <li>• Description</li>
                    <li>• Due date</li>
                    <li>• Status (New, In Progress, Complete)</li>
                    <li>• Priority (Low, Medium, High)</li>
                    <li>• Project (connects to Project)</li>
                    <li>• Assigned to (connects to User)</li>
                  </ul>
                </div>
                <div class="bg-dark-700/50 p-4 rounded-lg border border-dark-600/50">
                  <h5 class="text-white font-medium mb-2 flex items-center">
                    <div class="w-6 h-6 rounded-full bg-yellow-500/20 flex items-center justify-center mr-2">
                      <i class="fas fa-comment text-yellow-400 text-xs"></i>
                    </div>
                    Comment Model
                  </h5>
                  <p class="text-sm text-gray-300 mb-2">Discussion about specific tasks</p>
                  <ul class="text-sm text-gray-400 space-y-1">
                    <li>• Content</li>
                    <li>• Created date</li>
                    <li>• Author (connects to User)</li>
                    <li>• Task (connects to Task)</li>
                  </ul>
                </div>
              </div>
            </div>
            <div class="mt-6 bg-primary-500/10 border border-primary-500/20 rounded-lg p-4">
              <h4 class="text-primary-400 mt-0 mb-2 flex items-center text-base font-medium">
                <i class="fas fa-lightbulb mr-2"></i>
                How to describe your data models to Imagi
              </h4>
              <p class="text-gray-300 text-sm mb-0">
                When creating your application, clearly describe what information you need to store and how different types of data relate to each other. For example: "I need to store users who can create multiple projects. Each project can have many tasks, and tasks can have comments from users."
              </p>
            </div>
          </div>
        </div>

        <!-- Section 2: Business Logic -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-8 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-blue-500 to-sky-500"></div>
          <div class="pl-4">
            <h2 class="text-2xl font-bold text-white mb-4">2. Business Logic & App Behavior</h2>
            <p class="text-gray-300">
              Business logic defines how your application behaves - what happens when users perform certain actions. Imagi can create this logic based on your descriptions.
            </p>
            <div class="mt-6 space-y-6">
              <div class="bg-dark-800/50 p-5 rounded-lg border border-dark-700">
                <h4 class="text-white font-medium mb-3 flex items-center">
                  <div class="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center mr-3">
                    <i class="fas fa-shield-alt text-blue-400 text-sm"></i>
                  </div>
                  Authentication & Authorization
                </h4>
                <p class="text-gray-300 text-sm">
                  Controls who can access your application and what they can do:
                </p>
                <ul class="text-sm text-gray-400 space-y-1 mt-2">
                  <li>• Sign up, login, and logout</li>
                  <li>• Password reset functionality</li>
                  <li>• Role-based permissions (admin, regular user, etc.)</li>
                  <li>• Limiting access to certain features based on user role</li>
                </ul>
                <div class="mt-3 text-sm">
                  <strong class="text-blue-400">Example request:</strong> "Users should be able to register and log in. Only project owners should be able to delete their projects."
                </div>
              </div>
              
              <div class="bg-dark-800/50 p-5 rounded-lg border border-dark-700">
                <h4 class="text-white font-medium mb-3 flex items-center">
                  <div class="w-8 h-8 rounded-full bg-green-500/20 flex items-center justify-center mr-3">
                    <i class="fas fa-cogs text-green-400 text-sm"></i>
                  </div>
                  Data Operations
                </h4>
                <p class="text-gray-300 text-sm">
                  Defines how data can be created, read, updated, and deleted (CRUD):
                </p>
                <ul class="text-sm text-gray-400 space-y-1 mt-2">
                  <li>• Creating new records (e.g., adding a new task)</li>
                  <li>• Viewing existing data (e.g., listing all projects)</li>
                  <li>• Updating information (e.g., marking a task complete)</li>
                  <li>• Deleting records (e.g., removing a project)</li>
                </ul>
                <div class="mt-3 text-sm">
                  <strong class="text-green-400">Example request:</strong> "Users should be able to create, view, edit, and delete tasks. When a task is marked complete, its completion date should be automatically recorded."
                </div>
              </div>
              
              <div class="bg-dark-800/50 p-5 rounded-lg border border-dark-700">
                <h4 class="text-white font-medium mb-3 flex items-center">
                  <div class="w-8 h-8 rounded-full bg-yellow-500/20 flex items-center justify-center mr-3">
                    <i class="fas fa-filter text-yellow-400 text-sm"></i>
                  </div>
                  Filtering & Search
                </h4>
                <p class="text-gray-300 text-sm">
                  Helps users find specific information in your app:
                </p>
                <ul class="text-sm text-gray-400 space-y-1 mt-2">
                  <li>• Searching by keywords or phrases</li>
                  <li>• Filtering based on properties (e.g., tasks due today)</li>
                  <li>• Sorting information (e.g., newest first)</li>
                </ul>
                <div class="mt-3 text-sm">
                  <strong class="text-yellow-400">Example request:</strong> "Users should be able to search for tasks by title or description. They should also be able to filter tasks by status (complete/incomplete) and due date."
                </div>
              </div>
              
              <div class="bg-dark-800/50 p-5 rounded-lg border border-dark-700">
                <h4 class="text-white font-medium mb-3 flex items-center">
                  <div class="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center mr-3">
                    <i class="fas fa-bell text-purple-400 text-sm"></i>
                  </div>
                  Notifications & Events
                </h4>
                <p class="text-gray-300 text-sm">
                  Automates communication in your app:
                </p>
                <ul class="text-sm text-gray-400 space-y-1 mt-2">
                  <li>• Email notifications for important events</li>
                  <li>• In-app notifications and alerts</li>
                  <li>• Scheduled reminders (e.g., for approaching due dates)</li>
                </ul>
                <div class="mt-3 text-sm">
                  <strong class="text-purple-400">Example request:</strong> "Send email notifications when tasks are assigned to users. Send reminder notifications one day before a task is due."
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Section 3: Backend Tips -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-8 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-purple-500 to-violet-500"></div>
          <div class="pl-4">
            <h2 class="text-2xl font-bold text-white mb-4">3. Tips for Designing Your Backend</h2>
            
            <ul class="space-y-4 mt-4">
              <li class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-purple-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-sitemap text-purple-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Plan your data relationships</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    Think about how different types of data in your app relate to each other. For example, does each task belong to exactly one project, or can it belong to multiple projects?
                  </p>
                </div>
              </li>
              
              <li class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-purple-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-lock text-purple-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Consider privacy and permissions</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    Decide who should be able to see and modify different types of data. Be clear about this when describing your application to Imagi.
                  </p>
                </div>
              </li>
              
              <li class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-purple-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-calendar-alt text-purple-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Think about time-based operations</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    Consider if your app needs any time-based functionality like scheduling, reminders, or displaying "recently added" items.
                  </p>
                </div>
              </li>
              
              <li class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-purple-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-search text-purple-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Prioritize searchability</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    Think about how users will find information in your application. Specify which fields should be searchable or filterable.
                  </p>
                </div>
              </li>
            </ul>
          </div>
        </div>

        <!-- What's Next -->
        <h2>What's Next?</h2>
        <p>
          Now that you understand backend basics, explore these related resources:
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
          <router-link 
            to="/docs/project-structure" 
            class="block p-4 bg-dark-900/50 border border-dark-800 hover:border-primary-500/30 rounded-xl transition-all duration-300 transform hover:-translate-y-1 group"
          >
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-500/20 to-violet-500/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-primary-500/20">
                <i class="fas fa-sitemap text-xl text-primary-400"></i>
              </div>
              <div>
                <h3 class="text-white group-hover:text-primary-400 transition-colors font-medium text-lg">Project Structure</h3>
                <p class="text-gray-400 text-sm">Understand how your application is organized</p>
              </div>
            </div>
          </router-link>
          <router-link 
            to="/docs/deployment" 
            class="block p-4 bg-dark-900/50 border border-dark-800 hover:border-primary-500/30 rounded-xl transition-all duration-300 transform hover:-translate-y-1 group"
          >
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-500/20 to-violet-500/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-primary-500/20">
                <i class="fas fa-cloud-upload-alt text-xl text-primary-400"></i>
              </div>
              <div>
                <h3 class="text-white group-hover:text-primary-400 transition-colors font-medium text-lg">Deployment Guide</h3>
                <p class="text-gray-400 text-sm">Learn how to take your application live</p>
              </div>
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </DocsLayout>
</template>

<script setup>
import DocsLayout from '../layouts/DocsLayout.vue'
</script>

<style scoped>
@keyframes pulse-slow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.animate-pulse-slow {
  animation: pulse-slow 3s ease-in-out infinite;
}

/* Override Tailwind prose styling for lists with custom icons */
:deep(.prose ul) {
  list-style-type: none;
  padding-left: 0;
}

:deep(.prose ol) {
  padding-left: 1.75rem;
}
</style> 