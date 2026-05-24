import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAppStore } from '../store/appStore';

interface PrivateRouteProps {
  children: React.ReactNode;
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ children }) => {
  const user = useAppStore((state) => state.user);
  const token = localStorage.getItem('accessToken');

  if (!token || !user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export default PrivateRoute;