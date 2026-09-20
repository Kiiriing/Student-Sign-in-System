import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173
  },
  build: {
    // 产物分包：把体积大、更新频率低的依赖单独拆成 vendor chunk，
    // 业务代码迭代时用户只需重新下载业务 chunk，vendor 包可长期命中缓存
    rollupOptions: {
      output: {
        manualChunks(id: string) {
          if (id.includes('node_modules/echarts') || id.includes('node_modules/zrender')) {
            return 'vendor-echarts'
          }
          if (id.includes('node_modules/vue') || id.includes('node_modules/@vue')) {
            return 'vendor-vue'
          }
          return undefined
        }
      }
    }
  }
})