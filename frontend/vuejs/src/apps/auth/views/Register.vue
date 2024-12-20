<template>
  <div class="min-h-screen flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-300">
        Create your account
      </h2>
      <p class="mt-2 text-center text-sm text-gray-400">
        Or
        <router-link
          to="/auth/login"
          class="font-medium text-primary-500 hover:text-primary-400"
        >
          sign in to your account
        </router-link>
      </p>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-dark-800 py-8 px-4 shadow sm:rounded-lg sm:px-10">
        <form class="space-y-6" @submit.prevent="handleSubmit">
          <div>
            <label for="email" class="block text-sm font-medium text-gray-300">
              Email address
            </label>
            <div class="mt-1">
              <input
                id="email"
                v-model="form.email"
                type="email"
                required
                class="appearance-none block w-full px-3 py-2 border border-gray-700 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 bg-dark-700 text-gray-300 sm:text-sm"
                placeholder="Enter your email"
              />
            </div>
          </div>

          <div>
            <label for="username" class="block text-sm font-medium text-gray-300">
              Username
            </label>
            <div class="mt-1">
              <input
                id="username"
                v-model="form.username"
                type="text"
                required
                class="appearance-none block w-full px-3 py-2 border border-gray-700 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 bg-dark-700 text-gray-300 sm:text-sm"
                placeholder="Choose a username"
              />
            </div>
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-300">
              Password
            </label>
            <div class="mt-1">
              <input
                id="password"
                v-model="form.password"
                type="password"
                required
                class="appearance-none block w-full px-3 py-2 border border-gray-700 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 bg-dark-700 text-gray-300 sm:text-sm"
                placeholder="Create a password"
              />
            </div>
          </div>

          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-gray-300">
              Confirm password
            </label>
            <div class="mt-1">
              <input
                id="confirmPassword"
                v-model="form.confirmPassword"
                type="password"
                required
                class="appearance-none block w-full px-3 py-2 border border-gray-700 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 bg-dark-700 text-gray-300 sm:text-sm"
                placeholder="Confirm your password"
              />
            </div>
          </div>

          <div class="flex items-center">
            <input
              id="terms"
              v-model="form.acceptTerms"
              type="checkbox"
              required
              class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-700 rounded bg-dark-700"
            />
            <label for="terms" class="ml-2 block text-sm text-gray-300">
              I agree to the
              <router-link
                to="/terms"
                class="font-medium text-primary-500 hover:text-primary-400"
              >
                Terms of Service
              </router-link>
              and
              <router-link
                to="/privacy"
                class="font-medium text-primary-500 hover:text-primary-400"
              >
                Privacy Policy
              </router-link>
            </label>
          </div>

          <div>
            <button
              type="submit"
              :disabled="loading || !isFormValid"
              class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="loading">Creating account...</span>
              <span v-else>Create account</span>
            </button>
          </div>
        </form>

        <div v-if="error" class="mt-4 text-sm text-red-400">
          {{ error }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'Register',
  
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const form = ref({
      email: '',
      username: '',
      password: '',
      confirmPassword: '',
      acceptTerms: false
    })
    
    const loading = computed(() => store.getters['auth/isLoading'])
    const error = computed(() => store.getters['auth/error'])
    
    const isFormValid = computed(() => {
      return (
        form.value.email &&
        form.value.username &&
        form.value.password &&
        form.value.password === form.value.confirmPassword &&
        form.value.acceptTerms
      )
    })
    
    const handleSubmit = async () => {
      if (!isFormValid.value) return
      
      try {
        await store.dispatch('auth/register', {
          email: form.value.email,
          username: form.value.username,
          password: form.value.password
        })
        
        // Redirect to home page after successful registration
        router.push('/')
      } catch (err) {
        // Error is handled by the store
        console.error('Registration failed:', err)
      }
    }
    
    return {
      form,
      loading,
      error,
      isFormValid,
      handleSubmit
    }
  }
}
</script> 