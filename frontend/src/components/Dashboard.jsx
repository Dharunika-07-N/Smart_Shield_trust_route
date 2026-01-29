import React, { useEffect, useState } from 'react';
import AdminDashboard from './AdminDashboard';
import ModernDashboard from './ModernDashboard';
import DriverDashboard from './DriverDashboard';
import DispatcherDashboard from './DispatcherDashboard';
import CustomerDashboard from './CustomerDashboard';
import { useAuth } from '../context/AuthContext';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [role, setRole] = useState(user?.role || localStorage.getItem('role') || 'rider');

  useEffect(() => {
    if (user?.role) {
      setRole(user.role);
    }
  }, [user]);

  const setAuthFalse = () => {
    logout();
  };

  const renderDashboard = () => {
    switch (role) {
      case 'super_admin':
      case 'admin':
        return <AdminDashboard setAuth={setAuthFalse} />;
      case 'driver':
        return <DriverDashboard setAuth={setAuthFalse} />;
      case 'dispatcher':
        return <DispatcherDashboard setAuth={setAuthFalse} />;
      case 'customer':
        return <CustomerDashboard setAuth={setAuthFalse} />;
      case 'rider':
        return <ModernDashboard setAuth={setAuthFalse} />;
      default:
        return <ModernDashboard setAuth={setAuthFalse} />;
    }
  };

  return (
    <div className="dashboard-container h-screen overflow-hidden">
      {renderDashboard()}
    </div>
  );
};

export default Dashboard;
