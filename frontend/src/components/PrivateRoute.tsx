import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAppStore } from '../store/appStore';

interface PrivateRouteProps {
  children: React.ReactNode;
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ children }) => {
  const user = useAppStore((state) => state.user);
  const token = localStorage.getItem('accessToken');
  const [isChecking, setIsChecking] = React.useState(true);

  React.useEffect(() => {
    const timer = setTimeout(() => setIsChecking(false), 50);
    return () => clearTimeout(timer);
  }, []);

  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-purple-700 to-blue-800">
        <div className="text-white text-xl animate-pulse-fast">Проверка авторизации...</div>
      </div>
    );
  }

  if (!token || !user) {
    return <Navigate to="/login" replace />;
  }

  return <div className="animate-fadeIn">{children}</div>;
};

export default PrivateRoute;