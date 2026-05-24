import '@testing-library/jest-dom'

declare global {
  interface Window {
    _env_: {
      API_URL?: string
      VITE_API_URL?: string
      [key: string]: string | undefined
    }
  }
}

if (!window._env_) {
  window._env_ = {}
}