import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/auth': 'http://127.0.0.1:8000',
      '/providers': 'http://127.0.0.1:8000',
      '/jobs': 'http://127.0.0.1:8000',
      '/credits': 'http://127.0.0.1:8000',
      '/marketplace': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000'
    }
  }
})
