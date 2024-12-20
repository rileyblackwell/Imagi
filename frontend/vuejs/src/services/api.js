import axios from 'axios'
import store from '@/store'

const api = axios.create({
  baseURL: process.env.VUE_APP_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true
})

// Request interceptor for API calls
api.interceptors.request.use(
  config => {
    const token = store.state.auth.accessToken
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor for API calls
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config
    
    // If error is unauthorized and not already retrying
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        // Try to refresh the token
        const refreshToken = store.state.auth.refreshToken
        if (refreshToken) {
          const response = await api.post('/auth/token/refresh/', {
            refresh: refreshToken
          })
          
          const { access } = response.data
          store.commit('auth/SET_ACCESS_TOKEN', access)
          
          // Retry the original request
          originalRequest.headers['Authorization'] = `Bearer ${access}`
          return api(originalRequest)
        }
      } catch (err) {
        // If refresh fails, logout user
        store.dispatch('auth/logout')
      }
    }
    
    return Promise.reject(error)
  }
)

export const authAPI = {
  login(credentials) {
    return api.post('/auth/token/', credentials)
  },
  
  register(userData) {
    return api.post('/users/', userData)
  },
  
  refreshToken(refreshToken) {
    return api.post('/auth/token/refresh/', { refresh: refreshToken })
  },
  
  getMe() {
    return api.get('/users/me/')
  },
  
  updateProfile(profileData) {
    return api.patch('/users/me/', profileData)
  },
  
  updatePassword(passwordData) {
    return api.post('/users/me/change-password/', passwordData)
  },
  
  updatePreferences(preferences) {
    return api.patch('/users/me/preferences/', preferences)
  },
  
  requestPasswordReset(email) {
    return api.post('/auth/password/reset/', { email })
  },
  
  resetPassword(data) {
    return api.post('/auth/password/reset/confirm/', data)
  }
}

export const projectAPI = {
  getProjects() {
    return api.get('/projects/')
  },
  
  getProject(id) {
    return api.get(`/projects/${id}/`)
  },
  
  createProject(data) {
    return api.post('/projects/', data)
  },
  
  updateProject(id, data) {
    return api.put(`/projects/${id}/`, data)
  },
  
  deleteProject(id) {
    return api.delete(`/projects/${id}/`)
  }
}

export const contactAPI = {
  sendMessage(data) {
    return api.post('/contact/', data)
  }
}

export default api 