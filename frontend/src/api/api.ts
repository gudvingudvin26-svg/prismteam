import axios from 'axios'

declare global {
  interface Window {
    _env_: {
      VITE_API_URL?: string
      [key: string]: string | undefined
    }
  }
}

const getBaseUrl = () => {
  if (typeof process !== 'undefined' && process.env?.VITE_API_URL) {
    return process.env.VITE_API_URL
  }
  if (typeof window !== 'undefined' && window._env_?.VITE_API_URL) {
    return window._env_.VITE_API_URL
  }
  return 'http://localhost:8000'
}

const BASE_URL = getBaseUrl()

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refreshToken')
        const response = await axios.post(`${BASE_URL}/api/auth/refresh/`, {
          refresh: refreshToken
        })

        localStorage.setItem('accessToken', response.data.access)
        originalRequest.headers.Authorization = `Bearer ${response.data.access}`

        return api(originalRequest)
      } catch {
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export default api