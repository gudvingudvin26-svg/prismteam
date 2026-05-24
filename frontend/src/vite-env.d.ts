/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

declare global {
  interface Window {
    _env_: {
      API_URL?: string
      VITE_API_URL?: string
      [key: string]: string | undefined
    }
  }
}

export {}