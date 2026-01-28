
import React, { useState, useEffect } from 'react';
import {
    FiShield, FiMap, FiNavigation, FiUser, FiLogOut, FiBell, FiCheckCircle, FiChevronDown, FiChevronUp, FiTruck
} from 'react-icons/fi';
import RouteMap from './RouteMap';
import { api } from '../services/api';
import useLocation from '../hooks/useLocation';

const DriverDashboard = ({ setAuth }) => {
    const [activeTab, setActiveTab] = useState('route-map');
    const [panicAlerting, setPanicAlerting] = useState(false);
    const [driverId, setDriverId] = useState(localStorage.getItem('user_id') || 'DRIVER_001');
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
        if (!currentLocation || !driverId) {
            alert('Location or driver ID not available.');
            return;
        }
        if (!window.confirm('Trigger Emergency SOS alert?')) return;
        setPanicAlerting(true);
        try {
            const response = await api.triggerPanicButton({
                rider_id: driverId, // Reusing endpoint
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
                rider_id: driverId,
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
            <div className="flex-1 flex flex-col min-w-0">
                <header className="bg-slate-900 border-b border-white/10 p-4 flex items-center justify-between shadow-xl z-20">
                    <div className="flex items-center gap-3">
                        <div className="bg-emerald-500 p-2 rounded-lg text-white">
                            <FiTruck size={20} />
                        </div>
                        <div>
                            <h1 className="font-bold text-white leading-tight">SmartShield</h1>
                            <p className="text-[10px] text-emerald-400 font-bold uppercase tracking-wider">Professional Driver</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => setIsOnline(!isOnline)}
                            className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold transition-all ${isOnline ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'
                                }`}
                        >
                            <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]' : 'bg-red-500'}`} />
                            {isOnline ? 'Duty Active' : 'Off Duty'}
                        </button>
                        <button onClick={() => setAuth(false)} className="text-gray-400 hover:text-red-500 p-2 transition-colors">
                            <FiLogOut size={20} />
                        </button>
                    </div>
                </header>

                <div className="bg-white border-b border-gray-200 p-3 flex gap-3 shadow-md relative z-10">
                    <button
                        onClick={handlePanicButton}
                        disabled={panicAlerting}
                        className="flex-1 bg-red-600 text-white py-3.5 rounded-xl font-bold hover:bg-red-700 active:scale-95 transition-all shadow-lg shadow-red-500/20 flex items-center justify-center gap-2"
                    >
                        <span className="animate-pulse">⚠️</span> EMERGENCY SOS
                    </button>
                    <button
                        onClick={handleCheckIn}
                        className="flex-1 bg-slate-800 text-white py-3.5 rounded-xl font-bold hover:bg-slate-900 active:scale-95 transition-all shadow-lg flex items-center justify-center gap-2"
                    >
                        <FiCheckCircle className="text-emerald-400" /> STATUS CHECK
                    </button>
                </div>

                <main className="flex-1 relative">
                    <RouteMap />

                    <div
                        onClick={() => setIsTripInfoExpanded(!isTripInfoExpanded)}
                        className={`absolute top-4 shadow-2xl transition-all duration-500 ease-in-out bg-slate-900/95 backdrop-blur-md border border-white/10 text-white cursor-pointer overflow-hidden z-20 ${isTripInfoExpanded
                            ? 'left-4 right-4 p-5 rounded-2xl'
                            : 'right-4 w-auto rounded-full px-5 py-2.5 flex items-center gap-3 left-auto'
                            }`}
                    >
                        {isTripInfoExpanded ? (
                            <>
                                <div className="flex justify-between items-center text-xs mb-3">
                                    <span className="text-gray-400 font-bold uppercase tracking-wider">Route Task #7742</span>
                                    <span className="font-bold text-emerald-400 flex items-center gap-2">
                                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,1)]" />
                                        LIVE OPTIMIZED
                                    </span>
                                </div>
                                <div className="flex items-end gap-2">
                                    <div className="text-3xl font-black text-white tracking-tighter">18</div>
                                    <div className="text-sm font-bold text-gray-500 mb-1.5 uppercase">Mins remaining</div>
                                </div>
                                <div className="mt-3 p-3 bg-white/5 rounded-xl text-xs text-blue-400 font-bold flex items-center gap-2 border border-blue-500/20">
                                    <FiShield className="shrink-0" size={14} />
                                    Dynamic Re-routing: Safe Zone Active (Avoided Heavy Traffic)
                                </div>
                                <div className="absolute top-4 right-4 text-gray-600">
                                    <FiChevronUp size={20} />
                                </div>
                            </>
                        ) : (
                            <>
                                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                                <span className="font-black text-white text-sm">18 MINS</span>
                                <FiChevronDown className="text-gray-500" />
                            </>
                        )}
                    </div>
                </main>

                <nav className="bg-slate-900 border-t border-white/5 pb-safe z-20">
                    <div className="flex justify-around items-center h-20">
                        <button className="flex-1 h-full text-emerald-500 flex flex-col items-center justify-center gap-1 bg-white/5">
                            <FiNavigation size={24} />
                            <span className="text-[10px] font-black uppercase tracking-widest">Navigate</span>
                        </button>
                        <button className="flex-1 h-full text-gray-500 hover:text-gray-300 flex flex-col items-center justify-center gap-1 transition-colors">
                            <FiMap size={24} />
                            <span className="text-[10px] font-bold uppercase tracking-widest">Area</span>
                        </button>
                        <button className="flex-1 h-full text-gray-500 hover:text-gray-300 flex flex-col items-center justify-center gap-1 transition-colors">
                            <FiBell size={24} />
                            <span className="text-[10px] font-bold uppercase tracking-widest">Tasks</span>
                        </button>
                        <button className="flex-1 h-full text-gray-500 hover:text-gray-300 flex flex-col items-center justify-center gap-1 transition-colors">
                            <FiUser size={24} />
                            <span className="text-[10px] font-bold uppercase tracking-widest">Profile</span>
                        </button>
                    </div>
                </nav>
            </div>
        </div>
    );
};

export default DriverDashboard;
