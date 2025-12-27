import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  root: './frontend',
  server: {
    port: 5173,
    hmr: {
      // Enable HMR for better development experience
      overlay: true,
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: '../frontend/dist',
    emptyOutDir: true,
    rollupOptions: {
      input: './index.html',
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './frontend/src'),
    },
  },
})
