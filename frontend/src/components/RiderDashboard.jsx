
import React, { useState, useEffect } from 'react';
import {
    FiShield, FiMap, FiNavigation, FiUser, FiLogOut, FiBell, FiCheckCircle, FiChevronDown, FiChevronUp
} from 'react-icons/fi';
import RouteMap from './RouteMap';
import { api } from '../services/api';
import useLocation from '../hooks/useLocation';

const RiderDashboard = ({ setAuth }) => {
    const [activeTab, setActiveTab] = useState('route-map');
    const [panicAlerting, setPanicAlerting] = useState(false);
    const [riderId, setRiderId] = useState(localStorage.getItem('rider_id') || 'RIDER_402');
    const { location: currentLocation } = useLocation();
    const [isOnline, setIsOnline] = useState(true);
    const [isTripInfoExpanded, setIsTripInfoExpanded] = useState(true);

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
                        <div className="bg-blue-600 p-2 rounded-lg text-white">
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
                        <button onClick={() => setAuth(false)} className="text-gray-400 hover:text-red-500">
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
                        className="flex-1 bg-blue-600 text-white py-3 rounded-xl font-bold hover:bg-blue-700 active:scale-95 transition-all shadow-lg shadow-blue-500/20 flex items-center justify-center gap-2"
                    >
                        <FiCheckCircle /> SAFETY CHECK-IN
                    </button>
                </div>

                {/* Main Content Area */}
                <main className="flex-1 relative">
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
                                <div className="mt-1 text-xs text-blue-600 font-medium flex items-center gap-1">
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
                </main>

                {/* Bottom Nav */}
                <nav className="bg-white border-t border-gray-200 pb-safe">
                    <div className="flex justify-around p-2">
                        <button className="p-2 text-blue-600 flex flex-col items-center gap-1">
                            <FiMap size={24} />
                            <span className="text-[10px] font-bold">Map</span>
                        </button>
                        <button className="p-2 text-gray-400 hover:text-gray-600 flex flex-col items-center gap-1">
                            <FiBell size={24} />
                            <span className="text-[10px] font-medium">Alerts</span>
                        </button>
                        <button className="p-2 text-gray-400 hover:text-gray-600 flex flex-col items-center gap-1">
                            <FiUser size={24} />
                            <span className="text-[10px] font-medium">Profile</span>
                        </button>
                    </div>
                </nav>
            </div>
        </div>
    );
};

export default RiderDashboard;
