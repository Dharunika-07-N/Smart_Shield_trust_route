import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';
import { ROLE_ROUTES } from '../context/AuthContext';

/**
 * Dashboard.jsx — Legacy compatibility router.
 * If someone navigates to /dashboard, redirect them to their role-specific route.
 * The actual dashboard components are now mounted directly by App.jsx routes.
 */
const Dashboard = () => {
  const { user, isAuthenticated, loading } = useAuth();

  if (loading) return null;
  if (!isAuthenticated) return <Navigate to="/login" replace />;

  const route = ROLE_ROUTES[user?.role] || '/rider/dashboard';
  return <Navigate to={route} replace />;
};

export default Dashboard;
