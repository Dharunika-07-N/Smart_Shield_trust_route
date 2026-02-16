import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import Auth from './components/Auth';
import LandingPage from './components/LandingPage';
import NotFound from './components/NotFound';
import Unauthorized from './components/Unauthorized';
import ErrorBoundary from './components/ErrorBoundary';
import { useAuth } from './context/AuthContext';
import './App.css';

// Protected Route Wrapper
const ProtectedRoute = ({ children, requiredRole }) => {
  const { isAuthenticated, user, loading } = useAuth();
  const location = useLocation();

  if (loading) return (
    <div className="h-screen w-screen flex flex-col items-center justify-center bg-[#0F172A] text-white">
      <div className="w-16 h-16 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mb-4"></div>
      <p className="font-black tracking-widest uppercase text-xs animate-pulse">Initializing SmartShield...</p>
    </div>
  );

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requiredRole && user?.role !== requiredRole) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
};

function App() {
  const { isAuthenticated, login } = useAuth();

  return (
    <ErrorBoundary>
      <Router>
        <div className="App min-h-screen bg-slate-50">
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<LandingPage />} />
            <Route
              path="/login"
              element={!isAuthenticated ? <Auth setAuth={login} /> : <Navigate to="/dashboard" replace />}
            />
            <Route path="/unauthorized" element={<Unauthorized />} />

            {/* Protected Dashboard Routes */}
            <Route
              path="/dashboard/*"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />

            {/* Fallback */}
            <Route path="/404" element={<NotFound />} />
            <Route path="*" element={<Navigate to="/404" replace />} />
          </Routes>
        </div>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
