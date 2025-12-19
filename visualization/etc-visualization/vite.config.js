import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    proxy: {
      // 1. AI 业务后端 (FastAPI - 8001)
      // 注意：必须放在 '/api' 之前，否则会被下面的规则拦截
      '/api/chat': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        // 这里不需要 rewrite，因为你的 FastAPI 路由本身就包含了 /api/chat 前缀
      },
      
      // 2. 主业务后端 (Flask - 8080)
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true
      },
    }
  }
})
