import api from './api'

export const authApi = {
  login: (email: string, password: string) =>
    api.post('/api/auth/login/', { email, password }),

  register: (username: string, email: string, password: string, confirmPassword: string) =>
    api.post('/api/auth/register/', {
      username: username,
      email: email,
      password: password,
      again_password: confirmPassword,
      first_name: username
    }),

  getCurrentUser: () =>
    api.get('/api/auth/me/'),

  logout: async () => {
    try {
      await api.post('/logout/');
      document.cookie = 'access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
      document.cookie = 'refresh_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    } catch (e) {
      console.error('Logout error:', e);
    }
  }
}