import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Stats from './pages/Stats';
import CreateQuiz from './components/quiz/CreateQuiz';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/quizzes" element={<Dashboard />} />
        <Route path="/quizzes/create" element={<CreateQuiz />} />
        <Route path="/stats/:sessionId" element={<Stats />} />
        <Route path="*" element={<div className="p-6 text-center">404 - Страница не найдена</div>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;