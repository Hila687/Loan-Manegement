import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
  ],
  build: {
    // Hashed file names -> safe to cache forever in the browser.
    assetsDir: 'assets',
    sourcemap: false,
  },
})
