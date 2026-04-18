/**
 * @fileoverview Главная страница (лендинг)
 * Содержит шапку, герой-секцию, преимущества, призыв к действию и подвал.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { Button, Card } from '../components/ui';

/**
 * Компонент главной страницы
 * @returns {JSX.Element} Разметка лендинга
 */
const Home: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-md py-4 px-6 flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold text-blue-600">QuizMaster</Link>
        <div className="space-x-4">
          <Link to="/login">
            <Button variant="outline" size="sm">Войти</Button>
          </Link>
          <Link to="/register">
            <Button variant="primary" size="sm">Регистрация</Button>
          </Link>
        </div>
      </header>

      {/* Hero секция */}
      <section className="bg-gradient-to-r from-blue-500 to-purple-600 text-white py-20 px-6 text-center">
        <h1 className="text-5xl font-bold mb-4">Создавайте и проводите квизы онлайн</h1>
        <p className="text-xl mb-8">Простой способ устроить викторину для друзей, учеников или коллег</p>
        <div className="space-x-4">
          <Link to="/quizzes/create">
            <Button variant="primary" size="lg">Создать квиз</Button>
          </Link>
          <Link to="/join">
            <Button variant="outline" size="lg" className="bg-white text-blue-600 hover:bg-gray-100">Присоединиться</Button>
          </Link>
        </div>
      </section>

      {/* Преимущества */}
      <section className="py-16 px-6 bg-gray-50">
        <div className="container mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Почему выбирают QuizMaster</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="text-center">
              <div className="text-4xl mb-4">⚡</div>
              <h3 className="text-xl font-semibold mb-2">Быстро</h3>
              <p className="text-gray-600">Создайте квиз за пару минут, участники подключаются по коду</p>
            </Card>
            <Card className="text-center">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-xl font-semibold mb-2">Подробная статистика</h3>
              <p className="text-gray-600">Анализируйте результаты, узнавайте процент правильных ответов</p>
            </Card>
            <Card className="text-center">
              <div className="text-4xl mb-4">🖥️</div>
              <h3 className="text-xl font-semibold mb-2">Удобно</h3>
              <p className="text-gray-600">Работает на любом устройстве, без установки</p>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA секция */}
      <section className="bg-blue-600 text-white py-16 px-6 text-center">
        <h2 className="text-3xl font-bold mb-4">Готовы начать?</h2>
        <p className="text-xl mb-6">Создайте свой первый квиз прямо сейчас</p>
        <Link to="/quizzes/create">
          <Button variant="primary" size="lg" className="bg-white text-blue-600 hover:bg-gray-100">
            Создать квиз
          </Button>
        </Link>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 text-gray-300 py-6 text-center">
        <p>&copy; {new Date().getFullYear()} QuizMaster. Все права защищены.</p>
      </footer>
    </div>
  );
};

export default Home;