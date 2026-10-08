import { describe, it, expect, beforeEach, vi } from 'vitest'
import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'

const push = vi.fn()
const route = { query: {} as Record<string, unknown> }
vi.mock('vue-router', () => ({
  useRouter: () => ({ push }),
  useRoute: () => route
}))

const store = vi.hoisted(() => ({
  loading: false,
  login: vi.fn(),
  register: vi.fn(),
  clearError: vi.fn()
}))
vi.mock('../../stores/index', () => ({ useAuthStore: () => store }))

import { useSignInForm } from '../useSignInForm'
import { useRegisterForm } from '../useRegisterForm'

// The composables register an unmount hook, so they run inside a component.
function setup<T>(use: () => T): T {
  let result!: T
  mount(defineComponent({ setup() { result = use(); return () => null } }))
  return result
}

beforeEach(() => {
  push.mockReset()
  route.query = {}
  store.login.mockReset()
  store.register.mockReset()
})

describe('useSignInForm', () => {
  it('signs in and goes home', async () => {
    const form = setup(useSignInForm)
    await form.onSubmit({ username: ' alice ', password: 'pw' })
    expect(store.login).toHaveBeenCalledWith({ username: 'alice', password: 'pw' })
    expect(push).toHaveBeenCalledWith('/')
    expect(form.isSubmitting.value).toBe(false)
  })

  it('never trims the password, which may legitimately have spaces', async () => {
    const form = setup(useSignInForm)
    await form.onSubmit({ username: 'alice', password: ' pass word ' })
    expect(store.login).toHaveBeenCalledWith({ username: 'alice', password: ' pass word ' })
  })

  it('returns to the page that asked for sign-in', async () => {
    route.query = { redirect: '/dashboard' }
    const form = setup(useSignInForm)
    await form.onSubmit({ username: 'alice', password: 'pw' })
    expect(push).toHaveBeenCalledWith('/dashboard')
  })

  it('ignores a redirect that would leave the site', async () => {
    route.query = { redirect: '//evil.example' }
    const form = setup(useSignInForm)
    await form.onSubmit({ username: 'alice', password: 'pw' })
    expect(push).toHaveBeenCalledWith('/')
  })

  it('asks for both fields without calling the server', async () => {
    const form = setup(useSignInForm)
    await form.onSubmit({ username: 'alice', password: '' })
    expect(store.login).not.toHaveBeenCalled()
    expect(form.serverError.value).toBe('Username and password are required')
    expect(form.isSubmitting.value).toBe(false)
  })

  it('shows the server error and stays on the page', async () => {
    store.login.mockRejectedValue(new Error('Invalid username or password'))
    const form = setup(useSignInForm)
    await form.onSubmit({ username: 'alice', password: 'wrong' })
    expect(form.serverError.value).toBeTruthy()
    expect(push).not.toHaveBeenCalled()
  })
})

describe('useRegisterForm', () => {
  const valid = {
    username: 'alice',
    email: 'alice@example.com',
    password: 'Sup3rSecret',
    password_confirmation: 'Sup3rSecret',
    agreeToTerms: true
  }

  it('creates the account and goes home', async () => {
    const form = setup(() => useRegisterForm())
    await form.onSubmit(valid)
    expect(store.register).toHaveBeenCalledWith({
      username: 'alice',
      email: 'alice@example.com',
      password: 'Sup3rSecret',
      password_confirmation: 'Sup3rSecret',
      terms_accepted: true
    })
    expect(push).toHaveBeenCalledWith('/')
  })

  it('requires the terms box by default', async () => {
    const form = setup(() => useRegisterForm())
    await form.onSubmit({ ...valid, agreeToTerms: false })
    expect(store.register).not.toHaveBeenCalled()
    expect(form.serverError.value).toMatch(/Terms of Service/)
  })

  it('can run without a terms box, as generated projects do', async () => {
    const form = setup(() => useRegisterForm({ requireTerms: false }))
    await form.onSubmit({ ...valid, agreeToTerms: undefined })
    expect(store.register).toHaveBeenCalled()
  })

  it('catches mismatched and short passwords before the server', async () => {
    const form = setup(() => useRegisterForm())
    await form.onSubmit({ ...valid, password_confirmation: 'Different1' })
    expect(form.serverError.value).toBe('Passwords do not match')
    await form.onSubmit({ ...valid, password: 'Ab1', password_confirmation: 'Ab1' })
    expect(form.serverError.value).toBe('Password must be at least 8 characters long')
    expect(store.register).not.toHaveBeenCalled()
  })
})
