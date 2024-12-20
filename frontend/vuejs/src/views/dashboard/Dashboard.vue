<template>
  <div class="dashboard">
    <!-- Welcome Section -->
    <div class="welcome-section">
      <div>
        <h1>Welcome back, {{ user?.name || 'User' }}!</h1>
        <p class="text-muted">Here's what's happening with your projects today.</p>
      </div>
      <router-link to="/dashboard/projects/new" class="btn btn-primary">
        <i class="fas fa-plus"></i>
        New Project
      </router-link>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stats-card">
        <div class="stats-icon bg-primary">
          <i class="fas fa-project-diagram"></i>
        </div>
        <div class="stats-info">
          <h3>Total Projects</h3>
          <p class="stats-number">{{ totalProjects }}</p>
          <p class="stats-trend" :class="projectTrend.type">
            <i :class="projectTrend.icon"></i>
            {{ projectTrend.value }}% from last month
          </p>
        </div>
      </div>

      <div class="stats-card">
        <div class="stats-icon bg-success">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="stats-info">
          <h3>Completed</h3>
          <p class="stats-number">{{ completedProjects }}</p>
          <p class="stats-trend" :class="completedTrend.type">
            <i :class="completedTrend.icon"></i>
            {{ completedTrend.value }}% from last month
          </p>
        </div>
      </div>

      <div class="stats-card">
        <div class="stats-icon bg-warning">
          <i class="fas fa-clock"></i>
        </div>
        <div class="stats-info">
          <h3>In Progress</h3>
          <p class="stats-number">{{ inProgressProjects }}</p>
          <p class="stats-trend" :class="inProgressTrend.type">
            <i :class="inProgressTrend.icon"></i>
            {{ inProgressTrend.value }}% from last month
          </p>
        </div>
      </div>

      <div class="stats-card">
        <div class="stats-icon bg-info">
          <i class="fas fa-code-branch"></i>
        </div>
        <div class="stats-info">
          <h3>Deployments</h3>
          <p class="stats-number">{{ totalDeployments }}</p>
          <p class="stats-trend" :class="deploymentTrend.type">
            <i :class="deploymentTrend.icon"></i>
            {{ deploymentTrend.value }}% from last month
          </p>
        </div>
      </div>
    </div>

    <!-- Recent Projects -->
    <div class="section">
      <div class="section-header">
        <h2>Recent Projects</h2>
        <router-link to="/dashboard/projects" class="btn btn-outline-primary">
          View All
        </router-link>
      </div>

      <div class="projects-grid">
        <div 
          v-for="project in recentProjects" 
          :key="project.id"
          class="project-card"
        >
          <div class="project-header">
            <h3>{{ project.name }}</h3>
            <span :class="['status-badge', project.status]">
              {{ project.status }}
            </span>
          </div>
          <p class="project-description">{{ project.description }}</p>
          <div class="project-meta">
            <span class="meta-item">
              <i class="fas fa-calendar"></i>
              {{ formatDate(project.updatedAt) }}
            </span>
            <span class="meta-item">
              <i class="fas fa-code-branch"></i>
              {{ project.deployments }} deployments
            </span>
          </div>
          <div class="project-actions">
            <router-link 
              :to="`/dashboard/projects/${project.id}`"
              class="btn btn-outline-primary btn-sm"
            >
              View Details
            </router-link>
            <button 
              class="btn btn-outline-danger btn-sm"
              @click="deleteProject(project.id)"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Activity Timeline -->
    <div class="section">
      <div class="section-header">
        <h2>Recent Activity</h2>
      </div>

      <div class="timeline">
        <div 
          v-for="activity in recentActivity" 
          :key="activity.id"
          class="timeline-item"
        >
          <div class="timeline-icon" :class="activity.type">
            <i :class="activity.icon"></i>
          </div>
          <div class="timeline-content">
            <p class="activity-text">{{ activity.text }}</p>
            <span class="activity-time">{{ formatTime(activity.time) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import { format } from 'date-fns'
import { formatDistanceToNow } from 'date-fns'

export default {
  name: 'Dashboard',
  data() {
    return {
      totalProjects: 12,
      completedProjects: 8,
      inProgressProjects: 4,
      totalDeployments: 24,
      projectTrend: {
        type: 'positive',
        value: 12,
        icon: 'fas fa-arrow-up'
      },
      completedTrend: {
        type: 'positive',
        value: 18,
        icon: 'fas fa-arrow-up'
      },
      inProgressTrend: {
        type: 'negative',
        value: 5,
        icon: 'fas fa-arrow-down'
      },
      deploymentTrend: {
        type: 'positive',
        value: 24,
        icon: 'fas fa-arrow-up'
      },
      recentProjects: [
        {
          id: 1,
          name: 'E-commerce Website',
          description: 'Modern e-commerce platform with AI-powered recommendations',
          status: 'active',
          updatedAt: new Date(),
          deployments: 5
        },
        {
          id: 2,
          name: 'Portfolio Site',
          description: 'Personal portfolio website with blog functionality',
          status: 'completed',
          updatedAt: new Date(Date.now() - 86400000),
          deployments: 3
        }
      ],
      recentActivity: [
        {
          id: 1,
          type: 'create',
          icon: 'fas fa-plus',
          text: 'Created new project "Landing Page"',
          time: new Date()
        },
        {
          id: 2,
          type: 'deploy',
          icon: 'fas fa-rocket',
          text: 'Deployed "E-commerce Website" to production',
          time: new Date(Date.now() - 3600000)
        }
      ]
    }
  },
  computed: {
    ...mapGetters({
      user: 'auth/user'
    })
  },
  methods: {
    ...mapActions({
      fetchProjects: 'projects/fetchProjects'
    }),
    formatDate(date) {
      return format(date, 'MMM d, yyyy')
    },
    formatTime(date) {
      return formatDistanceToNow(date, { addSuffix: true })
    },
    async deleteProject(projectId) {
      if (confirm('Are you sure you want to delete this project?')) {
        try {
          await this.$store.dispatch('projects/deleteProject', projectId)
          this.recentProjects = this.recentProjects.filter(p => p.id !== projectId)
        } catch (error) {
          console.error('Failed to delete project:', error)
        }
      }
    }
  },
  async mounted() {
    try {
      await this.fetchProjects()
    } catch (error) {
      console.error('Failed to fetch projects:', error)
    }
  }
}
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

h1 {
  font-size: 2rem;
  color: #2d3748;
  margin: 0;
}

.text-muted {
  color: #718096;
  margin: 0.5rem 0 0;
}

/* Stats Cards */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stats-card {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.stats-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stats-icon i {
  font-size: 1.5rem;
}

.bg-primary {
  background-color: #6366f1;
}

.bg-success {
  background-color: #10b981;
}

.bg-warning {
  background-color: #f59e0b;
}

.bg-info {
  background-color: #3b82f6;
}

.stats-info h3 {
  font-size: 0.875rem;
  color: #718096;
  margin: 0;
}

.stats-number {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0.5rem 0;
}

.stats-trend {
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.stats-trend.positive {
  color: #10b981;
}

.stats-trend.negative {
  color: #ef4444;
}

/* Section Styles */
.section {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  font-size: 1.25rem;
  color: #2d3748;
  margin: 0;
}

/* Projects Grid */
.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.project-card {
  background: #f8fafc;
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.project-header h3 {
  font-size: 1.125rem;
  color: #2d3748;
  margin: 0;
}

.status-badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 1rem;
  text-transform: capitalize;
}

.status-badge.active {
  background-color: #dbeafe;
  color: #3b82f6;
}

.status-badge.completed {
  background-color: #dcfce7;
  color: #10b981;
}

.project-description {
  color: #718096;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.project-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #718096;
  font-size: 0.875rem;
}

.project-actions {
  display: flex;
  gap: 0.5rem;
}

/* Timeline */
.timeline {
  position: relative;
  padding-left: 2rem;
}

.timeline-item {
  position: relative;
  padding-bottom: 1.5rem;
}

.timeline-item:not(:last-child)::before {
  content: '';
  position: absolute;
  left: -1.5rem;
  top: 2rem;
  bottom: 0;
  width: 2px;
  background-color: #e2e8f0;
}

.timeline-icon {
  position: absolute;
  left: -2rem;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  z-index: 1;
}

.timeline-icon.create {
  background-color: #6366f1;
}

.timeline-icon.deploy {
  background-color: #10b981;
}

.timeline-content {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 0.5rem;
}

.activity-text {
  color: #4a5568;
  margin: 0;
}

.activity-time {
  font-size: 0.875rem;
  color: #718096;
}

@media (max-width: 768px) {
  .welcome-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .projects-grid {
    grid-template-columns: 1fr;
  }
}
</style> 