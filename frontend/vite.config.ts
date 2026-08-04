import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiUrl = env.VITE_API_URL || process.env.VITE_API_URL || ''

  return {
    plugins: [react()],
    define: {
      'import.meta.env.VITE_API_URL': JSON.stringify(apiUrl),
    },
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
  }
})
