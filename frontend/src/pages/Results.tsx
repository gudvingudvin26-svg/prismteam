import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card, Button } from '../components/ui';
import { sessionsApi } from '../api';

interface ParticipantResult {
  id: number;
  participant_name: string;
  score: number;
  total_questions: number;
  rank: number;
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
  const [myResult, setMyResult] = useState<ParticipantResult | null>(null);
  const [leaderboard, setLeaderboard] = useState<ParticipantResult[]>([]);
  const [questionsStats, setQuestionsStats] = useState<QuestionStat[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchResults = async () => {
      if (!sessionId) return;
      try {
        const [myRes, leaderRes, statsRes] = await Promise.all([
          sessionsApi.getMyResult(Number(sessionId)),
          sessionsApi.getResults(Number(sessionId)),
          sessionsApi.getQuestionsStats(Number(sessionId)),
        ]);

        console.log('My result:', myRes.data);
        console.log('Leaderboard:', leaderRes.data);
        console.log('Questions stats:', statsRes.data);

        setMyResult(myRes.data);
        setLeaderboard(leaderRes.data);
        setQuestionsStats(statsRes.data);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };
    fetchResults();
  }, [sessionId]);

  if (loading) return <div className="flex justify-center items-center h-screen text-white">Загрузка результатов...</div>;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800 py-8 px-4">
      <div className="max-w-4xl mx-auto bg-white/90 backdrop-blur-sm rounded-lg shadow-xl p-6">
        <h1 className="text-2xl font-bold mb-6 text-gray-900">Результаты</h1>

        {myResult && (
          <Card className="p-6 mb-8 text-center bg-blue-50">
            <h2 className="text-xl font-semibold mb-2">Ваш результат</h2>
            <p className="text-3xl font-bold text-blue-600">{myResult.score} баллов</p>
            <p>Правильных ответов: {myResult.score}</p>
            <p>Место: {myResult.rank}</p>
          </Card>
        )}

        <h2 className="text-xl font-semibold mb-4">Таблица лидеров</h2>
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
                <tr key={p.id} className="border-t">
                  <td className="p-3">{idx + 1}</td>
                  <td className="p-3">{p.participant_name || 'Без имени'}</td>
                  <td className="p-3">{p.score}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>

        <h2 className="text-xl font-semibold mb-4">Статистика по вопросам</h2>
        <div className="space-y-3">
          {questionsStats.map((stat) => (
            <Card key={stat.question_id} className="p-4">
              <p className="font-medium">{stat.question_text}</p>
              <div className="w-full bg-gray-200 rounded-full h-4 mt-2">
                <div
                  className="bg-green-500 h-4 rounded-full"
                  style={{ width: `${stat.correct_percent}%` }}
                ></div>
              </div>
              <p className="text-sm text-gray-600 mt-1">
                {stat.correct_count} из {stat.total_answers} правильных ({stat.correct_percent}%)
              </p>
            </Card>
          ))}
        </div>

        <div className="mt-8 flex gap-4 justify-center">
          <Link to="/">
            <Button variant="outline">На главную</Button>
          </Link>
          <Link to="/join">
            <Button variant="primary">Играть снова</Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Results;