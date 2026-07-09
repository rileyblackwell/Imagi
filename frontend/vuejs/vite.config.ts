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
})
