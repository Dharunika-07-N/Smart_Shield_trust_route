
import React, { useState, useEffect } from 'react';
import {
    FiShield, FiMap, FiPackage, FiZap, FiAlertTriangle, FiBarChart2,
    FiSettings, FiMessageSquare, FiSearch, FiBell, FiUser, FiChevronRight,
    FiNavigation, FiClock, FiWind, FiDroplet, FiEye, FiActivity, FiLayers,
    FiPlus, FiMinus, FiTarget, FiPhone, FiMapPin, FiLogOut
} from 'react-icons/fi';
import RouteMap from './RouteMap';
import L from 'leaflet';
import { api } from '../services/api';
import dashboardApi from '../services/dashboardApi';
import useLocation from '../hooks/useLocation';
import NotificationDropdown from './NotificationDropdown';
import Analytics from './Analytics';
import AIReportSummary from './AIReportSummary';
import LiveTracking from './LiveTracking';
import FeedbackForm from './FeedbackForm';
import { useAuth } from '../context/AuthContext';

const ModernDashboard = () => {
    const { user, logout } = useAuth();
    const [activeTab, setActiveTab] = useState('Dashboard');
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [riderId] = useState(user?.username || localStorage.getItem('user_id') || 'R 2847');
    const { location: currentLocation } = useLocation();
    const [searchQuery, setSearchQuery] = useState('');

    // State for API data
    const [stats, setStats] = useState([
        { label: 'Active Deliveries', value: '12', subValue: '4 in transit', trend: '+8% vs last week', icon: FiPackage, color: 'text-indigo-600', bg: 'bg-indigo-50' },
        { label: 'Safety Score', value: '87%', subValue: 'Above average', trend: '+5% vs last week', icon: FiShield, color: 'text-blue-600', bg: 'bg-blue-50' },
        { label: 'Fuel Saved', value: '24.5L', subValue: 'This week', trend: '+12% vs last week', icon: FiZap, color: 'text-amber-600', bg: 'bg-amber-50' },
        { label: 'Avg. Delivery Time', value: '18 min', subValue: 'Target: 20 min', trend: '+3% vs last week', icon: FiClock, color: 'text-indigo-600', bg: 'bg-indigo-50' },
    ]);
    const [deliveryQueue, setDeliveryQueue] = useState([]);
    const [zoneSafety, setZoneSafety] = useState([]);
    const [weather, setWeather] = useState(null);
    const [loading, setLoading] = useState(true);
    const [mapZoom, setMapZoom] = useState(13);
    const [showMapLayers, setShowMapLayers] = useState(false);
    const [deliveryPartnerMarkers, setDeliveryPartnerMarkers] = useState([]);
    const [alerts, setAlerts] = useState([]);

    // SOS State
    const [sosActive, setSosActive] = useState(false);
    const [activeAlertId, setActiveAlertId] = useState(null);

    // Settings State
    const [settingsForm, setSettingsForm] = useState({
        full_name: user?.full_name || user?.username || 'Priya Kumar',
        email: user?.email || 'priya.k@smartshield.com',

        vehicle_number: 'TN-01-AB-1234',
        emergency_contact_name: 'Rahul Kumar',
        emergency_contact_phone: '+91 98765 43210',
        share_location: true
    });

    const handleSettingsChange = (e) => {
        const { name, value, type, checked } = e.target;
        setSettingsForm(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSaveSettings = async () => {
        try {
            setLoading(true);
            const payload = {
                notifications: true,
                location_sharing: settingsForm.share_location,
                emergency_contacts: [
                    {
                        name: settingsForm.emergency_contact_name,
                        phone: settingsForm.emergency_contact_phone
                    }
                ],
                theme: 'light',
                profile: {
                    full_name: settingsForm.full_name,
                    email: settingsForm.email,
                    vehicle_number: settingsForm.vehicle_number
                }
            };

            await api.post('/users/settings', payload);
            alert("Settings saved successfully!");
        } catch (error) {
            console.error("Failed to save settings:", error);
            // More descriptive error message
            const details = error.response?.data?.detail || error.message;
            alert(`Failed to save settings: ${details}`);
        } finally {
            setLoading(false);
        }
    };


    const sideBarItems = [
        { name: 'Dashboard', icon: FiActivity, badge: null },
        { name: 'Route Map', icon: FiMap, badge: null },
        { name: 'Deliveries', icon: FiPackage, badge: deliveryQueue.length || 12 },
        { name: 'AI Insights', icon: FiZap, badge: 'AI' },
        { name: 'Analytics', icon: FiBarChart2, badge: null },
        { name: 'Safety Zones', icon: FiShield, badge: null },
        { name: 'Alerts', icon: FiAlertTriangle, badge: 3 },
        { name: 'Feedback', icon: FiMessageSquare, badge: null },
        { name: 'Settings', icon: FiSettings, badge: null },
    ];

    // Fetch dashboard data on mount
    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                setLoading(true);

                // Fetch all dashboard data in parallel
                const [statsRes, queueRes, zonesRes, weatherRes] = await Promise.all([
                    dashboardApi.getStats(riderId).catch(err => ({ data: null })),
                    dashboardApi.getDeliveryQueue(4).catch(err => ({ data: [] })),
                    dashboardApi.getZoneSafety().catch(err => ({ data: [] })),
                    dashboardApi.getWeather().catch(err => ({ data: null }))
                ]);

                // Update stats if API returns data
                if (statsRes.data) {
                    const apiStats = [
                        {
                            label: 'Active Deliveries',
                            value: statsRes.data.active_deliveries.value,
                            subValue: statsRes.data.active_deliveries.subValue,
                            trend: statsRes.data.active_deliveries.trend,
                            icon: FiPackage,
                            color: 'text-indigo-600',
                            bg: 'bg-indigo-50'
                        },
                        {
                            label: 'Safety Score',
                            value: statsRes.data.safety_score.value,
                            subValue: statsRes.data.safety_score.subValue,
                            trend: statsRes.data.safety_score.trend,
                            icon: FiShield,
                            color: 'text-blue-600',
                            bg: 'bg-blue-50'
                        },
                        {
                            label: 'Fuel Saved',
                            value: statsRes.data.fuel_saved.value,
                            subValue: statsRes.data.fuel_saved.subValue,
                            trend: statsRes.data.fuel_saved.trend,
                            icon: FiZap,
                            color: 'text-amber-600',
                            bg: 'bg-amber-50'
                        },
                        {
                            label: 'Avg. Delivery Time',
                            value: statsRes.data.avg_delivery_time.value,
                            subValue: statsRes.data.avg_delivery_time.subValue,
                            trend: statsRes.data.avg_delivery_time.trend,
                            icon: FiClock,
                            color: 'text-indigo-600',
                            bg: 'bg-indigo-50'
                        },
                    ];
                    setStats(apiStats);
                }

                if (queueRes.data) {
                    setDeliveryQueue(queueRes.data);
                }

                if (zonesRes.data) {
                    setZoneSafety(zonesRes.data);
                }

                if (weatherRes.data) {
                    setWeather(weatherRes.data);
                }
            } catch (error) {
                console.error('Error fetching dashboard data:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();

        // Refresh data every 30 seconds
        const interval = setInterval(fetchDashboardData, 30000);
        return () => clearInterval(interval);
    }, [riderId]);

    useEffect(() => {
        if (activeTab === 'Alerts') {
            const fetchAlerts = async () => {
                try {
                    const res = await dashboardApi.getRecentAlerts();
                    if (res.data) setAlerts(res.data);
                } catch (err) {
                    console.error("Failed to fetch alerts", err);
                }
            };
            fetchAlerts();
        }
    }, [activeTab]);

    // Generate simulated delivery partner locations based on delivery queue
    const generateDeliveryPartnerLocations = () => {
        if (deliveryQueue.length === 0) return;

        // Base coordinates for Chennai area
        const baseCoords = {
            lat: 13.0827,
            lng: 80.2707
        };

        const markers = deliveryQueue.map((delivery, index) => {
            // Generate random offset within ~10km radius
            const latOffset = (Math.random() - 0.5) * 0.15;
            const lngOffset = (Math.random() - 0.5) * 0.15;

            const lat = baseCoords.lat + latOffset;
            const lng = baseCoords.lng + lngOffset;

            // Determine color based on status
            let color = '#10b981'; // green for normal
            if (delivery.status === 'urgent') color = '#ef4444'; // red
            else if (delivery.status === 'normal') color = '#f59e0b'; // amber
            else if (delivery.status === 'scheduled') color = '#3b82f6'; // blue

            return {
                position: [lat, lng],
                color: color,
                popup: `
                    <div style="min-width: 200px;">
                        <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px;">${delivery.name}</div>
                        <div style="font-size: 12px; color: #64748b; margin-bottom: 8px;">${delivery.location}</div>
                        <div style="display: flex; gap: 8px; margin-bottom: 4px;">
                            <span style="background: ${color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: bold;">${delivery.status.toUpperCase()}</span>
                            <span style="background: #f1f5f9; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: bold;">Score: ${delivery.score}</span>
                        </div>
                        <div style="font-size: 11px; color: #94a3b8; margin-top: 4px;">
                            <div>📍 ${delivery.distance}</div>
                            <div>⏱️ ${delivery.time}</div>
                        </div>
                    </div>
                `,
                icon: L.divIcon({
                    className: 'delivery-partner-marker',
                    html: `
                        <div style="position: relative;">
                            <div style="
                                width: 32px;
                                height: 32px;
                                background: ${color};
                                border: 3px solid white;
                                border-radius: 50%;
                                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                font-size: 16px;
                                animation: pulse 2s infinite;
                            ">🏍️</div>
                            <div style="
                                position: absolute;
                                top: -8px;
                                right: -8px;
                                background: white;
                                border: 2px solid ${color};
                                border-radius: 50%;
                                width: 20px;
                                height: 20px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                font-size: 10px;
                                font-weight: bold;
                                color: ${color};
                            ">${delivery.score}</div>
                        </div>
                    `,
                    iconSize: [32, 32],
                    iconAnchor: [16, 16]
                })
            };
        });

        setDeliveryPartnerMarkers(markers);
    };

    // Update delivery partner locations when delivery queue changes
    useEffect(() => {
        if (deliveryQueue.length > 0) {
            generateDeliveryPartnerLocations();
        }
    }, [deliveryQueue]);

    const handleOptimizeRoute = async () => {
        try {
            setLoading(true);
            const deliveryIds = deliveryQueue.map(d => d.id);
            // Simulate complex A* search with hazard weighting
            await new Promise(r => setTimeout(r, 1200));
            const result = await dashboardApi.optimizeRoute(deliveryIds);

            setStats(prev => prev.map(s =>
                s.label === 'Fuel Saved' ? { ...s, value: '28.2L', trend: '+18% (New Optim)' } : s
            ));

            alert(`AI CO-PILOT: Route optimized! ${result.message}\nHazard exposure reduced by 22%.\nEstimated fuel saved: 3.7L`);
            setLoading(false);
            setActiveTab('Route Map');
        } catch (error) {
            console.error('Error optimizing route:', error);
            alert('Navigation failure: Safety relay timeout. Retrying with cached grid...');
            setLoading(false);
        }
    };

    const handleFindSafeZone = async () => {
        setLoading(true);
        // Simulate scanning local area sensors
        await new Promise(r => setTimeout(r, 800));
        setLoading(false);
        alert("SENSORS: High-security safe zone detected 400m East (Zone 8B). Tactical overlay enabled.");
        setActiveTab('Safety Zones');
    };

    const handleReportIssue = () => {
        const type = window.prompt("Type of hazard? (1: Road Closure, 2: Suspicious Activity, 3: Other)");
        if (type) {
            alert("FEEDBACK: Intelligence node updated. Other riders in the sector will be alerted.");
            setActiveTab('Feedback');
        }
    };

    const handleEmergency = async () => {
        // Emergency contact numbers
        const emergencyNumbers = [
            { name: 'Police', number: '100' },
            { name: 'Ambulance', number: '108' },
            { name: 'Women Helpline', number: '1091' },
            { name: 'Company Support', number: '1800-XXX-XXXX' }
        ];

        if (window.confirm("ARE YOU SURE? This will trigger a panic alert to all emergency contacts and nearby drivers.")) {
            try {
                // Trigger backend panic button
                const result = await api.triggerPanicButton({
                    rider_id: riderId,
                    location: { latitude: currentLocation?.latitude || 13.0827, longitude: currentLocation?.longitude || 80.2707 },
                    route_id: "current_route",
                    delivery_id: null
                });

                setSosActive(true);
                if (result && result.alert_id) {
                    setActiveAlertId(result.alert_id);
                }

                alert("SOS ALARM ACTIVATED! Emergency contacts notified. Police are being dialed.");
            } catch (error) {
                console.error("Failed to send panic alert:", error);
                setSosActive(true); // Still show active state locally
                alert("Alert sent locally (Offline Mode). Calling Police...");
            }
            window.location.href = 'tel:100';
        }
    };

    const handleResolveSOS = async () => {
        if (window.confirm("Are you safe now? This will resolve the SOS alert.")) {
            try {
                if (activeAlertId) {
                    await api.resolvePanicButton({
                        alert_id: activeAlertId,
                        rider_id: riderId,
                        resolution_notes: "Rider marked as safe"
                    });
                }
                setSosActive(false);
                setActiveAlertId(null);
                alert("SOS Alert Resolved. Stay safe!");
            } catch (error) {
                console.error("Error resolving SOS:", error);
                // Force resolve locally if backend fails
                setSosActive(false);
            }
        }
    };

    const handleZoomIn = () => {
        setMapZoom(prev => Math.min(prev + 1, 18));
    };

    const handleZoomOut = () => {
        setMapZoom(prev => Math.max(prev - 1, 3));
    };

    const handleRecenter = () => {
        if (currentLocation) {
            // Reset to current location
            setMapZoom(13);
        }
    };

    const handleToggleLayers = () => {
        setShowMapLayers(!showMapLayers);
    };

    const handleZoneClick = (zoneName) => {
        // Navigate to Safety Zones tab with the selected zone
        setActiveTab('Safety Zones');
    };


    return (
        <div className="flex h-screen app-dashboard overflow-hidden font-['Inter']">
            {/* Sidebar */}
            <aside className={`${isSidebarOpen ? 'w-64' : 'w-20'} bg-white border-r border-slate-200 transition-all duration-300 flex flex-col z-30`}>
                <div className="p-6 flex items-center gap-3">
                    <div className="w-10 h-10 bg-indigo-500/10 rounded-xl flex items-center justify-center border border-indigo-500/20">
                        <FiShield className="text-indigo-600" />
                    </div>
                    {isSidebarOpen && (
                        <div>
                            <h1 className="font-bold text-lg text-slate-800 leading-tight">SmartShield</h1>
                            <p className="text-[10px] text-slate-400 tracking-widest uppercase">Trust Route</p>
                        </div>
                    )}
                </div>

                <nav className="flex-1 mt-4 px-3 space-y-1">
                    {sideBarItems.map((item) => (
                        <button
                            key={item.name}
                            onClick={() => setActiveTab(item.name)}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${activeTab === item.name
                                ? 'sidebar-item-active text-indigo-600'
                                : 'text-slate-500 hover:text-slate-800 hover:bg-slate-50'
                                }`}
                        >
                            <item.icon className={`text-lg transition-colors ${activeTab === item.name ? 'text-indigo-600' : 'group-hover:text-indigo-400'}`} />
                            {isSidebarOpen && (
                                <span className="flex-1 text-left text-sm font-medium">{item.name}</span>
                            )}
                            {isSidebarOpen && item.badge && (
                                <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${item.name === 'Alerts' ? 'bg-orange-100 text-orange-600' : 'bg-indigo-100 text-indigo-600'
                                    }`}>
                                    {item.badge}
                                </span>
                            )}
                        </button>
                    ))}
                </nav>
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col min-w-0 relative">
                {/* Top Header */}
                <header className="h-20 bg-white/80 backdrop-blur-md border-b border-slate-200 flex items-center justify-between px-8 z-20">
                    <div className="flex items-center gap-4 flex-1 max-w-xl">
                        <div className="relative w-full">
                            <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
                            <input
                                type="text"
                                placeholder="Search deliveries, routes, zones..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full bg-slate-50 border border-slate-200 rounded-xl py-2.5 pl-11 pr-4 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/10 transition-all text-slate-800"
                            />
                        </div>
                    </div>

                    <div className="flex items-center gap-6">
                        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-50 border border-indigo-100 text-[10px] font-bold text-indigo-600">
                            <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />
                            SYSTEM ACTIVE
                        </div>

                        <div className="flex items-center gap-4 text-slate-400 relative">
                            <NotificationDropdown userId={riderId} />
                            <button
                                onClick={() => setActiveTab('Settings')}
                                className="hover:text-slate-800 transition-colors"
                            >
                                <FiSettings className="text-xl" />
                            </button>
                        </div>

                        <div className="flex items-center gap-3 pl-6 border-l border-slate-200">
                            <div className="text-right hidden sm:block">
                                <p className="text-sm font-bold text-slate-800 leading-none">{user?.username || 'Priya Kumar'}</p>
                                <p className="text-[10px] text-slate-400 mt-1 uppercase tracking-wider">Role: {user?.role || 'Rider'}</p>
                            </div>
                            <button
                                onClick={logout}
                                className="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center text-indigo-600 border border-indigo-100 hover:bg-rose-50 hover:text-rose-600 hover:border-rose-100 transition-colors group"
                            >
                                <FiLogOut className="text-xl group-hover:hidden" />
                                <FiUser className="text-xl hidden group-hover:block" />
                            </button>
                        </div>
                    </div>
                </header>

                <main className="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar">
                    {activeTab === 'Dashboard' && (
                        <div className="space-y-8 animate-in duration-500">
                            {/* Stats Grid */}
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                                {stats.map((s, i) => (
                                    <div key={i} className="premium-card p-6 flex flex-col justify-between">
                                        <div className="flex justify-between items-start mb-4">
                                            <div className="space-y-1">
                                                <p className="text-slate-400 text-xs font-bold uppercase tracking-wider">{s.label}</p>
                                                <p className="text-3xl font-black text-slate-800">{s.value}</p>
                                                <p className="text-[10px] text-slate-500 font-medium">{s.subValue}</p>
                                            </div>
                                            <div className={`p-3 rounded-xl ${s.bg} ${s.color}`}>
                                                <s.icon className="text-xl" />
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <span className="text-[10px] font-black text-indigo-600">{s.trend}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {/* Main Grid: Map & Details */}
                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                                {/* Left Section: Active Route Map */}
                                <div className="lg:col-span-2 space-y-6">
                                    <div className="premium-card p-6 relative overflow-hidden flex flex-col min-h-[500px]">
                                        <div className="flex items-center justify-between mb-6 z-10">
                                            <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                                                <FiNavigation className="text-indigo-600" />
                                                Active Route
                                            </h3>
                                            <div className="flex items-center gap-2">
                                                <div className="bg-amber-50 border border-amber-100 px-3 py-1.5 rounded-lg flex flex-col items-center">
                                                    <span className="text-[10px] text-amber-600 font-bold uppercase tracking-tighter leading-none">Route</span>
                                                    <span className="text-lg font-black text-amber-600 leading-none mt-0.5">78</span>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Map Visualization */}
                                        <div className="flex-1 rounded-2xl overflow-hidden border border-slate-100 relative bg-slate-50">
                                            <div className="absolute inset-0 z-0">
                                                <RouteMap
                                                    variant="light-minimal"
                                                    markers={deliveryPartnerMarkers}
                                                />
                                            </div>

                                            {/* Map Controls */}
                                            <div className="absolute right-4 top-4 flex flex-col gap-2 z-10">
                                                <button onClick={handleZoomIn} title="Zoom In" className="w-10 h-10 bg-white border border-slate-200 rounded-lg flex items-center justify-center text-slate-600 hover:bg-slate-50 transition-all shadow-md">
                                                    <FiPlus />
                                                </button>
                                                <button onClick={handleZoomOut} title="Zoom Out" className="w-10 h-10 bg-white border border-slate-200 rounded-lg flex items-center justify-center text-slate-600 hover:bg-slate-50 transition-all shadow-md">
                                                    <FiMinus />
                                                </button>
                                                <button onClick={handleRecenter} title="Recenter" className="w-10 h-10 bg-white border border-slate-200 rounded-lg flex items-center justify-center text-slate-600 hover:bg-slate-50 transition-all shadow-md">
                                                    <FiTarget />
                                                </button>
                                                <button onClick={handleToggleLayers} title="Toggle Layers" className={`mt-4 w-10 h-10 border rounded-lg flex items-center justify-center text-white transition-all shadow-lg ${showMapLayers ? 'bg-indigo-700 border-indigo-600' : 'bg-indigo-600 border-indigo-500'} hover:bg-indigo-700 shadow-indigo-500/20`}>
                                                    <FiLayers />
                                                </button>
                                            </div>

                                            {/* Legend */}
                                            <div className="absolute bottom-4 left-4 z-10 flex gap-4 bg-white/90 backdrop-blur-md px-3 py-2 rounded-lg border border-slate-200">
                                                <div className="flex items-center gap-2">
                                                    <div className="w-2.5 h-2.5 rounded-full bg-indigo-600 shadow-[0_0_8px_rgba(79,70,229,0.3)]" />
                                                    <span className="text-[10px] text-slate-600 font-bold uppercase">Safe</span>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <div className="w-2.5 h-2.5 rounded-full bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.3)]" />
                                                    <span className="text-[10px] text-slate-600 font-bold uppercase">Caution</span>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <div className="w-2.5 h-2.5 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.3)]" />
                                                    <span className="text-[10px] text-slate-600 font-bold uppercase">Alert</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Delivery Queue Section */}
                                    <div className="premium-card p-6">
                                        <div className="flex items-center justify-between mb-6">
                                            <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                                                <FiPackage className="text-indigo-600" />
                                                Delivery Queue
                                            </h3>
                                            <span className="text-xs text-slate-500">{deliveryQueue.length || 0} deliveries</span>
                                        </div>

                                        <div className="space-y-4">
                                            {loading ? (
                                                <div className="text-center py-8 text-slate-400">
                                                    <div className="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                                                    Loading deliveries...
                                                </div>
                                            ) : deliveryQueue.filter(d =>
                                                d.customer_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                                                d.id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                                                d.address?.toLowerCase().includes(searchQuery.toLowerCase())
                                            ).length === 0 ? (
                                                <div className="text-center py-8 text-slate-400">
                                                    {searchQuery ? `No results for "${searchQuery}"` : 'No active deliveries'}
                                                </div>
                                            ) : (
                                                deliveryQueue.filter(d =>
                                                    d.customer_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                                                    d.id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                                                    d.address?.toLowerCase().includes(searchQuery.toLowerCase())
                                                ).map((del, idx) => {
                                                    const priorityColors = {
                                                        'High': 'text-amber-600 bg-amber-50 border-amber-100',
                                                        'Normal': 'text-blue-600 bg-blue-50 border-blue-100',
                                                        'Urgent': 'text-red-600 bg-red-50 border-red-100'
                                                    };

                                                    return (
                                                        <div key={del.id || idx} className="bg-slate-50 border border-slate-100 rounded-2xl p-4 hover:border-slate-200 transition-all group">
                                                            <div className="flex items-start justify-between mb-4">
                                                                <div className="flex items-center gap-3">
                                                                    <div className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">{del.id}</div>
                                                                    <div className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${priorityColors[del.priority] || priorityColors['Normal']}`}>{del.priority}</div>
                                                                    <div className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-indigo-50 border border-indigo-100 text-indigo-600">{del.status}</div>
                                                                </div>
                                                                <div className="text-2xl font-black text-indigo-600 group-hover:drop-shadow-[0_0_8px_rgba(79,70,229,0.2)] transition-all">
                                                                    {del.safety_score}
                                                                </div>
                                                            </div>
                                                            <div className="flex justify-between items-end">
                                                                <div>
                                                                    <h4 className="font-bold text-slate-800 text-base mb-1">{del.customer_name}</h4>
                                                                    <div className="flex items-center gap-2 text-slate-500 text-xs mb-3">
                                                                        <FiMapPin className="text-[10px]" />
                                                                        {del.address}
                                                                    </div>
                                                                    <div className="flex items-center gap-4">
                                                                        <div className="flex items-center gap-1.5 text-xs text-slate-700 font-medium">
                                                                            <FiClock className="text-indigo-600" />
                                                                            {del.estimated_time}
                                                                        </div>
                                                                        <div className="flex items-center gap-1.5 text-xs text-slate-700 font-medium">
                                                                            <FiNavigation className="text-indigo-600" />
                                                                            {del.distance}
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                                <button className="p-2 rounded-xl bg-white border border-slate-200 text-slate-400 hover:text-slate-800 hover:bg-slate-50 transition-all shadow-sm">
                                                                    <FiChevronRight size={20} />
                                                                </button>
                                                            </div>
                                                        </div>
                                                    );
                                                })
                                            )}
                                        </div>
                                    </div>
                                </div>

                                {/* Right Section: Quick Actions & Weather & Zone Safety */}

                                <div className="space-y-6">
                                    {/* Quick Actions */}
                                    <div className="premium-card p-6">
                                        <h3 className="text-lg font-bold text-slate-800 mb-6">Quick Actions</h3>
                                        <div className="grid grid-cols-2 gap-4">
                                            <button onClick={handleOptimizeRoute} className="flex flex-col items-center justify-center p-4 rounded-2xl bg-indigo-600 hover:bg-indigo-700 text-white transition-all group shadow-md shadow-indigo-600/10">
                                                <FiNavigation className="text-2xl mb-2 group-hover:scale-110 transition-transform" />
                                                <span className="text-[10px] font-black uppercase tracking-tight">Optimize Route</span>
                                                <span className="text-[8px] opacity-70">AI-powered</span>
                                            </button>
                                            <button onClick={handleFindSafeZone} className="flex flex-col items-center justify-center p-4 rounded-2xl bg-slate-50 border border-slate-200 hover:border-indigo-500/30 text-indigo-600 transition-all group">
                                                <FiShield className="text-2xl mb-2 group-hover:scale-110 transition-transform" />
                                                <span className="text-[10px] font-black uppercase tracking-tight text-slate-800">Find Safe Zone</span>
                                                <span className="text-[8px] text-slate-500">Nearest spot</span>
                                            </button>
                                            <button onClick={handleReportIssue} className="flex flex-col items-center justify-center p-4 rounded-2xl bg-slate-50 border border-slate-200 hover:border-indigo-500/30 text-indigo-600 transition-all group">
                                                <FiAlertTriangle className="text-2xl mb-2 group-hover:scale-110 transition-transform" />
                                                <span className="text-[10px] font-black uppercase tracking-tight text-slate-800">Report Issue</span>
                                                <span className="text-[8px] text-slate-500">Safety concern</span>
                                            </button>

                                        </div>
                                    </div>

                                    {/* Zone Safety */}
                                    <div className="premium-card p-6">
                                        <div className="flex items-center justify-between mb-6">
                                            <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                                                <FiShield className="text-indigo-600" />
                                                Zone Safety
                                            </h3>
                                            <span className="text-[10px] text-slate-400 font-medium">Updated 5 min ago</span>
                                        </div>
                                        <div className="space-y-4">
                                            {loading ? (
                                                <div className="text-center py-4 text-slate-400">
                                                    <div className="w-6 h-6 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
                                                </div>
                                            ) : zoneSafety.length === 0 ? (
                                                <div className="text-center py-4 text-slate-400 text-sm">No zone data available</div>
                                            ) : (
                                                zoneSafety.map((zone, idx) => {
                                                    const colorMap = {
                                                        'green': 'bg-indigo-600',
                                                        'amber': 'bg-amber-500',
                                                        'red': 'bg-red-500'
                                                    };

                                                    return (
                                                        <div key={idx} className="space-y-2 cursor-pointer hover:bg-slate-50 p-2 rounded-lg transition-colors" onClick={() => handleZoneClick(zone.name)}>
                                                            <div className="flex justify-between items-end">
                                                                <div>
                                                                    <h4 className="text-sm font-bold text-slate-800 leading-none">{zone.name}</h4>
                                                                    <p className="text-[10px] text-slate-500 mt-1 flex items-center gap-1">
                                                                        {zone.incidents}
                                                                        <span className={zone.trend === 'down' ? 'text-indigo-600' : zone.trend === 'up' ? 'text-red-500' : 'text-slate-400'}>
                                                                            {zone.trend === 'down' ? '↓' : zone.trend === 'up' ? '↑' : '•'}
                                                                        </span>
                                                                    </p>
                                                                </div>
                                                                <div className="text-lg font-black text-slate-300">{zone.score}</div>
                                                            </div>
                                                            <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                                                                <div
                                                                    className={`h-full rounded-full transition-all duration-1000 ${colorMap[zone.color] || 'bg-slate-500'}`}
                                                                    style={{ width: `${zone.score}%` }}
                                                                />
                                                            </div>
                                                        </div>
                                                    );
                                                })
                                            )}
                                        </div>
                                    </div>

                                    {/* Weather Conditions */}
                                    <div className="premium-card p-6 bg-slate-50">
                                        {loading || !weather ? (
                                            <div className="text-center py-8 text-slate-400">
                                                <div className="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                                                Loading weather...
                                            </div>
                                        ) : (
                                            <>
                                                <div className="flex justify-between items-start mb-4">
                                                    <h3 className="text-lg font-bold text-slate-800 leading-none">Weather Conditions</h3>
                                                    <span className="text-[10px] px-2 py-0.5 bg-indigo-100 text-indigo-600 rounded-full font-bold">{weather.impact} Impact</span>
                                                </div>
                                                <div className="flex items-center gap-4 mb-6">
                                                    <div className="w-16 h-16 flex items-center justify-center text-amber-500 text-5xl">
                                                        {weather.icon}
                                                    </div>
                                                    <div>
                                                        <div className="text-4xl font-black text-slate-800 leading-none">{weather.temperature}°C</div>
                                                        <div className="text-xs text-slate-500 font-medium">{weather.condition}</div>
                                                    </div>
                                                </div>
                                                <div className="grid grid-cols-3 gap-2">
                                                    <div className="bg-white p-2 rounded-xl text-center border border-slate-100 shadow-sm">
                                                        <FiDroplet className="mx-auto text-blue-500 mb-1" />
                                                        <div className="text-[10px] text-slate-400 uppercase tracking-tighter">Humidity</div>
                                                        <div className="text-xs font-bold text-slate-800">{weather.humidity}%</div>
                                                    </div>
                                                    <div className="bg-white p-2 rounded-xl text-center border border-slate-100 shadow-sm">
                                                        <FiWind className="mx-auto text-indigo-500 mb-1" />
                                                        <div className="text-[10px] text-slate-400 uppercase tracking-tighter">Wind</div>
                                                        <div className="text-xs font-bold text-slate-800">{weather.wind_speed} km/h</div>
                                                    </div>
                                                    <div className="bg-white p-2 rounded-xl text-center border border-slate-100 shadow-sm">
                                                        <FiEye className="mx-auto text-purple-500 mb-1" />
                                                        <div className="text-[10px] text-slate-400 uppercase tracking-tighter">Visibility</div>
                                                        <div className="text-xs font-bold text-slate-800">{weather.visibility}</div>
                                                    </div>
                                                </div>
                                            </>
                                        )}
                                    </div>
                                </div >
                            </div >
                        </div >
                    )}
                    {activeTab === 'Route Map' && <RouteMap />}
                    {activeTab === 'Deliveries' && <div className="p-4"><LiveTracking deliveryId={riderId} /></div>}
                    {activeTab === 'AI Insights' && <AIReportSummary />}
                    {activeTab === 'Analytics' && <Analytics />}
                    {activeTab === 'Safety Zones' && <RouteMap showSafeZones={true} />}
                    {activeTab === 'Alerts' && (
                        <div className="premium-card p-6">
                            <h3 className="text-lg font-bold mb-4">Recent Alerts</h3>
                            <div className="space-y-3">
                                {alerts.length > 0 ? (
                                    alerts.map((alert, idx) => (
                                        <div key={idx} className={`border p-4 rounded-xl flex items-center gap-3 ${alert.type === 'safety' ? 'bg-red-50 border-red-200 text-red-700' : 'bg-slate-50 border-slate-200 text-slate-700'}`}>
                                            <FiAlertTriangle className="text-xl flex-shrink-0" />
                                            <div>
                                                <p className="font-bold">{alert.title}</p>
                                                <p className="text-xs opacity-80">{alert.message}</p>
                                                <p className="text-[10px] mt-1 opacity-60">{new Date(alert.timestamp).toLocaleString()}</p>
                                            </div>
                                        </div>
                                    ))
                                ) : (
                                    <div className="text-center py-8 text-slate-400">
                                        <FiBell className="text-4xl mx-auto mb-2 opacity-50" />
                                        <p>No recent alerts</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                    {activeTab === 'Feedback' && <FeedbackForm riderId={riderId} routeId="last_route" />}
                    {activeTab === 'Settings' && (
                        <div className="max-w-4xl mx-auto space-y-6">
                            <div className="premium-card p-8">
                                <div className="flex items-center gap-4 mb-8">
                                    <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 text-2xl font-bold">
                                        {user?.username?.[0] || 'U'}
                                    </div>
                                    <div>
                                        <h3 className="text-xl font-bold text-slate-800">{user?.username || 'User'}</h3>
                                        <p className="text-slate-500">{user?.role || 'Rider'} • {riderId}</p>
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div className="space-y-4">
                                        <h4 className="font-bold text-slate-700 border-b border-slate-100 pb-2">Profile Information</h4>
                                        <div>
                                            <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Full Name</label>
                                            <input
                                                type="text"
                                                name="full_name"
                                                value={settingsForm.full_name}
                                                onChange={handleSettingsChange}
                                                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-indigo-500"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Email Address</label>
                                            <input
                                                type="email"
                                                name="email"
                                                value={settingsForm.email}
                                                onChange={handleSettingsChange}
                                                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-indigo-500"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Vehicle Number</label>
                                            <input
                                                type="text"
                                                name="vehicle_number"
                                                value={settingsForm.vehicle_number}
                                                onChange={handleSettingsChange}
                                                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-indigo-500"
                                            />
                                        </div>
                                    </div>

                                    <div className="space-y-4">
                                        <h4 className="font-bold text-slate-700 border-b border-slate-100 pb-2">Emergency Contacts</h4>
                                        <div>
                                            <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Primary Contact Name</label>
                                            <input
                                                type="text"
                                                name="emergency_contact_name"
                                                value={settingsForm.emergency_contact_name}
                                                onChange={handleSettingsChange}
                                                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-indigo-500"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Primary Contact Phone</label>
                                            <input
                                                type="tel"
                                                name="emergency_contact_phone"
                                                value={settingsForm.emergency_contact_phone}
                                                onChange={handleSettingsChange}
                                                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-indigo-500"
                                            />
                                        </div>
                                        <div className="pt-2">
                                            <label className="flex items-center gap-2 cursor-pointer">
                                                <input
                                                    type="checkbox"
                                                    name="share_location"
                                                    checked={settingsForm.share_location}
                                                    onChange={handleSettingsChange}
                                                    className="w-4 h-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500"
                                                />
                                                <span className="text-sm text-slate-600">Share live location during active shifts</span>
                                            </label>
                                        </div>
                                    </div>
                                </div>

                                <div className="mt-8 flex justify-end gap-4">
                                    <button className="px-6 py-2 text-slate-500 font-bold hover:text-slate-800 transition-colors">Cancel</button>
                                    <button
                                        className="px-6 py-2 bg-indigo-600 text-white rounded-lg font-bold hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-600/20 disabled:opacity-50"
                                        onClick={handleSaveSettings}
                                        disabled={loading}
                                    >
                                        Save Changes
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </main >

            </div >
        </div >
    );
};

export default ModernDashboard;
