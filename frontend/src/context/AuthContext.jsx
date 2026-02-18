import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

// Maps each role to its default dashboard route
export const ROLE_ROUTES = {
    super_admin: '/admin/dashboard',
    admin: '/admin/dashboard',
    dispatcher: '/dispatcher/dashboard',
    driver: '/driver/dashboard',
    rider: '/rider/dashboard',
    customer: '/customer/dashboard',
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);

    // Restore session from localStorage on mount
    useEffect(() => {
        try {
            const token = localStorage.getItem('auth_token');
            const storedUser = localStorage.getItem('user_data');
            if (token && storedUser) {
                const parsed = JSON.parse(storedUser);
                setUser(parsed);
                setIsAuthenticated(true);
            }
        } catch (e) {
            // Corrupted storage — clear it
            localStorage.clear();
        }
        setLoading(false);
    }, []);

    const login = (data) => {
        const userData = {
            username: data.username || 'User',
            role: data.role || 'rider',
            id: data.user_id || null,
            full_name: data.full_name || data.username || 'User',
            email: data.email || null,
        };

        localStorage.setItem('auth_token', data.access_token || 'dev_token');
        localStorage.setItem('user_data', JSON.stringify(userData));
        // Legacy keys for backward compatibility with older components
        localStorage.setItem('role', userData.role);
        localStorage.setItem('user_id', userData.id || '');
        localStorage.setItem('user', userData.username);

        setUser(userData);
        setIsAuthenticated(true);
    };

    const logout = () => {
        localStorage.clear();
        setUser(null);
        setIsAuthenticated(false);
    };

    const hasRole = (...roles) => {
        return roles.includes(user?.role);
    };

    const getDefaultRoute = () => {
        return ROLE_ROUTES[user?.role] || '/rider/dashboard';
    };

    return (
        <AuthContext.Provider value={{
            user,
            isAuthenticated,
            login,
            logout,
            loading,
            hasRole,
            getDefaultRoute,
        }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
