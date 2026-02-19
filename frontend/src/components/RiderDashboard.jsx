
import React, { useState, useEffect } from 'react';
import {
    FiShield, FiMap, FiNavigation, FiUser, FiLogOut, FiBell, FiCheckCircle, FiChevronDown, FiChevronUp
} from 'react-icons/fi';
import RouteMap from './RouteMap';
import { api } from '../services/api';
import useLocation from '../hooks/useLocation';
import { useAuth } from '../context/AuthContext';

const RiderDashboard = () => {
    const { user, logout } = useAuth();
    const [activeTab, setActiveTab] = useState('route-map');
    const [panicAlerting, setPanicAlerting] = useState(false);
    const [riderId, setRiderId] = useState(user?.id || localStorage.getItem('user_id') || 'RIDER_402');
    const { location: currentLocation } = useLocation();
    const [isOnline, setIsOnline] = useState(true);
    const [isTripInfoExpanded, setIsTripInfoExpanded] = useState(true);
    const [activeView, setActiveView] = useState('map'); // 'map', 'alerts', 'profile'
    const [safetyAlerts, setSafetyAlerts] = useState([
        { id: 1, type: 'weather', msg: 'Rain expected in Zone 3B. Proceed with caution.', time: '10m ago' },
        { id: 2, type: 'traffic', msg: 'High congestion detected on Highway 4.', time: '25m ago' },
        { id: 3, type: 'safety', msg: 'All secure checkpoints verified for your route.', time: '1h ago' }
    ]);

    useEffect(() => {
        const timer = setTimeout(() => {
            setIsTripInfoExpanded(false);
        }, 3000);
        return () => clearTimeout(timer);
    }, []);

    const handlePanicButton = async () => {
        if (!currentLocation || !riderId) {
            alert('Location or rider ID not available.');
            return;
        }
        if (!window.confirm('Trigger Emergency SOS alert?')) return;
        setPanicAlerting(true);
        try {
            const response = await api.triggerPanicButton({
                rider_id: riderId,
                location: currentLocation,
            });
            if (response.success) alert('Emergency SOS alert sent successfully!');
        } catch (error) {
            alert('Failed to send alert.');
        } finally {
            setPanicAlerting(false);
        }
    };

    const handleCheckIn = async () => {
        if (!currentLocation) return;
        try {
            await api.checkIn({
                rider_id: riderId,
                location: currentLocation,
                is_night_shift: new Date().getHours() >= 18 || new Date().getHours() < 6
            });
            alert("Check-in successful!");
        } catch (e) {
            alert("Check-in failed.");
        }
    };

    return (
        <div className="flex h-screen bg-gray-50 overflow-hidden">
            {/* Mobile-First Header */}
            <div className="flex-1 flex flex-col min-w-0">
                <header className="bg-white border-b border-gray-200 p-4 flex items-center justify-between shadow-sm z-10">
                    <div className="flex items-center gap-3">
                        <div className="bg-indigo-600 p-2 rounded-lg text-white">
                            <FiShield size={20} />
                        </div>
                        <div>
                            <h1 className="font-bold text-gray-900 leading-tight">SmartShield</h1>
                            <p className="text-xs text-gray-500">Rider App</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => setIsOnline(!isOnline)}
                            className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold transition-all ${isOnline ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
                                }`}
                        >
                            <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-500' : 'bg-gray-400'}`} />
                            {isOnline ? 'Online' : 'Offline'}
                        </button>
                        <button onClick={logout} className="text-gray-400 hover:text-red-500">
                            <FiLogOut size={20} />
                        </button>
                    </div>
                </header>

                {/* Action Bar */}
                <div className="bg-white border-b border-gray-200 p-3 flex gap-3 overflow-x-auto">
                    <button
                        onClick={handlePanicButton}
                        disabled={panicAlerting}
                        className="flex-1 bg-red-600 text-white py-3 rounded-xl font-bold hover:bg-red-700 active:scale-95 transition-all shadow-lg shadow-red-500/20 flex items-center justify-center gap-2"
                    >
                        <span className="animate-pulse">⚠️</span> SOS ALERT
                    </button>
                    <button
                        onClick={handleCheckIn}
                        className="flex-1 bg-indigo-600 text-white py-3 rounded-xl font-bold hover:bg-indigo-700 active:scale-95 transition-all shadow-lg shadow-indigo-500/20 flex items-center justify-center gap-2"
                    >
                        <FiCheckCircle /> SAFETY CHECK-IN
                    </button>
                </div>

                {/* Main Content Area */}
                <main className="flex-1 relative overflow-y-auto">
                    {activeView === 'map' && (
                        <>
                            <RouteMap />
                            {/* Overlay Status Card */}
                            <div
                                onClick={() => setIsTripInfoExpanded(!isTripInfoExpanded)}
                                className={`absolute top-4 transition-all duration-500 ease-in-out bg-white/95 backdrop-blur-sm shadow-xl border border-gray-100 cursor-pointer overflow-hidden z-20 ${isTripInfoExpanded
                                    ? 'left-4 right-4 p-4 rounded-xl'
                                    : 'right-4 w-auto rounded-full px-4 py-2 flex items-center gap-2 left-auto'
                                    }`}
                            >
                                {isTripInfoExpanded ? (
                                    <>
                                        <div className="flex justify-between items-center text-sm mb-2">
                                            <span className="text-gray-500 font-medium">Current Trip</span>
                                            <span className="font-bold text-green-600 flex items-center gap-1">
                                                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                                                On Track
                                            </span>
                                        </div>
                                        <div className="text-2xl font-black text-gray-900 tracking-tight">
                                            14 <span className="text-base font-normal text-gray-500">mins</span>
                                        </div>
                                        <div className="mt-1 text-xs text-indigo-600 font-medium flex items-center gap-1">
                                            <FiShield size={12} />
                                            via Safe Zone Corridor
                                        </div>
                                        <div className="absolute top-2 right-2 text-gray-300">
                                            <FiChevronUp />
                                        </div>
                                    </>
                                ) : (
                                    <>
                                        <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                                        <span className="font-bold text-gray-900 text-sm">14 mins</span>
                                        <FiChevronDown className="text-gray-400" />
                                    </>
                                )}
                            </div>
                        </>
                    )}

                    {activeView === 'alerts' && (
                        <div className="p-6 space-y-4 animate-in fade-in slide-in-from-bottom-4">
                            <h2 className="text-xl font-black text-gray-900 mb-6">Safety Feed</h2>
                            {safetyAlerts.map(alert => (
                                <div key={alert.id} className="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm flex gap-4">
                                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${alert.type === 'weather' ? 'bg-blue-50 text-blue-600' :
                                            alert.type === 'traffic' ? 'bg-amber-50 text-amber-600' :
                                                'bg-green-50 text-green-600'
                                        }`}>
                                        <FiBell size={20} />
                                    </div>
                                    <div>
                                        <p className="text-sm font-bold text-gray-800">{alert.msg}</p>
                                        <p className="text-[10px] text-gray-400 font-black uppercase tracking-widest mt-1">{alert.time}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {activeView === 'profile' && (
                        <div className="p-6 space-y-8 animate-in fade-in slide-in-from-bottom-4">
                            <div className="flex flex-col items-center text-center">
                                <div className="w-24 h-24 bg-indigo-100 rounded-3xl flex items-center justify-center text-indigo-600 font-black text-3xl mb-4 border-4 border-white shadow-xl">
                                    {user?.full_name?.[0] || 'R'}
                                </div>
                                <h2 className="text-2xl font-black text-gray-900">{user?.full_name || 'Rider Pro'}</h2>
                                <p className="text-sm text-gray-500">ID: {riderId}</p>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm">
                                    <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Safety Rating</p>
                                    <p className="text-xl font-black text-indigo-600">4.98/5</p>
                                </div>
                                <div className="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm">
                                    <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Total Trips</p>
                                    <p className="text-xl font-black text-gray-900">1,204</p>
                                </div>
                            </div>

                            <div className="bg-indigo-600 p-6 rounded-[2rem] text-white shadow-xl shadow-indigo-500/20">
                                <p className="text-xs font-black uppercase tracking-widest opacity-60 mb-1">Daily Safety Bonus</p>
                                <p className="text-3xl font-black">$45.50</p>
                                <div className="mt-4 h-1.5 bg-white/20 rounded-full overflow-hidden">
                                    <div className="h-full bg-white w-3/4"></div>
                                </div>
                                <p className="text-[10px] mt-2 font-bold">Goal: 5 consecutive safe trips (4/5 complete)</p>
                            </div>
                        </div>
                    )}
                </main>

                {/* Bottom Nav */}
                <nav className="bg-white border-t border-gray-200 pb-safe">
                    <div className="flex justify-around p-2">
                        <button
                            onClick={() => setActiveView('map')}
                            className={`p-2 flex flex-col items-center gap-1 flex-1 transition-all ${activeView === 'map' ? 'text-indigo-600 bg-indigo-50/50 rounded-xl' : 'text-gray-400'}`}
                        >
                            <FiMap size={24} />
                            <span className={`text-[10px] font-black uppercase tracking-widest ${activeView === 'map' ? 'opacity-100' : 'opacity-60'}`}>Map</span>
                        </button>
                        <button
                            onClick={() => setActiveView('alerts')}
                            className={`p-2 flex flex-col items-center gap-1 flex-1 transition-all ${activeView === 'alerts' ? 'text-indigo-600 bg-indigo-50/50 rounded-xl' : 'text-gray-400'}`}
                        >
                            <FiBell size={24} />
                            <span className={`text-[10px] font-black uppercase tracking-widest ${activeView === 'alerts' ? 'opacity-100' : 'opacity-60'}`}>Alerts</span>
                        </button>
                        <button
                            onClick={() => setActiveView('profile')}
                            className={`p-2 flex flex-col items-center gap-1 flex-1 transition-all ${activeView === 'profile' ? 'text-indigo-600 bg-indigo-50/50 rounded-xl' : 'text-gray-400'}`}
                        >
                            <FiUser size={24} />
                            <span className={`text-[10px] font-black uppercase tracking-widest ${activeView === 'profile' ? 'opacity-100' : 'opacity-60'}`}>Profile</span>
                        </button>
                    </div>
                </nav>
            </div>
        </div>
    );
};

export default RiderDashboard;
