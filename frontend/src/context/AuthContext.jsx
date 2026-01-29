import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('auth_token');
        const userData = localStorage.getItem('user');
        const role = localStorage.getItem('role');

        if (token && userData) {
            setUser({ username: userData, role: role });
            setIsAuthenticated(true);
        }
        setLoading(false);
    }, []);

    const login = (data) => {
        localStorage.setItem('auth_token', data.access_token || 'dev_token');
        localStorage.setItem('user', data.username || 'user');
        localStorage.setItem('role', data.role || 'rider');
        localStorage.setItem('user_id', data.user_id || 'ID_001');

        setUser({ username: data.username, role: data.role });
        setIsAuthenticated(true);
    };

    const logout = () => {
        localStorage.clear();
        setUser(null);
        setIsAuthenticated(false);
    };

    return (
        <AuthContext.Provider value={{ user, isAuthenticated, login, logout, loading }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
