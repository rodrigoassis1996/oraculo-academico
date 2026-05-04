import { createBrowserRouter, Navigate } from 'react-router-dom';
import { LoginPage } from '../pages/auth';
import { DashboardPage } from '../pages/dashboard';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/projetos" replace />,
  },
  {
    path: '/login',
    element: <LoginPage onGoogleLogin={() => window.location.href = '/projetos'} />,
  },
  {
    path: '/projetos',
    element: <DashboardPage />,
  },
  {
    path: '/pesquisas',
    element: <DashboardPage />,
  },
  {
    path: '/biblioteca',
    element: <DashboardPage />,
  },
  {
    path: '/configuracoes',
    element: <DashboardPage />,
  },
  {
    path: '*',
    element: <Navigate to="/projetos" replace />,
  }
]);
