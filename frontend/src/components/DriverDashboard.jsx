import React, { useState, useEffect } from 'react';
import {
    FiShield, FiNavigation, FiUser, FiLogOut, FiBell,
    FiCheckCircle, FiChevronDown, FiChevronUp, FiTruck,
    FiMap, FiAlertTriangle, FiPhone, FiMessageSquare,
    FiClock, FiZap
} from 'react-icons/fi';
import RouteMap from './RouteMap';
import { api } from '../services/api';
import useLocation from '../hooks/useLocation';

const DriverDashboard = ({ setAuth }) => {
    const [activeTab, setActiveTab] = useState('Map');
    const [panicAlerting, setPanicAlerting] = useState(false);
    const [driverId, setDriverId] = useState(localStorage.getItem('user_id') || 'DRIVER_001');
    const { location: currentLocation } = useLocation();
    const [isOnline, setIsOnline] = useState(true);
    const [isTripExpanded, setIsTripExpanded] = useState(true);

    // Mock Active Delivery
    const activeTrip = {
        id: '#7742-XJ',
        customer: 'Suresh Kumar',
        address: '24, Lotus Apts, Velachery, Chennai',
        eta: '12 min',
        distance: '3.4 km',
        safetyAlert: 'Safe Route Active',
        markers: [
            { position: [12.9716, 80.2452], color: '#10b981', popup: 'Customer Location' }
        ]
    };

    const handlePanicButton = async () => {
        if (!currentLocation || !driverId) return;
        if (!window.confirm('🚨 Trigger Emergency SOS alert? Help will be dispatched immediately.')) return;

        setPanicAlerting(true);
        try {
            await api.triggerPanicButton({
                rider_id: driverId,
                location: currentLocation,
            });
            alert('Emergency SOS Signal Sent. Help is on the way.');
        } catch (error) {
            alert('SOS Signal Error. Please use alternate contact.');
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
            alert("Location Shared Successfully");
        } catch (e) {
            alert("Check-in Error");
        }
    };

    return (
        <div className="flex h-screen bg-slate-50 text-slate-800 font-['Inter'] overflow-hidden flex-col">
            {/* Header */}
            <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 shrink-0 z-30">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
                        <FiTruck size={18} />
                    </div>
                    <div>
                        <h1 className="text-slate-900 font-bold text-sm leading-none">SmartShield</h1>
                        <p className="text-[10px] text-indigo-600 font-bold uppercase tracking-wider mt-0.5">Active Duty</p>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2 px-3 py-1 bg-indigo-50 border border-indigo-100 rounded-full">
                        <div className="w-1.5 h-1.5 bg-indigo-600 rounded-full animate-pulse"></div>
                        <span className="text-[10px] font-bold text-indigo-600 uppercase tracking-widest">Online</span>
                    </div>
                    <button
                        onClick={() => {
                            localStorage.removeItem('auth_token');
                            setAuth(false);
                        }}
                        className="text-slate-500 hover:text-rose-500 transition-colors"
                    >
                        <FiLogOut size={20} />
                    </button>
                </div>
            </header>

            {/* Emergency & Status Quick Bar */}
            <div className="bg-white border-b border-slate-200 p-2 flex gap-2 z-20">
                <button
                    onClick={handlePanicButton}
                    disabled={panicAlerting}
                    className="flex-1 bg-rose-50 hover:bg-rose-600 border border-rose-200 text-rose-600 hover:text-white py-3 rounded-2xl font-black text-xs transition-all flex items-center justify-center gap-2 shadow-sm"
                >
                    <FiAlertTriangle className={panicAlerting ? "animate-spin" : "animate-pulse"} /> SOS PANIC
                </button>
                <button
                    onClick={handleCheckIn}
                    className="flex-1 bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-800 py-3 rounded-2xl font-black text-xs transition-all flex items-center justify-center gap-2 shadow-sm"
                >
                    <FiCheckCircle className="text-indigo-600" /> STATUS CHECK
                </button>
            </div>

            <main className="flex-1 relative overflow-hidden">
                <RouteMap
                    variant="light-minimal"
                    markers={activeTrip.markers}
                    center={activeTrip.markers[0]?.position}
                />

                {/* Delivery Card - Floating */}
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
                                <p className="text-xs text-slate-400 font-bold uppercase tracking-widest mt-1">Order {activeTrip.id}</p>
                            </div>
                            <div className="flex flex-col items-end">
                                <span className="text-2xl font-black text-indigo-600">{activeTrip.eta}</span>
                                <span className="text-[10px] text-slate-400 font-black uppercase">{activeTrip.distance}</span>
                            </div>
                        </div>

                        <div className="space-y-4 mb-8">
                            <div className="flex items-start gap-4">
                                <div className="w-10 h-10 bg-slate-50 rounded-xl flex items-center justify-center text-slate-400 shrink-0 border border-slate-100">
                                    <FiUser />
                                </div>
                                <div className="flex-1">
                                    <p className="text-[10px] text-slate-400 font-bold uppercase">Customer</p>
                                    <p className="text-sm font-bold text-slate-900 mt-0.5">{activeTrip.customer}</p>
                                </div>
                                <div className="flex gap-2">
                                    <button className="w-10 h-10 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center border border-blue-100"><FiPhone size={18} /></button>
                                    <button className="w-10 h-10 bg-indigo-50 text-indigo-600 rounded-xl flex items-center justify-center border border-indigo-100"><FiMessageSquare size={18} /></button>
                                </div>
                            </div>

                            <div className="flex items-start gap-4">
                                <div className="w-10 h-10 bg-slate-50 rounded-xl flex items-center justify-center text-indigo-600 shrink-0 border border-slate-100">
                                    <FiMapPin />
                                </div>
                                <div>
                                    <p className="text-[10px] text-slate-400 font-bold uppercase">Destination</p>
                                    <p className="text-sm font-bold text-slate-900 mt-0.5 leading-relaxed">{activeTrip.address}</p>
                                </div>
                            </div>

                            <div className="p-4 bg-indigo-50 border border-indigo-100 rounded-2xl flex items-center gap-3">
                                <FiShield className="text-indigo-600 shrink-0" />
                                <span className="text-xs font-bold text-indigo-600">{activeTrip.safetyAlert}</span>
                                <div className="ml-auto flex gap-1">
                                    <div className="w-1 h-3 bg-indigo-500 rounded-full animate-pulse"></div>
                                    <div className="w-1 h-2 bg-indigo-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                                </div>
                            </div>
                        </div>

                        <div className="flex gap-3">
                            <button className="flex-[2] py-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl font-black text-sm transition-all flex items-center justify-center gap-2 shadow-lg shadow-indigo-500/20">
                                <FiNavigation /> START NAVIGATION
                            </button>
                            <button className="flex-1 py-4 bg-white hover:bg-slate-50 text-slate-800 rounded-2xl font-black text-sm transition-all border border-slate-200">
                                ARRIVED
                            </button>
                        </div>
                    </div>
                </div>
            </main>

            {/* Bottom Nav */}
            <nav className="h-20 bg-white border-t border-slate-200 flex items-center justify-around shrink-0 pb-safe">
                <button
                    onClick={() => setActiveTab('Map')}
                    className={`flex flex-col items-center gap-1 flex-1 h-full justify-center transition-all ${activeTab === 'Map' ? 'text-indigo-600 bg-indigo-50/50' : 'text-slate-400'}`}
                >
                    <FiMap size={24} />
                    <span className="text-[8px] font-bold uppercase tracking-widest">Map</span>
                </button>
                <button
                    onClick={() => setActiveTab('Tasks')}
                    className={`flex flex-col items-center gap-1 flex-1 h-full justify-center transition-all ${activeTab === 'Tasks' ? 'text-indigo-600 bg-indigo-50/50' : 'text-slate-400'}`}
                >
                    <FiBell size={24} />
                    <span className="text-[8px] font-bold uppercase tracking-widest">Tasks</span>
                </button>
                <button
                    onClick={() => setActiveTab('Profile')}
                    className={`flex flex-col items-center gap-1 flex-1 h-full justify-center transition-all ${activeTab === 'Profile' ? 'text-indigo-600 bg-indigo-50/50' : 'text-slate-400'}`}
                >
                    <FiUser size={24} />
                    <span className="text-[8px] font-bold uppercase tracking-widest">Profile</span>
                </button>
            </nav>
        </div>
    );
};

export default DriverDashboard;
