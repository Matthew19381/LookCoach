import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// Backend :8010. 127.0.0.1, not localhost: on Windows Node can resolve localhost to ::1
// while start-ekosystem.ps1 binds the backend to 127.0.0.1 only (same fix as ForgeBody).
const API_TARGET = process.env.VITE_API_TARGET || 'http://127.0.0.1:8010'
const proxy = {
  '/api': { target: API_TARGET, changeOrigin: true },
  '/uploads': { target: API_TARGET, changeOrigin: true },
}
// The phone opens the page through `tailscale serve` (Host: desktop-h6abdhd.tail081a9d.ts.net).
// Vite rejects unknown Host headers, so allow only Mateusz's tailnet, not every *.ts.net name.
const TAILNET_HOSTS = ['.tail081a9d.ts.net']

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
      importScripts: ['push-sw.js'],  // plan 5.5: push + notificationclick handlers
      globPatterns: ['**/*.{js,css,html,svg,png,ico,woff2}'],
      navigateFallback: '/index.html',
      runtimeCaching: [
        {
          urlPattern: ({ url }) => url.pathname.startsWith('/api/'),
          // NetworkFirst: fresh data online (SWR showed e.g. a product list without the product just added)
          handler: 'NetworkFirst',
          options: {
            cacheName: 'api-cache',
            expiration: { maxEntries: 100, maxAgeSeconds: 60 * 60 * 24 * 7 },
            cacheableResponse: { statuses: [0, 200] },
          },
        },
      ],
    },
    devOptions: { enabled: false },  // belongs to VitePWA, not workbox - it broke `vite build`
  })],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/setupTests.ts',
    include: ['src/**/*.{test,spec}.{js,jsx,ts,tsx}'],
    define: {
      'import.meta.env.VITE_API_URL': '"http://localhost:8010"'
    },
  },
  server: {
    port: 5175,
    host: true,
    allowedHosts: TAILNET_HOSTS,
    proxy,
  },
  // start-ekosystem.ps1 serves the built dist with `vite preview` on 5175.
  preview: { port: 5175, strictPort: true, allowedHosts: TAILNET_HOSTS, proxy },
})
