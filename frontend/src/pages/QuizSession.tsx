import React, { useEffect, useState } from 'react';
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
  const [selectedAnswers, setSelectedAnswers] = useState<number[]>([]);
  const [isAnswered, setIsAnswered] = useState(false);

  useEffect(() => {
    console.log('QuizSession mounted, sessionId:', sessionId);
    loadQuestion(0);
  }, [sessionId]);

  useEffect(() => {
    if (!question || isAnswered) return;

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          handleSubmitAnswer();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [question, isAnswered]);

  const loadQuestion = async (index: number) => {
    setLoading(true);
    setSelectedAnswers([]);
    setIsAnswered(false);
    setTimeLeft(30);

    try {
      console.log(`Loading question index ${index} for session ${sessionId}`);
      const response = await sessionsApi.getCurrentQuestion(parseInt(sessionId!), index);

      if (response.data.finished) {
        console.log('Quiz finished, redirecting to results page');
        navigate(`/results/${sessionId}`);
        return;
      }

      console.log('Question loaded:', response.data);
      setQuestion(response.data);
      setTimeLeft(response.data.timer || 30);
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
    setIsAnswered(true);

    try {
      console.log('Submitting answer for question:', question?.id);


      if (selectedAnswers.length > 0) {

        if (question?.question_type === 'multiple') {
          await sessionsApi.submitMultipleAnswers(
            parseInt(sessionId!),
            question!.id,
            selectedAnswers
          );
        } else {
          await sessionsApi.submitAnswer(
            parseInt(sessionId!),
            question!.id,
            selectedAnswers[0]
          );
        }

      } else {
        console.log('Time expired, no answer selected');
      }

      setTimeout(() => {
        loadQuestion(question!.index + 1);
      }, 500);

    } catch (error) {
      console.error('Error submitting answer:', error);
      setIsAnswered(false);
    }
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
        <Card className="p-8 text-center">
          <p className="text-gray-700 mb-4">Вопрос не найден</p>
          <Button onClick={() => navigate('/')}>На главную</Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800 py-8 px-4">
      <div className="max-w-3xl mx-auto">
        <Card className="p-8 bg-white/90 backdrop-blur-sm">
          <div className="mb-6 flex justify-between items-center">
            <span className="text-gray-500">Вопрос {question.index + 1}</span>
            <span className="text-2xl font-bold text-purple-600">⏱ {timeLeft} сек</span>
          </div>

          <h2 className="text-2xl font-bold mb-8 text-gray-900">{question.text}</h2>

          <div className="space-y-3">
            {question.answers.map((answer) => (
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
            ))}
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