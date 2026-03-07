import { BrowserRouter, Routes, Route } from 'react-router-dom'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<div>Главная страница</div>} />
        <Route path="/login" element={<div>Вход</div>} />
        <Route path="/register" element={<div>Регистрация</div>} />
        <Route path="/quizzes" element={<div>Список квизов</div>} />
        <Route path="/quizzes/create" element={<div>Создание квиза</div>} />
        <Route path="/quizzes/:id/edit" element={<div>Редактирование</div>} />
        <Route path="/play/:sessionId" element={<div>Игра</div>} />
        <Route path="/results/:sessionId" element={<div>Результаты</div>} />
        <Route path="*" element={<div>404 - Не найдено</div>} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
