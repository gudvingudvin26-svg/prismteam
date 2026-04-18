import { BrowserRouter, Routes, Route } from 'react-router-dom';
import PrivateRoute from './components/PrivateRoute';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import JoinQuiz from './pages/JoinQuiz';
import QuizSession from './pages/QuizSession';
import Results from './pages/Results';
import QuizList from './pages/organizer/QuizList';
import CreateQuiz from './pages/organizer/CreateQuiz';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/join" element={<JoinQuiz />} />
        <Route path="/play/:sessionId" element={<QuizSession />} />
        <Route path="/results/:sessionId" element={<Results />} />

        {/* Приватные маршруты для организатора */}
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          }
        />
        <Route
          path="/quizzes"
          element={
            <PrivateRoute>
              <QuizList />
            </PrivateRoute>
          }
        />
        <Route
          path="/quizzes/create"
          element={
            <PrivateRoute>
              <CreateQuiz />
            </PrivateRoute>
          }
        />
        <Route
          path="/quizzes/:id/edit"
          element={
            <PrivateRoute>
              <div>Редактирование квиза (в разработке)</div>
            </PrivateRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;