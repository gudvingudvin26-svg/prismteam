/**
 * @fileoverview Компонент для защиты маршрутов, требующих авторизации.
 * Если пользователь не авторизован, перенаправляет на страницу входа.
 */

import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAppStore } from '../store/appStore';

interface PrivateRouteProps {
  children: React.ReactNode;
}

/**
 * Компонент-обёртка для приватных маршрутов
 * @param children Дочерние элементы (страница, которую нужно защитить)
 * @returns {JSX.Element} Дочерние элементы или редирект на /login
 */
const PrivateRoute: React.FC<PrivateRouteProps> = ({ children }) => {
  const user = useAppStore((state) => state.user);
  const token = localStorage.getItem('accessToken');

  if (!token || !user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export default PrivateRoute;