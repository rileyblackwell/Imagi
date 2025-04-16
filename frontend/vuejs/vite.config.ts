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
        manualChunks: {
          // Fix circular dependency by putting related modules in the same chunk
          'layouts': [
            './src/shared/layouts/index.ts',
            './src/shared/layouts/DefaultLayout.vue',
            './src/shared/layouts/BaseLayout.vue',
            './src/shared/layouts/DashboardLayout.vue',
            './src/shared/layouts/MinimalLayout.vue',
            './src/apps/auth/layouts/AuthLayout.vue'
          ],
          // Fix builder services dynamic import issues
          'builder-services': [
            './src/apps/products/oasis/builder/services/fileService.ts',
            './src/apps/products/oasis/builder/services/projectService.ts',
            './src/apps/products/oasis/builder/services/agentService.ts'
          ],
          // Fix utils dynamic import issues
          'shared-utils': [
            './src/shared/utils/index.ts'
          ],
          // Split vendor libraries into separate chunks
          'vendor-vue': ['vue', 'vue-router', 'pinia'],
          'vendor-ui': ['@headlessui/vue', '@heroicons/vue'],
        }
      }
    }
  }
})
