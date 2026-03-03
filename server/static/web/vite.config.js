import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/aed_reviewer/api': {
        target: 'http://127.0.0.1:5100',
        changeOrigin: true,
      }
    }
  },
  watch: {
    include: 'src/**'
  },
  build: {
    outDir: '../../app/static/aed_reviewer/'
  },
  base: "/aed_reviewer"
})
