import React, { useState, useEffect, useRef } from 'react';
import { FiBell, FiX, FiCheck, FiAlertCircle, FiPackage, FiShield } from 'react-icons/fi';
import dashboardApi from '../services/dashboardApi';

const NotificationDropdown = ({ userId }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [loading, setLoading] = useState(false);
    const dropdownRef = useRef(null);

    // Fetch notifications
    const fetchNotifications = async () => {
        setLoading(true);
        try {
            const response = await dashboardApi.getAlerts();
            if (response && response.data) {
                const alerts = response.data.alerts || [];
                setNotifications(alerts);
                setUnreadCount(alerts.filter(n => !n.read).length);
            }
        } catch (error) {
            console.error('Error fetching notifications:', error);
            // Fallback to mock data
            setNotifications([
                {
                    id: 1,
                    type: 'delivery',
                    title: 'New delivery assigned',
                    message: 'Anna Nagar → T. Nagar',
                    timestamp: new Date(Date.now() - 2 * 60000).toISOString(),
                    read: false
                },
                {
                    id: 2,
                    type: 'safety',
                    title: 'Safety alert in Velachery',
                    message: 'Score dropped to 45',
                    timestamp: new Date(Date.now() - 15 * 60000).toISOString(),
                    read: false
                },
                {
                    id: 3,
                    type: 'success',
                    title: 'Delivery completed',
                    message: '#DEL-12345',
                    timestamp: new Date(Date.now() - 60 * 60000).toISOString(),
                    read: true
                }
            ]);
            setUnreadCount(2);
        } finally {
            setLoading(false);
        }
    };

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    // Fetch notifications on mount and when opened
    useEffect(() => {
        if (isOpen) {
            fetchNotifications();
        }
    }, [isOpen]);

    // Auto-refresh every 30 seconds
    useEffect(() => {
        const interval = setInterval(fetchNotifications, 30000);
        return () => clearInterval(interval);
    }, []);

    const toggleDropdown = () => {
        setIsOpen(!isOpen);
    };

    const markAsRead = (id) => {
        setNotifications(prev =>
            prev.map(n => n.id === id ? { ...n, read: true } : n)
        );
        setUnreadCount(prev => Math.max(0, prev - 1));
    };

    const markAllAsRead = () => {
        setNotifications(prev => prev.map(n => ({ ...n, read: true })));
        setUnreadCount(0);
    };

    const getIcon = (type) => {
        switch (type) {
            case 'delivery':
                return <FiPackage className="text-blue-500" />;
            case 'safety':
                return <FiAlertCircle className="text-red-500" />;
            case 'success':
                return <FiCheck className="text-green-500" />;
            default:
                return <FiShield className="text-emerald-500" />;
        }
    };

    const formatTimeAgo = (timestamp) => {
        const now = new Date();
        const time = new Date(timestamp);
        const diffMs = now - time;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    };

    return (
        <div className="relative" ref={dropdownRef}>
            {/* Bell Icon Button */}
            <button
                onClick={toggleDropdown}
                className="relative p-2 rounded-full hover:bg-slate-100 transition-colors"
                aria-label="Notifications"
            >
                <FiBell className="w-6 h-6 text-slate-600" />
                {unreadCount > 0 && (
                    <span className="absolute top-0 right-0 w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
                        {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                )}
            </button>

            {/* Dropdown Panel */}
            {isOpen && (
                <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-2xl border border-slate-200 z-50 max-h-[500px] overflow-hidden flex flex-col">
                    {/* Header */}
                    <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between bg-slate-50">
                        <h3 className="font-bold text-slate-800 flex items-center gap-2">
                            <FiBell className="text-emerald-500" />
                            Notifications
                            {unreadCount > 0 && (
                                <span className="text-xs bg-red-500 text-white px-2 py-0.5 rounded-full">
                                    {unreadCount} unread
                                </span>
                            )}
                        </h3>
                        {unreadCount > 0 && (
                            <button
                                onClick={markAllAsRead}
                                className="text-xs text-emerald-600 hover:text-emerald-700 font-medium"
                            >
                                Mark all read
                            </button>
                        )}
                    </div>

                    {/* Notifications List */}
                    <div className="overflow-y-auto flex-1">
                        {loading ? (
                            <div className="p-8 text-center">
                                <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                                <p className="text-sm text-slate-500">Loading notifications...</p>
                            </div>
                        ) : notifications.length === 0 ? (
                            <div className="p-8 text-center">
                                <FiBell className="w-12 h-12 text-slate-300 mx-auto mb-2" />
                                <p className="text-sm text-slate-500">No notifications</p>
                            </div>
                        ) : (
                            notifications.map((notification) => (
                                <div
                                    key={notification.id}
                                    className={`px-4 py-3 border-b border-slate-100 hover:bg-slate-50 transition-colors cursor-pointer ${!notification.read ? 'bg-emerald-50/30' : ''
                                        }`}
                                    onClick={() => markAsRead(notification.id)}
                                >
                                    <div className="flex items-start gap-3">
                                        <div className="mt-1">
                                            {getIcon(notification.type)}
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-start justify-between gap-2">
                                                <h4 className="text-sm font-semibold text-slate-800 leading-tight">
                                                    {notification.title}
                                                </h4>
                                                {!notification.read && (
                                                    <div className="w-2 h-2 bg-emerald-500 rounded-full flex-shrink-0 mt-1"></div>
                                                )}
                                            </div>
                                            <p className="text-xs text-slate-600 mt-1">
                                                {notification.message}
                                            </p>
                                            <p className="text-xs text-slate-400 mt-1">
                                                {formatTimeAgo(notification.timestamp)}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>

                    {/* Footer */}
                    {notifications.length > 0 && (
                        <div className="px-4 py-2 border-t border-slate-200 bg-slate-50">
                            <button className="text-xs text-emerald-600 hover:text-emerald-700 font-medium w-full text-center">
                                View all notifications
                            </button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default NotificationDropdown;
