import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [
    vue(),
  ],
  server: {
    // Honor a harness/CI-assigned PORT, else default to 5173.
    // strictPort is false so Vite auto-increments (5174, 5175, …) when the
    // port is taken — lets multiple dev servers run side by side.
    port: Number(process.env.PORT) || 5173,
    strictPort: false,
    hmr: {
      overlay: false,
    },
    proxy: {
      '/api': {
        target: process.env.VITE_BACKEND_URL || 'http://localhost:8000',
        changeOrigin: true,
        ws: true,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
    extensions: ['.ts', '.js', '.vue', '.json'],
  },
  optimizeDeps: {
    // Pre-bundle these at server startup instead of letting Vite discover them
    // mid-load. The vee-validate rule/i18n packages are pulled in by the
    // validation plugin but aren't reliably caught by Vite's dep scanner, so on
    // a cold optimize cache they were discovered on the first page load —
    // triggering a re-optimize + full reload that intermittently rendered a
    // blank page (fixed only by a manual refresh). Listing them here removes the
    // mid-load reload entirely.
    include: [
      'vee-validate',
      '@vee-validate/rules',
      '@vee-validate/i18n',
    ],
  },
})
