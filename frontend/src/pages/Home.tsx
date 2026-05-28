import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Card, Button } from '../components/ui';
import { useAppStore } from '../store/appStore';
import { authApi } from '../api';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const user = useAppStore((state) => state.user);
  const setUser = useAppStore((state) => state.setUser);
  const isAuthenticated = !!user;

  const handleLogout = async () => {
    try {
      await authApi.logout();
    } catch (e) {
      console.error('Logout error:', e);
    }
    setUser(null);
    window.location.href = '/';
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800">
      <header className="sticky top-0 z-10 bg-white/10 backdrop-blur-md py-4 px-6 flex flex-wrap justify-between items-center gap-4 border-b border-white/20">
        <Link to="/" className="text-2xl font-bold text-white drop-shadow-md whitespace-nowrap">
          Only Quizes Fans
        </Link>
        <div className="flex gap-3 flex-wrap items-center">
          {isAuthenticated && (
            <span className="text-white/80 text-sm">👋 {user?.username || user?.email}</span>
          )}
          {isAuthenticated ? (
            <>
              <Link to="/dashboard">
                <Button variant="outline" size="md">
                  📊 Панель управления
                </Button>
              </Link>
              <Button variant="danger" size="md" onClick={handleLogout}>
                🚪 Выйти
              </Button>
            </>
          ) : (
            <>
              <Link to="/login">
                <Button variant="outline" size="md">
                  Войти
                </Button>
              </Link>
              <Link to="/register">
                <Button variant="outline" size="md">
                  Регистрация
                </Button>
              </Link>
            </>
          )}
        </div>
      </header>

      <section className="flex-1 flex items-center justify-center py-20 px-6 text-center">
        <div className="max-w-4xl mx-auto text-white">
          <h1 className="text-4xl md:text-6xl font-extrabold mb-4 drop-shadow-lg">
            Создавайте и проводите <br />
            <span className="bg-gradient-to-r from-yellow-300 to-pink-400 bg-clip-text text-transparent">
              квизы онлайн
            </span>
          </h1>
          <p className="text-xl md:text-2xl mb-8 max-w-2xl mx-auto text-purple-100">
            Простой способ устроить викторину для друзей, учеников или коллег
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <Link to={isAuthenticated ? "/quizzes/create" : "/register"}>
              <Button variant="outline" size="lg">
                Создать квиз
              </Button>
            </Link>
            <Link to="/join">
              <Button variant="outline" size="lg">
                Присоединиться
              </Button>
            </Link>
          </div>
        </div>
      </section>

      <section className="py-20 px-6 bg-black/20">
        <div className="container mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center text-white mb-12">
            Почему выбирают <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 to-pink-400">Only Quizes Fans</span>
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="text-center p-6 bg-white/90 backdrop-blur-sm border border-purple-200 shadow-xl transition-transform hover:scale-105">
              <div className="text-5xl mb-4">⚡</div>
              <h3 className="text-xl font-semibold mb-2 text-purple-800">Быстро</h3>
              <p className="text-gray-700">Создайте квиз за пару минут, участники подключаются по коду</p>
            </Card>
            <Card className="text-center p-6 bg-white/90 backdrop-blur-sm border border-purple-200 shadow-xl transition-transform hover:scale-105">
              <div className="text-5xl mb-4">📊</div>
              <h3 className="text-xl font-semibold mb-2 text-purple-800">Подробная статистика</h3>
              <p className="text-gray-700">Анализируйте результаты, узнавайте процент правильных ответов</p>
            </Card>
            <Card className="text-center p-6 bg-white/90 backdrop-blur-sm border border-purple-200 shadow-xl transition-transform hover:scale-105">
              <div className="text-5xl mb-4">🎯</div>
              <h3 className="text-xl font-semibold mb-2 text-purple-800">Любые темы</h3>
              <p className="text-gray-700">Создавайте квизы на любые темы: от истории до поп-культуры</p>
            </Card>
          </div>
        </div>
      </section>

      <section className="bg-gradient-to-r from-purple-900 to-blue-900 text-white py-16 px-6 text-center rounded-t-3xl">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Готовы начать?</h2>
          <p className="text-xl mb-6 text-purple-100">Создайте свой первый квиз прямо сейчас и удивите своих друзей</p>
          <Link to={isAuthenticated ? "/quizzes/create" : "/register"}>
            <Button variant="outline" size="lg">
              {isAuthenticated ? "Создать квиз" : "Зарегистрироваться"}
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Home;