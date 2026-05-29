import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Input, Card } from '../components/ui';
import { sessionsApi } from '../api';

const JoinQuiz: React.FC = () => {
  const navigate = useNavigate();
  const [code, setCode] = useState('');
  const [nickname, setNickname] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!code.trim() || code.length !== 6) {
      setError('Введите 6-значный код');
      return;
    }
    if (!nickname.trim()) {
      setError('Введите ваше имя');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const response = await sessionsApi.joinSession(code.toUpperCase(), nickname);
      const sessionId = response.data.session_id;
      navigate(`/play/${sessionId}`, { replace: true });
    } catch (err: any) {
      const status = err.response?.status;
      const data = err.response?.data;
      if (status === 404) {
        setError('Сессия с таким кодом не найдена');
      } else if (status === 400 && data?.error === 'Вы уже проходили этот квиз') {
        setError('Вы уже проходили этот квиз');
      } else {
        setError(data?.error || 'Ошибка подключения к сессии');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800 px-4">
      <Card className="max-w-md w-full p-8 bg-white/90 backdrop-blur-sm">
        <h2 className="text-2xl font-bold text-center mb-6 text-gray-900">Вход в игру</h2>
        <form onSubmit={handleSubmit}>
          <Input
            label="Код комнаты"
            value={code}
            onChange={(e) => setCode(e.target.value.toUpperCase())}
            placeholder="XXXXXX"
            maxLength={6}
            required
          />
          <Input
            label="Ваше имя"
            value={nickname}
            onChange={(e) => setNickname(e.target.value)}
            required
          />
          {error && <div className="mb-4 text-red-600 text-sm">{error}</div>}
          <Button type="submit" fullWidth isLoading={loading}>
            {loading ? 'Подключение...' : 'Войти'}
          </Button>
        </form>
      </Card>
    </div>
  );
};

export default JoinQuiz;