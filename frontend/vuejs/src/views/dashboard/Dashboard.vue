<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <div class="container">
        <h1>Dashboard</h1>
        <p class="welcome-message" v-if="user">Welcome back, {{ user.username }}!</p>
      </div>
    </header>

    <main class="container">
      <div class="row">
        <!-- Quick Stats -->
        <div class="col-md-4">
          <div class="stats-card">
            <div class="stats-icon">
              <i class="fas fa-project-diagram"></i>
            </div>
            <div class="stats-content">
              <h3>{{ projects.length }}</h3>
              <p>Total Projects</p>
            </div>
          </div>
        </div>
        
        <div class="col-md-4">
          <div class="stats-card">
            <div class="stats-icon">
              <i class="fas fa-clock"></i>
            </div>
            <div class="stats-content">
              <h3>{{ activeProjects.length }}</h3>
              <p>Active Projects</p>
            </div>
          </div>
        </div>
        
        <div class="col-md-4">
          <div class="stats-card">
            <div class="stats-icon">
              <i class="fas fa-check-circle"></i>
            </div>
            <div class="stats-content">
              <h3>{{ completedProjects.length }}</h3>
              <p>Completed Projects</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Projects -->
      <section class="recent-projects mt-5">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2>Recent Projects</h2>
          <router-link to="/projects" class="btn btn-primary">
            View All Projects
          </router-link>
        </div>

        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="error" class="alert alert-danger" role="alert">
          {{ error }}
        </div>

        <div v-else-if="projects.length === 0" class="text-center py-5">
          <div class="empty-state">
            <i class="fas fa-folder-open fa-3x mb-3"></i>
            <h3>No Projects Yet</h3>
            <p>Create your first project to get started</p>
            <router-link to="/projects/new" class="btn btn-primary">
              Create Project
            </router-link>
          </div>
        </div>

        <div v-else class="row">
          <div v-for="project in recentProjects" :key="project.id" class="col-md-6 col-lg-4 mb-4">
            <div class="project-card">
              <div class="project-header">
                <h3>{{ project.name }}</h3>
                <span :class="['status-badge', project.status]">
                  {{ project.status }}
                </span>
              </div>
              <p class="project-description">{{ project.description }}</p>
              <div class="project-footer">
                <span class="project-date">
                  <i class="far fa-calendar-alt"></i>
                  {{ formatDate(project.created_at) }}
                </span>
                <router-link :to="'/projects/' + project.id" class="btn btn-sm btn-outline-primary">
                  View Details
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'DashboardView',
  
  setup() {
    const store = useStore()
    
    const loading = computed(() => store.state.projects.loading)
    const error = computed(() => store.state.projects.error)
    const projects = computed(() => store.state.projects.projects)
    const user = computed(() => store.state.auth.user)
    
    const activeProjects = computed(() => 
      projects.value.filter(p => p.status === 'active')
    )
    
    const completedProjects = computed(() => 
      projects.value.filter(p => p.status === 'completed')
    )
    
    const recentProjects = computed(() => 
      [...projects.value]
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .slice(0, 6)
    )
    
    const formatDate = (date) => {
      return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }
    
    onMounted(async () => {
      try {
        await store.dispatch('projects/fetchProjects')
      } catch (err) {
        console.error('Failed to fetch projects:', err)
      }
    })
    
    return {
      loading,
      error,
      projects,
      user,
      activeProjects,
      completedProjects,
      recentProjects,
      formatDate
    }
  }
}
</script>

<style scoped>
.dashboard-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem 0;
  margin-bottom: 2rem;
}

.welcome-message {
  margin: 0.5rem 0 0;
  opacity: 0.9;
}

.stats-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stats-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.stats-content {
  h3 {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0;
  }
  
  p {
    margin: 0;
    color: #6c757d;
    font-size: 0.875rem;
  }
}

.project-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  
  h3 {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0;
  }
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: capitalize;
  
  &.active {
    background: rgba(40, 167, 69, 0.1);
    color: #28a745;
  }
  
  &.completed {
    background: rgba(23, 162, 184, 0.1);
    color: #17a2b8;
  }
  
  &.pending {
    background: rgba(255, 193, 7, 0.1);
    color: #ffc107;
  }
}

.project-description {
  color: #6c757d;
  font-size: 0.875rem;
  margin-bottom: 1rem;
  flex-grow: 1;
}

.project-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  
  .project-date {
    color: #6c757d;
    font-size: 0.875rem;
    
    i {
      margin-right: 0.5rem;
    }
  }
}

.empty-state {
  color: #6c757d;
  
  i {
    color: #dee2e6;
  }
  
  h3 {
    margin: 1rem 0 0.5rem;
  }
  
  p {
    margin-bottom: 1.5rem;
  }
}
</style> 