<template>
  <div class="project-details">
    <header class="page-header">
      <div class="container">
        <div class="d-flex justify-content-between align-items-start">
          <div>
            <div class="d-flex align-items-center gap-3">
              <router-link to="/projects" class="btn btn-link text-white p-0">
                <i class="fas fa-arrow-left"></i>
              </router-link>
              <h1>{{ project?.name || 'Loading...' }}</h1>
            </div>
            <p class="text-light mt-2 mb-0" v-if="project">{{ project.description }}</p>
          </div>
          <div class="d-flex gap-2" v-if="project">
            <button class="btn btn-light" @click="showEditModal = true">
              <i class="fas fa-edit"></i> Edit Project
            </button>
            <button class="btn btn-danger" @click="confirmDelete">
              <i class="fas fa-trash"></i> Delete Project
            </button>
          </div>
        </div>
      </div>
    </header>

    <main class="container py-4">
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>

      <!-- Project Content -->
      <div v-else-if="project" class="row g-4">
        <!-- Project Overview -->
        <div class="col-md-8">
          <div class="content-card">
            <div class="d-flex justify-content-between align-items-center mb-4">
              <h2>Project Overview</h2>
              <span :class="['status-badge', project.status]">
                {{ project.status }}
              </span>
            </div>

            <div class="row g-4">
              <div class="col-md-6">
                <div class="info-group">
                  <label>Created</label>
                  <div class="d-flex align-items-center">
                    <i class="far fa-calendar-alt text-muted me-2"></i>
                    <span>{{ formatDate(project.created_at) }}</span>
                  </div>
                </div>
              </div>

              <div class="col-md-6">
                <div class="info-group">
                  <label>Last Updated</label>
                  <div class="d-flex align-items-center">
                    <i class="far fa-clock text-muted me-2"></i>
                    <span>{{ formatDate(project.updated_at) }}</span>
                  </div>
                </div>
              </div>

              <div class="col-12">
                <div class="info-group">
                  <label>Description</label>
                  <p class="text-muted mb-0">{{ project.description }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Project Timeline -->
          <div class="content-card mt-4">
            <h2>Activity Timeline</h2>
            <div class="timeline">
              <div class="timeline-item" v-for="activity in projectActivities" :key="activity.id">
                <div class="timeline-icon" :class="activity.type">
                  <i :class="getActivityIcon(activity.type)"></i>
                </div>
                <div class="timeline-content">
                  <div class="d-flex justify-content-between align-items-start">
                    <strong>{{ activity.title }}</strong>
                    <small class="text-muted">{{ formatDate(activity.timestamp) }}</small>
                  </div>
                  <p class="mb-0">{{ activity.description }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Project Stats & Settings -->
        <div class="col-md-4">
          <!-- Quick Stats -->
          <div class="content-card">
            <h3>Project Statistics</h3>
            <div class="stats-list">
              <div class="stat-item">
                <div class="stat-icon">
                  <i class="fas fa-tasks"></i>
                </div>
                <div class="stat-content">
                  <span class="stat-value">{{ project.tasks_count || 0 }}</span>
                  <span class="stat-label">Total Tasks</span>
                </div>
              </div>

              <div class="stat-item">
                <div class="stat-icon">
                  <i class="fas fa-check-circle"></i>
                </div>
                <div class="stat-content">
                  <span class="stat-value">{{ project.completed_tasks_count || 0 }}</span>
                  <span class="stat-label">Completed Tasks</span>
                </div>
              </div>

              <div class="stat-item">
                <div class="stat-icon">
                  <i class="fas fa-clock"></i>
                </div>
                <div class="stat-content">
                  <span class="stat-value">{{ getDaysActive(project.created_at) }}</span>
                  <span class="stat-label">Days Active</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Project Settings -->
          <div class="content-card mt-4">
            <h3>Project Settings</h3>
            <form @submit.prevent="updateSettings">
              <div class="mb-3">
                <label class="form-label">Project Visibility</label>
                <select v-model="settings.visibility" class="form-select">
                  <option value="private">Private</option>
                  <option value="team">Team Only</option>
                  <option value="public">Public</option>
                </select>
              </div>

              <div class="mb-3">
                <label class="form-label">Notifications</label>
                <div class="form-check">
                  <input
                    type="checkbox"
                    id="taskUpdates"
                    v-model="settings.notifications.taskUpdates"
                    class="form-check-input"
                  />
                  <label class="form-check-label" for="taskUpdates">
                    Task updates
                  </label>
                </div>
                <div class="form-check">
                  <input
                    type="checkbox"
                    id="comments"
                    v-model="settings.notifications.comments"
                    class="form-check-input"
                  />
                  <label class="form-check-label" for="comments">
                    New comments
                  </label>
                </div>
              </div>

              <button type="submit" class="btn btn-primary w-100" :disabled="settingsLoading">
                <span v-if="settingsLoading" class="spinner-border spinner-border-sm me-1"></span>
                Save Settings
              </button>
            </form>
          </div>
        </div>
      </div>
    </main>

    <!-- Edit Project Modal -->
    <div class="modal" :class="{ 'show d-block': showEditModal }" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit Project</h5>
            <button type="button" class="btn-close" @click="closeEditModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="handleEdit">
              <div class="mb-3">
                <label for="projectName" class="form-label">Project Name</label>
                <input
                  type="text"
                  class="form-control"
                  id="projectName"
                  v-model="editForm.name"
                  required
                />
              </div>

              <div class="mb-3">
                <label for="projectDescription" class="form-label">Description</label>
                <textarea
                  class="form-control"
                  id="projectDescription"
                  v-model="editForm.description"
                  rows="3"
                  required
                ></textarea>
              </div>

              <div class="mb-3">
                <label for="projectStatus" class="form-label">Status</label>
                <select class="form-select" id="projectStatus" v-model="editForm.status" required>
                  <option value="pending">Pending</option>
                  <option value="active">Active</option>
                  <option value="completed">Completed</option>
                </select>
              </div>

              <div class="alert alert-danger" v-if="editError">
                {{ editError }}
              </div>

              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" @click="closeEditModal">
                  Cancel
                </button>
                <button type="submit" class="btn btn-primary" :disabled="editLoading">
                  <span v-if="editLoading" class="spinner-border spinner-border-sm me-1"></span>
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal" :class="{ 'show d-block': showDeleteModal }" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Delete Project</h5>
            <button type="button" class="btn-close" @click="closeDeleteModal"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete this project? This action cannot be undone.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeDeleteModal">
              Cancel
            </button>
            <button type="button" class="btn btn-danger" @click="handleDelete" :disabled="deleteLoading">
              <span v-if="deleteLoading" class="spinner-border spinner-border-sm me-1"></span>
              Delete Project
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Backdrop -->
    <div class="modal-backdrop fade show" v-if="showEditModal || showDeleteModal"></div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'ProjectDetails',
  
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    
    // State
    const showEditModal = ref(false)
    const showDeleteModal = ref(false)
    const editError = ref(null)
    const editLoading = ref(false)
    const deleteLoading = ref(false)
    const settingsLoading = ref(false)
    
    const editForm = ref({
      name: '',
      description: '',
      status: ''
    })
    
    const settings = ref({
      visibility: 'private',
      notifications: {
        taskUpdates: true,
        comments: true
      }
    })
    
    // Mock project activities (replace with real data from API)
    const projectActivities = ref([
      {
        id: 1,
        type: 'create',
        title: 'Project Created',
        description: 'Project was created',
        timestamp: new Date().toISOString()
      },
      {
        id: 2,
        type: 'update',
        title: 'Status Updated',
        description: 'Project status changed to Active',
        timestamp: new Date().toISOString()
      }
    ])
    
    // Computed
    const loading = computed(() => store.state.projects.loading)
    const error = computed(() => store.state.projects.error)
    const project = computed(() => store.state.projects.currentProject)
    
    // Methods
    const formatDate = (date) => {
      return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }
    
    const getDaysActive = (startDate) => {
      const start = new Date(startDate)
      const now = new Date()
      const diffTime = Math.abs(now - start)
      return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    }
    
    const getActivityIcon = (type) => {
      switch (type) {
        case 'create':
          return 'fas fa-plus'
        case 'update':
          return 'fas fa-edit'
        case 'delete':
          return 'fas fa-trash'
        default:
          return 'fas fa-info'
      }
    }
    
    const closeEditModal = () => {
      showEditModal.value = false
      editError.value = null
      if (project.value) {
        editForm.value = {
          name: project.value.name,
          description: project.value.description,
          status: project.value.status
        }
      }
    }
    
    const handleEdit = async () => {
      editLoading.value = true
      editError.value = null
      
      try {
        await store.dispatch('projects/updateProject', {
          id: project.value.id,
          data: editForm.value
        })
        closeEditModal()
      } catch (err) {
        editError.value = err.response?.data?.message || 'Failed to update project'
      } finally {
        editLoading.value = false
      }
    }
    
    const confirmDelete = () => {
      showDeleteModal.value = true
    }
    
    const closeDeleteModal = () => {
      showDeleteModal.value = false
    }
    
    const handleDelete = async () => {
      deleteLoading.value = true
      
      try {
        await store.dispatch('projects/deleteProject', project.value.id)
        router.push('/projects')
      } catch (err) {
        console.error('Failed to delete project:', err)
      } finally {
        deleteLoading.value = false
      }
    }
    
    const updateSettings = async () => {
      settingsLoading.value = true
      
      try {
        // TODO: Implement project settings update
        await new Promise(resolve => setTimeout(resolve, 1000))
        console.log('Settings updated:', settings.value)
      } catch (err) {
        console.error('Failed to update settings:', err)
      } finally {
        settingsLoading.value = false
      }
    }
    
    // Lifecycle
    onMounted(async () => {
      const projectId = route.params.id
      try {
        await store.dispatch('projects/fetchProject', projectId)
        if (project.value) {
          editForm.value = {
            name: project.value.name,
            description: project.value.description,
            status: project.value.status
          }
        }
      } catch (err) {
        console.error('Failed to fetch project:', err)
      }
    })
    
    return {
      loading,
      error,
      project,
      showEditModal,
      showDeleteModal,
      editForm,
      editError,
      editLoading,
      deleteLoading,
      settingsLoading,
      settings,
      projectActivities,
      formatDate,
      getDaysActive,
      getActivityIcon,
      closeEditModal,
      handleEdit,
      confirmDelete,
      closeDeleteModal,
      handleDelete,
      updateSettings
    }
  }
}
</script>

<style scoped>
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem 0;
  margin-bottom: 2rem;
}

.content-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.status-badge {
  display: inline-block;
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

.info-group {
  label {
    display: block;
    font-size: 0.875rem;
    font-weight: 500;
    color: #6c757d;
    margin-bottom: 0.5rem;
  }
}

.stats-list {
  display: grid;
  gap: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  
  .stat-icon {
    width: 40px;
    height: 40px;
    border-radius: 8px;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #667eea;
  }
  
  .stat-content {
    display: flex;
    flex-direction: column;
    
    .stat-value {
      font-size: 1.25rem;
      font-weight: 600;
    }
    
    .stat-label {
      font-size: 0.875rem;
      color: #6c757d;
    }
  }
}

.timeline {
  position: relative;
  padding: 1rem 0;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 1rem;
    height: 100%;
    width: 2px;
    background: #e9ecef;
  }
}

.timeline-item {
  position: relative;
  padding-left: 3rem;
  padding-bottom: 2rem;
  
  &:last-child {
    padding-bottom: 0;
  }
}

.timeline-icon {
  position: absolute;
  left: 0;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  
  &.create {
    background: rgba(40, 167, 69, 0.1);
    border-color: #28a745;
    color: #28a745;
  }
  
  &.update {
    background: rgba(255, 193, 7, 0.1);
    border-color: #ffc107;
    color: #ffc107;
  }
  
  &.delete {
    background: rgba(220, 53, 69, 0.1);
    border-color: #dc3545;
    color: #dc3545;
  }
}

.timeline-content {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
}

.modal {
  background-color: rgba(0, 0, 0, 0.5);
}
</style> 