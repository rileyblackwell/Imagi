<template>
  <div class="min-h-screen flex items-center justify-center bg-dark-900 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-white">
          Create your account
        </h2>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="name" class="sr-only">Full name</label>
            <input
              id="name"
              v-model="name"
              name="name"
              type="text"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-dark-700 placeholder-gray-500 text-white rounded-t-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm bg-dark-800"
              placeholder="Full name"
            />
          </div>
          <div>
            <label for="email" class="sr-only">Email address</label>
            <input
              id="email"
              v-model="email"
              name="email"
              type="email"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-dark-700 placeholder-gray-500 text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm bg-dark-800"
              placeholder="Email address"
            />
          </div>
          <div>
            <label for="password" class="sr-only">Password</label>
            <input
              id="password"
              v-model="password"
              name="password"
              type="password"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-dark-700 placeholder-gray-500 text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm bg-dark-800"
              placeholder="Password"
            />
          </div>
          <div>
            <label for="confirmPassword" class="sr-only">Confirm password</label>
            <input
              id="confirmPassword"
              v-model="confirmPassword"
              name="confirmPassword"
              type="password"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-dark-700 placeholder-gray-500 text-white rounded-b-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm bg-dark-800"
              placeholder="Confirm password"
            />
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="isLoading || !isValid"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
          >
            <span class="absolute left-0 inset-y-0 flex items-center pl-3">
              <i class="fas fa-user-plus text-primary-500 group-hover:text-primary-400" aria-hidden="true"></i>
            </span>
            {{ isLoading ? 'Creating account...' : 'Create account' }}
          </button>
        </div>
      </form>

      <div class="mt-6">
        <div class="relative">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-dark-700"></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-2 bg-dark-900 text-gray-300">
              Already have an account?
            </span>
          </div>
        </div>

        <div class="mt-6">
          <router-link
            to="/auth/login"
            class="w-full flex justify-center py-2 px-4 border border-dark-700 rounded-md shadow-sm text-sm font-medium text-gray-300 bg-dark-800 hover:bg-dark-700"
          >
            Sign in instead
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Register',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    const name = ref('')
    const email = ref('')
    const password = ref('')
    const confirmPassword = ref('')
    const isLoading = ref(false)

    const isValid = computed(() => {
      return (
        name.value.length > 0 &&
        email.value.length > 0 &&
        password.value.length >= 8 &&
        password.value === confirmPassword.value
      )
    })

    async function handleSubmit() {
      if (!isValid.value) return

      isLoading.value = true
      try {
        const success = await authStore.register({
          name: name.value,
          email: email.value,
          password: password.value
        })

        if (success) {
          router.push('/builder')
        }
      } catch (error) {
        console.error('Registration error:', error)
      } finally {
        isLoading.value = false
      }
    }

    return {
      name,
      email,
      password,
      confirmPassword,
      isLoading,
      isValid,
      handleSubmit
    }
  }
}
</script> 