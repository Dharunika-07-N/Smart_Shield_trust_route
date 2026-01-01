
import React, { useEffect, useState } from 'react';
import AdminDashboard from './AdminDashboard';
import RiderDashboard from './RiderDashboard';
import CustomerDashboard from './CustomerDashboard';

const Dashboard = ({ setAuth }) => {
  const [role, setRole] = useState(localStorage.getItem('role') || 'rider');

  useEffect(() => {
    // Sync role with local storage in case it changes
    const storedRole = localStorage.getItem('role');
    if (storedRole) {
      setRole(storedRole);
    }
  }, []);

  console.log('Current Dashboard Role:', role);

  if (role === 'admin') {
    return <AdminDashboard setAuth={setAuth} />;
  } else if (role === 'customer') {
    return <CustomerDashboard setAuth={setAuth} />;
  } else {
    // Default to Rider Dashboard for 'rider' and 'delivery_person'
    return <RiderDashboard setAuth={setAuth} />;
  }
};

export default Dashboard;
