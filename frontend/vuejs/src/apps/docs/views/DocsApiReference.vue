<template>
  <DocsLayout>
    <div class="max-w-4xl mx-auto">
      <!-- Page header with attractive styling -->
      <div class="mb-10">
        <div class="inline-block px-4 py-1.5 bg-primary-500/10 rounded-full mb-4">
          <span class="text-primary-400 font-semibold text-sm tracking-wider">DOCUMENTATION</span>
        </div>
        <h1 class="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
          API Reference
        </h1>
        <p class="text-xl text-gray-300 leading-relaxed">
          Complete reference for the Imagi Oasis REST API endpoints and SDK.
        </p>
      </div>

      <!-- Attractive divider -->
      <div class="relative h-16 mb-10">
        <div class="absolute inset-x-0 h-px mx-auto w-2/3 sm:w-1/2 bg-gradient-to-r from-transparent via-primary-500/30 to-transparent animate-pulse-slow"></div>
      </div>

      <!-- Main content with sections -->
      <div class="prose prose-invert prose-lg max-w-none">
        <!-- API Coming Soon Notice -->
        <div class="bg-primary-500/10 border border-primary-500/20 rounded-xl p-6 my-8">
          <div class="flex items-start">
            <div class="flex-shrink-0 w-10 h-10 rounded-full bg-primary-500/20 flex items-center justify-center mr-4">
              <i class="fas fa-code text-primary-400"></i>
            </div>
            <div>
              <h3 class="text-white font-bold mt-0 mb-2">API Coming Soon</h3>
              <p class="text-gray-300 m-0">
                The Imagi Oasis API is currently under development and not yet available for public use.
                This documentation provides a preview of planned endpoints and functionality.
                Stay tuned for updates on API availability.
              </p>
            </div>
          </div>
        </div>
      
        <h2>Introduction</h2>
        <p>
          The upcoming Imagi Oasis API will enable you to programmatically interact with your projects,
          generate code, and manage deployments. The API follows RESTful principles and
          uses standard HTTP status codes and methods.
        </p>

        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-6 my-8">
          <h3 class="text-primary-400 mt-0">Base URL</h3>
          <div class="bg-dark-800 p-3 rounded-md overflow-x-auto">
            <code class="text-green-400">https://api.imagioasis.com/api/v1</code>
          </div>

          <h3 class="text-primary-400 mt-6">Authentication</h3>
          <p class="mb-4">
            All API requests require authentication using a Bearer token.
          </p>
          <div class="bg-dark-800 p-3 rounded-md overflow-x-auto">
            <code class="text-yellow-400">Authorization: Bearer YOUR_API_KEY</code>
          </div>

          <h3 class="text-primary-400 mt-6">Rate Limiting</h3>
          <p class="mb-0">
            API calls are limited based on your subscription plan. Rate limit information is included in the response headers.
          </p>
        </div>

        <!-- API Endpoints Section -->
        <h2>API Endpoints</h2>
        <p>
          The following endpoints are available for interacting with Imagi Oasis:
        </p>

        <!-- Project Endpoints -->
        <div class="mt-8 space-y-6">
          <div class="border border-dark-800 rounded-xl overflow-hidden">
            <div class="bg-dark-900 p-4 border-b border-dark-800 flex items-center justify-between">
              <div class="flex items-center">
                <div class="px-2 py-1 bg-green-500/20 rounded text-green-400 font-mono text-sm mr-3">GET</div>
                <h3 class="text-white font-medium m-0">/projects</h3>
              </div>
              <button class="text-gray-400 hover:text-white transition-colors" @click="toggleEndpoint('getProjects')">
                <i :class="[isEndpointExpanded('getProjects') ? 'fas fa-chevron-up' : 'fas fa-chevron-down']"></i>
              </button>
            </div>
            <div v-if="isEndpointExpanded('getProjects')" class="p-4 bg-dark-800/50">
              <div class="mb-4">
                <p class="text-gray-300 m-0">
                  Returns a list of all projects associated with your account.
                </p>
              </div>
              <div class="mb-4">
                <h4 class="text-primary-400 text-sm font-medium mb-2">Parameters</h4>
                <div class="bg-dark-800 rounded-md overflow-hidden">
                  <table class="w-full border-collapse">
                    <thead>
                      <tr class="border-b border-dark-700">
                        <th class="text-left p-3 text-gray-400 font-medium">Name</th>
                        <th class="text-left p-3 text-gray-400 font-medium">Type</th>
                        <th class="text-left p-3 text-gray-400 font-medium">Description</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr class="border-b border-dark-700">
                        <td class="p-3 text-primary-400 font-mono text-sm">page</td>
                        <td class="p-3 text-yellow-400">integer</td>
                        <td class="p-3 text-gray-300">Page number (default: 1)</td>
                      </tr>
                      <tr>
                        <td class="p-3 text-primary-400 font-mono text-sm">limit</td>
                        <td class="p-3 text-yellow-400">integer</td>
                        <td class="p-3 text-gray-300">Results per page (default: 20, max: 100)</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div class="mb-4">
                <h4 class="text-primary-400 text-sm font-medium mb-2">Response</h4>
                <div class="bg-dark-800 p-3 rounded-md overflow-x-auto">
                  <pre class="text-gray-300 m-0 whitespace-pre"><code>{
  "projects": [
    {
      "id": "proj_123abc",
      "name": "Task Manager",
      "description": "A task management application",
      "created_at": "2023-04-15T10:30:00Z",
      "updated_at": "2023-04-20T15:45:00Z",
      "status": "active"
    },
    ...
  ],
  "meta": {
    "current_page": 1,
    "total_pages": 5,
    "total_count": 42
  }
}</code></pre>
                </div>
              </div>
            </div>
          </div>

          <div class="border border-dark-800 rounded-xl overflow-hidden">
            <div class="bg-dark-900 p-4 border-b border-dark-800 flex items-center justify-between">
              <div class="flex items-center">
                <div class="px-2 py-1 bg-blue-500/20 rounded text-blue-400 font-mono text-sm mr-3">POST</div>
                <h3 class="text-white font-medium m-0">/projects</h3>
              </div>
              <button class="text-gray-400 hover:text-white transition-colors" @click="toggleEndpoint('createProject')">
                <i :class="[isEndpointExpanded('createProject') ? 'fas fa-chevron-up' : 'fas fa-chevron-down']"></i>
              </button>
            </div>
            <div v-if="isEndpointExpanded('createProject')" class="p-4 bg-dark-800/50">
              <div class="mb-4">
                <p class="text-gray-300 m-0">
                  Creates a new project with the specified parameters.
                </p>
              </div>
              <div class="mb-4">
                <h4 class="text-primary-400 text-sm font-medium mb-2">Request Body</h4>
                <div class="bg-dark-800 p-3 rounded-md overflow-x-auto">
                  <pre class="text-gray-300 m-0 whitespace-pre"><code>{
  "name": "E-commerce Platform",
  "description": "Online store with product catalog and checkout",
  "project_type": "web_application",
  "tech_stack": {
    "frontend": "vue",
    "backend": "django",
    "database": "postgresql"
  }
}</code></pre>
                </div>
              </div>
              <div class="mb-4">
                <h4 class="text-primary-400 text-sm font-medium mb-2">Response</h4>
                <div class="bg-dark-800 p-3 rounded-md overflow-x-auto">
                  <pre class="text-gray-300 m-0 whitespace-pre"><code>{
  "id": "proj_456def",
  "name": "E-commerce Platform",
  "description": "Online store with product catalog and checkout",
  "created_at": "2023-05-10T09:15:00Z",
  "updated_at": "2023-05-10T09:15:00Z",
  "status": "initializing",
  "project_type": "web_application",
  "tech_stack": {
    "frontend": "vue",
    "backend": "django",
    "database": "postgresql"
  }
}</code></pre>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Generation Endpoints -->
        <h3 class="mt-12">Code Generation</h3>
        <p>
          Endpoints for generating code and components.
        </p>

        <div class="mt-6 border border-dark-800 rounded-xl overflow-hidden">
          <div class="bg-dark-900 p-4 border-b border-dark-800 flex items-center justify-between">
            <div class="flex items-center">
              <div class="px-2 py-1 bg-blue-500/20 rounded text-blue-400 font-mono text-sm mr-3">POST</div>
              <h3 class="text-white font-medium m-0">/projects/{project_id}/generate</h3>
            </div>
            <button class="text-gray-400 hover:text-white transition-colors" @click="toggleEndpoint('generateCode')">
              <i :class="[isEndpointExpanded('generateCode') ? 'fas fa-chevron-up' : 'fas fa-chevron-down']"></i>
            </button>
          </div>
          <div v-if="isEndpointExpanded('generateCode')" class="p-4 bg-dark-800/50">
            <div class="mb-4">
              <p class="text-gray-300 m-0">
                Generates code based on the provided description or requirements.
              </p>
            </div>
            <div class="mb-4">
              <h4 class="text-primary-400 text-sm font-medium mb-2">Path Parameters</h4>
              <div class="bg-dark-800 rounded-md overflow-hidden">
                <table class="w-full border-collapse">
                  <thead>
                    <tr class="border-b border-dark-700">
                      <th class="text-left p-3 text-gray-400 font-medium">Name</th>
                      <th class="text-left p-3 text-gray-400 font-medium">Type</th>
                      <th class="text-left p-3 text-gray-400 font-medium">Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td class="p-3 text-primary-400 font-mono text-sm">project_id</td>
                      <td class="p-3 text-yellow-400">string</td>
                      <td class="p-3 text-gray-300">The ID of the project</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div class="mb-4">
              <h4 class="text-primary-400 text-sm font-medium mb-2">Request Body</h4>
              <div class="bg-dark-800 p-3 rounded-md overflow-x-auto">
                <pre class="text-gray-300 m-0 whitespace-pre"><code>{
  "description": "Create a login form with email and password fields, plus a 'Forgot Password' link",
  "type": "component",
  "options": {
    "language": "vue",
    "styling": "tailwind",
    "add_validation": true
  }
}</code></pre>
              </div>
            </div>
            <div class="mb-4">
              <h4 class="text-primary-400 text-sm font-medium mb-2">Response</h4>
              <div class="bg-dark-800 p-3 rounded-md overflow-x-auto">
                <pre class="text-gray-300 m-0 whitespace-pre"><code>{
  "id": "gen_789ghi",
  "status": "completed",
  "files": [
    {
      "path": "components/LoginForm.vue",
      "content": "<!-- Generated login form component code -->",
      "language": "vue"
    }
  ],
  "created_at": "2023-05-15T14:30:00Z"
}</code></pre>
              </div>
            </div>
          </div>
        </div>

        <!-- SDK Section -->
        <h2 class="mt-12">JavaScript SDK</h2>
        <p>
          For convenience, we provide a JavaScript SDK that simplifies API integration.
        </p>

        <div class="mt-6 bg-dark-900/50 border border-dark-800 rounded-xl p-6">
          <h3 class="text-primary-400 mt-0">Installation</h3>
          <div class="bg-dark-800 p-3 rounded-md overflow-x-auto">
            <code class="text-gray-300">npm install @imagi/sdk</code>
          </div>

          <h3 class="text-primary-400 mt-6">Usage Example</h3>
          <div class="bg-dark-800 p-3 rounded-md overflow-x-auto">
            <pre class="text-gray-300 m-0 whitespace-pre"><code>import { ImagiClient } from '@imagi/sdk';

const client = new ImagiClient('YOUR_API_KEY');

// List projects
client.projects.list()
  .then(projects => console.log(projects))
  .catch(error => console.error(error));

// Create a new project
client.projects.create({
  name: 'My Awesome Project',
  description: 'Description of my project',
  projectType: 'web_application'
})
  .then(project => console.log(project))
  .catch(error => console.error(error));</code></pre>
          </div>
        </div>

        <!-- Additional Resources -->
        <div class="mt-12 bg-primary-500/10 border border-primary-500/20 rounded-xl p-6">
          <h3 class="text-primary-400 mt-0 flex items-center">
            <i class="fas fa-info-circle mr-2"></i>
            Need More Help?
          </h3>
          <p class="mb-4">
            If you need additional assistance, explore these resources:
          </p>
          <ul class="mb-4">
            <li>Check our <router-link to="/docs/troubleshooting" class="text-primary-400 hover:text-primary-300 transition-colors">Troubleshooting Guide</router-link></li>
            <li>Join our <a href="#" class="text-primary-400 hover:text-primary-300 transition-colors">Discord community</a></li>
            <li>Contact <a href="#" class="text-primary-400 hover:text-primary-300 transition-colors">Support Team</a></li>
          </ul>
        </div>
      </div>
    </div>
  </DocsLayout>
</template>

<script setup>
import { ref } from 'vue'
import DocsLayout from '../layouts/DocsLayout.vue'

// Track expanded endpoint sections
const expandedEndpoints = ref(new Set(['getProjects']))

// Toggle endpoint visibility
const toggleEndpoint = (endpointId) => {
  if (expandedEndpoints.value.has(endpointId)) {
    expandedEndpoints.value.delete(endpointId)
  } else {
    expandedEndpoints.value.add(endpointId)
  }
}

// Check if an endpoint is expanded
const isEndpointExpanded = (endpointId) => {
  return expandedEndpoints.value.has(endpointId)
}
</script>

<style scoped>
@keyframes pulse-slow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.animate-pulse-slow {
  animation: pulse-slow 3s ease-in-out infinite;
}
</style> 