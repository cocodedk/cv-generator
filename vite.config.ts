import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  root: './frontend',
  // Base path for GitHub Pages deployment
  // Set via VITE_BASE_PATH environment variable (e.g., /cv/ for repo named 'cv')
  // Defaults to empty string for local development
  base: process.env.VITE_BASE_PATH || '',
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
      input: path.resolve(__dirname, 'frontend/index.html'),
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './frontend/src'),
    },
  },
})
