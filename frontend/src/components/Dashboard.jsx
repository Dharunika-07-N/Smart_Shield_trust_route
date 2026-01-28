
import React, { useEffect, useState } from 'react';
import AdminDashboard from './AdminDashboard';
import RiderDashboard from './RiderDashboard';
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

  switch (role) {
    case 'admin':
    case 'super_admin':
      return <AdminDashboard setAuth={setAuth} />;
    case 'driver':
      return <DriverDashboard setAuth={setAuth} />;
    case 'dispatcher':
      return <DispatcherDashboard setAuth={setAuth} />;
    case 'rider':
      return <RiderDashboard setAuth={setAuth} />;
    default:
      return <RiderDashboard setAuth={setAuth} />;
  }
};

export default Dashboard;
