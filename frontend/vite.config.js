import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),          // 支持 .vue 语法
    vueDevTools(),  // 开发时调试工具
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  // 🚀 本地开发服务器配置
  server: {
    port: 5173, // Vue 默认端口
    proxy: {
      // 当访问 /api 时，转发到 Flask 后端
      '/api': {
        target: 'http://127.0.0.1:8080', // Flask 运行地址
        changeOrigin: true, // 允许跨域
        secure: false
      }
    }
  }
})
