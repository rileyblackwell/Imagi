<template>
  <div class="min-h-screen flex items-center justify-center bg-dark-900 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-white">
          Sign in to your account
        </h2>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="email" class="sr-only">Email address</label>
            <input
              id="email"
              v-model="email"
              name="email"
              type="email"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-dark-700 placeholder-gray-500 text-white rounded-t-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm bg-dark-800"
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
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-dark-700 placeholder-gray-500 text-white rounded-b-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm bg-dark-800"
              placeholder="Password"
            />
          </div>
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <input
              id="remember-me"
              name="remember-me"
              type="checkbox"
              v-model="rememberMe"
              class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-dark-700 rounded bg-dark-800"
            />
            <label for="remember-me" class="ml-2 block text-sm text-gray-300">
              Remember me
            </label>
          </div>

          <div class="text-sm">
            <router-link
              to="/auth/forgot-password"
              class="font-medium text-primary-500 hover:text-primary-400"
            >
              Forgot your password?
            </router-link>
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="isLoading"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            <span class="absolute left-0 inset-y-0 flex items-center pl-3">
              <i class="fas fa-lock text-primary-500 group-hover:text-primary-400" aria-hidden="true"></i>
            </span>
            {{ isLoading ? 'Signing in...' : 'Sign in' }}
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
              New to Imagi?
            </span>
          </div>
        </div>

        <div class="mt-6">
          <router-link
            to="/auth/register"
            class="w-full flex justify-center py-2 px-4 border border-dark-700 rounded-md shadow-sm text-sm font-medium text-gray-300 bg-dark-800 hover:bg-dark-700"
          >
            Create an account
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const authStore = useAuthStore()

    const email = ref('')
    const password = ref('')
    const rememberMe = ref(false)
    const isLoading = ref(false)

    async function handleSubmit() {
      isLoading.value = true
      try {
        const success = await authStore.login({
          email: email.value,
          password: password.value,
          remember: rememberMe.value
        })

        if (success) {
          const redirectPath = route.query.redirect || '/builder'
          router.push(redirectPath)
        }
      } catch (error) {
        console.error('Login error:', error)
      } finally {
        isLoading.value = false
      }
    }

    return {
      email,
      password,
      rememberMe,
      isLoading,
      handleSubmit
    }
  }
}
</script> 