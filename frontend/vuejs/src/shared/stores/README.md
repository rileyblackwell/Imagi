# Shared Stores in Imagi Oasis

This directory contains shared stores that manage global state across the entire application. These stores are designed to be used by multiple modules/apps within the Imagi Oasis platform.

## Architecture

Imagi Oasis follows a modular store pattern where:

1. **Shared stores** (this directory): Manage global application state
2. **Module stores**: Contain module-specific logic but delegate to shared stores

This allows for:
- Centralized state management for critical application data
- Consistent state across modules
- Module-specific operations without duplicating state

## Available Stores

### Auth Store (`auth.ts`)

Manages user authentication state across the application.

```js
// Example usage
import { useAuthStore } from '@/shared/stores/auth'

// In a component or service
const authStore = useAuthStore()
const isLoggedIn = authStore.isAuthenticated
const userData = authStore.user
```

### Balance Store (`balance.ts`)

Manages user credit balance across the application.

```js
// Example usage
import { useBalanceStore } from '@/shared/stores/balance'

// In a component or service
const balanceStore = useBalanceStore()
const currentBalance = balanceStore.balance
const formattedBalance = balanceStore.formattedBalance
```

## How Module Stores Should Use Shared Stores

### For auth:

```js
// In a module store
import { defineStore } from 'pinia'
import { useAuthStore as useGlobalAuthStore } from '@/shared/stores/auth'

export const useModuleAuthStore = defineStore('module-auth', () => {
  // Get global auth store
  const globalAuthStore = useGlobalAuthStore()
  
  // Computed properties
  const isAuthenticated = computed(() => globalAuthStore.isAuthenticated)
  
  // Module-specific auth actions
  // ...
})
```

### For balance:

```js
// In a module store
import { defineStore } from 'pinia'
import { useBalanceStore as useGlobalBalanceStore } from '@/shared/stores/balance'

export const useModuleBalanceStore = defineStore('module-balance', () => {
  // Get global balance store
  const globalBalanceStore = useGlobalBalanceStore()
  
  // Computed properties
  const balance = computed(() => globalBalanceStore.balance)
  
  // Module-specific balance actions
  // ...
})
```

## Best Practices

1. **Never duplicate state**: Always use the shared store for critical state.
2. **Keep module-specific logic in module stores**: Add module-specific behavior there.
3. **Use computed properties**: Expose global state via computed properties.
4. **Update global state consistently**: Use the appropriate shared store methods.
5. **Listen for changes**: Watch shared store state for reactive updates.

## Initialization

Shared stores are initialized in `App.vue` during application startup. If you add a new shared store, make sure to:

1. Import it in `App.vue`
2. Initialize it in the `onMounted` lifecycle hook
3. Add watchers for dependent state (e.g., clear balance when user logs out) 