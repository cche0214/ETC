import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    proxy: {
      // 主业务后端（8080）
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true
      },

    }
  }
})
