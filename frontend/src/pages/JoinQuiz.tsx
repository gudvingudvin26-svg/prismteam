/**
 * @fileoverview Страница для входа участника в игру по коду.
 * Участник вводит 6-значный код и свой никнейм, затем перенаправляется на страницу игры.
 */

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
    try {
      const response = await sessionsApi.joinSession(code.toUpperCase(), nickname);
      const sessionId = response.data.session_id; // предположим, что бэк возвращает session_id
      navigate(`/play/${sessionId}`);
    } catch (err) {
      setError('Неверный код или ошибка подключения');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
      <Card className="max-w-md w-full p-8">
        <h2 className="text-2xl font-bold text-center mb-6">Вход в игру</h2>
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
            Войти
          </Button>
        </form>
      </Card>
    </div>
  );
};

export default JoinQuiz;