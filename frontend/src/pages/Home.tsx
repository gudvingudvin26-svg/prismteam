/**
 * @fileoverview Главная страница с фиолетово-синим градиентом, тремя карточками преимуществ и белыми кнопками.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { Button, Card } from '../components/ui';

const Home: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-white/10 backdrop-blur-md py-4 px-6 flex justify-between items-center border-b border-white/20">
        <Link to="/" className="text-2xl font-bold text-white drop-shadow-md">
          Only Quizes Fans
        </Link>
        <div className="space-x-4">
          <Link to="/login">
            <Button variant="outline" size="sm" className="!text-black bg-white border-white hover:bg-gray-100">
              Войти
            </Button>
          </Link>
          <Link to="/register">
            <Button variant="primary" size="sm" className="!text-black bg-white hover:bg-gray-100 shadow-lg">
              Регистрация
            </Button>
          </Link>
        </div>
      </header>

      {/* Hero секция */}
      <section className="flex-1 flex items-center justify-center py-20 px-6 text-center">
        <div className="max-w-4xl mx-auto text-white">
          <h1 className="text-5xl md:text-7xl font-extrabold mb-4 drop-shadow-lg">
            Создавайте и проводите <br />
            <span className="bg-gradient-to-r from-yellow-300 to-pink-400 bg-clip-text text-transparent">
              квизы онлайн
            </span>
          </h1>
          <p className="text-xl md:text-2xl mb-8 max-w-2xl mx-auto text-purple-100">
            Простой способ устроить викторину для друзей, учеников или коллег
          </p>
          <div className="space-x-4">
            <Link to="/quizzes/create">
              <Button variant="primary" size="lg" className="!text-black bg-white hover:bg-gray-100 shadow-lg">
                Создать квиз
              </Button>
            </Link>
            <Link to="/join">
              <Button variant="outline" size="lg" className="!text-black bg-white border-white hover:bg-gray-100">
                Присоединиться
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Преимущества — три карточки */}
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
              <p className="text-gray-700">Создавайте квизы на любые темы: от истории до поп-культуры. Вдохновляйте и обучайте!</p>
            </Card>
          </div>
          <div className="mt-8 text-center text-purple-100 text-lg">
            ✨ Тысячи вопросов, миллионы возможностей. Присоединяйтесь к сообществу создателей квизов! ✨
          </div>
        </div>
      </section>

      {/* CTA секция */}
      <section className="bg-gradient-to-r from-purple-900 to-blue-900 text-white py-16 px-6 text-center rounded-t-3xl">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Готовы начать?</h2>
          <p className="text-xl mb-6 text-purple-100">Создайте свой первый квиз прямо сейчас и удивите своих друзей</p>
          <Link to="/quizzes/create">
            <Button variant="primary" size="lg" className="!text-black bg-white hover:bg-gray-100 shadow-xl">
              Создать квиз бесплатно
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer удалён полностью */}
    </div>
  );
};

export default Home;