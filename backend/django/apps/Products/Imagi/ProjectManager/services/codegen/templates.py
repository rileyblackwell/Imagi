"""
Template and content generators for ProjectCreationService.

This module centralizes all large string templates and content generation
used to scaffold VueJS frontend and Django backend projects.
"""
from __future__ import annotations

import os
import json

# =============================
# VueJS Frontend Templates
# =============================

def vite_config() -> str:
    return (
        "import { defineConfig } from 'vite'\n"
        "import vue from '@vitejs/plugin-vue'\n"
        "import path from 'path'\n"
        "import type { ViteDevServer } from 'vite'\n\n"
        "\n"
        "// Custom middleware to safely handle URI encoding issues\n"
        "function safeDecodeMiddleware(req: any, res: any, next: any) {\n"
        "  const originalUrl = req.url;\n\n"
        "  if (!originalUrl) {\n"
        "    next();\n"
        "    return;\n"
        "  }\n\n"
        "  try {\n"
        "    // Test if URL causes decodeURI to fail\n"
        "    decodeURI(originalUrl);\n"
        "  } catch (e) {\n"
        "    // If it fails, replace problematic characters\n"
        "    req.url = originalUrl\n"
        "      .replace(/%(?![0-9A-Fa-f]{2})/g, '%25') // Fix unescaped % signs\n"
        "      .replace(/\\\\/g, '/');  // Replace backslashes with forward slashes\n\n"
        "    console.warn('Fixed malformed URI:', originalUrl, '→', req.url);\n"
        "  }\n\n"
        "  next();\n"
        "}\n\n\n"
        "// Set base path depending on environment\n"
        "// Use '/' for both development and production unless specifically deploying to a subdirectory\n"
        "// If you need to deploy to a subdirectory, set VITE_BASE_PATH environment variable\n"
        "const BASE_PATH = process.env.VITE_BASE_PATH || '/';\n\n\n"
        "export default defineConfig({\n"
        "  base: BASE_PATH,\n"
        "  plugins: [\n"
        "    vue(),\n"
        "    // Handle missing pattern SVG references\n"
        "    {\n"
        "      name: 'resolve-svg-patterns',\n"
        "      resolveId(id) {\n"
        "        // Resolve grid-pattern.svg and dot-pattern.svg as empty modules\n"
        "        if (id === '/grid-pattern.svg' || id === '/dot-pattern.svg' || \n"
        "            id.endsWith('grid-pattern.svg') || id.endsWith('dot-pattern.svg')) {\n"
        "          return '\\0empty-svg-module'\n"
        "        }\n"
        "        return null\n"
        "      },\n"
        "      load(id) {\n"
        "        if (id === '\\0empty-svg-module') {\n"
        "          // Return a valid transparent SVG pattern that works with url() references\n"
        "          return `export default \"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40' viewBox='0 0 40 40'%3E%3Cg fill='%23f0f0f0' fill-opacity='0.1'%3E%3Ccircle cx='20' cy='20' r='1'/%3E%3C/g%3E%3C/svg%3E\"`\n"
        "        }\n"
        "        return null\n"
        "      }\n"
        "    },\n"
        "    // Add custom plugin to handle malformed URIs\n"
        "    {\n"
        "      name: 'fix-malformed-uris',\n"
        "      configureServer(server: ViteDevServer) {\n"
        "        server.middlewares.use(safeDecodeMiddleware);\n"
        "      }\n"
        "    }\n"
        "  ],\n"
        "  server: {\n"
        "    // No need to set base here; handled globally above\n"
        "    port: 5173,\n"
        "    strictPort: true, // This will fail if port 5173 is not available\n"
        "    hmr: {\n"
        "      overlay: false, // Disable the HMR error overlay to prevent URI errors from breaking the UI\n"
        "    },\n"
        "    proxy: {\n"
        "      // Proxy all API requests to the Django backend\n"
        "      // This allows consistent API calls using relative URLs in both development and production\n"
        "      '/api': {\n"
        "        target: process.env.VITE_BACKEND_URL || 'http://localhost:8000',\n"
        "        changeOrigin: true,\n"
        "        secure: false,\n"
        "        configure: (proxy, _options) => {\n"
        "          const backendUrl = process.env.VITE_BACKEND_URL || 'http://localhost:8000';\n\n"
        "          proxy.on('proxyReq', (proxyReq, req, _res) => {\n"
        "            // Log request info when debugging\n"
        "            if (process.env.NODE_ENV !== 'production') {\n"
        "              console.log(`🔄 Proxy: ${req.method} ${req.url} → ${backendUrl}${req.url}`);\n"
        "            }\n"
        "          });\n\n"
        "          proxy.on('proxyRes', (proxyRes, req, _res) => {\n"
        "            // Ensure proper headers for streaming responses\n"
        "            if (req.headers.accept?.includes('text/event-stream')) {\n"
        "              proxyRes.headers['content-type'] = 'text/event-stream';\n"
        "              proxyRes.headers['cache-control'] = 'no-cache';\n"
        "              proxyRes.headers['connection'] = 'keep-alive';\n"
        "            }\n"
        "          });\n\n"
        "          proxy.on('error', (err, req, _res) => {\n"
        "            console.error(`❌ Proxy Error: ${req.method} ${req.url} → ${backendUrl}${req.url}`, err.message);\n"
        "          });\n"
        "        }\n"
        "      }\n"
        "    }\n"
        "  },\n"
        "  resolve: {\n"
        "    alias: {\n"
        "      '@': path.resolve(__dirname, './src'),\n"
        "    },\n"
        "    extensions: ['.ts', '.js', '.vue', '.json'] // Prioritize TypeScript files\n"
        "  },\n"
        "  build: {\n"
        "    target: 'esnext',\n"
        "    sourcemap: true,\n"
        "    chunkSizeWarningLimit: 800, // Increase chunk size warning limit\n"
        "    rollupOptions: {\n"
        "      output: {\n"
        "        manualChunks(id) {\n"
        "          // Handle file service circular dependencies\n"
        "          if (id.includes('fileService.ts')) {\n"
        "            return 'builder-services';\n"
        "          }\n\n"
        "          // Handle UI library chunks only if they're actually imported\n"
        "          if (id.includes('node_modules/@headlessui/vue') || \n"
        "              id.includes('node_modules/@heroicons/vue')) {\n"
        "            return 'vendor-ui';\n"
        "          }\n\n"
        "          // Vue ecosystem libraries\n"
        "          if (id.includes('node_modules/vue') || \n"
        "              id.includes('node_modules/vue-router') || \n"
        "              id.includes('node_modules/pinia')) {\n"
        "            return 'vendor-vue';\n"
        "          }\n\n"
        "          // Shared utilities\n"
        "          if (id.includes('/shared/utils/')) {\n"
        "            return 'shared-utils';\n"
        "          }\n\n"
        "          // Handle layouts\n"
        "          if (id.includes('/shared/layouts/') || id.includes('/apps/auth/layouts/')) {\n"
        "            return 'layouts';\n"
        "          }\n"
        "        }\n"
        "      }\n"
        "    }\n"
        "  }\n"
        "})\n"
    )


def tailwind_config() -> str:
    return (
        "/** @type {import('tailwindcss').Config} */\n"
        "export default {\n"
        "  content: [\n"
        "    \"./index.html\",\n"
        "    \"./src/**/*.{vue,js,ts,jsx,tsx}\",\n"
        "  ],\n"
        "  theme: {\n"
        "    extend: {},\n"
        "  },\n"
        "  plugins: [],\n"
        "}\n"
    )


def django_additional_settings() -> str:
    """Django CORS and DRF settings snippet to append to settings.py."""
    return (
        """
# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Allow all for development
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
}
"""
    )


def postcss_config() -> str:
    return (
        "export default {\n"
        "  plugins: {\n"
        "    tailwindcss: {},\n"
        "    autoprefixer: {},\n"
        "  },\n"
        "}\n"
    )


def index_html(project_name: str) -> str:
    return (
        f"""<!DOCTYPE html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\">
    <meta http-equiv=\"X-UA-Compatible\" content=\"IE=edge\">
    <meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\">
    <link rel=\"icon\" href=\"/favicon.ico\">
    <title>{project_name} - Transform Text to Web Apps</title>
    <link rel=\"stylesheet\" href=\"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css\" />
  </head>
  <body class=\"bg-gray-900 text-white\">
    <noscript>
      <strong>We're sorry but {project_name} doesn't work properly without JavaScript enabled. Please enable it to continue.</strong>
    </noscript>
    <div id=\"app\"></div>
    <script type=\"module\" src=\"/src/main.ts\"></script>
  </body>
</html>
"""
    )


def vue_main_js() -> str:
    return """import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import type { AxiosInstance } from 'axios'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { 
  faUser, 
  faLock, 
  faCircleNotch,
  faExclamationCircle,
  faCheckCircle,
  faSpinner,
  faEye,
  faEyeSlash 
} from '@fortawesome/free-solid-svg-icons'
import config from '@/shared/config'
import './assets/css/main.css'

// Add icons to library
library.add(
  faUser,
  faLock,
  faCircleNotch,
  faExclamationCircle,
  faCheckCircle,
  faSpinner,
  faEye,
  faEyeSlash
)

// Configure axios
axios.defaults.baseURL = config.apiUrl
axios.defaults.withCredentials = true
axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'

// Create Vue app instance
const app = createApp(App)

// Type augmentation (available at runtime even without .d.ts)
declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $axios: AxiosInstance;
  }
}

// Add global properties
app.config.globalProperties.$axios = axios

// Use plugins
app.use(createPinia())
app.use(router)

// Dynamically load auth validation plugin if auth app exists
import('@/apps/auth/plugins/validation')
  .then((module) => {
    if (module.validationPlugin) {
      app.use(module.validationPlugin)
    }
  })
  .catch(() => {
    // Auth app not installed, skip validation plugin
  })

// Register global components
app.component('font-awesome-icon', FontAwesomeIcon)

// Mount app
app.mount('#app')
"""


def vue_shared_config_ts() -> str:
    return """// Centralized frontend configuration
// Respects Vite environment variable VITE_BACKEND_URL; falls back to localhost
const apiBase = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'

const config = {
  apiUrl: `${apiBase}/api`,
}

export default config
"""


def vue_validation_plugin_ts() -> str:
    return """import { configure, defineRule } from 'vee-validate'
import { required, email } from '@vee-validate/rules'
import { localize } from '@vee-validate/i18n'
import type { App } from 'vue'

// Define base rules
defineRule('required', () => true)
defineRule('email', (value: string) => {
  if (value && !/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(value)) {
    return 'Please enter a valid email address'
  }
  return true
})

// Simple username validation
defineRule('username', () => true)

// Add terms agreement validation
defineRule('terms', () => true)

// Registration specific password validation
defineRule('registration_password', (value: string) => {
  if (value && value.length < 8) return 'Password must be at least 8 characters'
  if (value && !/[A-Z]/.test(value)) return 'Password must contain at least one uppercase letter'
  if (value && !/[a-z]/.test(value)) return 'Password must contain at least one lowercase letter'
  if (value && !/[0-9]/.test(value)) return 'Password must contain at least one number'
  return true
})

defineRule('password_confirmation', (value: string, [target]: string[]) => {
  if (value && target && value !== target) {
    return 'Passwords must match'
  }
  return true
})

// Add login-specific validation rules
defineRule('login_username', () => true)

defineRule('login_password', () => true)

const errorMessages = {
  'This username is already taken. Please choose another one.': 'This username is already taken. Please try another one.',
  'A user is already registered with this e-mail address.': 'This email is already registered. Please use another one or sign in.',
  'Password must be at least 8 characters long': 'Password must be at least 8 characters long.',
  'Passwords don\\'t match': 'Passwords don\\'t match. Please make sure they are identical.',
  'Unable to complete registration. Please try again.': 'Unable to complete registration. Please try again.',
  'No account found with this username': 'No account found with this username. Please check your spelling or create an account.',
  'Invalid password. Please try again': 'Incorrect password. Please try again.',
  'This account has been disabled': 'This account has been disabled. Please contact support.',
  'Unable to log in with provided credentials.': 'Invalid username or password. Please try again.',
  'Username is required': 'Username is required.',
  'Password is required': 'Password is required.',
  'Not found.': 'Account not found. Please check your username.',
  'Authentication credentials were not provided.': 'Please enter your login credentials.',
  'Invalid credentials': 'Username or password is incorrect.',
  'Login failed. Please try again later': 'Login failed. Please try again later.',
  'Login failed: No token received': 'Unable to log in. Please try again.',
  'Network Error': 'Unable to connect to server. Please check your internet connection.',
  'Login failed: Please try again': 'Login failed. Please try again later.',
  'Login failed: Invalid response format': 'Unable to complete login. Please try again.',
  'Invalid server response: Missing token': 'Unable to complete login. Please try again.',
  'default': 'An unexpected error occurred. Please try again.'
} as const

export const formatAuthError = (error: unknown, context: 'login' | 'register' = 'login'): string => {
  if (!error) return errorMessages.default
  
  if (error instanceof Error) {
    const message = error.message
    
    // Check if this is an axios error with a response
    const axiosError = error as any
    if (axiosError?.response?.data) {
      const responseData = axiosError.response.data
      
      // Check for different error formats
      if (responseData.error) {
        return errorMessages[responseData.error as keyof typeof errorMessages] || responseData.error
      }
      
      if (responseData.detail) {
        if (typeof responseData.detail === 'object') {
          const errorMessages = []
          
          for (const [field, message] of Object.entries(responseData.detail)) {
            if (field === 'non_field_errors' || field === 'error') {
              errorMessages.push(message)
            } else {
              errorMessages.push(`${field}: ${message}`)
            }
          }
          
          return errorMessages.join('\\n')
        }
        
        return responseData.detail
      }
      
      // Handle non_field_errors array
      if (responseData.non_field_errors && Array.isArray(responseData.non_field_errors)) {
        return responseData.non_field_errors[0]
      }
    }
    
    // Check message against our known error messages
    const formattedMessage = errorMessages[message as keyof typeof errorMessages]
    return formattedMessage || message
  }
  
  // If error is just a string
  if (typeof error === 'string') {
    return errorMessages[error as keyof typeof errorMessages] || error
  }
  
  return errorMessages.default
}

export const validationPlugin = {
  install: (app: App) => {
    configure({
      validateOnInput: false,
      validateOnBlur: false,
      validateOnChange: false,
      validateOnModelUpdate: false,
      generateMessage: () => '',
    })
  }
}

export { defineRule, errorMessages }
"""


def vue_app_vue(project_name: str, project_description: str | None) -> str:
    return """<template>
  <div id=\"app\" class=\"min-h-screen bg-gray-50 text-gray-900 flex flex-col\">
    <router-view v-slot=\"{ Component }\" class=\"flex-grow\">
      <transition name=\"fade\" mode=\"out-in\">
        <component :is=\"Component\" />
      </transition>
    </router-view>
  </div>
</template>

<script setup>
// Minimal App shell; no shared components or global stores used.
</script>
"""


def vue_router_index() -> str:
    return """import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

// Auto-import all route modules from apps
// Supports both TS and JS router modules if present
const modules = import.meta.glob('@/apps/**/router/index.{ts,js}', { eager: true })

// Extract routes from each module (default export or named `routes`)
const routeModules = Object.values(modules)
  .map((mod) => (mod && 'default' in mod ? mod.default : (mod && mod.routes) || []))
  .flat()

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // Basic home route for initial project load
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { title: 'Home' }
    },
    // Inject all app routes discovered above
    ...routeModules,
    // 404 fallback
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/shared/components/pages/NotFound.vue')
    }
  ]
})

export default router
"""


def vue_store_main() -> str:
    return """import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useMainStore = defineStore('main', () => {
  const message = ref('Hello from Pinia store!')

  function updateMessage(newMessage) {
    message.value = newMessage
  }

  return { message, updateMessage }
})
"""


def vue_api_service() -> str:
    return """import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios'

// Helper: read a cookie by name (used for CSRF)
function getCookie(name: string): string | null {
  let cookieValue: string | null = null
  if (typeof document !== 'undefined' && document.cookie) {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

// Create the centralized API client
const api: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 60000,
  withCredentials: true,
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  }
})

// Request interceptor
api.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // Attach Authorization header from localStorage
    try {
      if (!config.headers['Authorization']) {
        const raw = typeof window !== 'undefined' ? localStorage.getItem('token') : null
        if (raw) {
          let token: string | null = null
          try {
            const parsed = JSON.parse(raw)
            token = typeof parsed === 'string' ? parsed : parsed?.value
            const expires = parsed?.expires
            if (expires && Date.now() > Number(expires)) {
              token = null
            }
          } catch {
            token = raw
          }
          if (token) {
            config.headers['Authorization'] = `Token ${token}`
          }
        }
      }
    } catch (_) {}

    // Attach CSRF token for unsafe methods
    const method = (config.method || 'get').toLowerCase()
    const unsafe = ['post', 'put', 'patch', 'delete'].includes(method)
    if (unsafe) {
      const csrfToken = getCookie('csrftoken')
      if (csrfToken && !config.headers['X-CSRFToken']) {
        config.headers['X-CSRFToken'] = csrfToken
      }
    }
    
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // Handle 401 Unauthorized
    if (error.response?.status === 401) {
      try {
        window.dispatchEvent(new CustomEvent('app:auth-unauthorized', { detail: { url: error.config?.url } }))
      } catch {}
    }
    
    if (!error.response) {
      return Promise.reject(new Error('Network error: Unable to connect to server'))
    }
    
    if (error.code === 'ECONNABORTED') {
      return Promise.reject(new Error('Request timeout'))
    }
    
    return Promise.reject(error)
  }
)

// CSRF token helper
export async function getCsrfToken(): Promise<void> {
  try {
    await api.get('/v1/auth/csrf/')
  } catch (error) {
    console.warn('Failed to fetch CSRF token:', error)
  }
}

// Export the configured API client
export default api
"""


def vue_shared_auth_store() -> str:
    return """import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import axios from 'axios'
import api from '@/shared/services/api'

// Define User type based on what the backend returns
interface User {
  id: number;
  email?: string;
  username: string;
  name?: string;
  balance?: number;
  created_at?: string;
  updated_at?: string;
}

// Define token data structure interface
interface TokenData {
  value: string;
  expires: number;
}

// Create a function to safely parse JSON with a fallback
const safeJSONParse = <T>(jsonString: string | null, fallback: T): T => {
  if (!jsonString) return fallback
  try {
    return JSON.parse(jsonString) as T
  } catch {
    return fallback
  }
}

// Set cache duration for auth init calls to prevent duplicates
const AUTH_CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

/**
 * Global authentication store for managing user sessions across the application
 */
export const useAuthStore = defineStore('global-auth', () => {
  // State
  const token = ref<string | null>(getStoredToken())
  const user = ref<User | null>(getStoredUser())
  const isAuthenticated = ref(!!token.value)
  const sessionTimeout = ref<number | null>(null)
  const initialized = ref(false)
  const loading = ref(false)
  const lastInitTime = ref<number>(0)
  const pendingAuthCheck = ref<Promise<boolean> | null>(null)
  
  // Watch for changes to authentication state and sync with localStorage
  watch(() => isAuthenticated.value, (newValue) => {
    if (newValue && token.value && user.value) {
      // If becoming authenticated, make sure token is set in axios
      axios.defaults.headers.common['Authorization'] = `Token ${token.value}`
    }
  })

  // Helper function to get the stored token
  function getStoredToken(): string | null {
    try {
      const tokenData = safeJSONParse<TokenData | null>(localStorage.getItem('token'), null)
      if (!tokenData?.value) return null
      if (tokenData.expires && Date.now() > tokenData.expires) {
        localStorage.removeItem('token')
        return null
      }
      return tokenData.value
    } catch {
      return null
    }
  }

  // Helper function to get the stored user
  function getStoredUser(): User | null {
    return safeJSONParse(localStorage.getItem('user'), null)
  }

  // Getters
  const currentUser = computed(() => user.value)
  const userBalance = computed(() => user.value?.balance || 0)

  // Actions
  const setAuthState = (userData: User | null, authToken: string | null) => {
    user.value = userData
    token.value = authToken
    isAuthenticated.value = !!authToken
    
    if (authToken && userData) {
      // Store token in localStorage with expiry
      const tokenData: TokenData = {
        value: authToken,
        expires: Date.now() + (24 * 60 * 60 * 1000) // 24 hours
      }
      localStorage.setItem('token', JSON.stringify(tokenData))
      localStorage.setItem('user', JSON.stringify(userData))
      
      // Set axios default auth header
      axios.defaults.headers.common['Authorization'] = `Token ${authToken}`
      sessionTimeout.value = 30 * 60 * 1000 // 30 minutes
    } else {
      clearStoredAuth()
    }
  }
  
  // Function to restore auth state from localStorage without API calls
  const restoreAuthState = (userData: User, authToken: string) => {
    user.value = userData
    token.value = authToken
    isAuthenticated.value = true
    
    // Set axios default auth header
    axios.defaults.headers.common['Authorization'] = `Token ${authToken}`
  }

  // Helper to clear stored authentication data
  const clearStoredAuth = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    
    // Clear cookies
    document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
    document.cookie = 'auth_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
    document.cookie = 'sessionid=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
    
    // Remove auth header
    delete axios.defaults.headers.common['Authorization']
    sessionTimeout.value = null
  }

  const initAuth = async () => {
    const now = Date.now()
    if (initialized.value && (now - lastInitTime.value) < AUTH_CACHE_DURATION) {
      if (token.value && !isAuthenticated.value) {
        isAuthenticated.value = true
        axios.defaults.headers.common['Authorization'] = `Token ${token.value}`
      }
      return
    }
    
    if (pendingAuthCheck.value) {
      return pendingAuthCheck.value
    }
    
    const authCheckPromise = (async () => {
      try {
        loading.value = true
        
        const storedToken = getStoredToken()
        const storedUser = getStoredUser()
        
        if (!storedToken) {
          await clearAuth()
          loading.value = false
          initialized.value = true
          lastInitTime.value = now
          return false
        }
        
        token.value = storedToken
        user.value = storedUser
        axios.defaults.headers.common['Authorization'] = `Token ${storedToken}`
        
        try {
          const response = await api.get('/v1/auth/init/')
          
          if (response.data.isAuthenticated) {
            user.value = response.data.user
            isAuthenticated.value = true
            localStorage.setItem('user', JSON.stringify(response.data.user))
            lastInitTime.value = now
            return true
          } else {
            return false
          }
        } catch (error) {
          console.error('Failed to validate auth with server:', error)
          return false
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error)
        await clearAuth()
        return false
      } finally {
        loading.value = false
        initialized.value = true
        setTimeout(() => {
          pendingAuthCheck.value = null
        }, 0)
      }
    })()
    
    pendingAuthCheck.value = authCheckPromise
    return authCheckPromise
  }

  const clearAuth = async () => {
    user.value = null
    token.value = null
    isAuthenticated.value = false
    clearStoredAuth()
    initialized.value = false
  }

  const logout = async () => {
    return await clearAuth()
  }

  return {
    // State
    token,
    user,
    isAuthenticated,
    sessionTimeout,
    initialized,
    loading,
    
    // Getters
    currentUser,
    userBalance,
    
    // Actions
    setAuthState,
    restoreAuthState,
    initAuth,
    clearAuth,
    logout
  }
})
"""


def vue_home_view(project_name: str, project_description: str | None) -> str:
    safe_project_name = project_name.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
    safe_description = (project_description or '').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
    content = (
        "<template>\n"
        "  <div class=\"min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100\">\n"
        "    <div class=\"container mx-auto px-4 py-16\">\n"
        "      <div class=\"max-w-4xl mx-auto text-center\">\n"
        "        <h1 class=\"text-5xl font-bold text-gray-900 mb-6\">\n"
        "          Welcome to " + safe_project_name + "\n"
        "        </h1>\n\n"
        "        <p v-if=\"description\" class=\"text-xl text-gray-600 mb-8 max-w-2xl mx-auto\">\n"
        "          " + safe_description + "\n"
        "        </p>\n\n"
        "        <div class=\"bg-white rounded-2xl shadow-xl p-8 mb-8\">\n"
        "          <h2 class=\"text-2xl font-semibold text-gray-800 mb-4\">\n"
        "            Your VueJS + Django Application\n"
        "          </h2>\n"
        "          <p class=\"text-gray-600 mb-6\">\n"
        "            This project includes a modern VueJS frontend with Vite, TailwindCSS, and Pinia, \n"
        "            connected to a Django REST API backend.\n"
        "          </p>\n\n"
        "          <div class=\"grid md:grid-cols-2 gap-6\">\n"
        "            <div class=\"bg-blue-50 p-6 rounded-xl\">\n"
        "              <h3 class=\"text-lg font-medium text-blue-900 mb-2\">Frontend Tech Stack</h3>\n"
        "              <ul class=\"text-blue-700 space-y-1\">\n"
        "                <li>• Vue 3 with Composition API</li>\n"
        "                <li>• Vite for fast development</li>\n"
        "                <li>• TailwindCSS for styling</li>\n"
        "                <li>• Pinia for state management</li>\n"
        "                <li>• Axios for API calls</li>\n"
        "              </ul>\n"
        "            </div>\n\n"
        "            <div class=\"bg-green-50 p-6 rounded-xl\">\n"
        "              <h3 class=\"text-lg font-medium text-green-900 mb-2\">Backend Tech Stack</h3>\n"
        "              <ul class=\"text-green-700 space-y-1\">\n"
        "                <li>• Django 4.x framework</li>\n"
        "                <li>• Django REST Framework</li>\n"
        "                <li>• SQLite database</li>\n"
        "                <li>• CORS enabled</li>\n"
        "                <li>• Token authentication</li>\n"
        "              </ul>\n"
        "            </div>\n"
        "          </div>\n"
        "        </div>\n\n"
        "        <div class=\"flex flex-col sm:flex-row gap-4 justify-center\">\n"
        "          <button\n"
        "            @click=\"testApiConnection\"\n"
        "            :disabled=\"loading\"\n"
        "            class=\"bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-6 py-3 rounded-lg font-medium transition-colors\"\n"
        "          >\n"
        "            {{ loading ? 'Testing...' : 'Test API Connection' }}\n"
        "          </button>\n\n"
        "          <button\n"
        "            @click=\"updateStoreMessage\"\n"
        "            class=\"bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-medium transition-colors\"\n"
        "          >\n"
        "            Test Pinia Store\n"
        "          </button>\n"
        "        </div>\n\n"
        "        <div v-if=\"apiStatus\" class=\"mt-6 p-4 rounded-lg\" :class=\"apiStatus.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'\">\n"
        "          {{ apiStatus.message }}\n"
        "        </div>\n\n"
        "        <div class=\"mt-6 p-4 bg-gray-100 rounded-lg\">\n"
        "          <p class=\"text-gray-700\">Store Message: {{ mainStore.message }}</p>\n"
        "        </div>\n"
        "      </div>\n"
        "    </div>\n"
        "  </div>\n"
        "</template>\n\n"
        "<script setup>\n"
        "import { ref } from 'vue'\n"
        "import { useMainStore } from '@/stores/main'\n"
        "import api from '@/services/api'\n\n"
        "const mainStore = useMainStore()\n"
        "const loading = ref(false)\n"
        "const apiStatus = ref(null)\n"
        "const description = '" + safe_description + "'\n\n"
        "async function testApiConnection() {\n"
        "  loading.value = true\n"
        "  apiStatus.value = null\n\n"
        "  try {\n"
        "    const response = await api.get('/v1/health/')\n"
        "    apiStatus.value = {\n"
        "      success: true,\n"
        "      message: 'API connection successful! Backend is running.'\n"
        "    }\n"
        "  } catch (error) {\n"
        "    apiStatus.value = {\n"
        "      success: false,\n"
        "      message: 'API connection failed. Make sure the Django backend is running on port 8000.'\n"
        "    }\n"
        "  } finally {\n"
        "    loading.value = false\n"
        "  }\n"
        "}\n\n"
        "function updateStoreMessage() {\n"
        "  const messages = [\n"
        "    'Pinia store is working!',\n"
        "    'State management is active!',\n"
        "    'VueJS + Pinia = ❤️',\n"
        "    'Store updated successfully!'\n"
        "  ]\n"
        "  const randomMessage = messages[Math.floor(Math.random() * messages.length)]\n"
        "  mainStore.updateMessage(randomMessage)\n"
        "}\n"
        "</script>\n"
    )
    return content


def vue_main_css() -> str:
    return """@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html {
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }
}

@layer components {
  .btn {
    @apply px-4 py-2 rounded-lg font-medium transition-colors;
  }

  .btn-primary {
    @apply bg-blue-600 hover:bg-blue-700 text-white;
  }

  .btn-secondary {
    @apply bg-gray-200 hover:bg-gray-300 text-gray-800;
  }
}
"""

# =============================
# VueJS Scaffolding Helpers (file writers)
# =============================

def _sanitize_project_name(name: str) -> str:
    """Convert project name to a valid identifier for package names."""
    sanitized = ''.join(c if c.isalnum() else '_' for c in name)
    if not sanitized or not sanitized[0].isalpha():
        sanitized = 'project_' + sanitized
    return sanitized


def create_vuejs_frontend_files(frontend_path: str, project_name: str, project_description: str | None) -> None:
    """Create VueJS frontend with Vite, Pinia, TailwindCSS, and Axios (vanilla JS)."""
    # package.json aligned with main Imagi frontend so all required packages are installed
    package_json = {
        "name": f"{_sanitize_project_name(project_name).lower()}-frontend",
        "version": "1.0.0",
        "private": True,
        "type": "module",
        "scripts": {
            "dev": "vite --host",
            "dev:debug": "vite --host --debug",
            "build": "vue-tsc --noEmit && vite build",
            "preview": "vite preview",
            "start": "vite preview --host --port $PORT",
            "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx --fix --ignore-path .gitignore",
            "clean": "rm -rf node_modules dist .vite",
            "type-check": "vue-tsc --noEmit",
            "audit:fix": "npm audit fix",
            "audit:fix-force": "npm audit fix --force"
        },
        "dependencies": {
            "@fortawesome/fontawesome-svg-core": "^6.5.1",
            "@fortawesome/free-brands-svg-icons": "^6.5.1",
            "@fortawesome/free-solid-svg-icons": "^6.5.1",
            "@fortawesome/vue-fontawesome": "^3.0.5",
            "@headlessui/vue": "^1.7.23",
            "@heroicons/vue": "^2.2.0",
            "@stripe/stripe-js": "^3.0.3",
            "@vee-validate/i18n": "^4.15.0",
            "@vee-validate/rules": "^4.15.0",
            "axios": "^1.6.7",
            "chart.js": "^4.4.0",
            "gsap": "^3.12.5",
            "isomorphic-dompurify": "^2.22.0",
            "lodash-es": "^4.17.21",
            "marked": "^15.0.7",
            "pinia": "^2.1.7",
            "tailwindcss": "^3.4.1",
            "uuid": "^11.1.0",
            "vee-validate": "^4.15.0",
            "vue": "^3.4.15",
            "vue-chartjs": "^5.3.0",
            "vue-router": "^4.2.5"
        },
        "devDependencies": {
            "@eslint/config-array": "^0.19.2",
            "@eslint/object-schema": "^2.1.6",
            "@tailwindcss/typography": "^0.5.10",
            "@types/dompurify": "^3.0.5",
            "@types/lodash-es": "^4.17.12",
            "@types/marked": "^5.0.2",
            "@types/node": "^20.11.0",
            "@types/uuid": "^10.0.0",
            "@typescript-eslint/eslint-plugin": "^6.21.0",
            "@typescript-eslint/parser": "^6.21.0",
            "@vitejs/plugin-vue": "^5.0.4",
            "@vue/eslint-config-prettier": "^9.0.0",
            "@vue/eslint-config-typescript": "^12.0.0",
            "@vue/tsconfig": "^0.5.1",
            "autoprefixer": "^10.4.17",
            "eslint": "^8.57.1",
            "eslint-config-standard": "^17.1.0",
            "eslint-import-resolver-typescript": "^3.8.5",
            "eslint-plugin-import": "^2.31.0",
            "eslint-plugin-prettier": "^5.1.3",
            "eslint-plugin-unused-imports": "^4.1.4",
            "eslint-plugin-vue": "^9.21.1",
            "glob": "^10.3.10",
            "lru-cache": "^10.2.0",
            "postcss": "^8.4.33",
            "prettier": "^3.2.4",
            "rimraf": "^5.0.5",
            "typescript": "~5.3.3",
            "vite": "^6.2.1",
            "vue-tsc": "^2.2.0"
        },
        "overrides": {
            "inflight": "^2.0.0",
            "glob": "^10.3.10",
            "rimraf": "^5.0.5",
            "@humanwhocodes/config-array": "@eslint/config-array@^0.19.2",
            "@humanwhocodes/object-schema": "@eslint/object-schema@^2.1.6"
        }
    }

    with open(os.path.join(frontend_path, 'package.json'), 'w') as f:
        f.write(json.dumps(package_json, indent=2))

    # vite.config.js
    with open(os.path.join(frontend_path, 'vite.config.ts'), 'w') as f:
        f.write(vite_config())

    # tsconfig.json for TypeScript support
    tsconfig = {
        "compilerOptions": {
            "target": "ESNext",
            "useDefineForClassFields": True,
            "lib": ["ESNext", "DOM", "DOM.Iterable"],
            "module": "ESNext",
            "skipLibCheck": True,
            "moduleResolution": "bundler",
            "resolveJsonModule": True,
            "isolatedModules": True,
            "noEmit": True,
            "jsx": "preserve",
            "baseUrl": ".",
            "paths": {
                "@/*": ["./src/*"]
            }
        },
        "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.vue", "src/**/*.js"],
        "exclude": ["node_modules", "dist"]
    }

    with open(os.path.join(frontend_path, 'tsconfig.json'), 'w') as f:
        f.write(json.dumps(tsconfig, indent=2))

    # Tailwind and PostCSS
    with open(os.path.join(frontend_path, 'tailwind.config.js'), 'w') as f:
        f.write(tailwind_config())

    with open(os.path.join(frontend_path, 'postcss.config.js'), 'w') as f:
        f.write(postcss_config())

    # index.html
    with open(os.path.join(frontend_path, 'index.html'), 'w') as f:
        f.write(index_html(project_name))

    # src files
    create_vuejs_src_files(frontend_path, project_name, project_description)


def create_vuejs_src_files(frontend_path: str, project_name: str, project_description: str | None) -> None:
    """Create VueJS source files structure under src/."""
    src_path = os.path.join(frontend_path, 'src')

    # Create directories (excluding auth - will be created by prebuilt app)
    directories = [
        'components',
        'components/atoms',
        'components/molecules',
        'components/organisms',
        'apps',
        'views',
        'router',
        'stores',
        'services',
        'types',
        'assets',
        'assets/css',
        'shared',
        'shared/components',
        'shared/components/pages',
        'shared/stores',
        'shared/services'
    ]

    for directory in directories:
        os.makedirs(os.path.join(src_path, directory), exist_ok=True)

    # main.ts
    with open(os.path.join(src_path, 'main.ts'), 'w') as f:
        f.write(vue_main_js())

    # App.vue
    with open(os.path.join(src_path, 'App.vue'), 'w') as f:
        f.write(vue_app_vue(project_name, project_description))

    # router/index.js (use JS file instead of TS)
    with open(os.path.join(src_path, 'router', 'index.js'), 'w') as f:
        f.write(vue_router_index())

    # shared/config.ts
    with open(os.path.join(src_path, 'shared', 'config.ts'), 'w') as f:
        f.write(vue_shared_config_ts())

    # shared/stores/auth.ts - Global auth store
    with open(os.path.join(src_path, 'shared', 'stores', 'auth.ts'), 'w') as f:
        f.write(vue_shared_auth_store())

    # shared/services/api.ts - Centralized API client
    with open(os.path.join(src_path, 'shared', 'services', 'api.ts'), 'w') as f:
        f.write(vue_api_service())

    # Note: auth app files (including validation.ts) are now created by prebuilt_apps.py

    # stores/main.js
    with open(os.path.join(src_path, 'stores', 'main.js'), 'w') as f:
        f.write(vue_store_main())

    # services/api.ts (legacy location for backwards compatibility)
    with open(os.path.join(src_path, 'services', 'api.ts'), 'w') as f:
        f.write(vue_api_service())

    # views/HomeView.vue
    with open(os.path.join(src_path, 'views', 'HomeView.vue'), 'w') as f:
        f.write(vue_home_view(project_name, project_description))

    # assets/css/main.css
    with open(os.path.join(src_path, 'assets', 'css', 'main.css'), 'w') as f:
        f.write(vue_main_css())

    # shared/components/pages/NotFound.vue used by router fallback
    not_found_vue = (
        "<template>\n"
        "  <div class=\"min-h-screen flex items-center justify-center bg-gray-50\">\n"
        "    <div class=\"text-center\">\n"
        "      <h1 class=\"text-6xl font-bold text-gray-900\">404</h1>\n"
        "      <p class=\"mt-4 text-gray-600\">Page not found</p>\n"
        "      <router-link to=\"/\" class=\"mt-6 inline-block text-indigo-600 hover:underline\">Go Home</router-link>\n"
        "    </div>\n"
        "  </div>\n"
        "</template>\n"
    )
    with open(os.path.join(src_path, 'shared', 'components', 'pages', 'NotFound.vue'), 'w') as f:
        f.write(not_found_vue)


# =============================
# Dev Scripts
# =============================

def start_dev_sh() -> str:
    return (
        "#!/bin/bash\n"
        "# Development startup script for dual-stack application\n\n"
        "echo \"🚀 Starting development servers...\"\n\n"
        "# Function to cleanup background processes\n"
        "cleanup() {\n"
        "    echo \"\"\n"
        "    echo \"🛑 Stopping development servers...\"\n"
        "    jobs -p | xargs -r kill\n"
        "    exit\n"
        "}\n\n"
        "# Set up signal handling\n"
        "trap cleanup SIGINT SIGTERM\n\n"
        "# Check if npm dependencies are installed\n"
        "if [ ! -d \"frontend/vuejs/node_modules\" ]; then\n"
        "    echo \"📦 Installing frontend dependencies...\"\n"
        "    cd frontend/vuejs && npm install && cd ../..\n"
        "fi\n\n"
        "# Start Django backend\n"
        "echo \"🐍 Starting Django backend on port 8000...\"\n"
        "cd backend/django && python manage.py runserver &\n"
        "DJANGO_PID=$!\n\n"
        "# Wait a moment for Django to start\n"
        "sleep 3\n\n"
        "# Start Vue frontend  \n"
        "echo \"⚡ Starting Vue frontend on port 5173...\"\n"
        "cd frontend/vuejs && npm run dev &\n"
        "VUE_PID=$!\n\n"
        "echo \"\"\n"
        "echo \"✅ Development servers started!\"\n"
        "echo \"🌐 Frontend: http://localhost:5173\"\n"
        "echo \"🔧 Backend API: http://localhost:8000\"\n"
        "echo \"📱 Press Ctrl+C to stop both servers\"\n\n"
        "# Wait for background processes\n"
        "wait\n"
    )


# =============================
# Django Backend Templates
# =============================

def django_pipfile() -> str:
    return (
        "[[source]]\n"
        "url = \"https://pypi.org/simple\"\n"
        "verify_ssl = true\n"
        "name = \"pypi\"\n\n"
        "[packages]\n"
        "django = \"~=4.2.3\"\n"
        "djangorestframework = \"~=3.14.0\"\n"
        "django-cors-headers = \"~=4.1.0\"\n\n"
        "[dev-packages]\n\n"
        "[requires]\n"
        "python_version = \"3.10\"\n"
    )


def django_project_views() -> str:
    return (
        "from django.shortcuts import render\n"
        "from django.http import HttpResponse, JsonResponse\n"
        "from django.views.generic import TemplateView\n\n"
        "def home(request):\n"
        "    \"\"\"Home page view.\"\"\"\n"
        "    return JsonResponse({\n"
        "        'message': 'Django backend is running!',\n"
        "        'status': 'success'\n"
        "    })\n\n"
        "class HomeView(TemplateView):\n"
        "    \"\"\"Class-based home page view.\"\"\"\n"
        "    template_name = 'index.html'\n"
    )


def django_base_template(project_name: str) -> str:
    return (
        f"<!DOCTYPE html>\n"
        f"<html lang=\"en\">\n"
        f"<head>\n"
        f"    <meta charset=\"UTF-8\">\n"
        f"    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
        f"    <title>{{% block title %}}{project_name}{{% endblock %}}</title>\n"
        f"    <link rel=\"stylesheet\" href=\"{{% static 'css/styles.css' %}}\">\n"
        f"    {{% block extra_css %}}{{% endblock %}}\n"
        f"</head>\n"
        f"<body>\n"
        f"    {{% block content %}}{{% endblock %}}\n\n"
        f"    {{% block extra_js %}}{{% endblock %}}\n"
        f"</body>\n"
        f"</html>\n"
    )


def django_index_template(project_name: str, project_description: str | None) -> str:
    safe_project_name = project_name.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
    safe_description = (project_description or '').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
    description_content = ''
    if (project_description or '').strip():
        description_content = f"    <p class=\"project-description\">{safe_description}</p>"
    return (
        "{% extends 'base.html' %}\n"
        "{% load static %}\n\n"
        "{% block title %}Welcome | "
        + safe_project_name
        + "{% endblock %}\n\n"
        "{% block content %}\n"
        "<div class=\"welcome-container\">\n"
        "    <h1>Welcome to "
        + safe_project_name
        + "</h1>\n"
        + description_content
        + "\n    <p>This is your Django backend API. The frontend is served separately on port 5173.</p>\n"
        "    <div class=\"cta-button\">\n"
        "        <a href=\"/admin/\">Go to Admin</a>\n"
        "        <a href=\"/api/\">Browse API</a>\n"
        "    </div>\n"
        "</div>\n"
        "{% endblock %}\n"
    )


def django_static_css() -> str:
    return (
        "/* Django Backend Styles */\n"
        ":root {\n"
        "    --primary-color: #4f46e5;\n"
        "    --secondary-color: #818cf8;\n"
        "    --text-color: #1f2937;\n"
        "    --bg-color: #ffffff;\n"
        "}\n\n"
        "body {\n"
        "    font-family: system-ui, -apple-system, sans-serif;\n"
        "    color: var(--text-color);\n"
        "    background-color: var(--bg-color);\n"
        "    line-height: 1.5;\n"
        "    margin: 0;\n"
        "    padding: 0;\n"
        "}\n\n"
        ".welcome-container {\n"
        "    max-width: 800px;\n"
        "    margin: 5rem auto;\n"
        "    padding: 2rem;\n"
        "    background-color: #f9fafb;\n"
        "    border-radius: 0.5rem;\n"
        "    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);\n"
        "    text-align: center;\n"
        "}\n\n"
        "h1 {\n"
        "    color: var(--primary-color);\n"
        "    margin-bottom: 1rem;\n"
        "}\n\n"
        ".project-description {\n"
        "    font-size: 1.125rem;\n"
        "    color: #6b7280;\n"
        "    margin: 1.5rem 0;\n"
        "    font-style: italic;\n"
        "    line-height: 1.6;\n"
        "}\n\n"
        ".cta-button {\n"
        "    margin-top: 2rem;\n"
        "    display: flex;\n"
        "    gap: 1rem;\n"
        "    justify-content: center;\n"
        "    flex-wrap: wrap;\n"
        "}\n\n"
        ".cta-button a {\n"
        "    display: inline-block;\n"
        "    background-color: var(--primary-color);\n"
        "    color: white;\n"
        "    padding: 0.75rem 1.5rem;\n"
        "    border-radius: 0.375rem;\n"
        "    text-decoration: none;\n"
        "    font-weight: 500;\n"
        "    transition: background-color 0.2s;\n"
        "}\n\n"
        ".cta-button a:hover {\n"
        "    background-color: var(--secondary-color);\n"
        "}\n"
    )


# =============================
# Files for API app
# =============================

def api_apps_py() -> str:
    return (
        "from django.apps import AppConfig\n\n"
        "class ApiConfig(AppConfig):\n"
        "    default_auto_field = 'django.db.models.BigAutoField'\n"
        "    name = 'api'\n"
    )


def api_models_py() -> str:
    return (
        "from django.db import models\n\n"
        "class HealthCheck(models.Model):\n"
        "    \"\"\"Simple model for API health checks\"\"\"\n"
        "    timestamp = models.DateTimeField(auto_now_add=True)\n"
        "    status = models.CharField(max_length=20, default='healthy')\n\n"
        "    def __str__(self):\n"
        "        return f\"Health check at {self.timestamp}\"\n"
    )


def api_serializers_py() -> str:
    return (
        "from rest_framework import serializers\n"
        "from .models import HealthCheck\n\n"
        "class HealthCheckSerializer(serializers.ModelSerializer):\n"
        "    class Meta:\n"
        "        model = HealthCheck\n"
        "        fields = ['id', 'timestamp', 'status']\n"
    )


def api_views_py() -> str:
    return (
        "from rest_framework.decorators import api_view\n"
        "from rest_framework.response import Response\n"
        "from rest_framework import status\n"
        "from .models import HealthCheck\n"
        "from .serializers import HealthCheckSerializer\n\n"
        "@api_view(['GET'])\n"
        "def health_check(request):\n"
        "    \"\"\"Health check endpoint for frontend to test API connection\"\"\"\n"
        "    health = HealthCheck.objects.create()\n"
        "    serializer = HealthCheckSerializer(health)\n\n"
        "    return Response({\n"
        "        'status': 'healthy',\n"
        "        'message': 'Django backend is running successfully!',\n"
        "        'data': serializer.data\n"
        "    }, status=status.HTTP_200_OK)\n\n"
        "@api_view(['GET', 'POST'])\n"
        "def example_endpoint(request):\n"
        "    \"\"\"Example API endpoint\"\"\"\n"
        "    if request.method == 'GET':\n"
        "        return Response({\n"
        "            'message': 'This is a GET request to the Django API',\n"
        "            'data': {'example': 'data'}\n"
        "        })\n"
        "    elif request.method == 'POST':\n"
        "        return Response({\n"
        "            'message': 'This is a POST request to the Django API',\n"
        "            'received_data': request.data\n"
        "        })\n"
    )


def api_urls_py() -> str:
    return (
        "from django.urls import path, include\n\n"
        "urlpatterns = [\n"
        "    path('v1/', include('api.v1.url')),\n"
        "]\n"
    )


def api_v1_url_py() -> str:
    return (
        "from django.http import JsonResponse\n"
        "from django.urls import path\n\n"
        "def health(_request):\n"
        "    return JsonResponse({\n"
        "        'status': 'healthy',\n"
        "        'message': 'Django backend is running successfully!'\n"
        "    })\n\n"
        "urlpatterns = [\n"
        "    path('health/', health, name='health'),\n"
        "]\n"
    )


def api_admin_py() -> str:
    return (
        "from django.contrib import admin\n"
        "from .models import HealthCheck\n\n"
        "@admin.register(HealthCheck)\n"
        "class HealthCheckAdmin(admin.ModelAdmin):\n"
        "    list_display = ['id', 'timestamp', 'status']\n"
        "    list_filter = ['status', 'timestamp']\n"
        "    readonly_fields = ['timestamp']\n"
    )


# =============================
# Miscellaneous project templates
# =============================

def fullstack_gitignore() -> str:
    return (
        "# Python\n"
        "__pycache__/\n"
        "*.py[cod]\n"
        "*$py.class\n"
        "*.so\n"
        ".Python\n"
        "env/\n"
        "build/\n"
        "develop-eggs/\n"
        "dist/\n"
        "downloads/\n"
        "eggs/\n"
        ".eggs/\n"
        "lib/\n"
        "lib64/\n"
        "parts/\n"
        "sdist/\n"
        "var/\n"
        "*.egg-info/\n"
        ".installed.cfg\n"
        "*.egg\n\n"
        "# Django\n"
        "*.log\n"
        "local_settings.py\n"
        "db.sqlite3\n"
        "db.sqlite3-journal\n"
        "media\n\n"
        "# Virtual Environment\n"
        "venv/\n"
        "ENV/\n\n"
        "# Node.js\n"
        "node_modules/\n"
        "npm-debug.log*\n"
        "yarn-debug.log*\n"
        "yarn-error.log*\n\n"
        "# IDE\n"
        ".idea/\n"
        ".vscode/\n"
        "*.swp\n"
        "*.swo\n\n"
        "# macOS\n"
        ".DS_Store\n\n"
        "# Windows\n"
        "Thumbs.db\n\n"
        "# Build outputs\n"
        "dist/\n"
        ".nuxt/\n"
        ".next/\n"
        "out/\n\n"
        "# Environment variables\n"
        ".env\n"
        ".env.local\n"
        ".env.development.local\n"
        ".env.test.local\n"
        ".env.production.local\n"
    )


def fullstack_readme(project_name: str, project_description: str | None) -> str:
    return (
        f"# {project_name}\n\n"
        f"{project_description or 'A full-stack web application with VueJS frontend and Django backend.'}\n\n"
        f"## Tech Stack\n\n"
        f"### Frontend\n"
        f"- **Vue 3** with Composition API\n"
        f"- **Vite** for fast development and building\n"
        f"- **TailwindCSS** for styling\n"
        f"- **Pinia** for state management\n"
        f"- **Axios** for API communication\n"
        f"- **TypeScript** for type safety\n\n"
        f"### Backend\n"
        f"- **Django 4.x** web framework\n"
        f"- **Django REST Framework** for API development\n"
        f"- **SQLite** database (development)\n"
        f"- **CORS** enabled for frontend communication\n\n"
        f"## Getting Started\n\n"
        f"### Prerequisites\n\n"
        f"- Node.js >= 16.x\n"
        f"- Python >= 3.10\n"
        f"- pipenv\n\n"
        f"### Installation\n\n"
        f"1. **Frontend dependencies are automatically installed in the background during project creation.**\n"
        f"   You can start development immediately - dependencies will install while you work.\n"
        f"   If you need to reinstall them manually:\n"
        f"   ```bash\n"
        f"   cd frontend/vuejs\n"
        f"   npm install\n"
        f"   ```\n\n"
        f"2. **Install backend dependencies:**\n"
        f"   ```bash\n"
        f"   cd backend/django\n"
        f"   pipenv install\n"
        f"   ```\n\n"
        f"3. **Setup Django database:**\n"
        f"   ```bash\n"
        f"   cd backend/django\n"
        f"   pipenv shell\n"
        f"   python manage.py migrate\n"
        f"   python manage.py createsuperuser  # Optional\n"
        f"   ```\n\n"
        f"### Development\n\n"
        f"**Start both servers using the included script:**\n\n"
        f"```bash\n"
        f"./start-dev.sh\n"
        f"```\n\n"
        f"**Or start them separately:**\n\n"
        f"**Frontend (VueJS + Vite):**\n"
        f"```bash\n"
        f"cd frontend/vuejs\n"
        f"npm run dev\n"
        f"```\n"
        f"Frontend will be available at: http://localhost:5173\n\n"
        f"**Backend (Django):**\n"
        f"```bash\n"
        f"cd backend/django\n"
        f"pipenv shell\n"
        f"python manage.py runserver\n"
        f"```\n"
        f"Backend API will be available at: http://localhost:8000\n\n"
        f"### API Endpoints\n\n"
        f"- `GET /api/v1/health/` - Health check endpoint\n\n"
        f"### Project Structure\n\n"
        f"```\n"
        f"{project_name}/\n"
        f"├── frontend/vuejs/          # VueJS frontend application\n"
        f"│   ├── src/\n"
        f"│   │   ├── components/      # Vue components\n"
        f"│   │   ├── views/          # Page views\n"
        f"│   │   ├── stores/         # Pinia stores\n"
        f"│   │   └── services/       # API services\n"
        f"│   └── package.json\n"
        f"├── backend/django/         # Django backend application\n"
        f"│   ├── api/               # Django API app\n"
        f"│   ├── {project_name}/    # Django project settings\n"
        f"│   └── manage.py\n"
        f"└── README.md\n"
        f"```\n\n"
        f"## Building for Production\n\n"
        f"**Frontend:**\n"
        f"```bash\n"
        f"cd frontend/vuejs\n"
        f"npm run build\n"
        f"```\n\n"
        f"**Backend:**\n"
        f"Configure production settings and deploy using your preferred method.\n"
    )


# =============================
# Legacy/basic helpers
# =============================

def basic_model_py() -> str:
    return """from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
"""


def basic_views_py() -> str:
    return '''from django.shortcuts import render
from django.http import JsonResponse
from .models import Item

def index(request):
    # Render the index page
    items = Item.objects.all()
    return render(request, 'core/index.html', {'items': items})

def item_list(request):
    # Return a JSON list of items
    items = Item.objects.all().values('id', 'name', 'description')
    return JsonResponse({'items': list(items)})
'''


def basic_urls_py() -> str:
    return """from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/items/', views.item_list, name='item-list'),
]
"""


def basic_project_urls_py() -> str:
    return """from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
]
"""


def basic_project_views_py() -> str:
    return '''from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView

def home(request):
    # Home page view.
    return render(request, 'index.html')

class HomeView(TemplateView):
    # Class-based home page view.
    template_name = 'index.html'
'''


def basic_manage_py(project_name: str) -> str:
    return f"""#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{project_name}.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
"""


def basic_settings_py(project_name: str) -> str:
    secret_key = ''.join(['x' for _ in range(50)])
    return f"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '{secret_key}'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = '{project_name}.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = '{project_name}.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
"""
