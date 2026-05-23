import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button, Card } from '../components/ui';
import { sessionsApi } from '../api';

interface Answer {
  id: number;
  text: string;
}

interface QuestionData {
  id: number;
  text: string;
  timer: number;
  index: number;
  finished?: boolean;
  answers: Answer[];
}

const QuizSession: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const [question, setQuestion] = useState<QuestionData | null>(null);
  const [answered, setAnswered] = useState(false);
  const [timeLeft, setTimeLeft] = useState<number | null>(null);
  const [error, setError] = useState('');
  const [questionIndex, setQuestionIndex] = useState(0);
  const [showTransition, setShowTransition] = useState(false);

  const fetchCurrentQuestion = async () => {
    if (!sessionId) return;
    setShowTransition(true);
    try {
      const res = await sessionsApi.getCurrentQuestion(Number(sessionId), questionIndex);
      if (res.data.finished) {
        navigate(`/results/${sessionId}`);
        return;
      }
      setTimeout(() => {
        setQuestion(res.data);
        if (res.data.timer) setTimeLeft(res.data.timer);
        setAnswered(false);
        setShowTransition(false);
      }, 300);
    } catch (err) {
      console.error('Error fetching question:', err);
      setError('Не удалось загрузить вопрос');
      setShowTransition(false);
    }
  };

  useEffect(() => {
    fetchCurrentQuestion();
  }, [sessionId, questionIndex]);

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
    try {
      await sessionsApi.submitAnswer(Number(sessionId), question!.id, -1);
      setQuestionIndex(prev => prev + 1);
    } catch (err) {
      setError('Ошибка при отправке ответа');
    }
  };

  const handleAnswer = async (answerId: number) => {
    if (answered) return;
    setAnswered(true);
    try {
      await sessionsApi.submitAnswer(Number(sessionId), question!.id, answerId);
      setQuestionIndex(prev => prev + 1);
    } catch (err) {
      setError('Ошибка при отправке ответа');
    }
  };

  if (error) return <div className="text-red-600 text-center mt-10">{error}</div>;

  if (showTransition) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-white border-opacity-50 mx-auto mb-4"></div>
          <p className="text-white text-lg animate-pulse">Загрузка следующего вопроса...</p>
        </div>
      </div>
    );
  }

  if (!question) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800 flex items-center justify-center p-4">
      <Card className="max-w-2xl w-full p-8 bg-white/90 backdrop-blur-sm animate-fadeIn">
        {timeLeft !== null && (
          <div className={`text-right text-2xl font-mono mb-4 transition-all duration-300 ${timeLeft <= 5 ? 'text-red-600 animate-pulse' : 'text-gray-600'}`}>
            {timeLeft} сек
          </div>
        )}
        <h2 className="text-2xl font-bold mb-6 text-gray-900">{question.text}</h2>
        <div className="space-y-3">
          {question.answers.map((answer, idx) => (
            <Button
              key={answer.id}
              variant="outline"
              fullWidth
              onClick={() => handleAnswer(answer.id)}
              disabled={answered}
              className={`transform transition-all duration-200 hover:scale-105 ${answered ? 'opacity-50' : ''}`}
              style={{ animationDelay: `${idx * 50}ms` }}
            >
              {answer.text}
            </Button>
          ))}
        </div>
        {answered && (
          <div className="mt-4 text-center text-gray-500 animate-pulse">
            Ответ принят, загружаем следующий вопрос...
          </div>
        )}
      </Card>
    </div>
  );
};

export default QuizSession;