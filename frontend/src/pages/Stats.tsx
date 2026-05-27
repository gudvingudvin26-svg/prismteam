import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Button } from '../components/ui';
import { quizzesApi, sessionsApi } from '../api';
import { useAppStore } from '../store/appStore';

interface UserStats {
  created_quizzes: number;
  completed_quizzes: number;
  total_correct_answers: number;
  total_points: number;
  average_score: number;
}

const Stats: React.FC = () => {
  const navigate = useNavigate();
  const user = useAppStore((state) => state.user);
  const [stats, setStats] = useState<UserStats>({
    created_quizzes: 0,
    completed_quizzes: 0,
    total_correct_answers: 0,
    total_points: 0,
    average_score: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      try {
        const response = await quizzesApi.getMyQuizzes();
        const userQuizzes = response.data;

        let completedQuizIds = new Set();
        let totalCorrect = 0;
        let totalPoints = 0;

        for (const quiz of userQuizzes) {
          try {
            const sessionsResponse = await sessionsApi.getSessionsForQuiz(quiz.id);
            const sessions = sessionsResponse.data;

            for (const session of sessions) {
              if (session.status === 'completed' && session.participant_name && session.participant_name !== '') {
                completedQuizIds.add(quiz.id);

                try {
                  const resultsResponse = await sessionsApi.getMyResult(session.id);
                  const sessionResults = resultsResponse.data;

                  console.log(`Session ${session.id} (player: ${session.participant_name}) results:`, sessionResults);

                  if (sessionResults) {
                    if (sessionResults.correct_answers) {
                      totalCorrect += sessionResults.correct_answers;
                    }
                    if (sessionResults.score) {
                      totalPoints += sessionResults.score;
                    }
                  }
                } catch (e) {
                  console.error('Error fetching session results:', e);
                }
              }
            }
          } catch (e) {
            console.error('Error fetching sessions for quiz:', e);
          }
        }

        const averageScore = completedQuizIds.size > 0 ? Math.round(totalPoints / completedQuizIds.size) : 0;

        console.log('Final stats:', {
          created_quizzes: userQuizzes.length,
          completed_quizzes: completedQuizIds.size,
          total_correct_answers: totalCorrect,
          total_points: totalPoints,
          average_score: averageScore,
        });

        setStats({
          created_quizzes: userQuizzes.length,
          completed_quizzes: completedQuizIds.size,
          total_correct_answers: totalCorrect,
          total_points: totalPoints,
          average_score: averageScore,
        });
      } catch (err: any) {
        console.error('Error fetching stats:', err);
        setError('Ошибка загрузки статистики');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800">
        <div className="text-white text-xl">Загрузка статистики...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800">
        <Card className="p-8 text-center max-w-md bg-white/90 backdrop-blur-sm">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Ошибка</h2>
          <p className="text-gray-700 mb-6">{error}</p>
          <div className="flex gap-4 justify-center">
            <Button variant="outline" onClick={() => navigate(-1)}>Назад</Button>
            <Button onClick={() => navigate('/dashboard')}>В панель управления</Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-white">Статистика игрока</h1>
          <div className="flex gap-4">
            <Button variant="outline" onClick={() => navigate(-1)} className="!text-black bg-white hover:bg-gray-100">
              Назад
            </Button>
            <Button variant="outline" onClick={() => navigate('/dashboard')} className="!text-black bg-white hover:bg-gray-100">
              Панель управления
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <Card className="p-4 text-center bg-white/90 backdrop-blur-sm">
            <p className="text-gray-500 text-sm mb-1">Создано квизов</p>
            <p className="text-3xl font-bold text-purple-600">{stats.created_quizzes}</p>
          </Card>
          <Card className="p-4 text-center bg-white/90 backdrop-blur-sm">
            <p className="text-gray-500 text-sm mb-1">Пройдено квизов</p>
            <p className="text-3xl font-bold text-blue-600">{stats.completed_quizzes}</p>
          </Card>
          <Card className="p-4 text-center bg-white/90 backdrop-blur-sm">
            <p className="text-gray-500 text-sm mb-1">Правильных ответов</p>
            <p className="text-3xl font-bold text-green-600">{stats.total_correct_answers}</p>
          </Card>
          <Card className="p-4 text-center bg-white/90 backdrop-blur-sm">
            <p className="text-gray-500 text-sm mb-1">Всего баллов</p>
            <p className="text-3xl font-bold text-orange-600">{stats.total_points}</p>
          </Card>
          <Card className="p-4 text-center bg-white/90 backdrop-blur-sm">
            <p className="text-gray-500 text-sm mb-1">Средний балл</p>
            <p className="text-3xl font-bold text-red-600">{stats.average_score}</p>
          </Card>
        </div>

        <div className="bg-white/90 backdrop-blur-sm rounded-lg shadow-xl p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900">Детализация</h2>
          <div className="space-y-2 text-gray-700">
            <p>• Вы создали <span className="font-bold text-purple-600">{stats.created_quizzes}</span> квизов</p>
            <p>• Вы прошли <span className="font-bold text-blue-600">{stats.completed_quizzes}</span> квизов</p>
            <p>• Правильных ответов: <span className="font-bold text-green-600">{stats.total_correct_answers}</span></p>
            <p>• Всего набрано баллов: <span className="font-bold text-orange-600">{stats.total_points}</span></p>
            <p>• Средний балл за квиз: <span className="font-bold text-red-600">{stats.average_score}</span></p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Stats;