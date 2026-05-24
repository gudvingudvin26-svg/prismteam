import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button, Input, Card } from '../components/ui';
import { authApi } from '../api';
import { useAppStore } from '../store/appStore';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const setUser = useAppStore((state) => state.setUser);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password) {
      setError('Заполните все поля');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const response = await authApi.login(email, password);
      const { access, refresh, user } = response.data;
      authApi.saveTokens(access, refresh);
      setUser(user);
      navigate('/dashboard');
    } catch (err: any) {
      const status = err.response?.status;
      const data = err.response?.data;

      if (status === 401) {
        setError('Неверный email или пароль');
      } else if (status === 400) {
        setError('Заполните все поля');
      } else {
        setError(data?.detail || data?.message || data?.error || 'Ошибка входа. Проверьте email и пароль.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="max-w-md w-full p-8 bg-white/90 backdrop-blur-sm">
        <div className="text-center mb-6">
          <h2 className="text-3xl font-bold text-gray-900">Вход</h2>
          <p className="text-gray-600 mt-2">Войдите в свой аккаунт</p>
        </div>

        <form onSubmit={handleSubmit}>
          <Input
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="example@mail.com"
            required
          />
          <Input
            label="Пароль"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
          />

          {error && (
            <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}

          <Button type="submit" fullWidth isLoading={loading}>
            {loading ? 'Вход...' : 'Войти'}
          </Button>
        </form>

        <p className="mt-6 text-center text-gray-600">
          Нет аккаунта?{' '}
          <Link to="/register" className="text-purple-600 hover:text-purple-700 font-medium hover:underline">
            Зарегистрироваться
          </Link>
        </p>
      </Card>
    </div>
  );
};

export default Login;