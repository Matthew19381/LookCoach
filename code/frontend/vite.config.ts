import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [react(), VitePWA({
    registerType: 'autoUpdate',
    manifest: {
      name: 'LookCoach — Asystent Stylizacji',
      short_name: 'LookCoach',
      description: 'Personalizowany asystent analizy i optymalizacji stylizacji.',
      start_url: '/',
      scope: '/',
      display: 'standalone',
      orientation: 'portrait',
      background_color: '#111827',
      theme_color: '#111827',
      lang: 'pl',
      icons: [
        { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png', purpose: 'any' },
        { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'any' },
        { src: '/icons/icon-maskable-192.png', sizes: '192x192', type: 'image/png', purpose: 'maskable' },
        { src: '/icons/icon-maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
      ],
      shortcuts: [],
    },
    workbox: {
      globPatterns: ['**/*.{js,css,html,svg,png,ico,woff2}'],
      navigateFallback: '/index.html',
      runtimeCaching: [
        {
          urlPattern: ({ url }) => url.pathname.startsWith('/api/'),
          handler: 'StaleWhileRevalidate',
          options: {
            cacheName: 'api-cache',
            expiration: { maxEntries: 100, maxAgeSeconds: 60 * 60 * 24 * 7 },
            cacheableResponse: { statuses: [0, 200] },
          },
        },
      ],
    },
    devOptions: { enabled: false },
  })],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/setupTests.ts',
    include: ['src/**/*.{test,spec}.{js,jsx,ts,tsx}'],
  },
  server: {
    port: 5175,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8010',
        changeOrigin: true,
      },
      '/uploads': {
        target: 'http://localhost:8010',
        changeOrigin: true,
      },
    },
  },
})
