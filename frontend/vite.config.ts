import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/assets': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/run_sse': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/apps': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  },
})
