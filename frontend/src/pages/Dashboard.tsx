import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button, Card } from '../components/ui';
import { quizzesApi, authApi } from '../api';
import { Quiz } from '../types';
import { useAppStore } from '../store/appStore';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const user = useAppStore((state) => state.user);
  const setUser = useAppStore((state) => state.setUser);
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
      } catch (error) {
        console.error('Ошибка загрузки квизов:', error);
        if (error.response?.status === 401) {
          authApi.logout();
          setUser(null);
          navigate('/login');
        }
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [isInitialized, navigate, setUser]);

  const handleLogout = () => {
    authApi.logout();
    setUser(null);
    navigate('/');
  };

  if (loading || !isInitialized) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800">
        <div className="text-white text-xl">Загрузка панели управления...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800">
      <header className="bg-white/10 backdrop-blur-md shadow-md py-4 px-6 flex justify-between items-center border-b border-white/20">
        <Link to="/" className="text-2xl font-bold text-white drop-shadow-md">QuizMaster</Link>
        <div className="flex items-center gap-4">
          <span className="text-white">Привет, {user?.first_name || user?.username || user?.email}</span>
          <Button variant="outline" size="sm" onClick={handleLogout} className="!text-black bg-white hover:bg-gray-100">Выйти</Button>
        </div>
      </header>

      <div className="flex">
        <aside className="w-64 bg-white/10 backdrop-blur-md shadow-md h-screen p-4 border-r border-white/20">
          <nav className="space-y-2">
            <Link to="/dashboard" className="block px-4 py-2 rounded hover:bg-white/20 text-white">Обзор</Link>
            <Link to="/quizzes" className="block px-4 py-2 rounded hover:bg-white/20 text-white">Квизы</Link>
            <Link to="/quizzes/create" className="block px-4 py-2 rounded hover:bg-white/20 text-white">Создать</Link>
            <Link to="/join" className="block px-4 py-2 rounded hover:bg-white/20 text-white">Присоединиться</Link>
          </nav>
        </aside>

        <main className="flex-1 p-6">
          <div className="bg-white/90 backdrop-blur-sm rounded-lg shadow-xl p-6">
            <h1 className="text-2xl font-bold mb-6 text-gray-900">Панель управления</h1>

            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <Card className="p-6 text-center bg-white shadow-md">
                <h3 className="text-gray-500 text-sm">Всего квизов</h3>
                <p className="text-3xl font-bold text-blue-600">{stats.totalQuizzes}</p>
              </Card>
              <Card className="p-6 text-center bg-white shadow-md">
                <h3 className="text-gray-500 text-sm">Всего участников</h3>
                <p className="text-3xl font-bold text-green-600">{stats.totalParticipants}</p>
              </Card>
            </div>

            <div className="mb-6 flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Последние квизы</h2>
              <Link to="/quizzes/create">
                <Button variant="primary" size="sm">Создать новый квиз</Button>
              </Link>
            </div>

            {quizzes.length === 0 ? (
              <Card className="p-8 text-center text-gray-500 bg-white shadow-md">
                У вас пока нет квизов. Нажмите «Создать новый квиз».
              </Card>
            ) : (
              <div className="space-y-4">
                {quizzes.slice(0, 5).map((quiz) => (
                  <Card key={quiz.id} className="p-4 flex justify-between items-center bg-white shadow-md">
                    <div>
                      <h3 className="font-semibold text-gray-900">{quiz.title}</h3>
                      <p className="text-sm text-gray-500">Создан: {new Date(quiz.created_at || Date.now()).toLocaleDateString()}</p>
                    </div>
                    <Link to={`/quizzes/${quiz.id}/edit`}>
                      <Button variant="outline" size="sm">Редактировать</Button>
                    </Link>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;