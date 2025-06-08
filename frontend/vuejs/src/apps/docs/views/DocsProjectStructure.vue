<template>
  <DocsLayout>
    <DocsContentWrapper
      title="Project Structure"
      description="Understanding the organization and architecture of Imagi Oasis generated projects."
      badge-text="ARCHITECTURE"
    >
      <!-- Overview -->
      <DocsCard color-variant="primary">
        <DocsCardHeader title="Overview" icon="fas fa-sitemap" color="primary" />
        <p class="text-gray-300 leading-relaxed">
          Imagi Oasis generates full-stack applications with a clear, maintainable project structure.
          Understanding this structure will help you navigate, customize, and extend your application.
        </p>
      </DocsCard>

      <!-- Project Structure -->
      <DocsCard color-variant="blue">
        <DocsCardHeader title="Standard Project Structure" icon="fas fa-folder-tree" color="blue" />
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
        <DocsCardHeader title="Frontend Architecture" icon="fas fa-layer-group" color="violet" />
        <p class="text-gray-300 leading-relaxed mb-6">
          The frontend follows a modular architecture based on Vue.js 3 with the Composition API.
          Components are organized following atomic design principles, allowing for reusability and maintainability.
        </p>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Components Card -->
          <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm">
            <div class="flex items-center mb-4">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-400/20 to-purple-400/20 border border-violet-400/20 flex items-center justify-center mr-3">
                <i class="fas fa-cubes text-violet-300"></i>
              </div>
              <h3 class="text-white font-semibold">Components</h3>
            </div>
            <p class="text-gray-300 text-sm mb-4">
              UI building blocks organized by complexity:
            </p>
            <ul class="space-y-3">
              <li class="flex items-start gap-3">
                <div class="w-6 h-6 rounded-lg bg-gradient-to-br from-violet-400/20 to-purple-400/20 border border-violet-400/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <i class="fas fa-atom text-violet-300 text-xs"></i>
                </div>
                <div>
                  <code class="text-violet-300 text-xs">atoms/</code>
                  <p class="text-gray-400 text-xs mt-0.5">Basic UI elements (buttons, inputs)</p>
                </div>
              </li>
              <li class="flex items-start gap-3">
                <div class="w-6 h-6 rounded-lg bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <i class="fas fa-puzzle-piece text-blue-300 text-xs"></i>
                </div>
                <div>
                  <code class="text-blue-300 text-xs">molecules/</code>
                  <p class="text-gray-400 text-xs mt-0.5">Combinations of atoms (form fields, cards)</p>
                </div>
              </li>
              <li class="flex items-start gap-3">
                <div class="w-6 h-6 rounded-lg bg-gradient-to-br from-cyan-400/20 to-blue-400/20 border border-cyan-400/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <i class="fas fa-microscope text-cyan-300 text-xs"></i>
                </div>
                <div>
                  <code class="text-cyan-300 text-xs">organisms/</code>
                  <p class="text-gray-400 text-xs mt-0.5">Complex UI sections (forms, headers)</p>
                </div>
              </li>
              <li class="flex items-start gap-3">
                <div class="w-6 h-6 rounded-lg bg-gradient-to-br from-emerald-400/20 to-green-400/20 border border-emerald-400/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <i class="fas fa-clone text-emerald-300 text-xs"></i>
                </div>
                <div>
                  <code class="text-emerald-300 text-xs">templates/</code>
                  <p class="text-gray-400 text-xs mt-0.5">Page layouts and structures</p>
                </div>
              </li>
            </ul>
          </div>
          
          <!-- State Management Card -->
          <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm">
            <div class="flex items-center mb-4">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center mr-3">
                <i class="fas fa-sitemap text-blue-300"></i>
              </div>
              <h3 class="text-white font-semibold">State Management</h3>
            </div>
            <p class="text-gray-300 text-sm mb-4">
              Pinia stores are organized by feature:
            </p>
            <ul class="space-y-3">
              <li class="flex items-start gap-3">
                <div class="w-6 h-6 rounded-lg bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <i class="fas fa-user-shield text-blue-300 text-xs"></i>
                </div>
                <div>
                  <code class="text-blue-300 text-xs">auth.ts</code>
                  <p class="text-gray-400 text-xs mt-0.5">Authentication state</p>
                </div>
              </li>
              <li class="flex items-start gap-3">
                <div class="w-6 h-6 rounded-lg bg-gradient-to-br from-cyan-400/20 to-blue-400/20 border border-cyan-400/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <i class="fas fa-database text-cyan-300 text-xs"></i>
                </div>
                <div>
                  <code class="text-cyan-300 text-xs">entities/</code>
                  <p class="text-gray-400 text-xs mt-0.5">Data models (users, products, etc.)</p>
                </div>
              </li>
              <li class="flex items-start gap-3">
                <div class="w-6 h-6 rounded-lg bg-gradient-to-br from-violet-400/20 to-purple-400/20 border border-violet-400/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <i class="fas fa-cog text-violet-300 text-xs"></i>
                </div>
                <div>
                  <code class="text-violet-300 text-xs">ui.ts</code>
                  <p class="text-gray-400 text-xs mt-0.5">UI state (theme, layout preferences)</p>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </DocsCard>

      <!-- Backend Architecture -->
      <DocsCard color-variant="cyan">
        <DocsCardHeader title="Backend Architecture" icon="fas fa-server" color="cyan" />
        <p class="text-gray-300 leading-relaxed mb-6">
          The backend follows Django and Django REST Framework best practices, with a clear separation of concerns.
        </p>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Data Models Card -->
          <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm">
            <div class="flex items-center mb-4">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400/20 to-green-400/20 border border-emerald-400/20 flex items-center justify-center mr-3">
                <i class="fas fa-database text-emerald-300"></i>
              </div>
              <h3 class="text-white font-semibold">Data Models</h3>
            </div>
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
            <div class="flex items-center mb-4">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400/20 to-blue-400/20 border border-cyan-400/20 flex items-center justify-center mr-3">
                <i class="fas fa-exchange-alt text-cyan-300"></i>
              </div>
              <h3 class="text-white font-semibold">API Endpoints</h3>
            </div>
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

      <!-- Best Practices -->
      <DocsCard color-variant="primary">
        <DocsCardHeader title="Best Practices for Customization" icon="fas fa-lightbulb" color="primary" />
        <p class="text-gray-300 leading-relaxed mb-6">
          Imagi Oasis generates code that follows best practices, but you have complete freedom to customize and extend it to meet your specific needs.
        </p>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <ul class="space-y-3">
            <DocsListItem icon="fas fa-puzzle-piece" color="primary" size="sm">
              Keep components modular and focused on a single responsibility
            </DocsListItem>
            <DocsListItem icon="fas fa-tag" color="blue" size="sm">
              Follow the established naming conventions for consistency
            </DocsListItem>
            <DocsListItem icon="fas fa-comment" color="cyan" size="sm">
              Add comments to explain complex logic or business rules
            </DocsListItem>
          </ul>
          
          <ul class="space-y-3">
            <DocsListItem icon="fas fa-flask" color="violet" size="sm">
              When adding new features, create appropriate tests
            </DocsListItem>
            <DocsListItem icon="fas fa-tachometer-alt" color="emerald" size="sm">
              Consider performance implications when modifying database models
            </DocsListItem>
            <DocsListItem icon="fas fa-shield-alt" color="orange" size="sm">
              Maintain security best practices in all customizations
            </DocsListItem>
          </ul>
        </div>
      </DocsCard>

      <!-- CTA -->
      <DocsCTASection 
        title="Ready to Build?" 
        icon="fas fa-rocket" 
        description="Now that you understand the project structure, create your first application and explore the generated code."
        buttonText="Create Project"
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

/* Override Tailwind prose styling for lists */
:deep(.prose ul) {
  list-style-type: none;
  padding-left: 0;
}
</style> 