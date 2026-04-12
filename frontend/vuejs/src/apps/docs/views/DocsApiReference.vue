<template>
  <DocsLayout>
    <DocsContentWrapper
      title="API Reference"
      description="Complete reference for the Imagi REST API endpoints and SDK."
      badge-text="API DOCUMENTATION"
    >
      <!-- API Coming Soon Notice -->
      <DocsCard color-variant="violet">
        <div class="flex items-start gap-4">
          <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-400/20 to-fuchsia-400/20 border border-violet-400/20 flex items-center justify-center flex-shrink-0">
            <i class="fas fa-code text-violet-300 text-xl"></i>
          </div>
          <div>
            <h3 class="text-white font-semibold text-lg mb-2">API Coming Soon</h3>
            <p class="text-white/50 leading-relaxed">
              The Imagi API is currently under development and not yet available for public use.
              This documentation provides a preview of planned endpoints and functionality.
              Stay tuned for updates on API availability.
            </p>
          </div>
        </div>
      </DocsCard>

      <!-- Introduction -->
      <DocsCard color-variant="primary">
        <DocsCardHeader title="Introduction" icon="fas fa-book-open" color="primary" />
        <p class="text-white/50 leading-relaxed mb-6">
          The upcoming Imagi API will enable you to programmatically interact with your projects,
          generate code, and manage deployments. The API follows RESTful principles and
          uses standard HTTP status codes and methods.
        </p>

        <div class="space-y-6">
          <div class="bg-white/[0.03] border border-white/[0.08] rounded-xl p-4">
            <h4 class="text-violet-400 font-medium mb-2">Base URL</h4>
            <div class="bg-[#0a0a0f] p-3 rounded-lg border border-white/[0.06] overflow-x-auto">
              <code class="text-emerald-400 text-sm">https://api.imagioasis.com/api/v1</code>
            </div>
          </div>

          <div class="bg-white/[0.03] border border-white/[0.08] rounded-xl p-4">
            <h4 class="text-violet-400 font-medium mb-2">Authentication</h4>
            <p class="text-white/50 text-sm mb-3">
              All API requests require authentication using a Bearer token.
            </p>
            <div class="bg-[#0a0a0f] p-3 rounded-lg border border-white/[0.06] overflow-x-auto">
              <code class="text-amber-400 text-sm">Authorization: Bearer YOUR_API_KEY</code>
            </div>
          </div>

          <div class="bg-white/[0.03] border border-white/[0.08] rounded-xl p-4">
            <h4 class="text-violet-400 font-medium mb-2">Rate Limiting</h4>
            <p class="text-white/50 text-sm">
              API calls are limited based on your subscription plan. Rate limit information is included in the response headers.
            </p>
          </div>
        </div>
      </DocsCard>

      <!-- API Endpoints Section -->
      <DocsCard color-variant="blue">
        <DocsCardHeader title="Project Endpoints" icon="fas fa-folder" color="blue" />
        
        <div class="space-y-4 mt-4">
          <!-- GET /projects -->
          <div class="border border-white/[0.08] rounded-xl overflow-hidden">
            <div class="bg-white/[0.02] p-4 border-b border-white/[0.08] flex items-center justify-between">
              <div class="flex items-center gap-3">
                <span class="px-2.5 py-1 bg-emerald-500/20 rounded-lg text-emerald-400 font-mono text-xs font-medium">GET</span>
                <code class="text-white/80 text-sm">/projects</code>
              </div>
              <button 
                class="text-white/40 hover:text-white transition-colors p-2" 
                @click="toggleEndpoint('getProjects')"
              >
                <i :class="[isEndpointExpanded('getProjects') ? 'fas fa-chevron-up' : 'fas fa-chevron-down']"></i>
              </button>
            </div>
            <div v-if="isEndpointExpanded('getProjects')" class="p-4 bg-white/[0.01]">
              <p class="text-white/50 text-sm mb-4">
                Returns a list of all projects associated with your account.
              </p>
              
              <h5 class="text-blue-400 text-sm font-medium mb-2">Parameters</h5>
              <div class="bg-[#0a0a0f] rounded-lg border border-white/[0.06] overflow-hidden mb-4">
                <table class="w-full">
                  <thead>
                    <tr class="border-b border-white/[0.06]">
                      <th class="text-left p-3 text-white/40 font-medium text-xs">Name</th>
                      <th class="text-left p-3 text-white/40 font-medium text-xs">Type</th>
                      <th class="text-left p-3 text-white/40 font-medium text-xs">Description</th>
                    </tr>
                  </thead>
                  <tbody class="text-sm">
                    <tr class="border-b border-white/[0.06]">
                      <td class="p-3 text-violet-400 font-mono">page</td>
                      <td class="p-3 text-amber-400">integer</td>
                      <td class="p-3 text-white/50">Page number (default: 1)</td>
                    </tr>
                    <tr>
                      <td class="p-3 text-violet-400 font-mono">limit</td>
                      <td class="p-3 text-amber-400">integer</td>
                      <td class="p-3 text-white/50">Results per page (default: 20, max: 100)</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              
              <h5 class="text-blue-400 text-sm font-medium mb-2">Response</h5>
              <div class="bg-[#0a0a0f] p-4 rounded-lg border border-white/[0.06] overflow-x-auto">
                <pre class="text-white/70 text-sm m-0"><code>{
  "projects": [
    {
      "id": "proj_123abc",
      "name": "Task Manager",
      "description": "A task management application",
      "created_at": "2023-04-15T10:30:00Z",
      "status": "active"
    }
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

          <!-- POST /projects -->
          <div class="border border-white/[0.08] rounded-xl overflow-hidden">
            <div class="bg-white/[0.02] p-4 border-b border-white/[0.08] flex items-center justify-between">
              <div class="flex items-center gap-3">
                <span class="px-2.5 py-1 bg-blue-500/20 rounded-lg text-blue-400 font-mono text-xs font-medium">POST</span>
                <code class="text-white/80 text-sm">/projects</code>
              </div>
              <button 
                class="text-white/40 hover:text-white transition-colors p-2" 
                @click="toggleEndpoint('createProject')"
              >
                <i :class="[isEndpointExpanded('createProject') ? 'fas fa-chevron-up' : 'fas fa-chevron-down']"></i>
              </button>
            </div>
            <div v-if="isEndpointExpanded('createProject')" class="p-4 bg-white/[0.01]">
              <p class="text-white/50 text-sm mb-4">
                Creates a new project with the specified parameters.
              </p>
              
              <h5 class="text-blue-400 text-sm font-medium mb-2">Request Body</h5>
              <div class="bg-[#0a0a0f] p-4 rounded-lg border border-white/[0.06] overflow-x-auto mb-4">
                <pre class="text-white/70 text-sm m-0"><code>{
  "name": "E-commerce Platform",
  "description": "Online store with product catalog",
  "project_type": "web_application",
  "tech_stack": {
    "frontend": "vue",
    "backend": "django"
  }
}</code></pre>
              </div>
              
              <h5 class="text-blue-400 text-sm font-medium mb-2">Response</h5>
              <div class="bg-[#0a0a0f] p-4 rounded-lg border border-white/[0.06] overflow-x-auto">
                <pre class="text-white/70 text-sm m-0"><code>{
  "id": "proj_456def",
  "name": "E-commerce Platform",
  "status": "initializing",
  "created_at": "2023-05-10T09:15:00Z"
}</code></pre>
              </div>
            </div>
          </div>
        </div>
      </DocsCard>

      <!-- Code Generation Endpoints -->
      <DocsCard color-variant="cyan">
        <DocsCardHeader title="Code Generation" icon="fas fa-wand-magic-sparkles" color="cyan" />
        
        <div class="space-y-4 mt-4">
          <!-- POST /projects/{project_id}/generate -->
          <div class="border border-white/[0.08] rounded-xl overflow-hidden">
            <div class="bg-white/[0.02] p-4 border-b border-white/[0.08] flex items-center justify-between">
              <div class="flex items-center gap-3">
                <span class="px-2.5 py-1 bg-blue-500/20 rounded-lg text-blue-400 font-mono text-xs font-medium">POST</span>
                <code class="text-white/80 text-sm">/projects/{project_id}/generate</code>
              </div>
              <button 
                class="text-white/40 hover:text-white transition-colors p-2" 
                @click="toggleEndpoint('generateCode')"
              >
                <i :class="[isEndpointExpanded('generateCode') ? 'fas fa-chevron-up' : 'fas fa-chevron-down']"></i>
              </button>
            </div>
            <div v-if="isEndpointExpanded('generateCode')" class="p-4 bg-white/[0.01]">
              <p class="text-white/50 text-sm mb-4">
                Generates code based on the provided description or requirements.
              </p>
              
              <h5 class="text-cyan-400 text-sm font-medium mb-2">Request Body</h5>
              <div class="bg-[#0a0a0f] p-4 rounded-lg border border-white/[0.06] overflow-x-auto mb-4">
                <pre class="text-white/70 text-sm m-0"><code>{
  "description": "Create a login form with email and password fields",
  "type": "component",
  "options": {
    "language": "vue",
    "styling": "tailwind",
    "add_validation": true
  }
}</code></pre>
              </div>
              
              <h5 class="text-cyan-400 text-sm font-medium mb-2">Response</h5>
              <div class="bg-[#0a0a0f] p-4 rounded-lg border border-white/[0.06] overflow-x-auto">
                <pre class="text-white/70 text-sm m-0"><code>{
  "id": "gen_789ghi",
  "status": "completed",
  "files": [
    {
      "path": "components/LoginForm.vue",
      "content": "...",
      "language": "vue"
    }
  ]
}</code></pre>
              </div>
            </div>
          </div>
        </div>
      </DocsCard>

      <!-- SDK Section -->
      <DocsCard color-variant="fuchsia">
        <DocsCardHeader title="JavaScript SDK" icon="fas fa-cube" color="fuchsia" />
        <p class="text-white/50 leading-relaxed mb-6">
          For convenience, we provide a JavaScript SDK that simplifies API integration.
        </p>

        <div class="space-y-6">
          <div class="bg-white/[0.03] border border-white/[0.08] rounded-xl p-4">
            <h4 class="text-fuchsia-400 font-medium mb-2">Installation</h4>
            <div class="bg-[#0a0a0f] p-3 rounded-lg border border-white/[0.06] overflow-x-auto">
              <code class="text-white/70 text-sm">npm install @imagi/sdk</code>
            </div>
          </div>

          <div class="bg-white/[0.03] border border-white/[0.08] rounded-xl p-4">
            <h4 class="text-fuchsia-400 font-medium mb-2">Usage Example</h4>
            <div class="bg-[#0a0a0f] p-4 rounded-lg border border-white/[0.06] overflow-x-auto">
              <pre class="text-white/70 text-sm m-0"><code>import { ImagiClient } from '@imagi/sdk';

const client = new ImagiClient('YOUR_API_KEY');

// List projects
const projects = await client.projects.list();

// Create a new project
const project = await client.projects.create({
  name: 'My Awesome Project',
  description: 'Description of my project'
});</code></pre>
            </div>
          </div>
        </div>
      </DocsCard>

      <!-- Additional Resources -->
      <DocsCTASection 
        title="Need More Help?" 
        icon="fas fa-question-circle" 
        description="If you need additional assistance with the API, check our troubleshooting guide or contact our support team."
        buttonText="View Troubleshooting"
        buttonLink="/docs/troubleshooting"
        buttonIcon="fas fa-wrench"
      />
    </DocsContentWrapper>
  </DocsLayout>
</template>

<script setup>
import { ref } from 'vue'
import DocsLayout from '../layouts/DocsLayout.vue'
import { DocsContentWrapper, DocsCard, DocsCardHeader, DocsCTASection } from '../components'

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
/* Override Tailwind prose styling */
:deep(.prose ul) {
  list-style-type: none;
  padding-left: 0;
}

:deep(.prose ol) {
  padding-left: 1.75rem;
}
</style>
