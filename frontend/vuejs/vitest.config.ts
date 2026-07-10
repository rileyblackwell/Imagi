import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  test: {
    // jsdom gives us window/localStorage/document for store + component tests.
    environment: 'jsdom',
    globals: true,
    // Only pick up co-located test files under __tests__ (already excluded
    // from the app tsconfig so they never affect type-check / build).
    include: ['src/**/__tests__/**/*.{test,spec}.{ts,js}'],
    clearMocks: true,
    restoreMocks: true,
  },
})
