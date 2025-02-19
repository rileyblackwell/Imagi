import type { ComputedRef } from 'vue'

export interface AuthState {
  isAuthenticated: ComputedRef<boolean>
  setAuthenticated: (status: boolean) => void
}

export declare function useAuth(): AuthState

export * from './useWindowSize'
export * from './useNotification' 