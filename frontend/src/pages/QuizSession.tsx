/**
 * @fileoverview Страница прохождения квиза участником.
 * Отображает текущий вопрос, таймер, варианты ответов.
 * После ответа переходит к следующему вопросу.
 * В конце игры перенаправляет на страницу результатов.
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button, Card } from '../components/ui';
import { sessionsApi } from '../api';
import { CurrentQuestion } from '../types';

const QuizSession: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const [question, setQuestion] = useState<CurrentQuestion | null>(null);
  const [loading, setLoading] = useState(true);
  const [answered, setAnswered] = useState(false);
  const [timeLeft, setTimeLeft] = useState<number | null>(null);
  const [error, setError] = useState('');

  const fetchCurrentQuestion = async () => {
    if (!sessionId) return;
    try {
      const res = await sessionsApi.getCurrentQuestion(Number(sessionId));
      setQuestion(res.data);
      if (res.data.timer) setTimeLeft(res.data.timer);
      setAnswered(false);
    } catch (err) {
      setError('Не удалось загрузить вопрос');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCurrentQuestion();
  }, [sessionId]);

  // Таймер
  useEffect(() => {
    if (timeLeft === null || timeLeft <= 0 || answered) return;
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev === null || prev <= 1) {
          clearInterval(timer);
          if (!answered) handleTimeout();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [timeLeft, answered]);

  const handleTimeout = async () => {
    if (answered) return;
    setAnswered(true);
    // Отправляем пустой ответ или -1, сигнализируя о просрочке
    try {
      await sessionsApi.submitAnswer(Number(sessionId), question!.id, -1);
      // Переход к следующему вопросу
      await fetchCurrentQuestion();
    } catch (err) {
      setError('Ошибка при отправке ответа');
    }
  };

  const handleAnswer = async (answerId: number) => {
    if (answered) return;
    setAnswered(true);
    try {
      await sessionsApi.submitAnswer(Number(sessionId), question!.id, answerId);
      // Загружаем следующий вопрос (если есть)
      await fetchCurrentQuestion();
    } catch (err) {
      setError('Ошибка при отправке ответа');
    }
  };

  if (loading) return <div className="flex justify-center items-center h-screen">Загрузка вопроса...</div>;
  if (error) return <div className="text-red-600 text-center mt-10">{error}</div>;
  if (!question) {
    // Вопросов больше нет – игра завершена
    navigate(`/results/${sessionId}`);
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <Card className="max-w-2xl w-full p-8">
        {timeLeft !== null && (
          <div className="text-right text-2xl font-mono mb-4">
            {timeLeft} сек
          </div>
        )}
        <h2 className="text-2xl font-bold mb-6">{question.text}</h2>
        <div className="space-y-3">
          {question.answers.map((answer) => (
            <Button
              key={answer.id}
              variant="outline"
              fullWidth
              onClick={() => handleAnswer(answer.id)}
              disabled={answered}
            >
              {answer.text}
            </Button>
          ))}
        </div>
        {answered && <div className="mt-4 text-center text-gray-500">Ответ принят, загружаем следующий вопрос...</div>}
      </Card>
    </div>
  );
};

export default QuizSession;