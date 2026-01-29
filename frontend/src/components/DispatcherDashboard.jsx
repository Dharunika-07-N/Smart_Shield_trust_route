import React, { useState, useEffect } from 'react';
import {
    FiShield, FiPackage, FiActivity, FiMap, FiUsers,
    FiAlertTriangle, FiNavigation, FiBarChart2, FiLogOut,
    FiHeadphones, FiSearch, FiBell, FiTruck, FiCheckCircle,
    FiClock, FiTrendingUp
} from 'react-icons/fi';
import Analytics from './Analytics';
import RouteMap from './RouteMap';
import LiveTracking from './LiveTracking';
import { api } from '../services/api';

const DispatcherDashboard = ({ setAuth }) => {
    const [activeTab, setActiveTab] = useState('Overview');
    const [isNetworkStable, setIsNetworkStable] = useState(true);

    const stats = [
        { label: 'Total Fleet', value: '184', icon: FiTruck, color: 'text-blue-400' },
        { label: 'Active Tasks', value: '42', icon: FiPackage, color: 'text-indigo-400' },
        { label: 'Safety Index', value: '98%', icon: FiShield, color: 'text-emerald-400' },
        { label: 'Network Load', value: '14%', icon: FiActivity, color: 'text-rose-400' }
    ];

    const menuItems = [
        { id: 'Overview', icon: FiActivity, label: 'Ops Overview' },
        { id: 'Fleet', icon: FiMap, label: 'Live Fleet Map' },
        { id: 'Queue', icon: FiPackage, label: 'Delivery Queue' },
        { id: 'Drivers', icon: FiUsers, label: 'Active Drivers' },
        { id: 'Performance', icon: FiBarChart2, label: 'Analytics' }
    ];

    return (
        <div className="flex h-screen bg-slate-50 text-slate-800 font-['Inter'] overflow-hidden">
            {/* Sidebar */}
            <aside className="w-64 bg-white border-r border-slate-200 flex flex-col z-30 shadow-sm">
                <div className="p-6 flex items-center gap-3">
                    <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
                        <FiHeadphones size={24} />
                    </div>
                    <div>
                        <h1 className="text-slate-900 font-bold leading-none">SmartShield</h1>
                        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mt-1">Dispatch Ops</p>
                    </div>
                </div>

                <nav className="flex-1 px-4 py-6 space-y-1">
                    {menuItems.map(item => (
                        <button
                            key={item.id}
                            onClick={() => setActiveTab(item.id)}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-semibold text-sm ${activeTab === item.id
                                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/20'
                                : 'text-slate-500 hover:text-slate-800 hover:bg-slate-50'
                                }`}
                        >
                            <item.icon size={18} />
                            {item.label}
                        </button>
                    ))}
                </nav>

                <div className="p-6 mt-auto">
                    <button
                        onClick={() => {
                            localStorage.removeItem('auth_token');
                            setAuth(false);
                        }}
                        className="w-full flex items-center gap-3 px-4 py-3 text-slate-500 hover:text-rose-400 transition-colors text-sm font-semibold"
                    >
                        <FiLogOut /> Disconnect
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col min-w-0">
                {/* Header */}
                <header className="h-20 bg-white/50 backdrop-blur-md border-b border-slate-200 flex items-center justify-between px-8 z-20">
                    <div className="flex items-center gap-4">
                        <h2 className="text-xl font-bold text-slate-900 tracking-tight">Fleet Intelligence</h2>
                        <div className="h-6 w-px bg-slate-200"></div>
                        <div className="flex items-center gap-2 px-3 py-1 bg-indigo-50 border border-indigo-100 rounded-full">
                            <div className="w-1.5 h-1.5 bg-indigo-600 rounded-full animate-pulse"></div>
                            <span className="text-[10px] font-bold text-indigo-600 uppercase tracking-widest">Master Node Active</span>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <button className="text-slate-400 hover:text-slate-900 transition-colors relative">
                            <FiBell size={20} />
                            <span className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-rose-500 rounded-full border-2 border-white"></span>
                        </button>
                        <div className="w-px h-8 bg-slate-800"></div>
                        <div className="flex items-center gap-3">
                            <div className="text-right hidden sm:block">
                                <p className="text-sm font-bold text-slate-900 leading-none">Dispatcher 402</p>
                                <p className="text-[10px] text-slate-500 mt-1 uppercase">Sector Chennai</p>
                            </div>
                            <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center text-slate-400 border border-slate-200 shadow-sm">
                                <FiHeadphones />
                            </div>
                        </div>
                    </div>
                </header>

                <main className="flex-1 overflow-y-auto p-8">
                    {activeTab === 'Overview' && (
                        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-700">
                            {/* Stats */}
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                                {stats.map((s, i) => (
                                    <div key={i} className="bg-white p-6 rounded-3xl border border-slate-200 hover:border-indigo-500/30 transition-all group shadow-sm">
                                        <div className="flex items-center justify-between mb-4">
                                            <div className={`p-3 bg-slate-50 ${s.color} rounded-2xl group-hover:scale-110 transition-transform`}>
                                                <s.icon size={24} />
                                            </div>
                                            <FiTrendingUp className="text-emerald-500" />
                                        </div>
                                        <p className="text-slate-500 text-xs font-bold uppercase tracking-widest">{s.label}</p>
                                        <p className="text-3xl font-black text-slate-900 mt-1">{s.value}</p>
                                    </div>
                                ))}
                            </div>

                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                                <div className="lg:col-span-2 space-y-8">
                                    <div className="bg-white p-8 rounded-[2.5rem] border border-slate-200 shadow-sm">
                                        <div className="flex items-center justify-between mb-8">
                                            <h3 className="text-lg font-bold text-slate-900">Live Operations Command</h3>
                                            <div className="flex gap-2">
                                                <button className="px-4 py-2 bg-indigo-600 text-white text-xs font-bold rounded-xl shadow-lg shadow-indigo-500/20 transition-all active:scale-95">Optimize All</button>
                                                <button className="px-4 py-2 bg-white text-slate-600 text-xs font-bold rounded-xl border border-slate-200 hover:bg-slate-50">Filter View</button>
                                            </div>
                                        </div>
                                        <div className="h-[400px] rounded-3xl overflow-hidden border border-slate-200">
                                            <LiveTracking />
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-8">
                                    <div className="bg-white p-8 rounded-[2.5rem] border border-slate-200 shadow-sm">
                                        <h3 className="text-lg font-bold text-slate-900 mb-6">Real-time Activity</h3>
                                        <div className="space-y-4">
                                            {[1, 2, 3, 4].map(i => (
                                                <div key={i} className="p-4 bg-slate-50 rounded-2xl border border-transparent group hover:border-indigo-500/30 transition-all">
                                                    <div className="flex items-center gap-3">
                                                        <div className="w-8 h-8 bg-indigo-50 text-indigo-600 rounded-lg flex items-center justify-center border border-indigo-100">
                                                            <FiTruck size={16} />
                                                        </div>
                                                        <div className="flex-1">
                                                            <div className="flex justify-between">
                                                                <p className="text-xs font-bold text-slate-900">Driver #4421</p>
                                                                <span className="text-[10px] text-slate-600 font-bold uppercase">2m ago</span>
                                                            </div>
                                                            <p className="text-[10px] text-slate-500 mt-0.5">Checked in at Zone 4B (Secure)</p>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                        <button className="w-full mt-6 py-4 bg-slate-50 hover:bg-slate-100 text-slate-600 rounded-2xl text-xs font-bold transition-all border border-slate-200">Full Access Log</button>
                                    </div>

                                    <div className="p-8 bg-indigo-600 rounded-[2.5rem] shadow-2xl shadow-indigo-900/20 text-white relative overflow-hidden group">
                                        <FiShield className="absolute -right-8 -bottom-8 text-white/5 w-40 h-40 group-hover:scale-150 transition-transform duration-1000" />
                                        <h4 className="text-lg font-black leading-tight mb-2">Network Safety Guarantee</h4>
                                        <p className="text-xs text-indigo-100/70 leading-relaxed mb-6">The SmartShield AI is current monitoring 184 active nodes with 0 safety breaches in the last 24h.</p>
                                        <div className="flex items-center gap-2">
                                            <FiCheckCircle size={16} />
                                            <span className="text-xs font-bold uppercase tracking-widest">Nodes Verified</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'Fleet' && (
                        <div className="h-full rounded-[2.5rem] overflow-hidden border border-slate-200 shadow-sm bg-white">
                            <LiveTracking />
                        </div>
                    )}

                    {activeTab === 'Performance' && (
                        <div className="bg-white p-8 rounded-[2.5rem] border border-slate-200 h-full shadow-sm">
                            <Analytics />
                        </div>
                    )}

                    {(activeTab === 'Queue' || activeTab === 'Drivers') && (
                        <div className="h-full flex flex-col items-center justify-center text-center">
                            <div className="p-12 bg-white rounded-[3rem] border border-slate-200 shadow-xl">
                                <FiPackage size={48} className="text-slate-200 mx-auto mb-6" />
                                <h3 className="text-2xl font-black text-slate-900">{activeTab} Interface</h3>
                                <p className="text-slate-500 mt-2 max-w-xs mx-auto">Connecting to real-time sync engine... Sector updates arriving shortly.</p>
                                <button className="mt-8 px-8 py-3 bg-indigo-600 text-white rounded-2xl font-bold shadow-lg shadow-indigo-500/20 transition-all">Retry Handshake</button>
                            </div>
                        </div>
                    )}
                </main>
            </div>
        </div>
    );
};

export default DispatcherDashboard;
