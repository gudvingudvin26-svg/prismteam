import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Card, Button } from '../components/ui';
import { quizzesApi, sessionsApi } from '../api';

const Stats: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [quizzes, setQuizzes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedQuiz, setSelectedQuiz] = useState<number | null>(null);
  const [quizStats, setQuizStats] = useState<any>(null);
  const [leaderboard, setLeaderboard] = useState<any[]>([]);
  const [questionsStats, setQuestionsStats] = useState<any[]>([]);

  useEffect(() => {
    loadQuizzes();
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const quizId = params.get('quiz');
    if (quizId && quizzes.length > 0) {
      const quiz = quizzes.find(q => q.id === parseInt(quizId));
      if (quiz) {
        loadQuizStats(parseInt(quizId));
      }
    }
  }, [quizzes, location.search]);

  const loadQuizzes = async () => {
    setLoading(true);
    try {
      const response = await quizzesApi.getMyQuizzes();
      setQuizzes(response.data);
    } catch (error) {
      console.error('Error loading quizzes:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadQuizStats = async (quizId: number) => {
    setSelectedQuiz(quizId);
    setLeaderboard([]);
    setQuestionsStats([]);
    setQuizStats(null);

    try {
      const sessionsResponse = await sessionsApi.getSessionsForQuiz(quizId);
      const sessions = sessionsResponse.data;

      const uniqueParticipants = new Map();

      for (const session of sessions) {
        if (session.participant_name) {
          try {
            const resultsResponse = await sessionsApi.getResults(session.id);
            const results = resultsResponse.data;

            if (Array.isArray(results)) {
              for (const result of results) {
                const name = result.participant_name || session.participant_name;
                if (!uniqueParticipants.has(name) || uniqueParticipants.get(name) < result.score) {
                  uniqueParticipants.set(name, result.score);
                }
              }
            } else if (results && typeof results === 'object') {
              const name = results.participant_name || session.participant_name;
              if (!uniqueParticipants.has(name) || uniqueParticipants.get(name) < (results.score || 0)) {
                uniqueParticipants.set(name, results.score || 0);
              }
            }
          } catch (e) {
            console.error('Error fetching results:', e);
          }
        }
      }

      const completedSessions = sessions.filter((s: any) => s.status === 'completed');
      const totalScore = Array.from(uniqueParticipants.values()).reduce((sum, score) => sum + score, 0);
      const averageScore = uniqueParticipants.size > 0 ? Math.round(totalScore / uniqueParticipants.size) : 0;

      setQuizStats({
        total_sessions: sessions.length,
        total_participants: uniqueParticipants.size,
        completed_sessions: completedSessions.length,
        average_score: averageScore
      });

      const leaderboardData = Array.from(uniqueParticipants.entries())
        .map(([name, score]) => ({ participant_name: name, score }))
        .sort((a, b) => b.score - a.score)
        .slice(0, 10);

      setLeaderboard(leaderboardData);

      if (completedSessions.length > 0) {
        const allQuestionsStats: { [key: number]: { text: string; total: number; correct: number } } = {};

        for (const session of completedSessions.slice(0, 5)) {
          try {
            const statsResponse = await sessionsApi.getQuestionsStats(session.id);
            if (Array.isArray(statsResponse.data)) {
              for (const stat of statsResponse.data) {
                if (!allQuestionsStats[stat.question_id]) {
                  allQuestionsStats[stat.question_id] = {
                    text: stat.question_text,
                    total: 0,
                    correct: 0
                  };
                }
                allQuestionsStats[stat.question_id].total += stat.total_answers || 0;
                allQuestionsStats[stat.question_id].correct += stat.correct_count || 0;
              }
            }
          } catch (e) {
            console.error('Error fetching stats:', e);
          }
        }

        const formattedStats = Object.values(allQuestionsStats).map(stat => ({
          question_text: stat.text,
          total_answers: stat.total,
          correct_count: stat.correct,
          correct_percent: stat.total > 0 ? Math.round((stat.correct / stat.total) * 100) : 0
        }));

        setQuestionsStats(formattedStats);
      }
    } catch (error) {
      console.error('Error loading quiz stats:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800">
        <div className="text-white text-xl">Загрузка статистики...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-6 flex-wrap gap-4">
          <h1 className="text-2xl font-bold text-white">Статистика</h1>
          <div className="flex gap-4">
            <Button variant="outline" onClick={() => navigate('/dashboard')}>
              ← Панель управления
            </Button>
            <Button variant="outline" onClick={() => navigate('/quizzes')}>
              Мои квизы
            </Button>
          </div>
        </div>

        {quizzes.length === 0 ? (
          <Card className="p-8 text-center bg-white/90 backdrop-blur-sm">
            <p className="text-gray-600">У вас пока нет квизов для отображения статистики.</p>
            <Button variant="primary" className="mt-4" onClick={() => navigate('/quizzes/create')}>
              Создать квиз
            </Button>
          </Card>
        ) : (
          <>
            <div className="grid md:grid-cols-2 gap-6 mb-8">
              {quizzes.map((quiz) => (
                <Card
                  key={quiz.id}
                  className={`p-5 bg-white/90 backdrop-blur-sm cursor-pointer hover:shadow-lg transition ${
                    selectedQuiz === quiz.id ? 'ring-2 ring-purple-500' : ''
                  }`}
                  onClick={() => loadQuizStats(quiz.id)}
                >
                  <h3 className="text-xl font-semibold mb-2 text-gray-900">{quiz.title}</h3>
                  <p className="text-gray-600 mb-4">{quiz.description || 'Без описания'}</p>
                  <div className="text-sm text-gray-500">
                    Создан: {new Date(quiz.created_at || Date.now()).toLocaleDateString()}
                  </div>
                </Card>
              ))}
            </div>

            {selectedQuiz && quizStats && (
              <div className="bg-white/90 backdrop-blur-sm rounded-lg shadow-xl p-6">
                <h2 className="text-xl font-bold mb-4 text-gray-900">Статистика квиза</h2>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                  <Card className="p-4 text-center bg-white shadow-md">
                    <p className="text-gray-500 text-sm">Всего сессий</p>
                    <p className="text-2xl font-bold text-blue-600">{quizStats.total_sessions || 0}</p>
                  </Card>
                  <Card className="p-4 text-center bg-white shadow-md">
                    <p className="text-gray-500 text-sm">Участников</p>
                    <p className="text-2xl font-bold text-green-600">{quizStats.total_participants || 0}</p>
                  </Card>
                  <Card className="p-4 text-center bg-white shadow-md">
                    <p className="text-gray-500 text-sm">Завершено</p>
                    <p className="text-2xl font-bold text-purple-600">{quizStats.completed_sessions || 0}</p>
                  </Card>
                  <Card className="p-4 text-center bg-white shadow-md">
                    <p className="text-gray-500 text-sm">Средний балл</p>
                    <p className="text-2xl font-bold text-orange-600">{quizStats.average_score || 0}</p>
                  </Card>
                </div>

                {leaderboard.length > 0 && (
                  <>
                    <h3 className="text-lg font-semibold mb-4 text-gray-900">Таблица лидеров</h3>
                    <div className="overflow-x-auto mb-8">
                      <table className="w-full">
                        <thead className="bg-gray-100">
                          <tr>
                            <th className="p-3 text-left">Место</th>
                            <th className="p-3 text-left">Участник</th>
                            <th className="p-3 text-left">Баллы</th>
                          </tr>
                        </thead>
                        <tbody>
                          {leaderboard.map((item, idx) => (
                            <tr key={idx} className="border-t">
                              <td className="p-3">{idx + 1}</td>
                              <td className="p-3">{item.participant_name}</td>
                              <td className="p-3 font-bold text-blue-600">{item.score}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </>
                )}

                {questionsStats.length > 0 && (
                  <>
                    <h3 className="text-lg font-semibold mb-4 text-gray-900">Статистика по вопросам</h3>
                    <div className="space-y-4">
                      {questionsStats.map((stat, idx) => (
                        <Card key={idx} className="p-4 bg-white shadow-md">
                          <p className="font-medium text-gray-900 mb-2">{stat.question_text}</p>
                          <div className="w-full bg-gray-200 rounded-full h-4">
                            <div
                              className="bg-green-500 h-4 rounded-full transition-all duration-500"
                              style={{ width: `${stat.correct_percent}%` }}
                            ></div>
                          </div>
                          <p className="text-sm text-gray-600 mt-2">
                            {stat.correct_count} из {stat.total_answers} правильных ({stat.correct_percent}%)
                          </p>
                        </Card>
                      ))}
                    </div>
                  </>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Stats;