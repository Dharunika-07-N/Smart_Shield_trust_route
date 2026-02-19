import React, { useState, useEffect } from 'react';
import {
    FiShield, FiPackage, FiActivity, FiMap, FiUsers,
    FiAlertTriangle, FiNavigation, FiBarChart2, FiLogOut,
    FiHeadphones, FiSearch, FiBell, FiTruck, FiCheckCircle,
    FiClock, FiTrendingUp, FiZap
} from 'react-icons/fi';
import Analytics from './Analytics';
import RouteMap from './RouteMap';
import LiveTracking from './LiveTracking';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';

const DispatcherDashboard = () => {
    const { user, logout } = useAuth();
    const [activeTab, setActiveTab] = useState('Overview');
    const [queue, setQueue] = useState([]);
    const [onlineDrivers, setOnlineDrivers] = useState([]);
    const [loading, setLoading] = useState(false);

    const fetchData = async () => {
        setLoading(true);
        try {
            if (activeTab === 'Queue') {
                const data = await api.get('/deliveries');
                setQueue(Array.isArray(data) ? data : []);
            } else if (activeTab === 'Drivers') {
                const data = await api.get('/users/online');
                setOnlineDrivers(Array.isArray(data) ? data : []);
            }
        } catch (e) {
            console.error("Failed to fetch dispatcher data", e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [activeTab]);

    const handleAutoDispatch = async () => {
        if (!window.confirm("Trigger automated AI delivery assignment?")) return;
        try {
            await api.post('/deliveries/auto-dispatch');
            alert("Auto-dispatch triggered successfully!");
            fetchData();
        } catch (e) {
            alert("Failed to trigger auto-dispatch: " + e.message);
        }
    };
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
                    <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 mb-4">
                        <p className="text-xs font-bold text-slate-800 truncate">{user?.full_name || user?.username}</p>
                        <p className="text-[10px] text-indigo-600 font-bold uppercase tracking-wider mt-0.5">Dispatcher</p>
                    </div>
                    <button
                        onClick={logout}
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
                                <p className="text-sm font-bold text-slate-900 leading-none">{user?.full_name || user?.username || 'Dispatcher'}</p>
                                <p className="text-[10px] text-indigo-600 mt-1 uppercase font-bold">Dispatch Ops</p>
                            </div>
                            <div className="w-10 h-10 bg-indigo-100 rounded-xl flex items-center justify-center text-indigo-600 border border-indigo-200 shadow-sm font-bold">
                                {(user?.full_name || user?.username || 'D')[0].toUpperCase()}
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

                    {activeTab === 'Queue' && (
                        <div className="space-y-6">
                            <div className="flex items-center justify-between">
                                <h2 className="text-2xl font-black text-slate-900">Delivery Queue</h2>
                                <button
                                    onClick={handleAutoDispatch}
                                    className="px-6 py-2.5 bg-indigo-600 text-white text-sm font-black rounded-xl shadow-lg shadow-indigo-500/20 hover:bg-indigo-700 transition-all active:scale-95 flex items-center gap-2"
                                >
                                    <FiZap size={16} /> AUTO-DISPATCH ALL
                                </button>
                            </div>
                            <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
                                {queue.length === 0 ? (
                                    <div className="py-20 text-center text-slate-400">
                                        <FiPackage size={48} className="mx-auto mb-4 opacity-20" />
                                        <p className="font-bold">Queue is empty</p>
                                    </div>
                                ) : (
                                    <table className="w-full text-sm">
                                        <thead>
                                            <tr className="bg-slate-50 border-b border-slate-100 uppercase text-[10px] font-black tracking-widest text-slate-400">
                                                <th className="text-left px-6 py-4">Order info</th>
                                                <th className="text-left px-4 py-4">Destination</th>
                                                <th className="text-left px-4 py-4">Safety</th>
                                                <th className="text-left px-4 py-4">Status</th>
                                                <th className="text-right px-6 py-4">Action</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-slate-50">
                                            {queue.map(item => (
                                                <tr key={item.id} className="hover:bg-slate-50/50 transition-colors">
                                                    <td className="px-6 py-4">
                                                        <p className="font-bold text-slate-800">{item.order_id}</p>
                                                        <p className="text-[10px] text-slate-400 uppercase font-black">{item.id?.substring(0, 8)}</p>
                                                    </td>
                                                    <td className="px-4 py-4">
                                                        <p className="text-xs text-slate-600 truncate max-w-[200px]">{item.dropoff_location?.address || 'N/A'}</p>
                                                    </td>
                                                    <td className="px-4 py-4">
                                                        <span className="text-xs font-bold text-indigo-600 bg-indigo-50 px-2 py-1 rounded-lg">
                                                            {item.safety_score || 85}%
                                                        </span>
                                                    </td>
                                                    <td className="px-4 py-4">
                                                        <span className={`px-2 py-1 rounded-full text-[10px] font-black uppercase tracking-wider ${item.status === 'pending' ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'}`}>
                                                            {item.status}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4 text-right">
                                                        <button className="text-indigo-600 font-bold text-xs hover:underline">Manage</button>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                )}
                            </div>
                        </div>
                    )}

                    {activeTab === 'Drivers' && (
                        <div className="space-y-6">
                            <h2 className="text-2xl font-black text-slate-900">Active Fleet</h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                {onlineDrivers.length === 0 ? (
                                    <div className="col-span-full py-20 text-center bg-white rounded-3xl border border-slate-200 border-dashed">
                                        <FiUsers size={48} className="mx-auto text-slate-100 mb-4" />
                                        <p className="text-slate-400 font-bold">No online drivers detected</p>
                                    </div>
                                ) : (
                                    onlineDrivers.map(dr => (
                                        <div key={dr.id} className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm hover:shadow-md transition-all">
                                            <div className="flex items-center gap-4 mb-4">
                                                <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center font-black text-xl border border-indigo-100">
                                                    {dr.full_name?.charAt(0) || dr.username?.charAt(0)}
                                                </div>
                                                <div className="flex-1 min-w-0">
                                                    <h3 className="font-bold text-slate-900 truncate">{dr.full_name || dr.username}</h3>
                                                    <div className="flex items-center gap-2">
                                                        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                                                        <span className="text-[10px] font-black text-emerald-600 uppercase tracking-widest">Active Now</span>
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="space-y-2 mb-6">
                                                <div className="flex justify-between text-[10px] font-bold text-slate-400 uppercase">
                                                    <span>Signal Strength</span>
                                                    <span className="text-slate-900">Optimal</span>
                                                </div>
                                                <div className="h-1 bg-slate-100 rounded-full overflow-hidden">
                                                    <div className="h-full bg-indigo-500 w-[92%]"></div>
                                                </div>
                                            </div>
                                            <div className="grid grid-cols-2 gap-2">
                                                <button className="py-2 bg-slate-50 text-slate-600 text-[10px] font-black uppercase rounded-xl border border-slate-200 hover:bg-slate-100">Profile</button>
                                                <button className="py-2 bg-indigo-600 text-white text-[10px] font-black uppercase rounded-xl hover:bg-indigo-700 shadow-lg shadow-indigo-500/10">Channel</button>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    )}
                </main>
            </div>
        </div>
    );
};

export default DispatcherDashboard;
