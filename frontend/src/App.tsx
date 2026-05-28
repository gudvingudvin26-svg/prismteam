import { BrowserRouter, Routes, Route } from 'react-router-dom';
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
const EditQuiz = lazy(() => import('./pages/EditQuiz'));
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
      try {
        const response = await authApi.getCurrentUser();
        console.log('Restored user:', response.data);
        setUser(response.data);
      } catch (error) {
        console.error('Ошибка восстановления пользователя:', error);
        setUser(null);
      } finally {
        setTimeout(() => setIsAppLoading(false), 100);
      }
    };
    restoreUser();
  }, [setUser]);

  if (isAppLoading) {
    return <LoadingSpinner />;
  }

  return (
    <BrowserRouter>
      <Suspense fallback={<LoadingSpinner />}>
        <div className="animate-fadeIn">
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
                  <EditQuiz />
                </PrivateRoute>
              }
            />
            <Route
              path="/stats"
              element={
                <PrivateRoute>
                  <Stats />
                </PrivateRoute>
              }
            />

            <Route path="*" element={<NotFound />} />
          </Routes>
        </div>
      </Suspense>
    </BrowserRouter>
  );
}

export default App;