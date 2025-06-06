/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/ban-types
  const component: DefineComponent<{}, {}, any>
  export default component
}

interface ImportMetaEnv {
  readonly BACKEND_URL: string
  readonly VITE_STRIPE_PUBLISHABLE_KEY: string
  readonly VITE_APP_TITLE: string
  readonly VITE_APP_VERSION: string
  readonly VITE_APP_ENV: string
  // more env variables...
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// Stripe global declaration
interface Window {
  Stripe?: any;
}
