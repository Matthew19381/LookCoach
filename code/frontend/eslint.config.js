import js from '@eslint/js'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'

const browserGlobals = {
  alert: 'readonly',
  Blob: 'readonly',
  cancelAnimationFrame: 'readonly',
  clearInterval: 'readonly',
  clearTimeout: 'readonly',
  confirm: 'readonly',
  console: 'readonly',
  crypto: 'readonly',
  CustomEvent: 'readonly',
  document: 'readonly',
  Event: 'readonly',
  fetch: 'readonly',
  File: 'readonly',
  FormData: 'readonly',
  history: 'readonly',
  HTMLElement: 'readonly',
  HTMLInputElement: 'readonly',
  Image: 'readonly',
  KeyboardEvent: 'readonly',
  location: 'readonly',
  localStorage: 'readonly',
  matchMedia: 'readonly',
  MouseEvent: 'readonly',
  navigator: 'readonly',
  performance: 'readonly',
  prompt: 'readonly',
  requestAnimationFrame: 'readonly',
  screen: 'readonly',
  sessionStorage: 'readonly',
  setInterval: 'readonly',
  setTimeout: 'readonly',
  URL: 'readonly',
  URLSearchParams: 'readonly',
  window: 'readonly',
}

export default [
  {
    ignores: ['coverage/**', 'dist/**', 'node_modules/**'],
  },
  {
    files: ['**/*.{js,jsx,ts,tsx}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
      globals: browserGlobals,
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...js.configs.recommended.rules,
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'warn',
      'react-refresh/only-export-components': [
        'warn',
        {
          allowConstantExport: true,
        },
      ],
    },
  },
]
