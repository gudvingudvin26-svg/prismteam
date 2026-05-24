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
    return null;
  }

  if (!token || !user) {
    return <Navigate to="/login" replace />;
  }

  return <div className="page-transition">{children}</div>;
};

export default PrivateRoute;