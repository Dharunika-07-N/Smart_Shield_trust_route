import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { useAuth } from './AuthContext';
import { createWebSocket } from '../services/websocket';
import { API_ROOT_URL } from '../utils/constants';

const NotificationContext = createContext(null);

export const NotificationProvider = ({ children }) => {
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const { isAuthenticated, user } = useAuth();
    const socketRef = useRef(null);

    useEffect(() => {
        if (isAuthenticated) {
            // Notifications WebSocket
            const endpoint = '/ws/notifications';

            socketRef.current = createWebSocket(
                endpoint,
                // onMessage
                (data) => {
                    // Message handler
                    setNotifications(prev => [data, ...prev].slice(0, 20));
                    setUnreadCount(prev => prev + 1);

                    // Show browser notification if permitted
                    if (Notification.permission === 'granted') {
                        new Notification('SmartShield Alert', {
                            body: data.message,
                            icon: '/shield-icon.png'
                        });
                    }
                },
                // onOpen
                () => {
                    console.log('[Notifications] WebSocket connected successfully');
                },
                // onClose
                () => {
                    console.log('[Notifications] WebSocket disconnected');
                },
                // onError
                (error) => {
                    console.warn('[Notifications] WebSocket error - notifications will not be real-time');
                    // App continues to work without WebSocket notifications
                }
            );

            // Request permission on mount
            if (Notification.permission === 'default') {
                Notification.requestPermission();
            }

            return () => {
                if (socketRef.current) {
                    socketRef.current.close();
                }
            };
        }
    }, [isAuthenticated]);

    const markAsRead = (id) => {
        setNotifications(prev => prev.filter(n => n.id !== id));
        setUnreadCount(prev => Math.max(0, prev - 1));
    };

    const clearAll = () => {
        setNotifications([]);
        setUnreadCount(0);
    };

    return (
        <NotificationContext.Provider value={{ notifications, unreadCount, markAsRead, clearAll }}>
            {children}
        </NotificationContext.Provider>
    );
};

export const useNotifications = () => useContext(NotificationContext);
