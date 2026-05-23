import api from './api'

export const authApi = {
  login: (email: string, password: string) =>
    api.post('/api/auth/login/', { email, password }),

  register: (username: string, email: string, password: string, password2: string) =>
    api.post('/api/auth/register/', {
      username: username,
      email: email,
      password: password,
      again_password: password2,
      first_name: username
    }),

  refresh: (refresh: string) =>
    api.post('/api/auth/refresh/', { refresh }),

  getProfile: () =>
    api.get('/api/auth/profile/'),

  saveTokens: (access: string, refresh: string) => {
    localStorage.setItem('accessToken', access)
    localStorage.setItem('refreshToken', refresh)
  },

  logout: () => {
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
  }
}