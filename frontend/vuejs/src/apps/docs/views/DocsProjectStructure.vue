<template>
  <DocsLayout>
    <div class="max-w-4xl mx-auto">
      <!-- Page header with attractive styling -->
      <div class="mb-10">
        <div class="inline-block px-4 py-1.5 bg-primary-500/10 rounded-full mb-4">
          <span class="text-primary-400 font-semibold text-sm tracking-wider">DOCUMENTATION</span>
        </div>
        <h1 class="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
          Project Structure
        </h1>
        <p class="text-xl text-gray-300 leading-relaxed">
          Understanding the organization and architecture of Imagi Oasis generated projects.
        </p>
      </div>

      <!-- Attractive divider -->
      <div class="relative h-16 mb-10">
        <div class="absolute inset-x-0 h-px mx-auto w-2/3 sm:w-1/2 bg-gradient-to-r from-transparent via-primary-500/30 to-transparent animate-pulse-slow"></div>
      </div>

      <!-- Main content with sections -->
      <div class="prose prose-invert prose-lg max-w-none">
        <h2>Overview</h2>
        <p>
          Imagi Oasis generates full-stack applications with a clear, maintainable project structure.
          Understanding this structure will help you navigate, customize, and extend your application.
        </p>

        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-6 my-8">
          <h3 class="text-primary-400 mt-0">Standard Project Structure</h3>
          <div class="bg-dark-800 p-3 rounded-md overflow-x-auto font-mono text-sm">
            <pre class="text-gray-300 m-0">project-root/
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
└── docker-compose.yml  # Docker configuration</pre>
          </div>
        </div>

        <h2>Frontend Architecture</h2>
        <p>
          The frontend follows a modular architecture based on Vue.js 3 with the Composition API.
          Components are organized following atomic design principles, allowing for reusability and maintainability.
        </p>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 my-8">
          <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-6">
            <h3 class="text-primary-400 mt-0 flex items-center">
              <div class="w-8 h-8 bg-primary-500/20 rounded-full flex items-center justify-center mr-3">
                <i class="fas fa-cubes text-primary-400"></i>
              </div>
              Components
            </h3>
            <p class="text-gray-300 text-sm">
              UI building blocks organized by complexity:
            </p>
            <ul class="mt-2 space-y-2 text-sm">
              <li class="flex items-start">
                <div class="flex-shrink-0 w-5 h-5 rounded-full bg-primary-500/20 flex items-center justify-center mr-2 mt-0.5">
                  <i class="fas fa-atom text-primary-400 text-xs"></i>
                </div>
                <span><code class="text-primary-400">atoms/</code> - Basic UI elements (buttons, inputs)</span>
              </li>
              <li class="flex items-start">
                <div class="flex-shrink-0 w-5 h-5 rounded-full bg-primary-500/20 flex items-center justify-center mr-2 mt-0.5">
                  <i class="fas fa-puzzle-piece text-primary-400 text-xs"></i>
                </div>
                <span><code class="text-primary-400">molecules/</code> - Combinations of atoms (form fields, cards)</span>
              </li>
              <li class="flex items-start">
                <div class="flex-shrink-0 w-5 h-5 rounded-full bg-primary-500/20 flex items-center justify-center mr-2 mt-0.5">
                  <i class="fas fa-microscope text-primary-400 text-xs"></i>
                </div>
                <span><code class="text-primary-400">organisms/</code> - Complex UI sections (forms, headers)</span>
              </li>
              <li class="flex items-start">
                <div class="flex-shrink-0 w-5 h-5 rounded-full bg-primary-500/20 flex items-center justify-center mr-2 mt-0.5">
                  <i class="fas fa-clone text-primary-400 text-xs"></i>
                </div>
                <span><code class="text-primary-400">templates/</code> - Page layouts and structures</span>
              </li>
            </ul>
          </div>
          
          <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-6">
            <h3 class="text-primary-400 mt-0 flex items-center">
              <div class="w-8 h-8 bg-blue-500/20 rounded-full flex items-center justify-center mr-3">
                <i class="fas fa-sitemap text-blue-400"></i>
              </div>
              State Management
            </h3>
            <p class="text-gray-300 text-sm">
              Pinia stores are organized by feature:
            </p>
            <ul class="mt-2 space-y-2 text-sm">
              <li class="flex items-start">
                <div class="flex-shrink-0 w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center mr-2 mt-0.5">
                  <i class="fas fa-user-shield text-blue-400 text-xs"></i>
                </div>
                <span><code class="text-blue-400">auth.ts</code> - Authentication state</span>
              </li>
              <li class="flex items-start">
                <div class="flex-shrink-0 w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center mr-2 mt-0.5">
                  <i class="fas fa-database text-blue-400 text-xs"></i>
                </div>
                <span><code class="text-blue-400">entities/</code> - Data models (users, products, etc.)</span>
              </li>
              <li class="flex items-start">
                <div class="flex-shrink-0 w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center mr-2 mt-0.5">
                  <i class="fas fa-cog text-blue-400 text-xs"></i>
                </div>
                <span><code class="text-blue-400">ui.ts</code> - UI state (theme, layout preferences)</span>
              </li>
            </ul>
          </div>
        </div>

        <h2>Backend Architecture</h2>
        <p>
          The backend follows Django and Django REST Framework best practices, with a clear separation of concerns.
        </p>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 my-8">
          <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-6">
            <h3 class="text-green-400 mt-0 flex items-center">
              <div class="w-8 h-8 bg-green-500/20 rounded-full flex items-center justify-center mr-3">
                <i class="fas fa-database text-green-400"></i>
              </div>
              Data Models
            </h3>
            <p class="text-gray-300 text-sm">
              Django models defined with proper relationships:
            </p>
            <div class="mt-3 bg-dark-800 p-3 rounded-md overflow-x-auto">
              <pre class="text-sm text-gray-300 m-0"><code class="language-python">class Project(models.Model):
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
          
          <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-6">
            <h3 class="text-green-400 mt-0 flex items-center">
              <div class="w-8 h-8 bg-green-500/20 rounded-full flex items-center justify-center mr-3">
                <i class="fas fa-exchange-alt text-green-400"></i>
              </div>
              API Endpoints
            </h3>
            <p class="text-gray-300 text-sm">
              RESTful APIs using Django REST Framework:
            </p>
            <div class="mt-3 bg-dark-800 p-3 rounded-md overflow-x-auto">
              <pre class="text-sm text-gray-300 m-0"><code class="language-python">class ProjectViewSet(viewsets.ModelViewSet):
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

        <h2>Customizing Your Project</h2>
        <p>
          Imagi Oasis generates code that follows best practices, but you have complete freedom to customize and extend it to meet your specific needs.
        </p>

        <div class="bg-primary-500/10 border border-primary-500/20 rounded-xl p-6 my-8">
          <h3 class="text-primary-400 mt-0 flex items-center">
            <i class="fas fa-lightbulb mr-2"></i>
            Best Practices for Customization
          </h3>
          <ul class="mb-0">
            <li>Keep components modular and focused on a single responsibility</li>
            <li>Follow the established naming conventions for consistency</li>
            <li>Add comments to explain complex logic or business rules</li>
            <li>When adding new features, create appropriate tests</li>
            <li>Consider performance implications when modifying database models</li>
          </ul>
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

/* Override Tailwind prose styling for lists */
:deep(.prose ul) {
  list-style-type: none;
  padding-left: 0;
}
</style> 