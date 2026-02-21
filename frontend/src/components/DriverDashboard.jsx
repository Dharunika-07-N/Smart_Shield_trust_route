import React, { useState, useEffect } from 'react';
import {
    FiShield, FiNavigation, FiUser, FiLogOut, FiBell,
    FiCheckCircle, FiChevronDown, FiChevronUp, FiTruck,
    FiMap, FiAlertTriangle, FiPhone, FiMessageSquare,
    FiClock, FiZap, FiMapPin, FiPackage, FiActivity, FiRefreshCw,
    FiBarChart2, FiSearch
} from 'react-icons/fi';
import RouteMap from './RouteMap';
import LiveNavigationHUD from './LiveNavigationHUD';
import { api } from '../services/api';
import useLocation from '../hooks/useLocation';
import { useAuth } from '../context/AuthContext';
import { useNotifications } from '../context/NotificationContext';

const DriverDashboard = () => {
    const { user, logout } = useAuth();
    const { notifications, unreadCount, markAsRead } = useNotifications();
    const [activeTab, setActiveTab] = useState('Map');
    const [panicAlerting, setPanicAlerting] = useState(false);
    const [driverId] = useState(user?.id || localStorage.getItem('user_id'));
    const { location: currentLocation } = useLocation();
    const [isOnline, setIsOnline] = useState(true);
    const [isTripExpanded, setIsTripExpanded] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [isNavigating, setIsNavigating] = useState(false);
    const [navigationSteps, setNavigationSteps] = useState([]);
    const [selectedRoute, setSelectedRoute] = useState(null);
    const [fetchingRoute, setFetchingRoute] = useState(false);
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);

    // Real Data States
    const [activeDelivery, setActiveDelivery] = useState(null);
    const [allDeliveries, setAllDeliveries] = useState([]);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({
        tasksDone: 0,
        safetyScore: 92,
        onlineHours: '6.4',
        earnings: '₹1,240'
    });

    // Fetch deliveries on mount
    useEffect(() => {
        if (user) fetchDeliveries();
    }, [user, driverId]);

    // Periodically send location updates if online and have active delivery
    useEffect(() => {
        if (!isOnline || !currentLocation) return;

        const interval = setInterval(async () => {
            try {
                // Update general tracking location
                await api.updateLocation({
                    delivery_id: activeDelivery?.id || 'idle',
                    route_id: activeDelivery?.route_id,
                    rider_id: driverId,
                    current_location: {
                        latitude: currentLocation.latitude,
                        longitude: currentLocation.longitude
                    },
                    status: activeDelivery ? activeDelivery.status : 'available'
                });
            } catch (e) {
                console.error("Location update failed", e);
            }
        }, 15000); // More frequent updates for better tracking

        return () => clearInterval(interval);
    }, [isOnline, currentLocation, activeDelivery, driverId]);

    const fetchDeliveries = async () => {
        setLoading(true);
        try {
            // Updated to use the corrected endpoint
            const data = await api.get('/deliveries');
            if (Array.isArray(data)) {
                setAllDeliveries(data);

                // Find first non-delivered delivery as active
                const active = data.find(d => ['assigned', 'pending', 'picked_up', 'in_transit'].includes(d.status));
                if (active) {
                    setActiveDelivery(active);
                } else {
                    setActiveDelivery(null);
                }

                // Update stats
                setStats(prev => ({
                    ...prev,
                    tasksDone: data.filter(d => d.status === 'delivered').length
                }));
            }
        } catch (error) {
            console.error("Error fetching deliveries:", error);
        } finally {
            setLoading(false);
        }
    };

    const handlePanicButton = async () => {
        if (!currentLocation || !driverId) return;
        if (!window.confirm('🚨 Trigger Emergency SOS alert? Help will be dispatched immediately.')) return;

        setPanicAlerting(true);
        try {
            await api.triggerPanicButton({
                rider_id: driverId,
                location: {
                    latitude: currentLocation.latitude,
                    longitude: currentLocation.longitude
                },
                delivery_id: activeDelivery?.id
            });
            alert('Emergency SOS Signal Sent. Help is on the way.');
        } catch (error) {
            alert('SOS Signal Error: ' + (error.message || 'Please use alternate contact.'));
        } finally {
            setPanicAlerting(false);
        }
    };

    const handleCheckIn = async () => {
        if (!currentLocation) return;
        try {
            await api.checkIn({
                rider_id: driverId,
                location: {
                    latitude: currentLocation.latitude,
                    longitude: currentLocation.longitude
                },
                delivery_id: activeDelivery?.id,
                is_night_shift: new Date().getHours() >= 18 || new Date().getHours() < 6
            });
            alert("Location Shared Successfully with Dispatch");
        } catch (e) {
            alert("Check-in Error: " + e.message);
        }
    };

    const updateStatus = async (newStatus) => {
        if (!activeDelivery) return;
        try {
            await api.put(`/deliveries/${activeDelivery.id}/status`, { status: newStatus });
            setActiveDelivery(prev => ({ ...prev, status: newStatus }));
            fetchDeliveries(); // Refresh list
        } catch (error) {
            alert("Status update failed: " + error.message);
        }
    };

    const handleStartNavigation = async () => {
        if (!activeDelivery || !currentLocation) return;

        const dest = activeDelivery.dropoff_location;
        if (!dest || !dest.lat || !dest.lng) {
            alert("Destination coordinates not found");
            return;
        }

        setFetchingRoute(true);
        try {
            // Update status to in_transit
            if (activeDelivery.status === 'assigned' || activeDelivery.status === 'picked_up') {
                await updateStatus('in_transit');
            }

            // Fetch optimized route from backend
            const response = await api.optimizeRoute({
                starting_point: { latitude: currentLocation.latitude, longitude: currentLocation.longitude },
                stops: [{
                    stop_id: activeDelivery.id,
                    address: dest.address,
                    coordinates: { latitude: dest.lat, longitude: dest.lng }
                }],
                optimize_for: ['safety', 'time']
            });

            if (response.success && response.data) {
                const route = response.data;
                setSelectedRoute(route);

                // Extract all instructions from segments
                const steps = [];
                route.segments?.forEach(seg => {
                    if (seg.instructions) {
                        steps.push(...seg.instructions);
                    }
                });
                setNavigationSteps(steps.length > 0 ? steps : ["Head towards destination"]);
                setIsNavigating(true);
                setIsTripExpanded(false); // Collapse trip card to show map more
            } else {
                // Fallback to Google Maps if backend fails
                window.open(`https://www.google.com/maps/dir/?api=1&destination=${dest.lat},${dest.lng}`, '_blank');
            }
        } catch (error) {
            console.error("Navigation setup failed:", error);
            // Fallback
            window.open(`https://www.google.com/maps/dir/?api=1&destination=${dest.lat},${dest.lng}`, '_blank');
        } finally {
            setFetchingRoute(false);
        }
    };

    const handleCallCustomer = () => {
        if (activeDelivery?.customer_phone) {
            window.location.href = `tel:${activeDelivery.customer_phone}`;
        } else {
            window.location.href = `tel:9876543210`; // Fallback
        }
    };

    // Components for different views
    const renderMapView = () => (
        <main className="flex-1 relative overflow-hidden flex flex-col">
            <div className="flex-1 relative">
                <RouteMap
                    variant="light-minimal"
                    showSafeZones={true}
                    route={selectedRoute}
                    markers={activeDelivery ? [
                        {
                            position: [activeDelivery.dropoff_location?.lat || 12.9716, activeDelivery.dropoff_location?.lng || 80.2452],
                            color: '#4f46e5',
                            popup: 'Destination'
                        }
                    ] : []}
                    center={isNavigating && currentLocation ? [currentLocation.latitude, currentLocation.longitude] : (activeDelivery ? [activeDelivery.dropoff_location?.lat, activeDelivery.dropoff_location?.lng] : null)}
                />

                {/* Live Navigation HUD Sidebar */}
                {isNavigating && (
                    <div className="absolute top-0 right-0 bottom-0 w-80 z-30 shadow-2xl border-l border-slate-200 bg-white flex flex-col overflow-hidden" style={{ zIndex: 40 }}>
                        <LiveNavigationHUD
                            route={selectedRoute}
                            currentLocation={currentLocation}
                            onClose={() => setIsNavigating(false)}
                            onDeliveryComplete={() => updateStatus('delivered')}
                            destination={activeDelivery?.dropoff_location}
                        />
                    </div>
                )}

                {/* Map Overlay Controls + Compact Nav Banner */}
                <div className="absolute top-4 left-4 right-4 z-10 flex flex-col gap-2" style={{ right: isNavigating ? '336px' : '16px' }}>
                    <div className="bg-white/90 backdrop-blur-md p-2 rounded-2xl border border-slate-200 shadow-lg flex items-center gap-3">
                        <div className={`w-3 h-3 rounded-full ${isOnline ? 'bg-emerald-500 animate-pulse' : 'bg-slate-400'}`}></div>
                        <span className="text-[10px] font-black uppercase tracking-widest text-slate-600">
                            {isOnline ? 'Live Tracking Active' : 'Offline'}
                        </span>
                    </div>
                    {/* Compact HUD Banner when navigating */}
                    {isNavigating && selectedRoute && (
                        <LiveNavigationHUD
                            route={selectedRoute}
                            currentLocation={currentLocation}
                            compact={true}
                        />
                    )}
                </div>

                {/* Delivery Card - Floating */}
                {activeDelivery && (
                    <div className={`absolute bottom-6 left-4 right-4 z-20 transition-all duration-500 ${isTripExpanded ? 'translate-y-0' : 'translate-y-[calc(100%-60px)]'}`}>
                        <div className="bg-white/95 backdrop-blur-xl border border-slate-200 rounded-[2.5rem] shadow-2xl p-6 overflow-hidden">
                            <div
                                className="flex items-center justify-center mb-4 cursor-pointer"
                                onClick={() => setIsTripExpanded(!isTripExpanded)}
                            >
                                <div className="w-12 h-1 bg-slate-200 rounded-full"></div>
                            </div>

                            <div className="flex items-center justify-between mb-6">
                                <div>
                                    <h2 className="text-2xl font-black text-slate-900 tracking-tight">Active Delivery</h2>
                                    <p className="text-xs text-slate-400 font-bold uppercase tracking-widest mt-1">Order {activeDelivery.order_id}</p>
                                </div>
                                <div className="flex flex-col items-end">
                                    <span className="text-2xl font-black text-indigo-600">
                                        {activeDelivery.status?.replace('_', ' ').toUpperCase()}
                                    </span>
                                    <span className="text-[10px] text-slate-400 font-black uppercase">{activeDelivery.estimated_distance || '5.2'} km away</span>
                                </div>
                            </div>

                            <div className="space-y-4 mb-8">
                                <div className="flex items-start gap-4">
                                    <div className="w-10 h-10 bg-slate-50 rounded-xl flex items-center justify-center text-slate-400 shrink-0 border border-slate-100">
                                        <FiUser />
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-[10px] text-slate-400 font-bold uppercase">Customer</p>
                                        <p className="text-sm font-bold text-slate-900 mt-0.5">{activeDelivery.customer_id || 'Suresh Kumar'}</p>
                                    </div>
                                    <div className="flex gap-2">
                                        <button onClick={handleCallCustomer} className="w-10 h-10 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center border border-blue-100"><FiPhone size={18} /></button>
                                        <button className="w-10 h-10 bg-indigo-50 text-indigo-600 rounded-xl flex items-center justify-center border border-indigo-100"><FiMessageSquare size={18} /></button>
                                    </div>
                                </div>

                                <div className="flex items-start gap-4">
                                    <div className="w-10 h-10 bg-slate-50 rounded-xl flex items-center justify-center text-indigo-600 shrink-0 border border-slate-100">
                                        <FiMapPin />
                                    </div>
                                    <div>
                                        <p className="text-[10px] text-slate-400 font-bold uppercase">Destination</p>
                                        <p className="text-sm font-bold text-slate-900 mt-0.5 leading-relaxed">{activeDelivery.dropoff_location?.address || '24, Lotus Apts, Velachery, Chennai'}</p>
                                    </div>
                                </div>

                                <div className="p-4 bg-indigo-50 border border-indigo-100 rounded-2xl flex items-center gap-3">
                                    <FiShield className="text-indigo-600 shrink-0" />
                                    <span className="text-xs font-bold text-indigo-600">Safe Route Active • Score {activeDelivery.safety_score || 85}</span>
                                    <div className="ml-auto flex gap-1">
                                        <div className="w-1 h-3 bg-indigo-500 rounded-full animate-pulse"></div>
                                        <div className="w-1 h-2 bg-indigo-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                                    </div>
                                </div>
                            </div>

                            <div className="flex gap-3">
                                {activeDelivery.status !== 'delivered' && (
                                    <>
                                        <button
                                            disabled={fetchingRoute}
                                            onClick={handleStartNavigation}
                                            className="flex-[2] py-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white rounded-2xl font-black text-sm transition-all flex items-center justify-center gap-2 shadow-lg shadow-indigo-500/20"
                                        >
                                            {fetchingRoute ? <FiRefreshCw className="animate-spin" /> : <FiNavigation />}
                                            {fetchingRoute ? 'PLANNING...' : 'START NAVIGATION'}
                                        </button>
                                        {activeDelivery.status === 'in_transit' ? (
                                            <button
                                                onClick={() => updateStatus('delivered')}
                                                className="flex-1 py-4 bg-emerald-500 hover:bg-emerald-600 text-white rounded-2xl font-black text-sm transition-all border border-emerald-400"
                                            >
                                                DELIVERED
                                            </button>
                                        ) : (
                                            <button
                                                onClick={() => updateStatus('picked_up')}
                                                className="flex-1 py-4 bg-white hover:bg-slate-50 text-slate-800 rounded-2xl font-black text-sm transition-all border border-slate-200"
                                            >
                                                PICKED UP
                                            </button>
                                        )}
                                    </>
                                )}
                            </div>
                        </div>
                    </div>
                )}

                {!activeDelivery && !loading && (
                    <div className="absolute inset-0 flex items-center justify-center bg-slate-50/50 backdrop-blur-sm z-10">
                        <div className="bg-white p-8 rounded-3xl shadow-xl border border-slate-200 text-center max-w-xs">
                            <div className="w-16 h-16 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                <FiCheckCircle size={32} />
                            </div>
                            <h3 className="text-xl font-black text-slate-900 mb-2">No Active Tasks</h3>
                            <p className="text-sm text-slate-500 font-medium">You're all caught up! Waiting for new assignments from dispatcher.</p>
                            <button onClick={fetchDeliveries} className="mt-6 w-full py-3 bg-indigo-600 text-white rounded-xl font-bold flex items-center justify-center gap-2">
                                <FiRefreshCw size={14} /> REFRESH QUEUE
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </main>
    );

    const renderTasksView = () => (
        <main className="flex-1 overflow-y-auto p-6 bg-slate-50">
            <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4 mb-6">
                <div>
                    <h2 className="text-2xl font-black text-slate-900 leading-tight">Delivery History</h2>
                    <p className="text-xs text-slate-500 font-medium">{allDeliveries.length} Total Assignments</p>
                </div>
                <div className="relative">
                    <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                        type="text"
                        placeholder="Search order ID or address..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="bg-white border border-slate-200 rounded-2xl py-2 pl-12 pr-4 text-sm focus:outline-none focus:border-indigo-500 transition-all w-full md:w-64 shadow-sm"
                    />
                </div>
            </div>
            <div className="space-y-4">
                {allDeliveries.length > 0 ? allDeliveries.filter(d =>
                    !searchTerm ||
                    d.order_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                    d.dropoff_location?.address?.toLowerCase().includes(searchTerm.toLowerCase())
                ).map((delivery) => (
                    <div key={delivery.id} className="bg-white p-5 rounded-3xl border border-slate-200 shadow-sm hover:shadow-md transition-all">
                        <div className="flex justify-between items-start mb-4">
                            <div>
                                <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest leading-none mb-1">Order {delivery.order_id}</p>
                                <h3 className="text-lg font-black text-slate-900">{delivery.dropoff_location?.address?.split(',')[0] || 'Unknown City'}</h3>
                            </div>
                            <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase ${delivery.status === 'delivered' ? 'bg-emerald-50 text-emerald-600 border border-emerald-100' :
                                delivery.status === 'in_transit' ? 'bg-indigo-50 text-indigo-600 border border-indigo-100' :
                                    'bg-amber-50 text-amber-600 border border-amber-100'
                                }`}>
                                {delivery.status?.replace('_', ' ')}
                            </span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                            <div className="flex items-center gap-2 text-slate-500 max-w-[70%]">
                                <FiMapPin size={14} className="text-indigo-600 shrink-0" />
                                <span className="truncate">{delivery.dropoff_location?.address || 'N/A'}</span>
                            </div>
                            <button
                                onClick={() => { setActiveDelivery(delivery); setActiveTab('Map'); }}
                                className="px-4 py-2 bg-indigo-50 text-indigo-600 rounded-xl font-black text-[10px] hover:bg-indigo-600 hover:text-white transition-all"
                            >
                                VIEW
                            </button>
                        </div>
                    </div>
                )) : (
                    <div className="text-center py-20 bg-white rounded-3xl border border-slate-200 border-dashed">
                        <FiPackage size={40} className="mx-auto text-slate-200 mb-4" />
                        <p className="text-slate-400 font-bold">No tasks assigned to you yet.</p>
                        <button onClick={fetchDeliveries} className="mt-4 text-indigo-600 font-black text-xs">REFRESH NOW</button>
                    </div>
                )}
            </div>
        </main>
    );

    const renderAlertsView = () => (
        <main className="flex-1 overflow-y-auto p-6 bg-slate-50">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h2 className="text-2xl font-black text-slate-900">Safety Network</h2>
                    <p className="text-xs text-slate-500 font-medium">Real-time alerts from and for drivers</p>
                </div>
                <button
                    onClick={() => {
                        const msg = window.prompt("Enter incident or hazard description:");
                        if (msg) api.post('/api/v1/feedback/alert', {
                            message: msg,
                            location: currentLocation,
                            type: 'hazard'
                        });
                    }}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest shadow-lg active:scale-95 transition-all flex items-center gap-2"
                >
                    <FiAlertTriangle size={14} /> REPORT
                </button>
            </div>
            <div className="space-y-4">
                {notifications.length > 0 ? notifications.map((n, idx) => (
                    <div key={idx} className="bg-white p-5 rounded-3xl border border-slate-200 shadow-sm border-l-4 border-l-indigo-600 animate-in fade-in slide-in-from-right duration-500">
                        <div className="flex gap-4">
                            <div className="w-10 h-10 bg-indigo-50 text-indigo-600 rounded-xl flex items-center justify-center shrink-0">
                                <FiBell />
                            </div>
                            <div className="flex-1">
                                <div className="flex justify-between items-start">
                                    <p className="text-sm font-bold text-slate-900">{n.message || 'New Safety Update'}</p>
                                    <button onClick={() => markAsRead(n.id)} className="text-slate-300 hover:text-rose-500"><FiLogOut size={12} /></button>
                                </div>
                                <p className="text-[10px] text-slate-400 mt-1 uppercase tracking-wider">{new Date(n.timestamp || Date.now()).toLocaleTimeString()} • Verified Hazard</p>
                            </div>
                        </div>
                    </div>
                )) : (
                    <div className="text-center py-20 bg-white rounded-[2.5rem] border border-slate-200 border-dashed">
                        <div className="w-16 h-16 bg-slate-50 text-slate-200 rounded-2xl flex items-center justify-center mx-auto mb-4">
                            <FiActivity size={32} />
                        </div>
                        <p className="text-slate-400 font-bold">No active safety alerts in your sector.</p>
                        <p className="text-[10px] text-slate-400 mt-1 uppercase tracking-widest">Scanning live network...</p>
                    </div>
                )}
            </div>
        </main>
    );

    return (
        <div className="flex h-screen bg-slate-50 text-slate-800 font-['Inter'] overflow-hidden flex-col md:flex-row">
            {/* Sidebar (Desktop) */}
            <aside className={`hidden md:flex w-20 lg:w-64 bg-white border-r border-slate-200 flex-col z-40 transition-all`}>
                <div className="p-6 flex items-center gap-3">
                    <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white shadow-lg shadow-indigo-500/20 shrink-0">
                        <FiShield size={24} />
                    </div>
                    <div className="hidden lg:block">
                        <h1 className="text-slate-900 font-black leading-none text-lg">SmartShield</h1>
                        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mt-1">Driver App</p>
                    </div>
                </div>

                <nav className="flex-1 px-4 py-6 space-y-2">
                    {[
                        { id: 'Map', icon: FiMap, label: 'Map Control' },
                        { id: 'Tasks', icon: FiPackage, label: 'Deliveries' },
                        { id: 'Alerts', icon: FiActivity, label: 'Safety Net', badge: unreadCount },
                        { id: 'Profile', icon: FiUser, label: 'Account' }
                    ].map(item => (
                        <button
                            key={item.id}
                            onClick={() => setActiveTab(item.id)}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-2xl transition-all font-bold text-sm ${activeTab === item.id
                                ? 'bg-indigo-600 text-white shadow-xl shadow-indigo-500/20'
                                : 'text-slate-400 hover:text-slate-800 hover:bg-slate-50'
                                }`}
                        >
                            <item.icon size={20} className="shrink-0" />
                            <span className="hidden lg:block">{item.label}</span>
                            {item.badge > 0 && (
                                <span className={`ml-auto w-5 h-5 rounded-full flex items-center justify-center text-[10px] ${activeTab === item.id ? 'bg-white text-indigo-600' : 'bg-rose-500 text-white'}`}>
                                    {item.badge}
                                </span>
                            )}
                        </button>
                    ))}
                </nav>

                <div className="p-6 mt-auto">
                    <button onClick={logout} className="w-full flex items-center gap-3 px-4 py-3 text-slate-400 hover:text-rose-500 transition-colors font-bold text-sm">
                        <FiLogOut size={20} />
                        <span className="hidden lg:block">Sign Out</span>
                    </button>
                </div>
            </aside>

            {/* Mobile Sidebar Overlay */}
            {isSidebarOpen && (
                <div
                    className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 md:hidden"
                    onClick={() => setIsSidebarOpen(false)}
                />
            )}

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col min-w-0">
                {/* Header */}
                <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 shrink-0 z-30">
                    <div className="flex items-center gap-3">
                        <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className="md:hidden p-2 -ml-2 text-slate-500">
                            <FiActivity size={20} />
                        </button>
                        <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white md:hidden">
                            <FiShield size={18} />
                        </div>
                        <div className="hidden sm:block">
                            <h1 className="text-slate-900 font-bold text-sm leading-none">Driver Center</h1>
                            <p className="text-[10px] text-indigo-600 font-bold uppercase tracking-wider mt-0.5">Fleet Node: {driverId}</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <div
                            onClick={() => setIsOnline(!isOnline)}
                            className={`cursor-pointer flex items-center gap-2 px-3 py-1 rounded-full transition-all border ${isOnline ? 'bg-emerald-50 border-emerald-100' : 'bg-slate-100 border-slate-200'}`}
                        >
                            <div className={`w-1.5 h-1.5 rounded-full ${isOnline ? 'bg-emerald-500 animate-pulse' : 'bg-slate-400'}`}></div>
                            <span className={`text-[10px] font-black uppercase tracking-widest ${isOnline ? 'text-emerald-600' : 'text-slate-500'}`}>
                                {isOnline ? 'Active' : 'Offline'}
                            </span>
                        </div>
                        <div className="text-right">
                            <p className="text-xs font-black text-slate-900 leading-none">{user?.full_name || user?.username || 'Driver'}</p>
                            <p className="text-[9px] text-slate-400 font-bold uppercase tracking-widest mt-0.5">Status: Verified</p>
                        </div>
                    </div>
                </header>

                {/* Status Bar */}
                {activeTab === 'Map' && (
                    <div className="bg-indigo-600 px-6 py-3 flex items-center justify-between z-20 shadow-lg">
                        <div className="flex gap-4">
                            <div className="text-white">
                                <p className="text-[8px] font-black uppercase tracking-widest opacity-70">Earnings</p>
                                <p className="text-sm font-black">{stats.earnings}</p>
                            </div>
                            <div className="w-px h-6 bg-white/20"></div>
                            <div className="text-white">
                                <p className="text-[8px] font-black uppercase tracking-widest opacity-70">Tasks</p>
                                <p className="text-sm font-black">{stats.tasksDone}</p>
                            </div>
                            <div className="w-px h-6 bg-white/20"></div>
                            <div className="text-white">
                                <p className="text-[8px] font-black uppercase tracking-widest opacity-70">Safety</p>
                                <p className="text-sm font-black">{stats.safetyScore}%</p>
                            </div>
                        </div>
                        <div className="flex gap-2">
                            <button
                                onClick={handlePanicButton}
                                className="bg-white/10 hover:bg-rose-500 text-white p-2 rounded-xl transition-all border border-white/20"
                                title="Emergency SOS"
                            >
                                <FiAlertTriangle size={18} />
                            </button>
                            <button
                                onClick={handleCheckIn}
                                className="bg-white text-indigo-600 px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest shadow-lg active:scale-95 transition-all"
                            >
                                CHECK IN
                            </button>
                        </div>
                    </div>
                )}

                {/* View Switcher */}
                {activeTab === 'Map' && renderMapView()}
                {activeTab === 'Tasks' && renderTasksView()}
                {activeTab === 'Alerts' && renderAlertsView()}
                {activeTab === 'Profile' && (
                    <main className="flex-1 overflow-y-auto p-6 bg-slate-50">
                        <h2 className="text-2xl font-black text-slate-900 mb-8">Your Profile</h2>
                        <div className="bg-white rounded-[2.5rem] border border-slate-200 shadow-sm overflow-hidden">
                            <div className="bg-indigo-600 h-24 relative">
                                <div className="absolute -bottom-10 left-8">
                                    <div className="w-20 h-20 bg-white rounded-3xl p-1 shadow-lg">
                                        <div className="w-full h-full bg-slate-100 rounded-2xl flex items-center justify-center text-slate-400 font-black text-2xl uppercase">
                                            {(user?.username || 'D')[0]}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="pt-14 p-8">
                                <div className="flex justify-between items-start mb-8">
                                    <div>
                                        <h3 className="text-2xl font-black text-slate-900">{user?.full_name || user?.username}</h3>
                                        <p className="text-indigo-600 font-bold uppercase text-xs tracking-widest">Verified Multi-Role Driver</p>
                                    </div>
                                    <div className="bg-emerald-50 text-emerald-600 px-3 py-1 rounded-full text-[10px] font-black border border-emerald-100 uppercase">Active</div>
                                </div>

                                <div className="space-y-6">
                                    <div className="flex items-center gap-4">
                                        <div className="w-10 h-10 bg-slate-50 rounded-xl flex items-center justify-center text-slate-400 border border-slate-100">
                                            <FiBell size={18} />
                                        </div>
                                        <div>
                                            <p className="text-[10px] text-slate-400 font-bold uppercase">Account ID</p>
                                            <p className="text-sm font-bold text-slate-900 uppercase">{user?.id}</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <div className="w-10 h-10 bg-slate-50 rounded-xl flex items-center justify-center text-slate-400 border border-slate-100">
                                            <FiUser size={18} />
                                        </div>
                                        <div>
                                            <p className="text-[10px] text-slate-400 font-bold uppercase">Role Permission</p>
                                            <p className="text-sm font-bold text-slate-900 uppercase">{user?.role}</p>
                                        </div>
                                    </div>
                                </div>

                                <button
                                    onClick={logout}
                                    className="w-full mt-10 py-4 bg-rose-50 hover:bg-rose-100 text-rose-600 rounded-2xl font-black text-sm transition-all border border-rose-100 flex items-center justify-center gap-2"
                                >
                                    <FiLogOut /> DISCONNECT SESSION
                                </button>
                            </div>
                        </div>
                    </main>
                )}

                {/* Bottom Nav (Mobile) */}
                <nav className="h-20 bg-white border-t border-slate-200 flex items-center justify-around shrink-0 pb-safe md:hidden">
                    {[
                        { id: 'Map', icon: FiMap, label: 'Map' },
                        { id: 'Tasks', icon: FiPackage, label: 'Tasks' },
                        { id: 'Alerts', icon: FiActivity, label: 'Alerts', badge: unreadCount },
                        { id: 'Profile', icon: FiUser, label: 'Profile' }
                    ].map(item => (
                        <button
                            key={item.id}
                            onClick={() => setActiveTab(item.id)}
                            className={`flex flex-col items-center gap-1 flex-1 h-full justify-center transition-all ${activeTab === item.id ? 'text-indigo-600 bg-indigo-50/50' : 'text-slate-400'}`}
                        >
                            <div className="relative">
                                <item.icon size={24} />
                                {item.badge > 0 && (
                                    <span className="absolute -top-1 -right-1 w-4 h-4 bg-rose-500 text-white text-[8px] font-black rounded-full flex items-center justify-center border-2 border-white">
                                        {item.badge}
                                    </span>
                                )}
                            </div>
                            <span className="text-[8px] font-bold uppercase tracking-widest">{item.label}</span>
                        </button>
                    ))}
                </nav>
            </div>
        </div>
    );
};

export default DriverDashboard;
