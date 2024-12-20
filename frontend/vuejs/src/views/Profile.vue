<template>
  <div class="profile-page">
    <header class="page-header">
      <div class="container">
        <h1>Profile Settings</h1>
        <p class="text-muted">Manage your account settings and preferences</p>
      </div>
    </header>

    <main class="container">
      <div class="row">
        <!-- Sidebar Navigation -->
        <div class="col-md-3">
          <div class="nav-card">
            <div class="nav flex-column nav-pills">
              <button
                class="nav-link"
                :class="{ active: activeTab === 'profile' }"
                @click="activeTab = 'profile'"
              >
                <i class="fas fa-user"></i>
                Profile Information
              </button>
              <button
                class="nav-link"
                :class="{ active: activeTab === 'security' }"
                @click="activeTab = 'security'"
              >
                <i class="fas fa-lock"></i>
                Security
              </button>
              <button
                class="nav-link"
                :class="{ active: activeTab === 'preferences' }"
                @click="activeTab = 'preferences'"
              >
                <i class="fas fa-cog"></i>
                Preferences
              </button>
            </div>
          </div>
        </div>

        <!-- Main Content -->
        <div class="col-md-9">
          <div class="content-card">
            <!-- Profile Information Tab -->
            <div v-if="activeTab === 'profile'" class="tab-content">
              <h2>Profile Information</h2>
              <p class="text-muted mb-4">Update your personal information and profile settings</p>

              <form @submit.prevent="updateProfile">
                <div class="mb-3">
                  <label for="username" class="form-label">Username</label>
                  <input
                    type="text"
                    id="username"
                    v-model="profileForm.username"
                    class="form-control"
                    :class="{ 'is-invalid': profileErrors.username }"
                    required
                  />
                  <div v-if="profileErrors.username" class="invalid-feedback">
                    {{ profileErrors.username }}
                  </div>
                </div>

                <div class="mb-3">
                  <label for="email" class="form-label">Email Address</label>
                  <input
                    type="email"
                    id="email"
                    v-model="profileForm.email"
                    class="form-control"
                    :class="{ 'is-invalid': profileErrors.email }"
                    required
                  />
                  <div v-if="profileErrors.email" class="invalid-feedback">
                    {{ profileErrors.email }}
                  </div>
                </div>

                <div class="mb-3">
                  <label for="fullName" class="form-label">Full Name</label>
                  <input
                    type="text"
                    id="fullName"
                    v-model="profileForm.fullName"
                    class="form-control"
                  />
                </div>

                <div class="mb-3">
                  <label for="bio" class="form-label">Bio</label>
                  <textarea
                    id="bio"
                    v-model="profileForm.bio"
                    class="form-control"
                    rows="3"
                  ></textarea>
                </div>

                <div v-if="profileError" class="alert alert-danger">
                  {{ profileError }}
                </div>

                <div v-if="profileSuccess" class="alert alert-success">
                  {{ profileSuccess }}
                </div>

                <button type="submit" class="btn btn-primary" :disabled="profileLoading">
                  <span v-if="profileLoading" class="spinner-border spinner-border-sm me-1"></span>
                  Save Changes
                </button>
              </form>
            </div>

            <!-- Security Tab -->
            <div v-if="activeTab === 'security'" class="tab-content">
              <h2>Security Settings</h2>
              <p class="text-muted mb-4">Manage your password and security preferences</p>

              <form @submit.prevent="updatePassword">
                <div class="mb-3">
                  <label for="currentPassword" class="form-label">Current Password</label>
                  <input
                    type="password"
                    id="currentPassword"
                    v-model="passwordForm.currentPassword"
                    class="form-control"
                    :class="{ 'is-invalid': passwordErrors.currentPassword }"
                    required
                  />
                  <div v-if="passwordErrors.currentPassword" class="invalid-feedback">
                    {{ passwordErrors.currentPassword }}
                  </div>
                </div>

                <div class="mb-3">
                  <label for="newPassword" class="form-label">New Password</label>
                  <input
                    type="password"
                    id="newPassword"
                    v-model="passwordForm.newPassword"
                    class="form-control"
                    :class="{ 'is-invalid': passwordErrors.newPassword }"
                    required
                  />
                  <div v-if="passwordErrors.newPassword" class="invalid-feedback">
                    {{ passwordErrors.newPassword }}
                  </div>
                </div>

                <div class="mb-3">
                  <label for="confirmPassword" class="form-label">Confirm New Password</label>
                  <input
                    type="password"
                    id="confirmPassword"
                    v-model="passwordForm.confirmPassword"
                    class="form-control"
                    :class="{ 'is-invalid': !passwordsMatch }"
                    required
                  />
                  <div v-if="!passwordsMatch" class="invalid-feedback">
                    Passwords must match
                  </div>
                </div>

                <div v-if="passwordError" class="alert alert-danger">
                  {{ passwordError }}
                </div>

                <div v-if="passwordSuccess" class="alert alert-success">
                  {{ passwordSuccess }}
                </div>

                <button type="submit" class="btn btn-primary" :disabled="passwordLoading">
                  <span v-if="passwordLoading" class="spinner-border spinner-border-sm me-1"></span>
                  Update Password
                </button>
              </form>
            </div>

            <!-- Preferences Tab -->
            <div v-if="activeTab === 'preferences'" class="tab-content">
              <h2>Preferences</h2>
              <p class="text-muted mb-4">Customize your account preferences and notifications</p>

              <form @submit.prevent="updatePreferences">
                <div class="mb-3">
                  <label class="form-label d-block">Email Notifications</label>
                  <div class="form-check">
                    <input
                      type="checkbox"
                      id="projectUpdates"
                      v-model="preferencesForm.notifications.projectUpdates"
                      class="form-check-input"
                    />
                    <label class="form-check-label" for="projectUpdates">
                      Project updates and changes
                    </label>
                  </div>
                  <div class="form-check">
                    <input
                      type="checkbox"
                      id="securityAlerts"
                      v-model="preferencesForm.notifications.securityAlerts"
                      class="form-check-input"
                    />
                    <label class="form-check-label" for="securityAlerts">
                      Security alerts and notifications
                    </label>
                  </div>
                  <div class="form-check">
                    <input
                      type="checkbox"
                      id="newsletter"
                      v-model="preferencesForm.notifications.newsletter"
                      class="form-check-input"
                    />
                    <label class="form-check-label" for="newsletter">
                      Newsletter and product updates
                    </label>
                  </div>
                </div>

                <div class="mb-3">
                  <label for="timezone" class="form-label">Timezone</label>
                  <select
                    id="timezone"
                    v-model="preferencesForm.timezone"
                    class="form-select"
                  >
                    <option value="UTC">UTC</option>
                    <option value="America/New_York">Eastern Time</option>
                    <option value="America/Chicago">Central Time</option>
                    <option value="America/Denver">Mountain Time</option>
                    <option value="America/Los_Angeles">Pacific Time</option>
                  </select>
                </div>

                <div v-if="preferencesError" class="alert alert-danger">
                  {{ preferencesError }}
                </div>

                <div v-if="preferencesSuccess" class="alert alert-success">
                  {{ preferencesSuccess }}
                </div>

                <button type="submit" class="btn btn-primary" :disabled="preferencesLoading">
                  <span v-if="preferencesLoading" class="spinner-border spinner-border-sm me-1"></span>
                  Save Preferences
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'ProfileView',
  
  setup() {
    const store = useStore()
    const activeTab = ref('profile')
    
    // Profile Form
    const profileForm = ref({
      username: '',
      email: '',
      fullName: '',
      bio: ''
    })
    
    const profileErrors = ref({})
    const profileError = ref(null)
    const profileSuccess = ref(null)
    const profileLoading = ref(false)
    
    // Password Form
    const passwordForm = ref({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })
    
    const passwordErrors = ref({})
    const passwordError = ref(null)
    const passwordSuccess = ref(null)
    const passwordLoading = ref(false)
    
    const passwordsMatch = computed(() => 
      passwordForm.value.newPassword === passwordForm.value.confirmPassword
    )
    
    // Preferences Form
    const preferencesForm = ref({
      notifications: {
        projectUpdates: true,
        securityAlerts: true,
        newsletter: false
      },
      timezone: 'UTC'
    })
    
    const preferencesError = ref(null)
    const preferencesSuccess = ref(null)
    const preferencesLoading = ref(false)
    
    // Load user data
    const user = computed(() => store.state.auth.user)
    
    if (user.value) {
      profileForm.value = {
        username: user.value.username,
        email: user.value.email,
        fullName: user.value.full_name || '',
        bio: user.value.bio || ''
      }
    }
    
    // Methods
    const updateProfile = async () => {
      profileLoading.value = true
      profileError.value = null
      profileSuccess.value = null
      profileErrors.value = {}
      
      try {
        await store.dispatch('auth/updateProfile', {
          username: profileForm.value.username,
          email: profileForm.value.email,
          full_name: profileForm.value.fullName,
          bio: profileForm.value.bio
        })
        
        profileSuccess.value = 'Profile updated successfully'
      } catch (err) {
        if (err.response?.data?.errors) {
          profileErrors.value = err.response.data.errors
        } else {
          profileError.value = err.response?.data?.message || 'Failed to update profile'
        }
      } finally {
        profileLoading.value = false
      }
    }
    
    const updatePassword = async () => {
      if (!passwordsMatch.value) {
        return
      }
      
      passwordLoading.value = true
      passwordError.value = null
      passwordSuccess.value = null
      passwordErrors.value = {}
      
      try {
        await store.dispatch('auth/updatePassword', {
          current_password: passwordForm.value.currentPassword,
          new_password: passwordForm.value.newPassword
        })
        
        passwordSuccess.value = 'Password updated successfully'
        passwordForm.value = {
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        }
      } catch (err) {
        if (err.response?.data?.errors) {
          passwordErrors.value = err.response.data.errors
        } else {
          passwordError.value = err.response?.data?.message || 'Failed to update password'
        }
      } finally {
        passwordLoading.value = false
      }
    }
    
    const updatePreferences = async () => {
      preferencesLoading.value = true
      preferencesError.value = null
      preferencesSuccess.value = null
      
      try {
        await store.dispatch('auth/updatePreferences', preferencesForm.value)
        preferencesSuccess.value = 'Preferences updated successfully'
      } catch (err) {
        preferencesError.value = err.response?.data?.message || 'Failed to update preferences'
      } finally {
        preferencesLoading.value = false
      }
    }
    
    return {
      activeTab,
      profileForm,
      profileErrors,
      profileError,
      profileSuccess,
      profileLoading,
      passwordForm,
      passwordErrors,
      passwordError,
      passwordSuccess,
      passwordLoading,
      passwordsMatch,
      preferencesForm,
      preferencesError,
      preferencesSuccess,
      preferencesLoading,
      updateProfile,
      updatePassword,
      updatePreferences
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

.nav-card {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  color: #495057;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  
  i {
    margin-right: 0.75rem;
    width: 20px;
  }
  
  &:hover {
    background-color: #f8f9fa;
    color: #667eea;
  }
  
  &.active {
    background-color: #667eea;
    color: white;
  }
}

.content-card {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.tab-content {
  h2 {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
  }
}

.form-check {
  margin-bottom: 0.5rem;
}
</style> 