import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Card } from '../components/ui';
import { quizzesApi } from '../api';
import { Quiz } from '../types';
import { useAppStore } from '../store/appStore';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const user = useAppStore((state) => state.user);
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ totalQuizzes: 0, totalParticipants: 0 });
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsInitialized(true), 50);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (!isInitialized) return;

    const fetchData = async () => {
      try {
        const response = await quizzesApi.getMyQuizzes();
        const myQuizzes = response.data;
        setQuizzes(myQuizzes);
        setStats({
          totalQuizzes: myQuizzes.length,
          totalParticipants: 0,
        });
      } catch (err: unknown) {
        console.error('Ошибка загрузки квизов:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [isInitialized]);

  if (loading || !isInitialized) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800">
        <div className="text-white text-xl">Загрузка панели управления...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800 flex">
      <aside className="w-64 bg-black/20 backdrop-blur-md border-r border-white/10 p-6 hidden md:flex flex-col">
        <div className="text-white text-2xl font-bold mb-10">QuizMaster</div>
        <nav className="space-y-4 flex-grow">
          <Link to="/dashboard" className="flex items-center gap-3 text-white/80 hover:text-white transition">
            📊 Обзор
          </Link>
          <Link to="/quizzes" className="flex items-center gap-3 text-white/80 hover:text-white transition">
            📋 Квизы
          </Link>
          <Link to="/quizzes/create" className="flex items-center gap-3 text-white/80 hover:text-white transition">
            ➕ Создать
          </Link>
          <Link to="/stats" className="flex items-center gap-3 text-white/80 hover:text-white transition">
            📈 Статистика
          </Link>
        </nav>
      </aside>

      <main className="flex-1 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-3xl font-bold text-white">Панель управления</h1>
            <div className="flex items-center gap-4">
              <span className="text-white/80 text-sm">👋 {user?.username || user?.email || 'Пользователь'}</span>
              <Link to="/">
                <button className="px-4 py-2 bg-white/10 border border-white/30 text-white rounded-lg hover:bg-white/20 transition font-medium">
                  🏠 Домой
                </button>
              </Link>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <Card className="p-6 text-center bg-white/90 backdrop-blur shadow-xl border-none">
              <h3 className="text-gray-500 text-sm">Всего квизов</h3>
              <p className="text-3xl font-bold text-blue-600">{stats.totalQuizzes}</p>
            </Card>
            <Card className="p-6 text-center bg-white/90 backdrop-blur shadow-xl border-none">
              <h3 className="text-gray-500 text-sm">Всего участников</h3>
              <p className="text-3xl font-bold text-green-600">{stats.totalParticipants}</p>
            </Card>
            <Link to="/stats">
              <Card className="p-6 text-center bg-white/90 backdrop-blur shadow-xl border-none cursor-pointer hover:bg-white transition">
                <h3 className="text-gray-500 text-sm">Моя статистика</h3>
                <p className="text-3xl font-bold text-purple-600">📈</p>
              </Card>
            </Link>
          </div>

          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold text-white">Мои квизы</h2>
            <Link to="/quizzes/create">
              <button className="px-5 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition font-medium shadow-lg">
                + Создать новый квиз
              </button>
            </Link>
          </div>

          {quizzes.length === 0 ? (
            <div className="bg-white/10 p-10 rounded-xl text-center text-white/70 border border-white/20">
              У вас пока нет квизов. Нажмите «Создать новый квиз».
            </div>
          ) : (
            <div className="space-y-4">
              {quizzes.map((quiz) => (
                <div key={quiz.id} className="bg-white/90 p-4 rounded-lg shadow flex justify-between items-center">
                  <div>
                    <h3 className="font-semibold text-gray-900">{quiz.title}</h3>
                    <p className="text-xs text-gray-500">Создан: {new Date(quiz.created_at || Date.now()).toLocaleDateString()}</p>
                  </div>
                  <div className="flex gap-2">
                    <Link to={`/quizzes/${quiz.id}/edit`} className="px-3 py-1.5 bg-gray-100 rounded hover:bg-gray-200 text-sm">
                      Редактировать
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Dashboard;