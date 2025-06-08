<template>
  <DocsLayout>
    <DocsContentWrapper
      title="Adding Backend Logic"
      description="Understanding how data and business logic work in your Imagi Oasis application."
      badge-text="BACKEND GUIDE"
    >
      <!-- Introduction -->
      <DocsCard color-variant="primary">
        <DocsCardHeader title="What is a Backend?" icon="fas fa-server" color="primary" />
        <p class="text-gray-300 leading-relaxed mb-4">
          Think of your application as having two main parts:
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm">
            <div class="flex items-center mb-3">
              <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-primary-400/20 to-indigo-400/20 border border-primary-400/20 flex items-center justify-center mr-3">
                <i class="fas fa-desktop text-primary-300 text-sm"></i>
              </div>
              <h4 class="text-white font-semibold">Frontend</h4>
            </div>
            <p class="text-gray-300 text-sm leading-relaxed">What users see and interact with (buttons, forms, pages)</p>
          </div>
          
          <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm">
            <div class="flex items-center mb-3">
              <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center mr-3">
                <i class="fas fa-server text-blue-300 text-sm"></i>
              </div>
              <h4 class="text-white font-semibold">Backend</h4>
            </div>
            <p class="text-gray-300 text-sm leading-relaxed">Where data is stored and processed (like the engine under a car's hood)</p>
          </div>
        </div>
        <p class="text-gray-300 leading-relaxed mt-4">
          With Imagi Oasis, you don't need to write code for your backend. Instead, you describe what you want your application to do, and Imagi creates both the frontend and backend for you.
        </p>
      </DocsCard>

      <!-- Data Models Section -->
      <DocsCard color-variant="violet">
        <DocsCardHeader title="Understanding Data Models" icon="fas fa-database" color="violet" />
        <p class="text-gray-300 leading-relaxed mb-6">
          Data models are the blueprints for how information is organized in your application. They define what types of information you'll store and how different pieces of data relate to each other.
        </p>
        
        <div class="bg-gradient-to-r from-violet-400/8 to-purple-400/8 rounded-2xl p-6 border border-violet-400/15 mb-6">
          <h4 class="text-violet-300 font-semibold text-lg mb-4 flex items-center">
            <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-violet-400/20 to-purple-400/20 border border-violet-400/20 flex items-center justify-center mr-3">
              <i class="fas fa-tasks text-violet-300 text-sm"></i>
            </div>
            Example: Task Management App
          </h4>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm">
              <div class="flex items-center mb-3">
                <div class="w-6 h-6 rounded-lg bg-gradient-to-br from-primary-400/20 to-indigo-400/20 border border-primary-400/20 flex items-center justify-center mr-2">
                  <i class="fas fa-user text-primary-300 text-xs"></i>
                </div>
                <h5 class="text-white font-medium text-sm">User Model</h5>
              </div>
              <p class="text-gray-300 text-xs mb-2">Stores information about your users</p>
              <ul class="space-y-1">
                <DocsListItem icon="fas fa-circle" color="primary" size="xs">Name</DocsListItem>
                <DocsListItem icon="fas fa-circle" color="primary" size="xs">Email</DocsListItem>
                <DocsListItem icon="fas fa-circle" color="primary" size="xs">Password (securely stored)</DocsListItem>
                <DocsListItem icon="fas fa-circle" color="primary" size="xs">Profile picture</DocsListItem>
              </ul>
            </div>
            
            <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm">
              <div class="flex items-center mb-3">
                <div class="w-6 h-6 rounded-lg bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center mr-2">
                  <i class="fas fa-th-list text-blue-300 text-xs"></i>
                </div>
                <h5 class="text-white font-medium text-sm">Project Model</h5>
              </div>
              <p class="text-gray-300 text-xs mb-2">Groups related tasks together</p>
              <ul class="space-y-1">
                <DocsListItem icon="fas fa-circle" color="blue" size="xs">Title</DocsListItem>
                <DocsListItem icon="fas fa-circle" color="blue" size="xs">Description</DocsListItem>
                <DocsListItem icon="fas fa-circle" color="blue" size="xs">Created date</DocsListItem>
                <DocsListItem icon="fas fa-circle" color="blue" size="xs">Owner (connects to User)</DocsListItem>
              </ul>
            </div>
            
            <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm">
              <div class="flex items-center mb-3">
                <div class="w-6 h-6 rounded-lg bg-gradient-to-br from-green-400/20 to-emerald-400/20 border border-green-400/20 flex items-center justify-center mr-2">
                  <i class="fas fa-tasks text-green-300 text-xs"></i>
                </div>
                <h5 class="text-white font-medium text-sm">Task Model</h5>
              </div>
              <p class="text-gray-300 text-xs mb-2">Individual tasks to be completed</p>
              <ul class="space-y-1">
                <DocsListItem icon="fas fa-circle" color="emerald" size="xs">Title</DocsListItem>
                <DocsListItem icon="fas fa-circle" color="emerald" size="xs">Description</DocsListItem>
                <DocsListItem icon="fas fa-circle" color="emerald" size="xs">Due date</DocsListItem>
                <DocsListItem icon="fas fa-circle" color="emerald" size="xs">Status (New, In Progress, Complete)</DocsListItem>
                <DocsListItem icon="fas fa-circle" color="emerald" size="xs">Priority (Low, Medium, High)</DocsListItem>
                <DocsListItem icon="fas fa-circle" color="emerald" size="xs">Project (connects to Project)</DocsListItem>
                <DocsListItem icon="fas fa-circle" color="emerald" size="xs">Assigned to (connects to User)</DocsListItem>
              </ul>
            </div>
            
            <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm">
              <div class="flex items-center mb-3">
                <div class="w-6 h-6 rounded-lg bg-gradient-to-br from-yellow-400/20 to-orange-400/20 border border-yellow-400/20 flex items-center justify-center mr-2">
                  <i class="fas fa-comment text-yellow-300 text-xs"></i>
                </div>
                <h5 class="text-white font-medium text-sm">Comment Model</h5>
              </div>
              <p class="text-gray-300 text-xs mb-2">Discussion about specific tasks</p>
              <ul class="space-y-1">
                <DocsListItem icon="fas fa-circle" color="yellow" size="xs">Content</DocsListItem>
                <DocsListItem icon="fas fa-circle" color="yellow" size="xs">Created date</DocsListItem>
                <DocsListItem icon="fas fa-circle" color="yellow" size="xs">Author (connects to User)</DocsListItem>
                <DocsListItem icon="fas fa-circle" color="yellow" size="xs">Task (connects to Task)</DocsListItem>
              </ul>
            </div>
          </div>
        </div>
        
        <div class="bg-gradient-to-r from-primary-400/8 to-indigo-400/8 rounded-2xl p-4 border border-primary-400/15">
          <h4 class="text-primary-300 font-medium mb-2 flex items-center">
            <i class="fas fa-lightbulb mr-2"></i>
            How to describe your data models to Imagi
          </h4>
          <p class="text-gray-300 text-sm leading-relaxed">
            When creating your application, clearly describe what information you need to store and how different types of data relate to each other. For example: "I need to store users who can create multiple projects. Each project can have many tasks, and tasks can have comments from users."
          </p>
        </div>
      </DocsCard>

      <!-- Business Logic Section -->
      <DocsCard color-variant="blue">
        <DocsCardHeader title="Business Logic & App Behavior" icon="fas fa-cogs" color="blue" />
        <p class="text-gray-300 leading-relaxed mb-6">
          Business logic defines how your application behaves - what happens when users perform certain actions. Imagi can create this logic based on your descriptions.
        </p>
        
        <div class="space-y-4">
          <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm">
            <div class="flex items-start gap-4">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center flex-shrink-0">
                <i class="fas fa-shield-alt text-blue-300"></i>
              </div>
              <div class="flex-1">
                <h4 class="text-white font-semibold mb-2">Authentication & Authorization</h4>
                <p class="text-gray-300 text-sm mb-3">
                  Controls who can access your application and what they can do:
                </p>
                <ul class="space-y-2">
                  <DocsListItem icon="fas fa-arrow-right" color="blue" size="sm">Sign up, login, and logout</DocsListItem>
                  <DocsListItem icon="fas fa-arrow-right" color="blue" size="sm">Password reset functionality</DocsListItem>
                  <DocsListItem icon="fas fa-arrow-right" color="blue" size="sm">Role-based permissions (admin, regular user, etc.)</DocsListItem>
                  <DocsListItem icon="fas fa-arrow-right" color="blue" size="sm">Limiting access to certain features based on user role</DocsListItem>
                </ul>
                <div class="mt-3 p-3 bg-blue-500/10 border border-blue-400/20 rounded-lg">
                  <p class="text-blue-300 text-sm font-medium">Example request:</p>
                  <p class="text-gray-300 text-sm mt-1">"Users should be able to register and log in. Only project owners should be able to delete their projects."</p>
                </div>
              </div>
            </div>
          </div>
          
          <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm">
            <div class="flex items-start gap-4">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-green-400/20 to-emerald-400/20 border border-green-400/20 flex items-center justify-center flex-shrink-0">
                <i class="fas fa-cogs text-green-300"></i>
              </div>
              <div class="flex-1">
                <h4 class="text-white font-semibold mb-2">Data Operations</h4>
                <p class="text-gray-300 text-sm mb-3">
                  Defines how data can be created, read, updated, and deleted (CRUD):
                </p>
                <ul class="space-y-2">
                  <DocsListItem icon="fas fa-arrow-right" color="emerald" size="sm">Creating new records (e.g., adding a new task)</DocsListItem>
                  <DocsListItem icon="fas fa-arrow-right" color="emerald" size="sm">Viewing existing data (e.g., listing all projects)</DocsListItem>
                  <DocsListItem icon="fas fa-arrow-right" color="emerald" size="sm">Updating information (e.g., marking a task complete)</DocsListItem>
                  <DocsListItem icon="fas fa-arrow-right" color="emerald" size="sm">Deleting records (e.g., removing a project)</DocsListItem>
                </ul>
                <div class="mt-3 p-3 bg-green-500/10 border border-green-400/20 rounded-lg">
                  <p class="text-green-300 text-sm font-medium">Example request:</p>
                  <p class="text-gray-300 text-sm mt-1">"Users should be able to create, view, edit, and delete tasks. When a task is marked complete, its completion date should be automatically recorded."</p>
                </div>
              </div>
            </div>
          </div>
          
          <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm">
            <div class="flex items-start gap-4">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-yellow-400/20 to-orange-400/20 border border-yellow-400/20 flex items-center justify-center flex-shrink-0">
                <i class="fas fa-filter text-yellow-300"></i>
              </div>
              <div class="flex-1">
                <h4 class="text-white font-semibold mb-2">Filtering & Search</h4>
                <p class="text-gray-300 text-sm mb-3">
                  Helps users find specific information in your app:
                </p>
                <ul class="space-y-2">
                  <DocsListItem icon="fas fa-arrow-right" color="yellow" size="sm">Searching by keywords or phrases</DocsListItem>
                  <DocsListItem icon="fas fa-arrow-right" color="yellow" size="sm">Filtering based on properties (e.g., tasks due today)</DocsListItem>
                  <DocsListItem icon="fas fa-arrow-right" color="yellow" size="sm">Sorting information (e.g., newest first)</DocsListItem>
                </ul>
                <div class="mt-3 p-3 bg-yellow-500/10 border border-yellow-400/20 rounded-lg">
                  <p class="text-yellow-300 text-sm font-medium">Example request:</p>
                  <p class="text-gray-300 text-sm mt-1">"Users should be able to search for tasks by title or description. They should also be able to filter tasks by status (complete/incomplete) and due date."</p>
                </div>
              </div>
            </div>
          </div>
          
          <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm">
            <div class="flex items-start gap-4">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-400/20 to-violet-400/20 border border-purple-400/20 flex items-center justify-center flex-shrink-0">
                <i class="fas fa-bell text-purple-300"></i>
              </div>
              <div class="flex-1">
                <h4 class="text-white font-semibold mb-2">Notifications & Events</h4>
                <p class="text-gray-300 text-sm mb-3">
                  Automates communication in your app:
                </p>
                <ul class="space-y-2">
                  <DocsListItem icon="fas fa-arrow-right" color="purple" size="sm">Email notifications for important events</DocsListItem>
                  <DocsListItem icon="fas fa-arrow-right" color="purple" size="sm">In-app notifications and alerts</DocsListItem>
                  <DocsListItem icon="fas fa-arrow-right" color="purple" size="sm">Scheduled reminders (e.g., for approaching due dates)</DocsListItem>
                </ul>
                <div class="mt-3 p-3 bg-purple-500/10 border border-purple-400/20 rounded-lg">
                  <p class="text-purple-300 text-sm font-medium">Example request:</p>
                  <p class="text-gray-300 text-sm mt-1">"Send email notifications when tasks are assigned to users. Send reminder notifications one day before a task is due."</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </DocsCard>

      <!-- Backend Design Tips -->
      <DocsCard color-variant="cyan">
        <DocsCardHeader title="Tips for Designing Your Backend" icon="fas fa-lightbulb" color="cyan" />
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm">
            <div class="flex items-start gap-3 mb-3">
              <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-cyan-400/20 to-blue-400/20 border border-cyan-400/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <i class="fas fa-sitemap text-cyan-300 text-sm"></i>
              </div>
              <div>
                <h4 class="text-white font-semibold text-sm">Plan your data relationships</h4>
              </div>
            </div>
            <p class="text-gray-300 text-xs leading-relaxed">
              Think about how different types of data in your app relate to each other. For example, does each task belong to exactly one project, or can it belong to multiple projects?
            </p>
          </div>
          
          <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm">
            <div class="flex items-start gap-3 mb-3">
              <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <i class="fas fa-lock text-blue-300 text-sm"></i>
              </div>
              <div>
                <h4 class="text-white font-semibold text-sm">Consider privacy and permissions</h4>
              </div>
            </div>
            <p class="text-gray-300 text-xs leading-relaxed">
              Decide who should be able to see and modify different types of data. Be clear about this when describing your application to Imagi.
            </p>
          </div>
          
          <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm">
            <div class="flex items-start gap-3 mb-3">
              <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-violet-400/20 to-purple-400/20 border border-violet-400/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <i class="fas fa-calendar-alt text-violet-300 text-sm"></i>
              </div>
              <div>
                <h4 class="text-white font-semibold text-sm">Think about time-based operations</h4>
              </div>
            </div>
            <p class="text-gray-300 text-xs leading-relaxed">
              Consider if your app needs any time-based functionality like scheduling, reminders, or displaying "recently added" items.
            </p>
          </div>
          
          <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm">
            <div class="flex items-start gap-3 mb-3">
              <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-400/20 to-green-400/20 border border-emerald-400/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <i class="fas fa-search text-emerald-300 text-sm"></i>
              </div>
              <div>
                <h4 class="text-white font-semibold text-sm">Prioritize searchability</h4>
              </div>
            </div>
            <p class="text-gray-300 text-xs leading-relaxed">
              Think about how users will find information in your application. Specify which fields should be searchable or filterable.
            </p>
          </div>
        </div>
      </DocsCard>

      <!-- What's Next Navigation -->
      <DocsCard>
        <DocsCardHeader title="What's Next?" icon="fas fa-arrow-right" />
        <p class="text-gray-300 leading-relaxed mb-6">
          Now that you understand backend basics, explore these related resources:
        </p>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <router-link 
            to="/docs/project-structure" 
            class="inline-flex items-center px-4 py-2 bg-gradient-to-r from-indigo-500/20 to-violet-500/20 hover:from-indigo-500/30 hover:to-violet-500/30 text-indigo-300 hover:text-indigo-200 rounded-xl transition-all duration-300 border border-indigo-400/20 hover:border-indigo-400/30 mr-4 mb-4"
          >
            <i class="fas fa-sitemap mr-2 text-sm"></i>
            Project Structure
          </router-link>
          
          <router-link 
            to="/docs/deployment" 
            class="inline-flex items-center px-4 py-2 bg-gradient-to-r from-indigo-500/20 to-violet-500/20 hover:from-indigo-500/30 hover:to-violet-500/30 text-indigo-300 hover:text-indigo-200 rounded-xl transition-all duration-300 border border-indigo-400/20 hover:border-indigo-400/30 mb-4"
          >
            <i class="fas fa-cloud-upload-alt mr-2 text-sm"></i>
            Deployment Guide
          </router-link>
        </div>
      </DocsCard>

      <!-- CTA Section -->
      <DocsCTASection 
        title="Ready to Build Your Backend?" 
        icon="fas fa-server" 
        description="Start creating your backend logic with clear descriptions and let Imagi handle the implementation."
        buttonText="Create a Project"
        buttonLink="/products/oasis/builder/dashboard"
        buttonIcon="fas fa-plus-circle"
      />
    </DocsContentWrapper>
  </DocsLayout>
</template>

<script setup>
import DocsLayout from '../layouts/DocsLayout.vue'
import { DocsContentWrapper, DocsCard, DocsCardHeader, DocsListItem, DocsCTASection } from '../components'
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