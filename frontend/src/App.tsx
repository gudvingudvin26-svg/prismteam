import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
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

function AppContent() {
  const location = useLocation();
  const setUser = useAppStore((state) => state.setUser);
  const user = useAppStore((state) => state.user);
  const [isAppLoading, setIsAppLoading] = useState(true);

  useEffect(() => {
    const restoreUser = async () => {
      const publicPaths = ['/', '/login', '/register', '/join', '/access-denied', '/not-found'];
      const isPublicPath = publicPaths.some(path => location.pathname === path);

      if (isPublicPath) {
        setIsAppLoading(false);
        return;
      }

      try {
        const response = await authApi.getCurrentUser();
        if (response.data && response.data.id) {
          setUser(response.data);
        } else {
          setUser(null);
        }
      } catch (error) {
        console.error('Not authenticated:', error);
        setUser(null);
      } finally {
        setTimeout(() => setIsAppLoading(false), 100);
      }
    };

    restoreUser();
  }, [location.pathname]);

  if (isAppLoading) {
    return <LoadingSpinner />;
  }

  return (
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
          <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
          <Route path="/quizzes" element={<PrivateRoute><QuizList /></PrivateRoute>} />
          <Route path="/quizzes/create" element={<PrivateRoute><CreateQuiz /></PrivateRoute>} />
          <Route path="/quizzes/:id/edit" element={<PrivateRoute><EditQuiz /></PrivateRoute>} />
          <Route path="/stats" element={<PrivateRoute><Stats /></PrivateRoute>} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
    </Suspense>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;