/**
 * @fileoverview Личный кабинет организатора.
 * Отображает приветствие, статистику и список последних квизов.
 * Доступен только авторизованным пользователям.
 */

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

  /** Загрузка квизов и подсчёт статистики */
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await quizzesApi.getMyQuizzes();
        const myQuizzes = response.data;
        setQuizzes(myQuizzes);
        setStats({
          totalQuizzes: myQuizzes.length,
          totalParticipants: 0, // TODO: заменить на реальный эндпоинт статистики
        });
      } catch (error) {
        console.error('Ошибка загрузки квизов:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleLogout = () => {
    authApi.logout();
    setUser(null);
    navigate('/');
  };

  if (loading) {
    return <div className="flex justify-center items-center h-screen">Загрузка...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-md py-4 px-6 flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold text-blue-600">QuizMaster</Link>
        <div className="flex items-center gap-4">
          <span className="text-gray-700">Привет, {user?.first_name || user?.email}</span>
          <Button variant="outline" size="sm" onClick={handleLogout}>Выйти</Button>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-white shadow-md h-screen p-4">
          <nav className="space-y-2">
            <Link to="/dashboard" className="block px-4 py-2 rounded hover:bg-blue-50 text-blue-600">Обзор</Link>
            <Link to="/quizzes" className="block px-4 py-2 rounded hover:bg-blue-50">Квизы</Link>
            <Link to="/quizzes/create" className="block px-4 py-2 rounded hover:bg-blue-50">Создать</Link>
            <Link to="/stats" className="block px-4 py-2 rounded hover:bg-blue-50">Статистика</Link>
          </nav>
        </aside>

        {/* Main content */}
        <main className="flex-1 p-6">
          <h1 className="text-2xl font-bold mb-6">Панель управления</h1>

          {/* Карточки статистики */}
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <Card className="p-6 text-center">
              <h3 className="text-gray-500 text-sm">Всего квизов</h3>
              <p className="text-3xl font-bold text-blue-600">{stats.totalQuizzes}</p>
            </Card>
            <Card className="p-6 text-center">
              <h3 className="text-gray-500 text-sm">Всего участников</h3>
              <p className="text-3xl font-bold text-green-600">{stats.totalParticipants}</p>
            </Card>
          </div>

          {/* Список последних квизов */}
          <div className="mb-6 flex justify-between items-center">
            <h2 className="text-xl font-semibold">Последние квизы</h2>
            <Link to="/quizzes/create">
              <Button variant="primary" size="sm">Создать новый квиз</Button>
            </Link>
          </div>

          {quizzes.length === 0 ? (
            <Card className="p-8 text-center text-gray-500">
              У вас пока нет квизов. Нажмите «Создать новый квиз».
            </Card>
          ) : (
            <div className="space-y-4">
              {quizzes.slice(0, 5).map((quiz) => (
                <Card key={quiz.id} className="p-4 flex justify-between items-center">
                  <div>
                    <h3 className="font-semibold">{quiz.title}</h3>
                    <p className="text-sm text-gray-500">Создан: {new Date(quiz.created_at).toLocaleDateString()}</p>
                  </div>
                  <Link to={`/quizzes/${quiz.id}/edit`}>
                    <Button variant="outline" size="sm">Редактировать</Button>
                  </Link>
                </Card>
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default Dashboard;