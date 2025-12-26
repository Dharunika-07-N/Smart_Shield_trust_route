import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import Auth from './components/Auth';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('token'));

  useEffect(() => {
    // Check for token existence periodically or on mount
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  return (
    <Router>
      <div className="App min-h-screen bg-gray-50">
        <Routes>
          <Route
            path="/"
            element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />}
          />
          <Route
            path="/login"
            element={!isAuthenticated ? <Auth setAuth={setIsAuthenticated} /> : <Navigate to="/dashboard" replace />}
          />
          <Route
            path="/dashboard/*"
            element={isAuthenticated ? <Dashboard setAuth={setIsAuthenticated} /> : <Navigate to="/login" replace />}
          />
          {/* Catch all redirect to root */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
