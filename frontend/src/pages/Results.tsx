import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Card, Button } from '../components/ui';
import { sessionsApi } from '../api';
import { useAppStore } from '../store/appStore';

interface MyResult {
  score: number;
  total_questions: number;
  correct_answers: number;
  rank: number;
}

interface LeaderboardEntry {
  participant_name: string;
  score: number;
  rank: number;
  id?: number;
}

interface QuestionStat {
  question_id: number;
  question_text: string;
  total_answers: number;
  correct_count: number;
  correct_percent: number;
}

const Results: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const user = useAppStore((state) => state.user);
  const [myResult, setMyResult] = useState<MyResult | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [questionsStats, setQuestionsStats] = useState<QuestionStat[]>([]);
  const [loading, setLoading] = useState(true);
  const [isOwner, setIsOwner] = useState(false);
  const [quizId, setQuizId] = useState<number | null>(null);

  useEffect(() => {
    const fetchResults = async () => {
      if (!sessionId) return;
      try {
        const [myRes, leaderRes, statsRes, sessionRes] = await Promise.all([
          sessionsApi.getMyResult(Number(sessionId)),
          sessionsApi.getResults(Number(sessionId)),
          sessionsApi.getQuestionsStats(Number(sessionId)),
          sessionsApi.getSession(Number(sessionId)),
        ]);

        setMyResult(myRes.data);
        setQuizId(sessionRes.data.quiz?.id || null);

        if (Array.isArray(leaderRes.data)) {
          setLeaderboard(leaderRes.data);
        } else {
          setLeaderboard([]);
        }

        if (Array.isArray(statsRes.data)) {
          setQuestionsStats(statsRes.data);
        } else {
          setQuestionsStats([]);
        }

        if (sessionRes.data && user && sessionRes.data.quiz?.created_by?.id === user.id) {
          setIsOwner(true);
        }
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };
    fetchResults();
  }, [sessionId, user]);

  useEffect(() => {
    const handlePopState = () => {
      if (sessionId) {
        navigate(`/results/${sessionId}`, { replace: true });
      }
    };

    window.addEventListener('popstate', handlePopState);
    history.pushState(null, '', window.location.href);

    return () => {
      window.removeEventListener('popstate', handlePopState);
    };
  }, [sessionId, navigate]);

  if (loading) return <div className="flex justify-center items-center h-screen text-white">Загрузка результатов...</div>;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800 py-8 px-4">
      <div className="max-w-4xl mx-auto bg-white/90 backdrop-blur-sm rounded-lg shadow-xl p-6">
        <div className="flex justify-between items-center mb-6 flex-wrap gap-4">
          <h1 className="text-2xl font-bold text-gray-900">Результаты</h1>
          <div className="flex gap-3 flex-wrap">
            {isOwner && (
              <>
                <Link to="/dashboard">
                  <Button variant="primary" className="!text-black bg-white hover:bg-gray-100">
                    📊 Панель управления
                  </Button>
                </Link>
                {quizId && (
                  <Link to={`/stats?quiz=${quizId}`}>
                    <Button variant="outline" className="!text-black bg-white hover:bg-gray-100">
                      📈 Статистика квиза
                    </Button>
                  </Link>
                )}
              </>
            )}
            <Link to="/">
              <Button variant="outline" className="!text-black bg-white hover:bg-gray-100">
                🏠 На главную
              </Button>
            </Link>
          </div>
        </div>

        {myResult && (
          <Card className="p-6 mb-8 text-center bg-gradient-to-r from-blue-50 to-purple-50">
            <h2 className="text-xl font-semibold mb-2">Ваш результат</h2>
            <p className="text-3xl font-bold text-blue-600">{myResult.score} баллов</p>
            <p className="mt-2">Правильных ответов: {myResult.correct_answers} из {myResult.total_questions}</p>
            <p className="text-lg font-semibold mt-2">Место: #{myResult.rank}</p>
          </Card>
        )}

        <h2 className="text-xl font-semibold mb-4">🏆 Таблица лидеров</h2>
        <Card className="p-0 overflow-hidden mb-8">
          <table className="w-full">
            <thead className="bg-gray-100">
              <tr>
                <th className="p-3 text-left">Место</th>
                <th className="p-3 text-left">Участник</th>
                <th className="p-3 text-left">Баллы</th>
              </tr>
            </thead>
            <tbody>
              {leaderboard.map((p, idx) => (
                <tr key={idx} className="border-t hover:bg-gray-50">
                  <td className="p-3 font-bold">#{p.rank || idx + 1}</td>
                  <td className="p-3">{p.participant_name || 'Без имени'}</td>
                  <td className="p-3 font-semibold text-blue-600">{p.score}</td>
                </tr>
              ))}
              {leaderboard.length === 0 && (
                <tr>
                  <td colSpan={3} className="p-3 text-center text-gray-500">Нет данных</td>
                </tr>
              )}
            </tbody>
          </table>
        </Card>

        {questionsStats.length > 0 && (
          <>
            <h2 className="text-xl font-semibold mb-4">📊 Статистика по вопросам</h2>
            <div className="space-y-3">
              {questionsStats.map((stat, idx) => (
                <Card key={stat.question_id || idx} className="p-4">
                  <p className="font-medium">{stat.question_text}</p>
                  <div className="w-full bg-gray-200 rounded-full h-4 mt-2">
                    <div
                      className="bg-green-500 h-4 rounded-full transition-all duration-500"
                      style={{ width: `${stat.correct_percent}%` }}
                    ></div>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    {stat.correct_count} из {stat.total_answers} правильных ({stat.correct_percent}%)
                  </p>
                </Card>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Results;