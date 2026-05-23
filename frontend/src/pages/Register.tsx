import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button, Input, Card } from '../components/ui';
import { authApi } from '../api';
import { useAppStore } from '../store/appStore';

const Register: React.FC = () => {
  const navigate = useNavigate();
  const setUser = useAppStore((state) => state.setUser);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const validate = (): boolean => {
    if (!name.trim()) {
      setError('Введите имя');
      return false;
    }
    if (!email.trim()) {
      setError('Введите email');
      return false;
    }
    if (!password) {
      setError('Введите пароль');
      return false;
    }
    if (password.length < 6) {
      setError('Пароль должен содержать минимум 6 символов');
      return false;
    }
    if (password !== confirmPassword) {
      setError('Пароли не совпадают');
      return false;
    }
    setError('');
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    try {
      const response = await authApi.register(name, email, password, confirmPassword);
      const { access, refresh, user } = response.data;
      authApi.saveTokens(access, refresh);
      setUser(user);
      navigate('/dashboard');
    } catch (err: any) {
      const data = err.response?.data;
      if (data && typeof data === 'object') {
        const firstError = Object.values(data)[0];
        setError(Array.isArray(firstError) ? firstError[0] : String(firstError));
      } else {
        setError('Ошибка регистрации. Попробуйте другой email.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="max-w-md w-full p-8 bg-white/90 backdrop-blur-sm">
        <div className="text-center mb-6">
          <h2 className="text-3xl font-bold text-gray-900">Регистрация</h2>
          <p className="text-gray-600 mt-2">Создайте аккаунт организатора</p>
        </div>

        <form onSubmit={handleSubmit}>
          <Input
            label="Имя"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <Input
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <Input
            label="Пароль"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
          />
          <Input
            label="Подтверждение пароля"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />

          {error && (
            <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}

          <Button type="submit" fullWidth isLoading={loading}>
            Зарегистрироваться
          </Button>
        </form>

        <p className="mt-6 text-center text-gray-600">
          Уже есть аккаунт?{' '}
          <Link to="/login" className="text-purple-600 hover:text-purple-700 font-medium hover:underline">
            Войти
          </Link>
        </p>
      </Card>
    </div>
  );
};

export default Register;