import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button, Input, Card } from '../components/ui';
import { authApi } from '../api';
import { useAppStore } from '../store/appStore';

const Register: React.FC = () => {
  const navigate = useNavigate();
  const setUser = useAppStore((state) => state.setUser);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      setError('Пароли не совпадают');
      return;
    }
    if (password.length < 6) {
      setError('Пароль должен содержать минимум 6 символов');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await authApi.register(username, email, password, confirmPassword);
      console.log('Registration response:', response.data);

      const { user } = response.data;
      setUser(user);

      window.location.href = '/dashboard';
    } catch (err: any) {
      console.error('Registration error:', err);
      const data = err.response?.data;
      if (data && typeof data === 'object') {
        if (data.error) {
          setError(data.error);
        } else if (data.email) {
          setError(Array.isArray(data.email) ? data.email[0] : data.email);
        } else if (data.username) {
          setError(Array.isArray(data.username) ? data.username[0] : data.username);
        } else {
          const firstError = Object.values(data)[0];
          setError(Array.isArray(firstError) ? firstError[0] : String(firstError));
        }
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
          <Input label="Имя пользователя" value={username} onChange={(e) => setUsername(e.target.value)} required />
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <Input label="Пароль" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          <Input label="Подтверждение пароля" type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required />

          {error && <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg text-sm">{error}</div>}

          <Button type="submit" fullWidth isLoading={loading}>
            Зарегистрироваться
          </Button>
        </form>

        <p className="mt-6 text-center text-gray-600">
          Уже есть аккаунт? <Link to="/login" className="text-purple-600 hover:underline">Войти</Link>
        </p>
      </Card>
    </div>
  );
};

export default Register;