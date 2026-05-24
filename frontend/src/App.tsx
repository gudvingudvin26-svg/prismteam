import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Suspense, lazy, useEffect, useState } from 'react';
import PrivateRoute from './components/PrivateRoute';
import { authApi } from './api';
import { useAppStore } from './store/appStore';

const Home = lazy(() => import('./pages/Home'));
const Login = lazy(() => import('./pages/Login'));
const Register = lazy(() => import('./pages/Register'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const JoinQuiz = lazy(() => import('./pages/JoinQuiz'));
const QuizSession = lazy(() => import('./pages/QuizSession'));
const Results = lazy(() => import('./pages/Results'));
const QuizList = lazy(() => import('./pages/organizer/QuizList'));
const CreateQuiz = lazy(() => import('./pages/organizer/CreateQuiz'));
const Stats = lazy(() => import('./pages/Stats'));
const AccessDenied = lazy(() => import('./pages/AccessDenied'));
const NotFound = lazy(() => import('./pages/NotFound'));

const LoadingSpinner = () => (
  <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800">
    <div className="text-white text-xl">Загрузка...</div>
  </div>
);

function App() {
  const setUser = useAppStore((state) => state.setUser);
  const [isAppLoading, setIsAppLoading] = useState(true);

  useEffect(() => {
    const restoreUser = async () => {
      const token = localStorage.getItem('accessToken');
      if (token) {
        try {
          const response = await authApi.getCurrentUser();
          setUser(response.data);
        } catch (error) {
          console.error('Ошибка восстановления пользователя:', error);
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
        }
      }
      setIsAppLoading(false);
    };

    restoreUser();
  }, [setUser]);

  if (isAppLoading) {
    return <LoadingSpinner />;
  }

  return (
    <BrowserRouter>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/join" element={<JoinQuiz />} />
          <Route path="/play/:sessionId" element={<QuizSession />} />
          <Route path="/results/:sessionId" element={<Results />} />
          <Route path="/access-denied" element={<AccessDenied />} />
          <Route path="/not-found" element={<NotFound />} />

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
                <CreateQuiz />
              </PrivateRoute>
            }
          />
          <Route
            path="/stats/:sessionId"
            element={
              <PrivateRoute>
                <Stats />
              </PrivateRoute>
            }
          />

          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

export default App;