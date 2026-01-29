
import React, { useState, useEffect } from 'react';
import {
    FiShield, FiMap, FiPackage, FiZap, FiAlertTriangle, FiBarChart2,
    FiSettings, FiMessageSquare, FiSearch, FiBell, FiUser, FiChevronRight,
    FiNavigation, FiClock, FiWind, FiDroplet, FiEye, FiActivity, FiLayers,
    FiPlus, FiMinus, FiTarget, FiPhone
} from 'react-icons/fi';
import RouteMap from './RouteMap';
import { api } from '../services/api';
import useLocation from '../hooks/useLocation';

const ModernDashboard = ({ setAuth }) => {
    const [activeTab, setActiveTab] = useState('Dashboard');
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [riderId] = useState(localStorage.getItem('user_id') || 'R 2847');
    const { location: currentLocation } = useLocation();

    const sideBarItems = [
        { name: 'Dashboard', icon: FiActivity, badge: null },
        { name: 'Route Map', icon: FiMap, badge: null },
        { name: 'Deliveries', icon: FiPackage, badge: 12 },
        { name: 'Safety Zones', icon: FiShield, badge: null },
        { name: 'Alerts', icon: FiAlertTriangle, badge: 3 },
        { name: 'Analytics', icon: FiBarChart2, badge: null },
        { name: 'Fuel Metrics', icon: FiZap, badge: null },
        { name: 'Feedback', icon: FiMessageSquare, badge: null },
        { name: 'Settings', icon: FiSettings, badge: null },
    ];

    const stats = [
        { label: 'Active Deliveries', value: '12', subValue: '4 in transit', trend: '+8% vs last week', icon: FiPackage, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
        { label: 'Safety Score', value: '87%', subValue: 'Above average', trend: '+5% vs last week', icon: FiShield, color: 'text-blue-500', bg: 'bg-blue-500/10' },
        { label: 'Fuel Saved', value: '24.5L', subValue: 'This week', trend: '+12% vs last week', icon: FiZap, color: 'text-amber-500', bg: 'bg-amber-500/10' },
        { label: 'Avg. Delivery Time', value: '18 min', subValue: 'Target: 20 min', trend: '+3% vs last week', icon: FiClock, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
    ];

    return (
        <div className="flex h-screen dark-dashboard overflow-hidden font-['Inter']">
            {/* Sidebar */}
            <aside className={`${isSidebarOpen ? 'w-64' : 'w-20'} bg-[#090e16] border-r border-white/5 transition-all duration-300 flex flex-col z-30`}>
                <div className="p-6 flex items-center gap-3">
                    <div className="w-10 h-10 bg-emerald-500/20 rounded-xl flex items-center justify-center border border-emerald-500/30">
                        <FiShield className="text-emerald-500 text-xl" />
                    </div>
                    {isSidebarOpen && (
                        <div>
                            <h1 className="font-bold text-lg text-white leading-tight">SmartShield</h1>
                            <p className="text-[10px] text-gray-500 tracking-widest uppercase">Trust Route</p>
                        </div>
                    )}
                </div>

                <nav className="flex-1 mt-4 px-3 space-y-1">
                    {sideBarItems.map((item) => (
                        <button
                            key={item.name}
                            onClick={() => setActiveTab(item.name)}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${activeTab === item.name
                                    ? 'sidebar-item-active'
                                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                                }`}
                        >
                            <item.icon className={`text-lg transition-colors ${activeTab === item.name ? 'text-emerald-500' : 'group-hover:text-emerald-400'}`} />
                            {isSidebarOpen && (
                                <span className="flex-1 text-left text-sm font-medium">{item.name}</span>
                            )}
                            {isSidebarOpen && item.badge && (
                                <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${item.name === 'Alerts' ? 'bg-orange-500/20 text-orange-500' : 'bg-emerald-500/20 text-emerald-500'
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
                <header className="h-20 bg-[#0b0f1a]/80 backdrop-blur-md border-b border-white/5 flex items-center justify-between px-8 z-20">
                    <div className="flex items-center gap-4 flex-1 max-w-xl">
                        <div className="relative w-full">
                            <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" />
                            <input
                                type="text"
                                placeholder="Search deliveries, routes, zones..."
                                className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 pl-11 pr-4 text-sm focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-all"
                            />
                        </div>
                    </div>

                    <div className="flex items-center gap-6">
                        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-[10px] font-bold text-emerald-500">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                            SYSTEM ACTIVE
                        </div>

                        <div className="flex items-center gap-4 text-gray-400 relative">
                            <button className="hover:text-white transition-colors relative">
                                <FiBell className="text-xl" />
                                <span className="absolute -top-1 -right-1 w-2 h-2 bg-orange-500 rounded-full border-2 border-[#0b0f1a]" />
                            </button>
                            <button className="hover:text-white transition-colors">
                                <FiSettings className="text-xl" />
                            </button>
                        </div>

                        <div className="flex items-center gap-3 pl-6 border-l border-white/10">
                            <div className="text-right hidden sm:block">
                                <p className="text-sm font-bold text-white leading-none">Priya Kumar</p>
                                <p className="text-[10px] text-gray-500 mt-1 uppercase tracking-wider">Rider ID: {riderId}</p>
                            </div>
                            <div className="w-10 h-10 bg-emerald-500/20 rounded-xl flex items-center justify-center text-emerald-500 border border-emerald-500/20">
                                <FiUser className="text-xl" />
                            </div>
                        </div>
                    </div>
                </header>

                <main className="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar">
                    {activeTab === 'Dashboard' && (
                        <div className="space-y-8 animate-in fade-in duration-500">
                            {/* Stats Grid */}
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                                {stats.map((s, i) => (
                                    <div key={i} className="premium-card p-6 flex flex-col justify-between">
                                        <div className="flex justify-between items-start mb-4">
                                            <div className="space-y-1">
                                                <p className="text-gray-500 text-xs font-bold uppercase tracking-wider">{s.label}</p>
                                                <p className="text-3xl font-black text-white">{s.value}</p>
                                                <p className="text-[10px] text-gray-400 font-medium">{s.subValue}</p>
                                            </div>
                                            <div className={`p-3 rounded-xl ${s.bg} ${s.color}`}>
                                                <s.icon className="text-xl" />
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <span className="text-[10px] font-black text-emerald-500">{s.trend}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {/* Main Grid: Map & Details */}
                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                                {/* Left Section: Active Route Map */}
                                <div className="lg:col-span-2 space-y-6">
                                    <div className="premium-card p-6 bg-[#111827]/40 relative overflow-hidden flex flex-col min-h-[500px]">
                                        <div className="flex items-center justify-between mb-6 z-10">
                                            <h3 className="text-lg font-bold text-white flex items-center gap-2">
                                                <FiNavigation className="text-emerald-500" />
                                                Active Route
                                            </h3>
                                            <div className="flex items-center gap-2">
                                                <div className="bg-amber-500/10 border border-amber-500/20 px-3 py-1.5 rounded-lg flex flex-col items-center">
                                                    <span className="text-[10px] text-amber-500 font-bold uppercase tracking-tighter leading-none">Route</span>
                                                    <span className="text-lg font-black text-amber-500 leading-none mt-0.5">78</span>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Map Visualization */}
                                        <div className="flex-1 rounded-2xl overflow-hidden border border-white/5 relative bg-[#090e16]">
                                            <div className="absolute inset-0 z-0">
                                                <RouteMap variant="dark-minimal" />
                                            </div>

                                            {/* Map Controls */}
                                            <div className="absolute right-4 top-4 flex flex-col gap-2 z-10">
                                                <button className="w-10 h-10 bg-[#111827] border border-white/10 rounded-lg flex items-center justify-center text-white hover:bg-white/5 transition-all shadow-lg">
                                                    <FiPlus />
                                                </button>
                                                <button className="w-10 h-10 bg-[#111827] border border-white/10 rounded-lg flex items-center justify-center text-white hover:bg-white/5 transition-all shadow-lg">
                                                    <FiMinus />
                                                </button>
                                                <button className="w-10 h-10 bg-[#111827] border border-white/10 rounded-lg flex items-center justify-center text-white hover:bg-white/5 transition-all shadow-lg">
                                                    <FiTarget />
                                                </button>
                                                <button className="mt-4 w-10 h-10 bg-emerald-500 border border-emerald-400 rounded-lg flex items-center justify-center text-white hover:bg-emerald-600 transition-all shadow-lg shadow-emerald-500/20">
                                                    <FiLayers />
                                                </button>
                                            </div>

                                            {/* Legend */}
                                            <div className="absolute bottom-4 left-4 z-10 flex gap-4 bg-[#090e16]/80 backdrop-blur-md px-3 py-2 rounded-lg border border-white/5">
                                                <div className="flex items-center gap-2">
                                                    <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                                                    <span className="text-[10px] text-gray-400 font-bold uppercase">Safe</span>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <div className="w-2.5 h-2.5 rounded-full bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]" />
                                                    <span className="text-[10px] text-gray-400 font-bold uppercase">Caution</span>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <div className="w-2.5 h-2.5 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]" />
                                                    <span className="text-[10px] text-gray-400 font-bold uppercase">Alert</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Delivery Queue Section (From Image 3) */}
                                    <div className="premium-card p-6">
                                        <div className="flex items-center justify-between mb-6">
                                            <h3 className="text-lg font-bold text-white flex items-center gap-2">
                                                <FiPackage className="text-emerald-500" />
                                                Delivery Queue
                                            </h3>
                                            <span className="text-xs text-gray-500">4 deliveries</span>
                                        </div>

                                        <div className="space-y-4">
                                            {[
                                                { id: '#DEL-2847', name: 'Rajesh Sharma', address: '42, Anna Nagar East, Chennai 600102', time: '12 mins', dist: '3.2 km', score: 88, status: 'In Transit', priority: 'High', priorityColor: 'text-amber-500 bg-amber-500/10 border-amber-500/20' },
                                                { id: '#DEL-2848', name: 'Lakshmi Venkat', address: '15/3, T. Nagar Main Road, Chennai 600017', time: '25 mins', dist: '5.8 km', score: 72, status: 'Pending', priority: 'Normal', priorityColor: 'text-blue-500 bg-blue-500/10 border-blue-500/20' },
                                                { id: '#DEL-2849', name: 'Amit Singh', address: '8, Adyar Bridge Road, Chennai 600020', time: '40 mins', dist: '8.4 km', score: 91, status: 'Pending', priority: 'Urgent', priorityColor: 'text-red-500 bg-red-500/10 border-red-500/20' },
                                            ].map((del, idx) => (
                                                <div key={idx} className="bg-white/5 border border-white/5 rounded-2xl p-4 hover:border-white/10 transition-all group">
                                                    <div className="flex items-start justify-between mb-4">
                                                        <div className="flex items-center gap-3">
                                                            <div className="text-[10px] font-bold text-gray-500 uppercase tracking-tighter">{del.id}</div>
                                                            <div className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${del.priorityColor}`}>{del.priority}</div>
                                                            <div className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-500">{del.status}</div>
                                                        </div>
                                                        <div className="text-2xl font-black text-emerald-500 group-hover:drop-shadow-[0_0_8px_rgba(16,185,129,0.3)] transition-all">
                                                            {del.score}
                                                        </div>
                                                    </div>
                                                    <div className="flex justify-between items-end">
                                                        <div>
                                                            <h4 className="font-bold text-white text-base mb-1">{del.name}</h4>
                                                            <div className="flex items-center gap-2 text-gray-500 text-xs mb-3">
                                                                <FiMapPin className="text-[10px]" />
                                                                {del.address}
                                                            </div>
                                                            <div className="flex items-center gap-4">
                                                                <div className="flex items-center gap-1.5 text-xs text-white/80 font-medium">
                                                                    <FiClock className="text-emerald-500" />
                                                                    {del.time}
                                                                </div>
                                                                <div className="flex items-center gap-1.5 text-xs text-white/80 font-medium">
                                                                    <FiNavigation className="text-emerald-500" />
                                                                    {del.dist}
                                                                </div>
                                                            </div>
                                                        </div>
                                                        <button className="p-2 rounded-xl bg-white/5 text-gray-400 hover:text-white hover:bg-white/10 transition-all">
                                                            <FiChevronRight size={20} />
                                                        </button>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>

                                {/* Right Section: Quick Actions & Weather & Zone Safety */}
                                <div className="space-y-6">
                                    {/* Quick Actions */}
                                    <div className="premium-card p-6">
                                        <h3 className="text-lg font-bold text-white mb-6">Quick Actions</h3>
                                        <div className="grid grid-cols-2 gap-4">
                                            <button className="flex flex-col items-center justify-center p-4 rounded-2xl bg-emerald-500 hover:bg-emerald-600 text-white transition-all group">
                                                <FiNavigation className="text-2xl mb-2 group-hover:scale-110 transition-transform" />
                                                <span className="text-[10px] font-black uppercase tracking-tight">Optimize Route</span>
                                                <span className="text-[8px] opacity-70">AI-powered</span>
                                            </button>
                                            <button className="flex flex-col items-center justify-center p-4 rounded-2xl bg-[#111827] border border-white/5 hover:border-emerald-500/30 text-emerald-500 transition-all group">
                                                <FiShield className="text-2xl mb-2 group-hover:scale-110 transition-transform" />
                                                <span className="text-[10px] font-black uppercase tracking-tight text-white">Find Safe Zone</span>
                                                <span className="text-[8px] text-gray-500">Nearest spot</span>
                                            </button>
                                            <button className="flex flex-col items-center justify-center p-4 rounded-2xl bg-[#111827] border border-white/5 hover:border-emerald-500/30 text-gray-400 transition-all group">
                                                <FiAlertTriangle className="text-2xl mb-2 group-hover:scale-110 transition-transform" />
                                                <span className="text-[10px] font-black uppercase tracking-tight text-white">Report Issue</span>
                                                <span className="text-[8px] text-gray-500">Safety concern</span>
                                            </button>
                                            <button className="flex flex-col items-center justify-center p-4 rounded-2xl bg-orange-600 hover:bg-orange-700 text-white transition-all group shadow-lg shadow-orange-600/20">
                                                <FiPhone className="text-2xl mb-2 group-hover:scale-110 transition-transform" />
                                                <span className="text-[10px] font-black uppercase tracking-tight">Emergency</span>
                                                <span className="text-[8px] opacity-70">Quick dial</span>
                                            </button>
                                        </div>
                                    </div>

                                    {/* Zone Safety (From Image 3) */}
                                    <div className="premium-card p-6">
                                        <div className="flex items-center justify-between mb-6">
                                            <h3 className="text-lg font-bold text-white flex items-center gap-2">
                                                <FiShield className="text-emerald-500" />
                                                Zone Safety
                                            </h3>
                                            <span className="text-[10px] text-gray-500 font-medium">Updated 5 min ago</span>
                                        </div>
                                        <div className="space-y-4">
                                            {[
                                                { name: 'T. Nagar', incidents: '12 incidents', trend: 'down', score: 72, color: 'bg-amber-500' },
                                                { name: 'Anna Nagar', incidents: '3 incidents', trend: 'neutral', score: 88, color: 'bg-emerald-500' },
                                                { name: 'Velachery', incidents: '28 incidents', trend: 'up', score: 45, color: 'bg-red-500' },
                                                { name: 'Adyar', incidents: '2 incidents', trend: 'down', score: 91, color: 'bg-emerald-500' },
                                            ].map((zone, idx) => (
                                                <div key={idx} className="space-y-2">
                                                    <div className="flex justify-between items-end">
                                                        <div>
                                                            <h4 className="text-sm font-bold text-white leading-none">{zone.name}</h4>
                                                            <p className="text-[10px] text-gray-500 mt-1 flex items-center gap-1">
                                                                {zone.incidents}
                                                                <span className={zone.trend === 'down' ? 'text-emerald-500' : zone.trend === 'up' ? 'text-red-500' : 'text-gray-400'}>
                                                                    {zone.trend === 'down' ? '↓' : zone.trend === 'up' ? '↑' : '•'}
                                                                </span>
                                                            </p>
                                                        </div>
                                                        <div className="text-lg font-black text-white/50">{zone.score}</div>
                                                    </div>
                                                    <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                                                        <div
                                                            className={`h-full rounded-full transition-all duration-1000 ${zone.color}`}
                                                            style={{ width: `${zone.score}%` }}
                                                        />
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Weather Conditions */}
                                    <div className="premium-card p-6 bg-gradient-to-br from-[#111827] to-[#090e16]">
                                        <div className="flex justify-between items-start mb-4">
                                            <h3 className="text-lg font-bold text-white leading-none">Weather Conditions</h3>
                                            <span className="text-[10px] px-2 py-0.5 bg-emerald-500/10 text-emerald-500 rounded-full font-bold">Low Impact</span>
                                        </div>
                                        <div className="flex items-center gap-4 mb-6">
                                            <div className="w-16 h-16 flex items-center justify-center text-amber-500 text-5xl">
                                                ☁️
                                            </div>
                                            <div>
                                                <div className="text-4xl font-black text-white leading-none">28°C</div>
                                                <div className="text-xs text-gray-500 font-medium">Partly Cloudy</div>
                                            </div>
                                        </div>
                                        <div className="grid grid-cols-3 gap-2">
                                            <div className="bg-white/5 p-2 rounded-xl text-center">
                                                <FiDroplet className="mx-auto text-blue-400 mb-1" />
                                                <div className="text-[10px] text-gray-500 uppercase tracking-tighter">Humidity</div>
                                                <div className="text-xs font-bold text-white">72%</div>
                                            </div>
                                            <div className="bg-white/5 p-2 rounded-xl text-center">
                                                <FiWind className="mx-auto text-emerald-400 mb-1" />
                                                <div className="text-[10px] text-gray-500 uppercase tracking-tighter">Wind</div>
                                                <div className="text-xs font-bold text-white">12 km/h</div>
                                            </div>
                                            <div className="bg-white/5 p-2 rounded-xl text-center">
                                                <FiEye className="mx-auto text-purple-400 mb-1" />
                                                <div className="text-[10px] text-gray-500 uppercase tracking-tighter">Visibility</div>
                                                <div className="text-xs font-bold text-white">Good</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                    {activeTab === 'Route Map' && <RouteMap />}
                </main>
            </div>
        </div>
    );
};

export default ModernDashboard;
