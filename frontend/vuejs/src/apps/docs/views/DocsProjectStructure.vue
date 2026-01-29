<template>
  <DocsLayout>
    <DocsContentWrapper
      title="Project Structure"
      description="Understanding the organization and architecture of Imagi generated projects."
      badge-text="ARCHITECTURE"
    >
      <!-- Overview -->
      <DocsCard color-variant="primary">
        <DocsCardHeader title="Overview" color="primary" />
        <p class="text-gray-300 leading-relaxed">
          Imagi generates full-stack applications with a clear, maintainable project structure.
          Understanding this structure will help you navigate, customize, and extend your application.
        </p>
      </DocsCard>

      <!-- Project Structure -->
      <DocsCard color-variant="blue">
        <DocsCardHeader title="Standard Project Structure" color="blue" />
        <div class="bg-dark-800/60 border border-white/10 rounded-xl p-4 mt-4 overflow-x-auto">
          <pre class="text-gray-300 text-sm leading-relaxed"><code>project-root/
├── frontend/           # Vue.js frontend application
│   ├── public/         # Static assets
│   ├── src/
│   │   ├── assets/     # Images, fonts, etc.
│   │   ├── components/ # Vue components
│   │   ├── views/      # Vue views (pages)
│   │   ├── router/     # Vue Router configuration
│   │   ├── store/      # Pinia store modules
│   │   ├── services/   # API service modules
│   │   ├── types/      # TypeScript type definitions
│   │   ├── utils/      # Utility functions
│   │   ├── App.vue     # Root component
│   │   └── main.ts     # Application entry point
│   └── package.json    # Frontend dependencies
│
├── backend/            # Django backend application
│   ├── api/            # API endpoints and serializers
│   ├── core/           # Core application settings
│   ├── models/         # Data models
│   ├── services/       # Business logic services
│   ├── utils/          # Utility functions
│   ├── tests/          # Backend tests
│   └── requirements.txt # Backend dependencies
│
├── README.md           # Project documentation
└── docker-compose.yml  # Docker configuration</code></pre>
        </div>
      </DocsCard>

      <!-- Frontend Architecture -->
      <DocsCard color-variant="violet">
        <DocsCardHeader title="Frontend Architecture" color="violet" />
        <p class="text-gray-300 leading-relaxed mb-6">
          The frontend follows a modular architecture based on Vue.js 3 with the Composition API.
          Components are organized following atomic design principles, allowing for reusability and maintainability.
        </p>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Components Card -->
          <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm">
            <h3 class="text-white font-semibold mb-4">Components</h3>
            <p class="text-gray-300 text-sm mb-4">
              UI building blocks organized by complexity:
            </p>
            <ul class="space-y-3">
              <li>
                <code class="text-white text-xs">atoms/</code>
                <p class="text-gray-400 text-xs mt-0.5">Basic UI elements (buttons, inputs)</p>
              </li>
              <li>
                <code class="text-white text-xs">molecules/</code>
                <p class="text-gray-400 text-xs mt-0.5">Combinations of atoms (form fields, cards)</p>
              </li>
              <li>
                <code class="text-white text-xs">organisms/</code>
                <p class="text-gray-400 text-xs mt-0.5">Complex UI sections (forms, headers)</p>
              </li>
              <li>
                <code class="text-white text-xs">templates/</code>
                <p class="text-gray-400 text-xs mt-0.5">Page layouts and structures</p>
              </li>
            </ul>
          </div>
          
          <!-- State Management Card -->
          <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm">
            <h3 class="text-white font-semibold mb-4">State Management</h3>
            <p class="text-gray-300 text-sm mb-4">
              Pinia stores are organized by feature:
            </p>
            <ul class="space-y-3">
              <li>
                <code class="text-white text-xs">auth.ts</code>
                <p class="text-gray-400 text-xs mt-0.5">Authentication state</p>
              </li>
              <li>
                <code class="text-white text-xs">entities/</code>
                <p class="text-gray-400 text-xs mt-0.5">Data models (users, products, etc.)</p>
              </li>
              <li>
                <code class="text-white text-xs">ui.ts</code>
                <p class="text-gray-400 text-xs mt-0.5">UI state (theme, layout preferences)</p>
              </li>
            </ul>
          </div>
        </div>
      </DocsCard>

      <!-- Backend Architecture -->
      <DocsCard color-variant="cyan">
        <DocsCardHeader title="Backend Architecture" color="cyan" />
        <p class="text-gray-300 leading-relaxed mb-6">
          The backend follows Django and Django REST Framework best practices, with a clear separation of concerns.
        </p>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Data Models Card -->
          <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm">
            <h3 class="text-white font-semibold mb-4">Data Models</h3>
            <p class="text-gray-300 text-sm mb-4">
              Django models defined with proper relationships:
            </p>
            <div class="bg-dark-800/60 border border-white/10 rounded-lg p-3 overflow-x-auto">
              <pre class="text-sm text-gray-300 leading-relaxed"><code class="language-python">class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        'auth.User', 
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name</code></pre>
            </div>
          </div>
          
          <!-- API Endpoints Card -->
          <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm">
            <h3 class="text-white font-semibold mb-4">API Endpoints</h3>
            <p class="text-gray-300 text-sm mb-4">
              RESTful APIs using Django REST Framework:
            </p>
            <div class="bg-dark-800/60 border border-white/10 rounded-lg p-3 overflow-x-auto">
              <pre class="text-sm text-gray-300 leading-relaxed"><code class="language-python">class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Project.objects.filter(
            owner=self.request.user
        )
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)</code></pre>
            </div>
          </div>
        </div>
      </DocsCard>
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

/* Override Tailwind prose styling for lists */
:deep(.prose ul) {
  list-style-type: none;
  padding-left: 0;
}
</style> 