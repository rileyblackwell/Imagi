import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5174,
    strictPort: true, // This will fail if port 5174 is not available
    proxy: {
      // Proxy API requests to the Django backend
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        configure: (proxy, _options) => {
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            // Log request info when debugging
            // console.log('Proxying request:', req.method, req.url);
          });
          
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            // Log response headers for debugging
            // console.log('Proxy response:', proxyRes.statusCode, req.url);
            
            // Ensure proper headers for streaming responses
            if (req.headers.accept?.includes('text/event-stream')) {
              proxyRes.headers['content-type'] = 'text/event-stream';
              proxyRes.headers['cache-control'] = 'no-cache';
              proxyRes.headers['connection'] = 'keep-alive';
            }
          });
          
          proxy.on('error', (err, _req, _res) => {
            console.error('Proxy error:', err);
          });
        }
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
    extensions: ['.ts', '.js', '.vue', '.json'] // Prioritize TypeScript files
  },
  build: {
    target: 'esnext',
    sourcemap: true
  }
})
