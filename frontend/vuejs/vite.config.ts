import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import type { ViteDevServer } from 'vite'

// Custom middleware to safely handle URI encoding issues
function safeDecodeMiddleware(req: any, res: any, next: any) {
  const originalUrl = req.url;
  
  if (!originalUrl) {
    next();
    return;
  }
  
  try {
    // Test if URL causes decodeURI to fail
    decodeURI(originalUrl);
  } catch (e) {
    // If it fails, replace problematic characters
    req.url = originalUrl
      .replace(/%(?![0-9A-Fa-f]{2})/g, '%25') // Fix unescaped % signs
      .replace(/\\/g, '/');  // Replace backslashes with forward slashes
    
    console.warn('Fixed malformed URI:', originalUrl, '→', req.url);
  }
  
  next();
}

// Set base path depending on environment
// '/' for development, '/products/oasis/builder/' for production deploys (e.g., on Railway)
// Force base path to '/' in development, regardless of env vars or CLI flags
// Only use '/products/oasis/builder/' in production deploys
const BASE_PATH = process.env.NODE_ENV === 'production' ? '/products/oasis/builder/' : '/';

export default defineConfig({
  base: BASE_PATH,
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
    },
    // Add custom plugin to handle malformed URIs
    {
      name: 'fix-malformed-uris',
      configureServer(server: ViteDevServer) {
        server.middlewares.use(safeDecodeMiddleware);
      }
    }
  ],
  server: {
    // No need to set base here; handled globally above
    port: 5174,
    strictPort: true, // This will fail if port 5174 is not available
    hmr: {
      overlay: false, // Disable the HMR error overlay to prevent URI errors from breaking the UI
    },
    proxy: {
      // Proxy all API requests to the Django backend
      // This allows consistent API calls using relative URLs in both development and production
      '/api': {
        target: process.env.VITE_BACKEND_URL || 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        configure: (proxy, _options) => {
          const backendUrl = process.env.VITE_BACKEND_URL || 'http://localhost:8000';
          
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            // Log request info when debugging
            if (process.env.NODE_ENV !== 'production') {
              console.log(`🔄 Proxy: ${req.method} ${req.url} → ${backendUrl}${req.url}`);
            }
          });
          
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            // Ensure proper headers for streaming responses
            if (req.headers.accept?.includes('text/event-stream')) {
              proxyRes.headers['content-type'] = 'text/event-stream';
              proxyRes.headers['cache-control'] = 'no-cache';
              proxyRes.headers['connection'] = 'keep-alive';
            }
          });
          
          proxy.on('error', (err, req, _res) => {
            console.error(`❌ Proxy Error: ${req.method} ${req.url} → ${backendUrl}${req.url}`, err.message);
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
