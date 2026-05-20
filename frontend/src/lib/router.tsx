import { createBrowserRouter, Navigate } from 'react-router-dom';
import { LoginPage } from '../pages/auth';
import { DashboardPage } from '../pages/dashboard';
import { ProtectedRoute } from '../components/ui/ProtectedRoute';

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
    element: (
      <ProtectedRoute>
        <DashboardPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/pesquisas',
    element: (
      <ProtectedRoute>
        <DashboardPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/biblioteca',
    element: (
      <ProtectedRoute>
        <DashboardPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/configuracoes',
    element: (
      <ProtectedRoute>
        <DashboardPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '*',
    element: <Navigate to="/projetos" replace />,
  }
]);
