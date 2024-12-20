<template>
  <div class="projects-page">
    <header class="page-header">
      <div class="container">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h1>Projects</h1>
            <p class="text-muted">Manage your projects and track their progress</p>
          </div>
          <button class="btn btn-primary" @click="showCreateModal = true">
            <i class="fas fa-plus"></i> New Project
          </button>
        </div>
      </div>
    </header>

    <main class="container">
      <!-- Filters and Search -->
      <div class="filters mb-4">
        <div class="row g-3">
          <div class="col-md-4">
            <input
              type="text"
              v-model="searchQuery"
              class="form-control"
              placeholder="Search projects..."
              @input="filterProjects"
            />
          </div>
          <div class="col-md-3">
            <select v-model="statusFilter" class="form-select" @change="filterProjects">
              <option value="">All Statuses</option>
              <option value="active">Active</option>
              <option value="completed">Completed</option>
              <option value="pending">Pending</option>
            </select>
          </div>
          <div class="col-md-3">
            <select v-model="sortBy" class="form-select" @change="filterProjects">
              <option value="created_desc">Newest First</option>
              <option value="created_asc">Oldest First</option>
              <option value="name_asc">Name A-Z</option>
              <option value="name_desc">Name Z-A</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Projects List -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <div v-else-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>

      <div v-else-if="filteredProjects.length === 0" class="text-center py-5">
        <div class="empty-state">
          <i class="fas fa-search fa-3x mb-3"></i>
          <h3>No Projects Found</h3>
          <p v-if="searchQuery || statusFilter">
            Try adjusting your search or filter criteria
          </p>
          <p v-else>
            Create your first project to get started
          </p>
          <button class="btn btn-primary" @click="showCreateModal = true">
            Create Project
          </button>
        </div>
      </div>

      <div v-else class="projects-grid">
        <div v-for="project in filteredProjects" :key="project.id" class="project-card">
          <div class="project-header">
            <h3>{{ project.name }}</h3>
            <div class="dropdown">
              <button class="btn btn-link" data-bs-toggle="dropdown">
                <i class="fas fa-ellipsis-v"></i>
              </button>
              <ul class="dropdown-menu dropdown-menu-end">
                <li>
                  <button class="dropdown-item" @click="editProject(project)">
                    <i class="fas fa-edit"></i> Edit
                  </button>
                </li>
                <li>
                  <button class="dropdown-item text-danger" @click="confirmDelete(project)">
                    <i class="fas fa-trash"></i> Delete
                  </button>
                </li>
              </ul>
            </div>
          </div>

          <span :class="['status-badge', project.status]">
            {{ project.status }}
          </span>

          <p class="project-description">{{ project.description }}</p>

          <div class="project-meta">
            <div class="meta-item">
              <i class="far fa-calendar-alt"></i>
              <span>Created: {{ formatDate(project.created_at) }}</span>
            </div>
            <div class="meta-item" v-if="project.updated_at">
              <i class="far fa-clock"></i>
              <span>Updated: {{ formatDate(project.updated_at) }}</span>
            </div>
          </div>

          <div class="project-footer">
            <router-link :to="'/projects/' + project.id" class="btn btn-outline-primary">
              View Details
            </router-link>
          </div>
        </div>
      </div>
    </main>

    <!-- Create/Edit Project Modal -->
    <div class="modal" :class="{ 'show d-block': showCreateModal }" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingProject ? 'Edit Project' : 'Create New Project' }}</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="handleSubmit">
              <div class="mb-3">
                <label for="projectName" class="form-label">Project Name</label>
                <input
                  type="text"
                  class="form-control"
                  id="projectName"
                  v-model="form.name"
                  required
                />
              </div>

              <div class="mb-3">
                <label for="projectDescription" class="form-label">Description</label>
                <textarea
                  class="form-control"
                  id="projectDescription"
                  v-model="form.description"
                  rows="3"
                  required
                ></textarea>
              </div>

              <div class="mb-3">
                <label for="projectStatus" class="form-label">Status</label>
                <select class="form-select" id="projectStatus" v-model="form.status" required>
                  <option value="pending">Pending</option>
                  <option value="active">Active</option>
                  <option value="completed">Completed</option>
                </select>
              </div>

              <div class="alert alert-danger" v-if="formError">
                {{ formError }}
              </div>

              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" @click="closeModal">
                  Cancel
                </button>
                <button type="submit" class="btn btn-primary" :disabled="formLoading">
                  <span v-if="formLoading" class="spinner-border spinner-border-sm me-1"></span>
                  {{ editingProject ? 'Update Project' : 'Create Project' }}
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
            <button type="button" class="btn btn-danger" @click="deleteProject" :disabled="deleteLoading">
              <span v-if="deleteLoading" class="spinner-border spinner-border-sm me-1"></span>
              Delete Project
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Backdrop -->
    <div class="modal-backdrop fade show" v-if="showCreateModal || showDeleteModal"></div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'ProjectsView',
  
  setup() {
    const store = useStore()
    
    // State
    const searchQuery = ref('')
    const statusFilter = ref('')
    const sortBy = ref('created_desc')
    const showCreateModal = ref(false)
    const showDeleteModal = ref(false)
    const editingProject = ref(null)
    const projectToDelete = ref(null)
    const formError = ref(null)
    const formLoading = ref(false)
    const deleteLoading = ref(false)
    
    const form = ref({
      name: '',
      description: '',
      status: 'pending'
    })
    
    // Computed
    const loading = computed(() => store.state.projects.loading)
    const error = computed(() => store.state.projects.error)
    const projects = computed(() => store.state.projects.projects)
    
    const filteredProjects = computed(() => {
      let result = [...projects.value]
      
      // Apply search filter
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        result = result.filter(project => 
          project.name.toLowerCase().includes(query) ||
          project.description.toLowerCase().includes(query)
        )
      }
      
      // Apply status filter
      if (statusFilter.value) {
        result = result.filter(project => project.status === statusFilter.value)
      }
      
      // Apply sorting
      switch (sortBy.value) {
        case 'created_asc':
          result.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
          break
        case 'created_desc':
          result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
          break
        case 'name_asc':
          result.sort((a, b) => a.name.localeCompare(b.name))
          break
        case 'name_desc':
          result.sort((a, b) => b.name.localeCompare(a.name))
          break
      }
      
      return result
    })
    
    // Methods
    const formatDate = (date) => {
      return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }
    
    const filterProjects = () => {
      // This method exists to handle filter changes
      // The actual filtering is done in the computed property
    }
    
    const resetForm = () => {
      form.value = {
        name: '',
        description: '',
        status: 'pending'
      }
      formError.value = null
      editingProject.value = null
    }
    
    const closeModal = () => {
      showCreateModal.value = false
      resetForm()
    }
    
    const editProject = (project) => {
      editingProject.value = project
      form.value = {
        name: project.name,
        description: project.description,
        status: project.status
      }
      showCreateModal.value = true
    }
    
    const handleSubmit = async () => {
      formLoading.value = true
      formError.value = null
      
      try {
        if (editingProject.value) {
          await store.dispatch('projects/updateProject', {
            id: editingProject.value.id,
            data: form.value
          })
        } else {
          await store.dispatch('projects/createProject', form.value)
        }
        closeModal()
      } catch (err) {
        formError.value = err.response?.data?.message || 'Failed to save project'
      } finally {
        formLoading.value = false
      }
    }
    
    const confirmDelete = (project) => {
      projectToDelete.value = project
      showDeleteModal.value = true
    }
    
    const closeDeleteModal = () => {
      showDeleteModal.value = false
      projectToDelete.value = null
    }
    
    const deleteProject = async () => {
      if (!projectToDelete.value) return
      
      deleteLoading.value = true
      
      try {
        await store.dispatch('projects/deleteProject', projectToDelete.value.id)
        closeDeleteModal()
      } catch (err) {
        console.error('Failed to delete project:', err)
      } finally {
        deleteLoading.value = false
      }
    }
    
    // Lifecycle
    onMounted(async () => {
      try {
        await store.dispatch('projects/fetchProjects')
      } catch (err) {
        console.error('Failed to fetch projects:', err)
      }
    })
    
    return {
      // State
      searchQuery,
      statusFilter,
      sortBy,
      showCreateModal,
      showDeleteModal,
      editingProject,
      form,
      formError,
      formLoading,
      deleteLoading,
      
      // Computed
      loading,
      error,
      projects,
      filteredProjects,
      
      // Methods
      formatDate,
      filterProjects,
      closeModal,
      editProject,
      handleSubmit,
      confirmDelete,
      closeDeleteModal,
      deleteProject
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

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.project-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
  
  .btn-link {
    color: #6c757d;
    padding: 0;
    
    &:hover {
      color: #343a40;
    }
  }
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: capitalize;
  margin-bottom: 1rem;
  
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

.project-meta {
  margin-bottom: 1rem;
  
  .meta-item {
    display: flex;
    align-items: center;
    color: #6c757d;
    font-size: 0.875rem;
    margin-bottom: 0.5rem;
    
    i {
      margin-right: 0.5rem;
      width: 16px;
    }
  }
}

.project-footer {
  margin-top: auto;
  
  .btn {
    width: 100%;
  }
}

.filters {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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

.modal {
  background-color: rgba(0, 0, 0, 0.5);
}

.dropdown-item {
  i {
    width: 20px;
    margin-right: 0.5rem;
  }
}
</style> 