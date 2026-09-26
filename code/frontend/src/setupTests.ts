import '@testing-library/jest-dom'

// Mock Vite environment variables for tests
Object.defineProperty(globalThis, 'import', {
  value: {
    meta: {
      env: {
        VITE_API_URL: 'http://localhost:8010'
      }
    }
  },
  writable: true,
  configurable: true
})
