import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [
    vue(),
    // Handle missing pattern SVG references
    {
      name: 'resolve-svg-patterns',
      resolveId(id) {
        // Resolve grid-pattern.svg and dot-pattern.svg as empty modules
        if (id === '/grid-pattern.svg' || id === '/dot-pattern.svg') {
          return '\0empty-module'
        }
        return null
      },
      load(id) {
        if (id === '\0empty-module') {
          // Return an empty SVG that works with url() references
          return `export default "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1' height='1'%3E%3C/svg%3E"`
        }
        return null
      }
    }
  ],
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
    sourcemap: true,
    chunkSizeWarningLimit: 800, // Increase chunk size warning limit
    rollupOptions: {
      output: {
        manualChunks(id) {
          // Handle file service circular dependencies
          if (id.includes('fileService.ts')) {
            return 'builder-services';
          }
          
          // Handle UI library chunks only if they're actually imported
          if (id.includes('node_modules/@headlessui/vue') || 
              id.includes('node_modules/@heroicons/vue')) {
            return 'vendor-ui';
          }
          
          // Vue ecosystem libraries
          if (id.includes('node_modules/vue') || 
              id.includes('node_modules/vue-router') || 
              id.includes('node_modules/pinia')) {
            return 'vendor-vue';
          }
          
          // Shared utilities
          if (id.includes('/shared/utils/')) {
            return 'shared-utils';
          }
          
          // Handle layouts
          if (id.includes('/shared/layouts/') || id.includes('/apps/auth/layouts/')) {
            return 'layouts';
          }
        }
      }
    }
  }
})
