import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import axios from 'axios'
import type { User } from '@/apps/auth/types/auth'

// Mock the shared API client so no real network calls happen.
const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}))
vi.mock('@/shared/services/api', () => ({
  default: apiMock,
  getCsrfToken: vi.fn(),
}))

import { useAuthStore } from '@/shared/stores/auth'

const sampleUser: User = {
  id: 1,
  username: 'alice',
  email: 'alice@example.com',
  name: 'Alice',
  balance: 42,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
}

describe('auth store', () => {
  beforeEach(() => {
    localStorage.clear()
    delete axios.defaults.headers.common['Authorization']
    setActivePinia(createPinia())
    apiMock.get.mockReset()
    apiMock.post.mockReset()
  })

  describe('setAuthState', () => {
    it('persists token and user and sets the axios auth header', () => {
      const store = useAuthStore()
      store.setAuthState(sampleUser, 'tok-123')

      expect(store.isAuthenticated).toBe(true)
      expect(store.token).toBe('tok-123')
      expect(store.currentUser).toEqual(sampleUser)
      expect(axios.defaults.headers.common['Authorization']).toBe('Token tok-123')

      // Token stored with an expiry envelope; user stored as JSON.
      const storedToken = JSON.parse(localStorage.getItem('token') as string)
      expect(storedToken.value).toBe('tok-123')
      expect(storedToken.expires).toBeGreaterThan(Date.now())
      expect(JSON.parse(localStorage.getItem('user') as string)).toEqual(sampleUser)
    })

    it('clears stored auth when called with nulls', () => {
      const store = useAuthStore()
      store.setAuthState(sampleUser, 'tok-123')
      store.setAuthState(null, null)

      expect(store.isAuthenticated).toBe(false)
      expect(localStorage.getItem('token')).toBeNull()
      expect(localStorage.getItem('user')).toBeNull()
      expect(axios.defaults.headers.common['Authorization']).toBeUndefined()
    })
  })

  describe('getters', () => {
    it('exposes the current user and balance', () => {
      const store = useAuthStore()
      store.setAuthState(sampleUser, 'tok-123')
      expect(store.currentUser).toEqual(sampleUser)
      expect(store.userBalance).toBe(42)
    })

    it('defaults balance to 0 when no user', () => {
      const store = useAuthStore()
      expect(store.userBalance).toBe(0)
    })
  })

  describe('clearAuth / logout', () => {
    it('resets all auth state', async () => {
      const store = useAuthStore()
      store.setAuthState(sampleUser, 'tok-123')
      await store.clearAuth()

      expect(store.token).toBeNull()
      expect(store.user).toBeNull()
      expect(store.isAuthenticated).toBe(false)
      expect(localStorage.getItem('token')).toBeNull()
    })

    it('logout delegates to clearAuth', async () => {
      const store = useAuthStore()
      store.setAuthState(sampleUser, 'tok-123')
      await store.logout()
      expect(store.isAuthenticated).toBe(false)
    })
  })

  describe('stored token hydration', () => {
    it('restores a valid non-expired token on creation', () => {
      localStorage.setItem(
        'token',
        JSON.stringify({ value: 'stored-tok', expires: Date.now() + 100000 }),
      )
      localStorage.setItem('user', JSON.stringify(sampleUser))
      const store = useAuthStore()
      expect(store.token).toBe('stored-tok')
      expect(store.isAuthenticated).toBe(true)
    })

    it('ignores an expired token on creation', () => {
      localStorage.setItem(
        'token',
        JSON.stringify({ value: 'old-tok', expires: Date.now() - 1000 }),
      )
      const store = useAuthStore()
      expect(store.token).toBeNull()
      expect(store.isAuthenticated).toBe(false)
    })
  })

  describe('initAuth', () => {
    it('validates a stored token against the server', async () => {
      localStorage.setItem(
        'token',
        JSON.stringify({ value: 'stored-tok', expires: Date.now() + 100000 }),
      )
      apiMock.get.mockResolvedValue({
        data: { isAuthenticated: true, user: sampleUser },
      })

      const store = useAuthStore()
      const result = await store.initAuth()

      expect(result).toBe(true)
      expect(apiMock.get).toHaveBeenCalledWith('/v1/auth/init/')
      expect(store.currentUser).toEqual(sampleUser)
      expect(store.isAuthenticated).toBe(true)
    })

    it('returns false when there is no stored token', async () => {
      const store = useAuthStore()
      const result = await store.initAuth()
      expect(result).toBe(false)
      expect(store.isAuthenticated).toBe(false)
    })
  })
})
