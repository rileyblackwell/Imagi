import axios, { AxiosHeaders } from 'axios'
import type { 
  InternalAxiosRequestConfig,
} from 'axios'
import type { 
  User, 
  LoginCredentials, 
  AuthResponse, 
  UserRegistrationData 
} from '@/apps/auth/types/auth'

// API Configuration
const API_PATH = '/api/v1/auth'
let BASE_URL = ''

// Determine base URL based on environment
const configureApiUrl = () => {
  const isProd = import.meta.env.PROD || import.meta.env.MODE === 'production'
  
  if (isProd) {
    // In production, always use relative URLs for browser requests
    // This ensures requests go through the Nginx proxy
    console.log('🔄 API: Configuring for production - using relative URLs')
    BASE_URL = API_PATH
  } else {
    // In development, we might need the full backend URL for local development
    const backendUrl = import.meta.env.VITE_BACKEND_URL || ''
    if (backendUrl) {
      console.log(`🔄 API: Using backend URL from env: ${backendUrl}`)
      BASE_URL = `${backendUrl}${API_PATH}`
    } else {
      console.log('🔄 API: Using relative URL (no backend URL configured)')
      BASE_URL = API_PATH
    }
  }
  
  console.log(`🔄 API: Configured BASE_URL: ${BASE_URL}`)
}

// Initialize the API URL configuration
configureApiUrl()

// Helper function to get CSRF token from cookies
function getCookie(name: string): string | null {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

// Setup axios interceptors for auth
const setupAxiosInterceptors = () => {
  // Add request interceptor
  axios.interceptors.request.use(
    async (config: InternalAxiosRequestConfig) => {
      // Create proper AxiosHeaders instance
      const headers = new AxiosHeaders({
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      })
      
      // Add CSRF token if not already present
      const csrfToken = getCookie('csrftoken')
      if (csrfToken) {
        headers.set('X-CSRFToken', csrfToken)
      }
      
      // Add Authorization header if token exists
      const tokenData = localStorage.getItem('token')
      if (tokenData) {
        try {
          const parsedToken = JSON.parse(tokenData)
          if (parsedToken?.value && Date.now() < parsedToken.expires) {
            headers.set('Authorization', `Token ${parsedToken.value}`)
          } else {
            // Token expired, remove it
            localStorage.removeItem('token')
          }
        } catch (e) {
          console.error('Failed to parse token data:', e)
          localStorage.removeItem('token')
        }
      }
      
      config.headers = headers
      
      // Set reasonable timeout
      if (!config.timeout) {
        config.timeout = 30000 // 30 seconds default timeout
      }
      
      return config
    },
    error => Promise.reject(error)
  )

  // Add response interceptor
  axios.interceptors.response.use(
    response => {
      // Add CORS debugging - log successful responses
      // console.log('API Response:', {
      //   url: response.config.url,
      //   status: response.status,
      //   headers: response.headers,
      //   data: response.data
      // });
      return response;
    },
    async error => {
      // Enhanced CORS debugging - log detailed error information
      // if (error.response) {
      //   console.error('API Error Response:', {
      //     url: error.config?.url,
      //     status: error.response.status,
      //     statusText: error.response.statusText,
      //     headers: error.response.headers,
      //     data: error.response.data,
      //     method: error.config?.method,
      //     requestHeaders: error.config?.headers
      //   });
      // } else {
      //   console.error('Network Error (No Response):', {
      //     url: error.config?.url,
      //     method: error.config?.method,
      //     message: error.message,
      //     code: error.code,
      //     requestHeaders: error.config?.headers
      //   });
      // }
      
      // Handle request timeout
      if (error.code === 'ECONNABORTED') {
        console.error('Request timed out:', error.config?.url)
        return Promise.reject(new Error('Network Error: Request timed out'))
      }
      
      // Handle network errors
      if (!error.response) {
        console.error('Network error:', error)
        return Promise.reject(new Error('Network Error: Unable to connect to server'))
      }
      
      // Handle 403 (CSRF) errors
      if (error.response?.status === 403 && !error.config._retry) {
        error.config._retry = true
        try {
          console.log('Getting new CSRF token due to 403 error')
          await AuthAPI.getCSRFToken()
          const newToken = getCookie('csrftoken')
          if (newToken) {
            error.config.headers['X-CSRFToken'] = newToken
          }
          return axios(error.config)
        } catch (retryError) {
          console.error('Failed to retry with new CSRF token:', retryError)
          return Promise.reject(retryError)
        }
      }
      
      // Handle 401 (Unauthorized) errors
      if (error.response?.status === 401) {
        console.log('Unauthorized request. Clearing auth data')
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        delete axios.defaults.headers.common['Authorization']
        
        // Only redirect to home if not already on an auth page
        const currentPath = window.location.pathname
        if (!currentPath.startsWith('/auth/')) {
          console.log('Redirecting to home from', currentPath)
          window.location.href = '/'
        }
      }
      
      return Promise.reject(error)
    }
  )
}

// Initialize interceptors
setupAxiosInterceptors()

let logoutPromise: Promise<any> | null = null

export const AuthAPI = {
  async getCSRFToken() {
    // Check if we're in production environment
    const isProd = import.meta.env.PROD || import.meta.env.MODE === 'production'
    const environment = isProd ? 'production' : 'development'
    
    // In production environment, we can bypass CSRF for API calls that go through Nginx
    if (isProd) {
      console.log('🔐 Production environment detected - CSRF checks handled by Nginx proxy')
      return { data: { csrf: 'production-bypass' } }
    }
    
    // For development environments, get a real CSRF token
    try {
      // Use a shorter timeout for CSRF token requests
      return await axios.get(`${BASE_URL}/csrf/`, {
        withCredentials: true,
        timeout: 10000 // 10 seconds timeout
      })
    } catch (error) {
      console.error('🔑 Failed to get CSRF token:', error)
      // If in production but failed for some reason, still allow requests to proceed
      if (isProd) {
        return { data: { csrf: 'production-bypass' } }
      }
      throw error
    }
  },

  async ensureCSRFToken(): Promise<string | null> {
    // Check if we're in a production environment
    const isProd = import.meta.env.PROD || import.meta.env.MODE === 'production'
    const environment = isProd ? 'production' : 'development'
    
    // In production environment, bypass CSRF token requirement - handled by Nginx
    if (isProd) {
      console.log('🔐 Production environment - bypassing CSRF requirement')
      return 'production-bypass'
    }
    
    try {
      // For development environments, check if CSRF token already exists in cookies
      let csrfToken = getCookie('csrftoken')
      
      // If no token, fetch a new one
      if (!csrfToken) {
        console.log('🔄 No CSRF token found, fetching a new one')
        const response = await this.getCSRFToken()
        
        // Check if we got a bypass token from the response
        if (response?.data?.csrf === 'production-bypass') {
          return 'production-bypass'
        }
        
        csrfToken = getCookie('csrftoken')
        if (!csrfToken) {
          console.error('⚠️ No CSRF token received')
          return null
        }
      }
      
      return csrfToken
    } catch (error) {
      console.error('❌ Error fetching CSRF token:', error)
      
      // If in production but failed for some reason, still allow requests to proceed
      if (isProd) {
        console.log('🔄 Error occurred but running in production environment - bypassing CSRF')
        return 'production-bypass'
      }
      return null
    }
  },

  async init(): Promise<{ data: { isAuthenticated: boolean; user: User } }> {
    const isProd = import.meta.env.PROD || import.meta.env.MODE === 'production';
    const url = isProd ? '/api/v1/auth/me/' : `${BASE_URL}/me/`;
    return await axios.get(url, { withCredentials: true })
  },

  async login(credentials: LoginCredentials): Promise<{ data: AuthResponse }> {
    const isProd = import.meta.env.PROD || import.meta.env.MODE === 'production';
    try {
      if (!credentials?.username || !credentials?.password) {
        throw new Error('Username and password are required')
      }

      // Make sure we have a CSRF token before attempting login
      const csrfToken = await this.ensureCSRFToken();
      if (!csrfToken) {
        console.error('Could not obtain CSRF token');
        throw new Error('Authentication error: Could not obtain security token');
      }
      
      // Call the actual login API endpoint with the correct URL based on environment
      const loginUrl = isProd ? '/api/v1/auth/login/' : `${BASE_URL}/login/`;
      console.log('🔑 AuthAPI: Sending login request to:', loginUrl);
      
      const response = await axios.post(loginUrl, credentials, {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        withCredentials: true,
        // Add timeout to prevent hanging requests
        timeout: 15000
      });

      // Validate response format
      if (!response.data) {
        throw new Error('Invalid server response: Empty response')
      }
      
      if (!response.data.token && !response.data.key) {
        console.error('Login response missing token:', response.data);
        throw new Error('Invalid server response: Missing token')
      }

      return { 
        data: {
          token: response.data.token || response.data.key,
          user: response.data.user || {}
        }
      }
    } catch (error: any) {
      console.error('Login error details:', error);
      
      // Handle network errors
      if (error.code === 'ECONNABORTED' || !error.response) {
        throw new Error('Network Error')
      }
      
      // Handle specific status codes with clear messages
      if (error.response?.status === 401) {
        throw new Error('Invalid credentials')
      }
      
      if (error.response?.status === 400) {
        const errorData = error.response.data
        
        // Check for error structure from backend
        if (errorData.error) {
          throw new Error(errorData.error)
        }
        
        if (errorData.detail) {
          // Check if detail is an object with field-specific errors
          if (typeof errorData.detail === 'object') {
            throw error // Pass the original error to preserve structure
          }
          throw new Error(errorData.detail)
        }
        
        if (errorData.non_field_errors?.[0]) {
          throw new Error(errorData.non_field_errors[0])
        }
        
        throw new Error('Invalid credentials')
      }
      
      // Fallback for other errors
      throw error
    }
  },

  async register(userData: UserRegistrationData): Promise<{ data: AuthResponse }> {
    // Check if we're in production Railway environment
    const isProd = import.meta.env.PROD || import.meta.env.MODE === 'production'
    const environment = isProd ? 'production' : 'development'
    const isRailway = import.meta.env.VITE_BACKEND_URL?.includes('.railway.internal') || false
    try {
      console.log('🔄 AuthAPI: Starting registration request')
      console.log('🌐 API Environment:', {
        axiosBaseUrl: axios.defaults.baseURL || 'Not set', // Where axios sends requests
        apiBaseUrl: BASE_URL, // Full API base URL used for requests
        apiPath: API_PATH, // API path component
        viteBackendEnv: import.meta.env.VITE_BACKEND_URL || 'Not defined', // Vite env variable
        environment: import.meta.env.MODE,
        isProd
      })
      
      // Ensure CSRF token is available
      console.log('🔑 AuthAPI: Getting CSRF token')
      const csrfToken = await this.ensureCSRFToken()
      console.log('🔑 AuthAPI: CSRF token obtained:', csrfToken ? 'Yes' : 'No')
      if (!csrfToken && !isProd) {
        console.error('Could not obtain CSRF token')
        throw new Error('Registration error: Could not obtain security token');
      }
      
      // Validate username (basic check only, server will check uniqueness)
      if (!userData.username || userData.username.trim() === '') {
        throw new Error('Username is required')
      }
      
      // Validate password requirements
      if (!userData.password || userData.password.length < 8) {
        throw new Error('Password must be at least 8 characters long')
      }
      
      // Confirm password matches confirmation
      if (userData.password !== userData.password_confirmation) {
        throw new Error('Passwords do not match')
      }
      
      // Validate terms acceptance
      if (!userData.terms_accepted) {
        throw new Error('You must accept the terms and conditions')
      }

      // Validate email format only (remove uniqueness check)
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(userData.email)) {
        throw new Error('Please enter a valid email address')
      }
      
      console.log('✅ AuthAPI: Client-side validation passed')

      // Prepare headers with proper handling for Railway environment
      const headers: Record<string, string> = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
      
      // Only add CSRF token if we have one and it's not the production-bypass placeholder
      if (csrfToken && csrfToken !== 'production-bypass') {
        headers['X-CSRFToken'] = csrfToken
      }
      
      // Log API request details
      console.log('📣 AuthAPI: Preparing request to', `${BASE_URL}/register/`, {
        headers,
        withCredentials: true,
        isProd
      })
      
      // We've already checked isProd earlier
      if (isProd) {
        console.log('🚀 AuthAPI: Running in production environment', {
          timeout: '30 seconds'
        })
      } else {
        console.log('💻 AuthAPI: Running in local/dev environment', {
          baseUrl: BASE_URL,
          timeout: '15 seconds'
        })
      }
      
      // Create timer for request duration measurement
      const startTime = performance.now();
      
      // For production, make the request path relative to ensure it goes through Nginx proxy
      // This is the critical fix that ensures requests don't go directly to backend.railway.internal
      const fullRequestUrl = isProd ? '/api/v1/auth/register/' : `${BASE_URL}/register/`;
      console.log('📤 AuthAPI: Sending request to:', fullRequestUrl);
      
      try {
        const response = await axios.post(fullRequestUrl, userData, {
          headers,
          withCredentials: true,
          // Increase timeout for production environments
          timeout: isProd 
            ? 30000 // 30 seconds for production
            : 15000 // 15 seconds for development environments
        })
        
        const duration = Math.round(performance.now() - startTime);
        console.log(`⏰ AuthAPI: Request completed in ${duration}ms`);
        
        // Log response status and structure (without sensitive data)
        console.log('✅ AuthAPI: Registration API response successful', {
          status: response.status,
          hasData: !!response.data,
          hasToken: !!(response.data?.token || response.data?.key),
          hasUser: !!response.data?.user
        })

      // Validate response format
      if (!response.data) {
        console.error('❌ AuthAPI: Empty response data')
        throw new Error('Invalid server response: Empty response')
      }
      
      if (!response.data.token && !response.data.key) {
        console.error('❌ AuthAPI: Missing token in response', response.data)
        throw new Error('Invalid server response: Missing token')
      }
      
      console.log('🔐 AuthAPI: Token received successfully')

      return { 
        data: {
          token: response.data.token || response.data.key,
          user: response.data.user || {}
        }
      }
    } catch (error) {
      // Connection issues during the request
      console.error('❌ AuthAPI: Error during API call', error)
      throw error
    }
    } catch (error: any) {
      // Handle network errors with detailed logging
      if (error.code === 'ECONNABORTED') {
        console.error('❌ AuthAPI: Request timeout error', {
          url: `${BASE_URL}/register/`,
          timeout: error.config?.timeout || 'unknown'
        })
        throw new Error('Network Error: Connection timed out')
      } else if (!error.response) {
        // Log full network error details
        console.error('❌ AuthAPI: Network connection error', {
          code: error.code || 'unknown',
          message: error.message || 'No error message',
          backendUrl: import.meta.env.VITE_BACKEND_URL || 'Not defined',
          apiUrl: `${BASE_URL}/register/`, 
          config: error.config ? {
            baseURL: error.config.baseURL,
            url: error.config.url,
            method: error.config.method,
            headers: error.config.headers,
            timeout: error.config.timeout
          } : 'No config available'
        })
        throw new Error('Network Error: Unable to connect to the server')
      }
      
      if (error.response?.status === 400) {
        const errorData = error.response.data
        
        // Check for error structure from backend
        if (errorData.error) {
          throw new Error(errorData.error)
        }
        
        if (errorData.detail) {
          // Check if detail is an object with field-specific errors
          if (typeof errorData.detail === 'object') {
            throw error // Pass the original error to preserve structure
          }
          throw new Error(errorData.detail)
        }
        
        // Handle specific field errors
        if (errorData.username) {
          // Make it clear this is a uniqueness error
          const usernameError = Array.isArray(errorData.username) ? errorData.username[0] : errorData.username;
          if (usernameError.includes('already') || usernameError.includes('taken')) {
            throw new Error('This username is already taken. Please choose another one.')
          }
          throw new Error(usernameError)
        }
        
        if (errorData.email) {
          throw new Error(Array.isArray(errorData.email) ? errorData.email[0] : errorData.email)
        }
        
        if (errorData.password) {
          throw new Error(Array.isArray(errorData.password) ? errorData.password[0] : errorData.password)
        }
        
        if (errorData.non_field_errors?.[0]) {
          throw new Error(errorData.non_field_errors[0])
        }
        
        throw new Error('Registration failed')
      }
      
      // Fallback for other errors
      throw error
    }
  },

  async logout(): Promise<void> {
    if (logoutPromise) {
      return logoutPromise
    }

    const isProd = import.meta.env.PROD || import.meta.env.MODE === 'production';
    const logoutUrl = isProd ? '/api/v1/auth/logout/' : `${BASE_URL}/logout/`;

    try {
      logoutPromise = axios.post(logoutUrl, {}, {
        withCredentials: true
      })
      await logoutPromise
      
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    } catch (error) {
      console.error('Logout error:', error)
      throw error
    } finally {
      logoutPromise = null
    }
  },

  async updateUser(userData: Partial<User>): Promise<{ data: User }> {
    const isProd = import.meta.env.PROD || import.meta.env.MODE === 'production';
    const updateUrl = isProd ? '/api/v1/auth/user/' : `${BASE_URL}/user/`;
    const response = await axios.patch(updateUrl, userData, { withCredentials: true })
    return response
  }
}
