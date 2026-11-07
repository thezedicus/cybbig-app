import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/',
  server: {
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8765',
        changeOrigin: false,
      },
      '/demo': {
        target: 'http://127.0.0.1:8765',
        changeOrigin: false,
      },
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    sourcemap: false,
    target: 'chrome130',
    // Application de bureau chargée depuis le disque : l'avertissement de 500 ko n'a pas de sens ici, et
    // écrit sur stderr il ferait échouer scripts/build-installer.ps1 (PowerShell 5.1 + ErrorActionPreference=Stop).
    chunkSizeWarningLimit: 1500,
  },
})
