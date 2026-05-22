import api from './api'

export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login/', { email, password }),

  register: (email: string, password: string, password2: string) =>
    api.post('/auth/register/', { email, password, password2 }),

  refresh: (refresh: string) =>
    api.post('/auth/refresh/', { refresh }),

  getProfile: () =>
    api.get('/auth/profile/'),

  saveTokens: (access: string, refresh: string) => {
    localStorage.setItem('accessToken', access)
    localStorage.setItem('refreshToken', refresh)
  },

  logout: () => {
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
  }
}