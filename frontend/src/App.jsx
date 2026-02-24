import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Auth from './components/Auth';
import LandingPage from './components/LandingPage';
import NotFound from './components/NotFound';
import Unauthorized from './components/Unauthorized';
import ErrorBoundary from './components/ErrorBoundary';
import AdminDashboard from './components/AdminDashboard';
import DispatcherDashboard from './components/DispatcherDashboard';
import DriverDashboard from './components/DriverDashboard';
import ModernDashboard from './components/ModernDashboard';
import CustomerDashboard from './components/CustomerDashboard';
import LiveTracking from './components/LiveTracking';
import { useAuth, ROLE_ROUTES } from './context/AuthContext';
import './App.css';

// ─── Loading Screen ────────────────────────────────────────────────────────────
const LoadingScreen = () => (
  <div className="h-screen w-screen flex flex-col items-center justify-center bg-[#0F172A] text-white">
    <div className="w-16 h-16 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mb-4" />
    <p className="font-black tracking-widest uppercase text-xs animate-pulse">Initializing SmartShield...</p>
  </div>
);

// ─── Protected Route (must be logged in) ──────────────────────────────────────
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) return <LoadingScreen />;
  if (!isAuthenticated) return <Navigate to="/login" state={{ from: location }} replace />;
  return children;
};

// ─── Role Guard (must have one of the allowed roles) ──────────────────────────
const RoleGuard = ({ children, allowedRoles }) => {
  const { user, isAuthenticated, loading, getDefaultRoute } = useAuth();

  if (loading) return <LoadingScreen />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;

  if (!allowedRoles.includes(user?.role)) {
    // Redirect to their own dashboard instead of a generic error
    return <Navigate to={getDefaultRoute()} replace />;
  }

  return children;
};

// ─── Smart Dashboard Redirect ─────────────────────────────────────────────────
// Sends authenticated users to their role-specific dashboard
const DashboardRedirect = () => {
  const { isAuthenticated, getDefaultRoute, loading } = useAuth();
  if (loading) return <LoadingScreen />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <Navigate to={getDefaultRoute()} replace />;
};

// ─── App ──────────────────────────────────────────────────────────────────────
function App() {
  const { isAuthenticated, login } = useAuth();

  return (
    <ErrorBoundary>
      <Router>
        <div className="App min-h-screen bg-slate-50">
          <Routes>
            {/* ── Public Routes ── */}
            <Route path="/" element={<LandingPage />} />
            <Route
              path="/login"
              element={!isAuthenticated ? <Auth setAuth={login} /> : <DashboardRedirect />}
            />
            <Route path="/unauthorized" element={<Unauthorized />} />

            {/* ── Generic /dashboard → redirect to role-specific ── */}
            <Route path="/dashboard" element={<DashboardRedirect />} />
            <Route path="/dashboard/*" element={<DashboardRedirect />} />

            {/* ── Admin / Super Admin ── */}
            <Route
              path="/admin/dashboard/*"
              element={
                <RoleGuard allowedRoles={['admin', 'super_admin']}>
                  <AdminDashboard />
                </RoleGuard>
              }
            />

            {/* ── Dispatcher ── */}
            <Route
              path="/dispatcher/dashboard/*"
              element={
                <RoleGuard allowedRoles={['dispatcher']}>
                  <DispatcherDashboard />
                </RoleGuard>
              }
            />

            {/* ── Driver ── */}
            <Route
              path="/driver/dashboard/*"
              element={
                <RoleGuard allowedRoles={['driver']}>
                  <DriverDashboard />
                </RoleGuard>
              }
            />

            {/* ── Rider ── */}
            <Route
              path="/rider/dashboard/*"
              element={
                <RoleGuard allowedRoles={['rider']}>
                  <ModernDashboard />
                </RoleGuard>
              }
            />

            {/* ── Customer ── */}
            <Route
              path="/customer/dashboard/*"
              element={
                <RoleGuard allowedRoles={['customer']}>
                  <CustomerDashboard />
                </RoleGuard>
              }
            />

            {/* ── Live Tracking Demo (all authenticated roles) ── */}
            <Route
              path="/tracking"
              element={
                <ProtectedRoute>
                  <div style={{
                    minHeight: '100vh',
                    background: '#f8fafc',
                    fontFamily: "'Inter', sans-serif",
                    padding: '0'
                  }}>
                    {/* Minimal header */}
                    <div style={{
                      background: 'white',
                      borderBottom: '1px solid #e5e7eb',
                      padding: '12px 24px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                        <div style={{
                          width: 36, height: 36,
                          background: 'linear-gradient(135deg, #4f46e5, #7c3aed)',
                          borderRadius: 10,
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          fontSize: 18
                        }}>🛡️</div>
                        <div>
                          <p style={{ margin: 0, fontWeight: 900, fontSize: 16, color: '#111827' }}>SmartShield</p>
                          <p style={{ margin: 0, fontSize: 10, color: '#6b7280', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1 }}>Live GPS Tracking</p>
                        </div>
                      </div>
                      <a href="/dashboard" style={{
                        fontSize: 12, color: '#4f46e5', fontWeight: 700,
                        textDecoration: 'none', padding: '6px 14px',
                        background: '#ede9fe', borderRadius: 8
                      }}>← Back to Dashboard</a>
                    </div>
                    {/* Live Tracking Component */}
                    <div style={{ padding: '24px' }}>
                      <LiveTracking />
                    </div>
                  </div>
                </ProtectedRoute>
              }
            />

            {/* ── Fallback ── */}
            <Route path="/404" element={<NotFound />} />
            <Route path="*" element={<Navigate to="/404" replace />} />
          </Routes>
        </div>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
