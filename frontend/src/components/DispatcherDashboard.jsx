
import React, { useState, useEffect } from 'react';
import {
    FiShield, FiPackage, FiTrendingUp, FiMap,
    FiActivity, FiAlertCircle, FiCheckCircle, FiAlertTriangle, FiCpu, FiNavigation,
    FiUser, FiLogOut, FiSettings, FiBarChart2, FiLayers, FiMessageSquare, FiTruck, FiHeadphones
} from 'react-icons/fi';
import Analytics from './Analytics';
import RouteMap from './RouteMap';
import LiveTracking from './LiveTracking';
import { api } from '../services/api';

const DispatcherDashboard = ({ setAuth }) => {
    const [activeTab, setActiveTab] = useState('tracking');
    const [panicAlerting, setPanicAlerting] = useState(false);
    const [isOperational, setIsOperational] = useState(true);
    const [liveAlerts, setLiveAlerts] = useState([]);

    useEffect(() => {
        const fetchAlerts = async () => {
            try {
                const res = await api.getAlerts();
                if (res.status === 'success') {
                    setLiveAlerts(res.data.slice(0, 8));
                }
            } catch (err) {
                console.warn('Failed to fetch alerts for dispatcher');
            }
        };
        fetchAlerts();
        const interval = setInterval(fetchAlerts, 10000);
        return () => clearInterval(interval);
    }, []);

    const navItems = [
        { id: 'tracking', label: 'Live Dispatch', icon: FiMap },
        { id: 'route-map', label: 'Route Control', icon: FiNavigation },
        { id: 'alerts', label: 'Activity Log', icon: FiActivity },
        { id: 'analytics', label: 'Performance', icon: FiBarChart2 },
    ];

    const stats = [
        { title: 'Active Riders', value: '84', icon: FiUser, color: 'text-blue-500' },
        { title: 'Pending Tasks', value: '12', icon: FiPackage, color: 'text-amber-500' },
        { title: 'Safe Routes', value: '98%', icon: FiShield, color: 'text-emerald-500' },
        { title: 'Avg Alert Res', value: '1.2m', icon: FiActivity, color: 'text-red-500' },
    ];

    return (
        <div className="flex h-screen bg-[#0F172A] overflow-hidden text-slate-100">
            {/* Sidebar */}
            <aside className="w-72 bg-slate-900/50 border-r border-slate-800 flex-shrink-0 flex flex-col backdrop-blur-xl">
                <div className="p-8">
                    <div className="flex items-center gap-3">
                        <div className="bg-indigo-600 p-2.5 rounded-2xl shadow-lg shadow-indigo-600/20">
                            <FiHeadphones className="text-2xl text-white" />
                        </div>
                        <div>
                            <div className="font-black text-xl tracking-tighter text-white">DISPATCH</div>
                            <div className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest">Control Center</div>
                        </div>
                    </div>
                </div>

                <nav className="flex-1 px-6 space-y-3 mt-4">
                    {navItems.map(item => (
                        <button
                            key={item.id}
                            onClick={() => setActiveTab(item.id)}
                            className={`w-full flex items-center gap-4 px-5 py-4 rounded-2xl font-bold transition-all ${activeTab === item.id
                                ? 'bg-indigo-600 text-white shadow-xl shadow-indigo-900/40'
                                : 'text-slate-500 hover:text-white hover:bg-white/5'
                                }`}
                        >
                            <item.icon className="text-xl" />
                            <span className="text-sm tracking-wide">{item.label}</span>
                        </button>
                    ))}
                </nav>

                <div className="p-6">
                    <div className={`p-4 rounded-2xl border transition-all ${isOperational ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-red-500/10 border-red-500/20'}`}>
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">System Link</span>
                            <div className={`w-2 h-2 rounded-full ${isOperational ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,1)]' : 'bg-red-500 animate-pulse'}`} />
                        </div>
                        <p className={`text-xs font-bold ${isOperational ? 'text-emerald-400' : 'text-red-400'}`}>
                            {isOperational ? 'Network Optimized' : 'Interference Detected'}
                        </p>
                    </div>

                    <button
                        onClick={() => setAuth(false)}
                        className="w-full mt-6 flex items-center gap-3 px-5 py-4 text-slate-500 hover:text-red-400 hover:bg-red-400/5 rounded-2xl transition-all font-bold"
                    >
                        <FiLogOut />
                        <span className="text-sm">Disconnect</span>
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
                <header className="h-24 bg-slate-900/30 border-b border-slate-800 flex items-center justify-between px-10 flex-shrink-0 z-10 backdrop-blur-md">
                    <div>
                        <h2 className="text-2xl font-black text-white tracking-tight">Active Operation</h2>
                        <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mt-1">Real-time Fleet Intelligence</p>
                    </div>

                    <div className="flex items-center gap-6">
                        <div className="flex items-center gap-3 bg-slate-800/50 p-2 pr-6 rounded-2xl border border-slate-700/50">
                            <div className="w-10 h-10 bg-indigo-600/20 rounded-xl flex items-center justify-center text-indigo-400 border border-indigo-500/20 font-black">
                                H
                            </div>
                            <div>
                                <p className="text-xs font-black text-white">Dispatcher Alpha</p>
                                <p className="text-[10px] text-slate-500 font-bold">OPS_7702</p>
                            </div>
                        </div>
                    </div>
                </header>

                <main className="flex-1 overflow-y-auto p-8 custom-scrollbar">
                    {activeTab === 'analytics' ? (
                        <div className="animate-in fade-in duration-500">
                            <Analytics />
                        </div>
                    ) : activeTab === 'alerts' ? (
                        <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <h3 className="text-xl font-bold text-white mb-6">Security & Traffic Feed</h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {liveAlerts.length > 0 ? liveAlerts.map(alert => (
                                    <div key={alert.id} className="bg-slate-900/50 border border-slate-800 p-5 rounded-2xl flex gap-4 hover:border-indigo-500/30 transition-all">
                                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-2xl shadow-inner ${alert.has_traffic_issues ? 'bg-red-500/10 text-red-500' : 'bg-emerald-500/10 text-emerald-500'}`}>
                                            {alert.has_traffic_issues ? <FiAlertTriangle /> : <FiCheckCircle />}
                                        </div>
                                        <div className="flex-1">
                                            <div className="flex justify-between items-start mb-1">
                                                <span className="text-[10px] font-black text-indigo-400 uppercase tracking-widest">{alert.service_type}</span>
                                                <span className="text-[10px] text-slate-500 font-bold">{new Date(alert.created_at).toLocaleTimeString()}</span>
                                            </div>
                                            <p className="text-sm font-bold text-white leading-tight">
                                                {alert.has_traffic_issues ? 'Anomalous Activity Detected on Route' : 'Route Verified: Safety Protocol Active'}
                                            </p>
                                            <p className="text-xs text-slate-500 mt-2 line-clamp-1 italic">
                                                Location: {alert.route_data?.start_node || 'Active Sector'}
                                            </p>
                                        </div>
                                    </div>
                                )) : (
                                    <div className="col-span-2 py-20 text-center">
                                        <FiActivity className="text-4xl text-slate-800 mx-auto mb-4" />
                                        <p className="text-slate-500 font-bold">Scanning for network activity...</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    ) : (
                        <div className="h-full flex flex-col gap-8">
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                                {stats.map((s, i) => (
                                    <div key={i} className="bg-slate-900/50 border border-slate-800 p-6 rounded-3xl hover:border-indigo-500/30 transition-all group">
                                        <div className="flex items-center justify-between mb-4">
                                            <div className={`p-3 rounded-2xl bg-white/5 ${s.color} group-hover:scale-110 transition-transform`}>
                                                <s.icon className="text-xl" />
                                            </div>
                                        </div>
                                        <p className="text-slate-400 text-[10px] font-black uppercase tracking-[0.2em]">{s.title}</p>
                                        <p className="text-3xl font-black text-white mt-1">{s.value}</p>
                                    </div>
                                ))}
                            </div>

                            <div className="flex-1 bg-slate-900/50 border border-slate-800 rounded-3xl overflow-hidden relative shadow-2xl">
                                {activeTab === 'tracking' ? <LiveTracking /> : <RouteMap />}
                            </div>
                        </div>
                    )}
                </main>
            </div>
        </div>
    );
};

export default DispatcherDashboard;
