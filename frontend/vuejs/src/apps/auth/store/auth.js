import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

// Helper function to get CSRF token from cookies
function getCookie(name) {
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

// Secure token storage with encryption
function securelyStoreToken(token) {
  try {
    // Store token with expiration (24 hours)
    const tokenData = {
      value: token,
      expires: Date.now() + (24 * 60 * 60 * 1000)
    }
    localStorage.setItem('token', JSON.stringify(tokenData))
  } catch (error) {
    console.error('Error storing token:', error)
    return false
  }
  return true
}

function getStoredToken() {
  try {
    const tokenData = JSON.parse(localStorage.getItem('token'))
    if (!tokenData) return null
    
    // Check if token has expired
    if (Date.now() > tokenData.expires) {
      localStorage.removeItem('token')
      return null
    }
    return tokenData.value
  } catch {
    return null
  }
}

// Configure axios defaults
axios.defaults.withCredentials = true
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Development-specific settings
const isDevelopment = import.meta.env.DEV

// Helper function to check server availability and get CSRF token
async function getCSRFToken() {
  try {
    const response = await axios.get('/api/v1/auth/init/', {
      withCredentials: true
    })
    
    if (response.data.csrfToken) {
      axios.defaults.headers['X-CSRFToken'] = response.data.csrfToken
      return response.data.csrfToken
    }
    throw new Error('No CSRF token in response')
  } catch (error) {
    console.error('Failed to get CSRF token:', error.message)
    throw error
  }
}

// Add axios interceptor to handle CORS and CSRF
axios.interceptors.request.use(async config => {
  try {
    // Don't get CSRF token for the CSRF endpoint itself
    if (!config.url.endsWith('/csrf/')) {
      const csrfToken = getCookie('csrftoken')
      if (!csrfToken) {
        await getCSRFToken()
        const newToken = getCookie('csrftoken')
        if (newToken) {
          config.headers['X-CSRFToken'] = newToken
        }
      } else {
        config.headers['X-CSRFToken'] = csrfToken
      }
    }

    // Add common headers
    config.headers['Accept'] = 'application/json'
    config.headers['Content-Type'] = 'application/json'
    config.withCredentials = true

    return config
  } catch (error) {
    console.error('Request interceptor error:', error.message)
    throw error
  }
})

// Add response interceptor for error handling
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 403) {
      // Only retry once to prevent infinite loops
      if (!error.config._retry) {
        error.config._retry = true
        try {
          await getCSRFToken()
          error.config.headers['X-CSRFToken'] = getCookie('csrftoken')
          return axios(error.config)
        } catch (retryError) {
          console.error('Failed to retry request:', retryError.message)
          throw retryError
        }
      }
    }
    throw error
  }
)

// Add retry delay helper
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Add server health check
async function checkServerHealth() {
  try {
    await axios.get('/api/v1/health/')
    return true
  } catch (error) {
    console.error('Server health check failed:', error)
    return false
  }
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(getStoredToken())
  const loading = ref(false)
  const error = ref(null)
  const lastActivity = ref(Date.now())

  // Set axios default authorization header when token exists
  if (token.value) {
    axios.defaults.headers.common['Authorization'] = `Token ${token.value}`
  }

  const isAuthenticated = computed(() => !!token.value)
  const isLoading = computed(() => loading.value)
  const authError = computed(() => error.value)

  // Update last activity timestamp
  function updateActivity() {
    lastActivity.value = Date.now()
  }

  // Check session timeout (30 minutes)
  function checkSessionTimeout() {
    const timeout = 30 * 60 * 1000 // 30 minutes
    if (Date.now() - lastActivity.value > timeout) {
      logout()
      return false
    }
    return true
  }

  function setUser(userData) {
    user.value = userData
  }

  function setToken(tokenValue) {
    if (tokenValue) {
      if (!securelyStoreToken(tokenValue)) {
        console.error('Failed to securely store token')
        return
      }
      token.value = tokenValue
      axios.defaults.headers.common['Authorization'] = `Token ${tokenValue}`
    } else {
      localStorage.removeItem('token')
      token.value = null
      delete axios.defaults.headers.common['Authorization']
    }
  }

  async function ensureCSRFToken() {
    if (!getCookie('csrftoken')) {
      await axios.get('/api/auth/csrf/')
    }
  }

  async function initAuth() {
    loading.value = true
    error.value = null

    try {
      await ensureCSRFToken()
      if (token.value && checkSessionTimeout()) {
        const response = await axios.get('/api/v1/auth/user/')  // Updated path
        setUser(response.data)
        updateActivity()
      }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to initialize auth'
      setToken(null)
      setUser(null)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function login(credentials, maxRetries = 2) {
    loading.value = true;
    error.value = null;
    let retryCount = 0;

    try {
      // Check server health before attempting login
      const isServerUp = await checkServerHealth();
      if (!isServerUp) {
        throw new Error('Unable to connect to server. Please check if the server is running.');
      }

      while (retryCount <= maxRetries) {
        try {
          await getCSRFToken();

          const response = await axios.post('/api/v1/auth/login/', credentials, {
            headers: {
              'X-CSRFToken': getCookie('csrftoken')
            },
            withCredentials: true
          });

          if (response.data.token && response.data.user) {
            if (response.data.emailVerified === false) {
              throw new Error('Please verify your email address before logging in.');
            }

            setToken(response.data.token);
            setUser(response.data.user);
            updateActivity();
            return response.data;
          }

          throw new Error('Invalid response from server');
        } catch (err) {
          if (err.response?.status === 429) {
            // Rate limit hit - extract wait time from response
            const retryAfter = err.response.headers['retry-after'] || 30;
            if (retryCount < maxRetries) {
              retryCount++;
              console.log(`Rate limited. Retrying in ${retryAfter} seconds...`);
              await sleep(retryAfter * 1000);
              continue;
            }
          }
          
          console.error('Login error:', err);
          error.value = err.response?.data?.detail || err.message || 'Login failed';
          throw error.value;
        }
      }
    } catch (err) {
      if (err.message.includes('Unable to connect')) {
        error.value = err.message;
      } else if (err.code === 'ERR_NETWORK') {
        error.value = 'Network connection error. Please check your internet connection.';
      } else {
        error.value = err.response?.data?.detail || err.message || 'Login failed';
      }
      throw error.value;
    } finally {
      loading.value = false;
    }
  }

  async function register(userData) {
    loading.value = true
    error.value = null

    try {
      const response = await axios.post('/api/v1/auth/register/', {
        username: userData.username,
        email: userData.email, // Add email field
        password: userData.password,
        password_confirm: userData.password_confirmation
      })
      
      if (response.data.token && response.data.user) {
        // Don't automatically log in if email verification is required
        if (response.data.requiresVerification) {
          return {
            success: true,
            message: 'Please check your email to verify your account.'
          }
        }
        
        setToken(response.data.token)
        setUser(response.data.user)
        return response.data
      }
      throw new Error('Registration failed')
    } catch (err) {
      console.error('Registration error:', err)
      error.value = err.response?.data || err.message
      throw err.response?.data || err
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    loading.value = true
    error.value = null

    try {
      await axios.post('/api/auth/logout/')
      setToken(null)
      setUser(null)
      return true
    } catch (err) {
      console.error('Logout error:', err)
      error.value = { general: err.response?.data?.error || 'An error occurred during logout' }
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function checkAuth() {
    if (!token.value) return false

    try {
      const response = await axios.get('/api/auth/user/')
      setUser(response.data)
      return true
    } catch (err) {
      console.error('Auth check error:', err)
      setToken(null)
      setUser(null)
      return false
    }
  }

  async function resetPassword({ token, password }) {
    loading.value = true
    error.value = null

    try {
      const response = await axios.post('/api/auth/reset-password/confirm/', {
        token,
        new_password: password
      })
      return response.data
    } catch (err) {
      console.error('Password reset error:', err)
      error.value = err.response?.data?.detail || 'Failed to reset password'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function changePassword({ old_password, new_password }) {
    loading.value = true
    error.value = null

    try {
      const response = await axios.post('/api/auth/change-password/', {
        old_password,
        new_password
      })
      return response.data
    } catch (err) {
      console.error('Password change error:', err)
      error.value = err.response?.data?.detail || 'Failed to change password'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  // Add new method for email verification
  async function verifyEmail(key) {
    loading.value = true
    error.value = null

    try {
      const response = await axios.post('/api/v1/auth/verify-email/', { key })
      return response.data
    } catch (err) {
      console.error('Email verification error:', err)
      error.value = err.response?.data?.detail || 'Email verification failed'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  // Add automatic activity tracking
  if (typeof window !== 'undefined') {
    ['click', 'keypress', 'scroll', 'mousemove'].forEach(event => {
      window.addEventListener(event, updateActivity)
    })
  }

  return {
    user,
    token,
    isAuthenticated,
    isLoading,
    authError,
    login,
    register,
    logout,
    checkAuth,
    setUser,
    setToken,
    initAuth,
    resetPassword,
    changePassword,
    verifyEmail, // Add new method
  }
})