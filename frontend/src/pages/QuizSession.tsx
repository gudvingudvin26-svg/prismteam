import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button, Card } from '../components/ui';
import { sessionsApi } from '../api';

interface Question {
  id: number;
  text: string;
  timer: number;
  index: number;
  question_type: string;
  answers: { id: number; text: string }[];
}

const QuizSession: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const [question, setQuestion] = useState<Question | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeLeft, setTimeLeft] = useState(30);
  const [globalTimeLeft, setGlobalTimeLeft] = useState<number | null>(null);
  const [selectedAnswers, setSelectedAnswers] = useState<number[]>([]);
  const [isAnswered, setIsAnswered] = useState(false);
  const [globalTimerStarted, setGlobalTimerStarted] = useState(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const globalTimerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const checkCompleted = async () => {
      try {
        const response = await sessionsApi.getSession(parseInt(sessionId!));
        if (response.data.is_completed) {
          navigate(`/results/${sessionId}`, { replace: true });
          return;
        }
      } catch (error) {
        console.error('Error checking session:', error);
      }
    };
    checkCompleted();
  }, [sessionId, navigate]);

  useEffect(() => {
    loadQuestion(0);
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (globalTimerRef.current) clearInterval(globalTimerRef.current);
    };
  }, [sessionId]);

  useEffect(() => {
    if (!question || isAnswered) return;

    if (timerRef.current) clearInterval(timerRef.current);

    timerRef.current = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timerRef.current!);
          handleAutoNext();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [question, isAnswered]);

  const startGlobalTimer = (quizTimerValue: number) => {
    // Запускаем таймер только один раз
    if (globalTimerStarted) return;

    if (globalTimerRef.current) clearInterval(globalTimerRef.current);

    setGlobalTimerStarted(true);
    setGlobalTimeLeft(quizTimerValue);

    console.log(`Общий таймер запущен: ${quizTimerValue} секунд`);

    globalTimerRef.current = setInterval(() => {
      setGlobalTimeLeft((prev) => {
        if (prev === null || prev <= 1) {
          if (globalTimerRef.current) clearInterval(globalTimerRef.current);
          handleGlobalTimeout();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const handleGlobalTimeout = async () => {
    console.log('Общий таймер закончился!');
    if (timerRef.current) clearInterval(timerRef.current);
    if (globalTimerRef.current) clearInterval(globalTimerRef.current);

    try {
      await sessionsApi.endSession(parseInt(sessionId!));
      navigate(`/results/${sessionId}`, { replace: true });
    } catch (error) {
      console.error('Error ending session:', error);
      navigate(`/results/${sessionId}`, { replace: true });
    }
  };

  const handleAutoNext = async () => {
    if (isAnswered) return;
    setIsAnswered(true);

    if (timerRef.current) clearInterval(timerRef.current);

    if (selectedAnswers.length === 0) {
      setTimeout(() => {
        loadQuestion(question!.index + 1);
      }, 500);
    } else {
      try {
        if (question?.question_type === 'multiple') {
          await sessionsApi.submitMultipleAnswers(parseInt(sessionId!), question!.id, selectedAnswers);
        } else {
          await sessionsApi.submitAnswer(parseInt(sessionId!), question!.id, selectedAnswers[0]);
        }
        setTimeout(() => {
          loadQuestion(question!.index + 1);
        }, 500);
      } catch (error) {
        console.error('Error submitting answer:', error);
        setIsAnswered(false);
      }
    }
  };

  const loadQuestion = async (index: number) => {
    setLoading(true);
    setSelectedAnswers([]);
    setIsAnswered(false);
    setTimeLeft(30);

    try {
      const response = await sessionsApi.getCurrentQuestion(parseInt(sessionId!), index);

      if (response.data.finished || response.data.is_completed) {
        navigate(`/results/${sessionId}`, { replace: true });
        return;
      }

      setQuestion(response.data);
      const questionTimer = response.data.timer || 30;
      setTimeLeft(questionTimer);

      if (!globalTimerStarted) {
        const sessionResponse = await sessionsApi.getSession(parseInt(sessionId!));
        let quizGlobalTimer = sessionResponse.data.quiz?.timer;

        if (!quizGlobalTimer || quizGlobalTimer <= 0) {
          console.log('Таймер не задан, используется значение по умолчанию: 60 секунд');
          quizGlobalTimer = 60;
        } else {
          console.log(`Таймер квиза: ${quizGlobalTimer} секунд`);
        }

        startGlobalTimer(quizGlobalTimer);
      }

    } catch (error) {
      console.error('Error fetching question:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleAnswer = (answerId: number) => {
    if (isAnswered) return;

    if (question?.question_type === 'multiple') {
      setSelectedAnswers(prev =>
        prev.includes(answerId)
          ? prev.filter(id => id !== answerId)
          : [...prev, answerId]
      );
    } else {
      setSelectedAnswers([answerId]);
    }
  };

  const handleSubmitAnswer = async () => {
    if (isAnswered) return;
    if (selectedAnswers.length === 0) return;

    setIsAnswered(true);
    if (timerRef.current) clearInterval(timerRef.current);

    try {
      if (question?.question_type === 'multiple') {
        await sessionsApi.submitMultipleAnswers(parseInt(sessionId!), question!.id, selectedAnswers);
      } else {
        await sessionsApi.submitAnswer(parseInt(sessionId!), question!.id, selectedAnswers[0]);
      }

      setTimeout(() => {
        loadQuestion(question!.index + 1);
      }, 500);
    } catch (error) {
      console.error('Error submitting answer:', error);
      setIsAnswered(false);
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800">
        <div className="text-white text-xl">Загрузка вопроса...</div>
      </div>
    );
  }

  if (!question) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800">
        <Card className="p-8 text-center bg-white/90 backdrop-blur-sm">
          <p className="text-gray-700 mb-4">Вопрос не найден</p>
          <Button onClick={() => navigate('/')}>На главную</Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800 py-8 px-4">
      <div className="max-w-3xl mx-auto">
        {globalTimeLeft !== null && (
          <div className="fixed top-4 right-4 bg-white/90 backdrop-blur-sm rounded-lg px-4 py-2 shadow-lg z-10">
            <span className="text-gray-600 mr-2">⏱ Общее время:</span>
            <span className={`text-2xl font-bold ${globalTimeLeft < 10 ? 'text-red-600' : 'text-purple-600'}`}>
              {formatTime(globalTimeLeft)}
            </span>
          </div>
        )}

        <Card className="p-8 bg-white/90 backdrop-blur-sm">
          <div className="mb-6 flex justify-between items-center">
            <span className="text-gray-500">Вопрос {question.index + 1}</span>
            <span className={`text-2xl font-bold ${timeLeft < 10 ? 'text-red-600 animate-pulse' : 'text-purple-600'}`}>
              ⏱ {timeLeft} сек
            </span>
          </div>

          <h2 className="text-2xl font-bold mb-8 text-gray-900">{question.text}</h2>

          <div className="space-y-3">
            {question.answers && question.answers.length > 0 ? (
              question.answers.map((answer) => (
                <button
                  key={answer.id}
                  onClick={() => toggleAnswer(answer.id)}
                  disabled={isAnswered}
                  className={`w-full text-left p-4 rounded-lg border transition ${
                    selectedAnswers.includes(answer.id)
                      ? 'bg-purple-100 border-purple-500'
                      : 'bg-white border-gray-300 hover:bg-purple-50'
                  } ${isAnswered ? 'cursor-not-allowed opacity-70' : 'cursor-pointer'}`}
                >
                  {answer.text}
                </button>
              ))
            ) : (
              <div className="text-center text-gray-500">Нет вариантов ответа</div>
            )}
          </div>

          <div className="mt-8">
            <Button
              onClick={handleSubmitAnswer}
              disabled={isAnswered || selectedAnswers.length === 0}
              fullWidth
            >
              {selectedAnswers.length === 0 ? 'Выберите ответ' : 'Ответить'}
            </Button>
          </div>

          {question.question_type === 'multiple' && (
            <p className="mt-4 text-sm text-gray-500 text-center">
              Выбрано вариантов: {selectedAnswers.length}
            </p>
          )}
        </Card>
      </div>
    </div>
  );
};

export default QuizSession;