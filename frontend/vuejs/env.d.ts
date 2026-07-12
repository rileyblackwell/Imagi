/// <reference types="vite/client" />

// Injected at build time via vite.config.ts `define`.
declare const __BUILD_TIME__: string

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}
