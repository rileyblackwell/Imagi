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
        "  // Keep Vite's dep-optimization cache inside the project rather than\n"
        "  // under node_modules/.vite. Generated projects share one installed\n"
        "  // node_modules (symlinked to a common store), so a node_modules-local\n"
        "  // cache would let concurrent dev servers clobber each other.\n"
        "  cacheDir: path.resolve(__dirname, '.vite-cache'),\n"
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
        "    // 5174 keeps generated apps clear of the main Imagi dev server on 5173;\n"
        "    // the Imagi preview runner overrides this with an explicit --port flag.\n"
        "    port: 5174,\n"
        "    strictPort: false, // Fall through to the next free port instead of failing\n"
        "    hmr: {\n"
        "      overlay: false, // Disable the HMR error overlay to prevent URI errors from breaking the UI\n"
        "    },\n"
        "    proxy: {\n"
        "      // Proxy all API requests to this app's own Django backend.\n"
        "      // The Imagi preview runner sets VITE_BACKEND_URL to the port it started\n"
        "      // the backend on; the fallback matches start-dev.sh (8080, not the main\n"
        "      // Imagi backend on 8000).\n"
        "      '/api': {\n"
        "        target: process.env.VITE_BACKEND_URL || 'http://localhost:8080',\n"
        "        changeOrigin: true,\n"
        "        secure: false,\n"
        "        configure: (proxy, _options) => {\n"
        "          const backendUrl = process.env.VITE_BACKEND_URL || 'http://localhost:8080';\n\n"
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
        r"""
# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]
# The dev server port is assigned dynamically (5174+), so accept any localhost port
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://(localhost|127\.0\.0\.1):\d+$",
]

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Allow all for development
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
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
declare module 'vue' {
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
    // App routes discovered via glob import (includes home at '/')
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

  // Method to check auth status without side effects
  const checkAuth = async (): Promise<boolean> => {
    // Use cached value if available and recent
    const now = Date.now()
    if (initialized.value && (now - lastInitTime.value) < AUTH_CACHE_DURATION) {
      return isAuthenticated.value
    }

    // If there's a pending auth check, return that promise
    if (pendingAuthCheck.value) {
      return pendingAuthCheck.value
    }

    if (!token.value) return false

    // Create a new auth check promise
    const authCheckPromise = (async () => {
      try {
        axios.defaults.headers.common['Authorization'] = `Token ${token.value}`
        const response = await api.get('/v1/auth/init/')
        const authStatus = !!response.data.isAuthenticated

        // Update the last check time
        lastInitTime.value = now
        return authStatus
      } catch {
        return false
      } finally {
        // Clear the pending auth check
        setTimeout(() => {
          pendingAuthCheck.value = null
        }, 0)
      }
    })()

    // Store the promise for reuse during concurrent calls
    pendingAuthCheck.value = authCheckPromise
    return authCheckPromise
  }

  const validateAuth = async () => {
    // Use cached value if available and recent
    const now = Date.now()
    if (initialized.value && (now - lastInitTime.value) < AUTH_CACHE_DURATION) {
      return isAuthenticated.value
    }

    // If there's a pending auth check, return that promise
    if (pendingAuthCheck.value) {
      return pendingAuthCheck.value
    }

    // Create a new auth check promise
    const authCheckPromise = (async () => {
      try {
        loading.value = true

        if (!token.value) {
          return false
        }

        axios.defaults.headers.common['Authorization'] = `Token ${token.value}`
        const response = await api.get('/v1/auth/init/')

        if (response.data.isAuthenticated) {
          // Update user data from server
          user.value = response.data.user
          isAuthenticated.value = true

          // Update stored user data
          localStorage.setItem('user', JSON.stringify(response.data.user))
          lastInitTime.value = now
          return true
        } else {
          // Do not clear auth on validation errors; preserve state and let callers decide.
          return false
        }
      } catch (error) {
        console.error('Auth validation error:', error)
        // Do not clear auth on validation errors; preserve state and let callers decide.
        return false
      } finally {
        loading.value = false
        // Clear the pending auth check
        setTimeout(() => {
          pendingAuthCheck.value = null
        }, 0)
      }
    })()

    // Store the promise for reuse during concurrent calls
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

  const refreshToken = async () => {
    try {
      const response = await api.post('/v1/auth/refresh-token/')
      if (response.data.token) {
        setAuthState(response.data.user, response.data.token)
        return true
      }
      return false
    } catch (error) {
      console.error('Token refresh failed:', error)
      return false
    }
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
    checkAuth,
    validateAuth,
    clearAuth,
    logout,
    refreshToken
  }
})
"""


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


# Canonical package.json for every generated frontend. Kept as a static asset
# (rather than inline here) so it is a single source of truth shared by the
# runtime scaffolder and the build-time dependency prewarm: the Docker image
# installs this exact dependency set once into the shared store, and every
# generated project then links against it instead of running its own install.
_FRONTEND_PACKAGE_JSON_PATH = os.path.join(
    os.path.dirname(__file__), 'assets', 'frontend_package.json'
)


def frontend_package_json(project_name: str) -> dict:
    """Return the canonical generated-frontend package.json for ``project_name``.

    Loads the shared asset and stamps in the per-project ``name``; every other
    field (the dependency set in particular) is identical across projects,
    which is what lets them share one installed ``node_modules``.
    """
    with open(_FRONTEND_PACKAGE_JSON_PATH, 'r') as f:
        package_json = json.load(f)
    package_json['name'] = f"{_sanitize_project_name(project_name).lower()}-frontend"
    return package_json


def create_vuejs_frontend_files(frontend_path: str, project_name: str, project_description: str | None) -> None:
    """Create VueJS frontend with Vite, Pinia, TailwindCSS, and Axios (vanilla JS)."""
    # package.json aligned with main Imagi frontend so all required packages are installed
    package_json = frontend_package_json(project_name)

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

    # env.d.ts — Vite client types so import.meta.env type-checks
    with open(os.path.join(src_path, 'env.d.ts'), 'w') as f:
        f.write('/// <reference types="vite/client" />\n')

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
        "# Ports 8080/5174 keep this app clear of the main Imagi dev servers (8000/5173)\n"
        "BACKEND_PORT=\"${BACKEND_PORT:-8080}\"\n"
        "FRONTEND_PORT=\"${FRONTEND_PORT:-5174}\"\n\n"
        "# Start Django backend\n"
        "echo \"🐍 Starting Django backend on port $BACKEND_PORT...\"\n"
        "cd backend/django && python manage.py runserver \"127.0.0.1:$BACKEND_PORT\" &\n"
        "DJANGO_PID=$!\n\n"
        "# Wait a moment for Django to start\n"
        "sleep 3\n\n"
        "# Start Vue frontend  \n"
        "echo \"⚡ Starting Vue frontend on port $FRONTEND_PORT...\"\n"
        "cd frontend/vuejs && VITE_BACKEND_URL=\"http://localhost:$BACKEND_PORT\" npm run dev -- --port \"$FRONTEND_PORT\" &\n"
        "VUE_PID=$!\n\n"
        "echo \"\"\n"
        "echo \"✅ Development servers started!\"\n"
        "echo \"🌐 Frontend: http://localhost:$FRONTEND_PORT\"\n"
        "echo \"🔧 Backend API: http://localhost:$BACKEND_PORT\"\n"
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
        "django = \"*\"\n"
        "djangorestframework = \"*\"\n"
        "django-cors-headers = \"*\"\n\n"
        "[dev-packages]\n\n"
        "[requires]\n"
        "python_version = \"3.13\"\n"
    )


def django_project_views() -> str:
    # The backend is API-only: all UI is served by the Vue frontend, so the
    # root view returns JSON instead of rendering a Django template.
    return (
        "from django.http import JsonResponse\n\n"
        "def home(request):\n"
        "    \"\"\"API root. The user interface is the Vue frontend, not Django.\"\"\"\n"
        "    return JsonResponse({\n"
        "        'message': 'Django backend is running!',\n"
        "        'status': 'success',\n"
        "        'api': '/api/'\n"
        "    })\n"
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
        ".vite-cache/\n"
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

def basic_project_urls_py() -> str:
    return """from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
]
"""


def basic_project_views_py() -> str:
    return '''from django.http import JsonResponse

def home(request):
    # API root. The user interface is served by the Vue frontend.
    return JsonResponse({'message': 'Django backend is running!', 'status': 'success'})
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
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
"""
