import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { getCookie, setCookie, removeCookie } from '../utils/auth';

const user = ref(null);
const loading = ref(false);
const error = ref(null);

export function useAuth() {
  const router = useRouter();

  // Computed properties
  const isAuthenticated = computed(() => !!user.value);
  const isLoading = computed(() => loading.value);
  const authError = computed(() => error.value);

  /**
   * Initialize auth state from stored token
   */
  async function initAuth() {
    const token = getCookie('auth_token');
    if (token) {
      try {
        const response = await axios.get('/api/auth/user/', {
          headers: { Authorization: `Bearer ${token}` }
        });
        user.value = response.data;
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      } catch (err) {
        console.error('Failed to initialize auth:', err);
        removeCookie('auth_token');
        user.value = null;
      }
    }
  }

  /**
   * Login user
   * @param {Object} credentials - User credentials
   * @param {string} credentials.email - User email
   * @param {string} credentials.password - User password
   */
  async function login(credentials) {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.post('/api/auth/login/', credentials);
      const { token, user: userData } = response.data;
      
      setCookie('auth_token', token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      user.value = userData;

      await router.push('/dashboard');
    } catch (err) {
      console.error('Login failed:', err);
      error.value = err.response?.data?.message || 'Login failed. Please try again.';
    } finally {
      loading.value = false;
    }
  }

  /**
   * Register new user
   * @param {Object} userData - User registration data
   * @param {string} userData.email - User email
   * @param {string} userData.password - User password
   * @param {string} userData.name - User full name
   */
  async function register(userData) {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.post('/api/auth/register/', userData);
      const { token, user: newUser } = response.data;

      setCookie('auth_token', token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      user.value = newUser;

      await router.push('/dashboard');
    } catch (err) {
      console.error('Registration failed:', err);
      error.value = err.response?.data?.message || 'Registration failed. Please try again.';
    } finally {
      loading.value = false;
    }
  }

  /**
   * Logout user
   */
  async function logout() {
    try {
      await axios.post('/api/auth/logout/');
    } catch (err) {
      console.error('Logout failed:', err);
    } finally {
      removeCookie('auth_token');
      delete axios.defaults.headers.common['Authorization'];
      user.value = null;
      await router.push('/');
    }
  }

  /**
   * Update user profile
   * @param {Object} profileData - Updated profile data
   */
  async function updateProfile(profileData) {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.patch('/api/auth/profile/', profileData);
      user.value = response.data;
    } catch (err) {
      console.error('Profile update failed:', err);
      error.value = err.response?.data?.message || 'Failed to update profile. Please try again.';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Change user password
   * @param {Object} passwordData - Password change data
   * @param {string} passwordData.old_password - Current password
   * @param {string} passwordData.new_password - New password
   */
  async function changePassword(passwordData) {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.post('/api/v1/auth/change-password/', passwordData);
      return response.data;
    } catch (err) {
      console.error('Password change failed:', err);
      error.value = err.response?.data?.errors || { detail: 'Failed to change password. Please try again.' };
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Request password reset
   * @param {string} email - User email
   */
  async function requestPasswordReset(email) {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.post('/api/v1/auth/reset-password/', { email });
      return response.data;
    } catch (err) {
      console.error('Password reset request failed:', err);
      error.value = err.response?.data?.errors || { detail: 'Failed to request password reset. Please try again.' };
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Reset password with token
   * @param {Object} resetData - Password reset data
   * @param {string} resetData.token - Reset token
   * @param {string} resetData.uid - User ID
   * @param {string} resetData.newPassword - New password
   * @param {string} resetData.confirmPassword - Confirm new password
   */
  async function resetPassword({ token, uid, newPassword, confirmPassword }) {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.post('/api/v1/auth/reset-password/confirm/', {
        token,
        uid,
        new_password1: newPassword,
        new_password2: confirmPassword
      });
      return response.data;
    } catch (err) {
      console.error('Password reset failed:', err);
      error.value = err.response?.data?.errors || { detail: 'Failed to reset password. Please try again.' };
      throw err;
    } finally {
      loading.value = false;
    }
  }

  return {
    user,
    isAuthenticated,
    isLoading,
    authError,
    initAuth,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    requestPasswordReset,
    resetPassword
  };
} 