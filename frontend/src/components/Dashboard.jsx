
import React, { useEffect, useState } from 'react';
import AdminDashboard from './AdminDashboard';
import ModernDashboard from './ModernDashboard';
import DriverDashboard from './DriverDashboard';
import DispatcherDashboard from './DispatcherDashboard';

const Dashboard = ({ setAuth }) => {
  const [role, setRole] = useState(localStorage.getItem('role') || 'rider');

  useEffect(() => {
    const storedRole = localStorage.getItem('role');
    if (storedRole) {
      setRole(storedRole);
    }
  }, []);

  console.log('Current Dashboard Role:', role);

  // Forcing ModernDashboard for all roles to ensure the user can see the new features
  return <ModernDashboard setAuth={setAuth} />;
};

export default Dashboard;
