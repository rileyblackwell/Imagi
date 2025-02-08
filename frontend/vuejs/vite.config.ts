import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  css: {
    postcss: './postcss.config.js'
  },
  server: {
    port: 5174,
    host: true,
    strictPort: true,
    cors: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    chunkSizeWarningLimit: 1000,
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': [
            'vue',
            'vue-router',
            'pinia',
            '@fortawesome/vue-fontawesome',
            'vee-validate'
          ]
        }
      }
    }
  },
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', '@fortawesome/vue-fontawesome', 'vee-validate']
  }
})
