import React, { useState, useEffect } from 'react';
import {
  FiShield, FiActivity, FiUsers, FiCpu, FiBarChart2,
  FiAlertTriangle, FiNavigation, FiSettings, FiLogOut,
  FiBell, FiSearch, FiMonitor, FiMap, FiCheckCircle
} from 'react-icons/fi';
import Analytics from './Analytics';
import RouteMap from './RouteMap';
import LiveTracking from './LiveTracking';
import TrainingCenter from './TrainingCenter';
import { api } from '../services/api';

const AdminDashboard = ({ setAuth }) => {
  const [activeTab, setActiveTab] = useState('Overview');
  const [systemHealth, setSystemHealth] = useState('stable'); // stable, warning, critical
  const [stats, setStats] = useState({
    activeDrivers: 42,
    fleetUtilization: '89%',
    safetyScore: 94,
    activeAlerts: 3
  });

  const menuItems = [
    { id: 'Overview', icon: FiMonitor, label: 'System Overview' },
    { id: 'Fleet', icon: FiMap, label: 'Fleet Map' },
    { id: 'Users', icon: FiUsers, label: 'User Management' },
    { id: 'Analytics', icon: FiBarChart2, label: 'Advanced Analytics' },
    { id: 'Training', icon: FiCpu, label: 'ML Training Center' },
    { id: 'Reports', icon: FiAlertTriangle, label: 'Incident Reports' }
  ];

  return (
    <div className="flex h-screen bg-[#0F172A] text-slate-300 font-['Inter'] overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-[#1E293B] border-r border-slate-800 flex flex-col z-30">
        <div className="p-6 flex items-center gap-3">
          <div className="w-10 h-10 bg-emerald-500 rounded-xl flex items-center justify-center text-white shadow-lg shadow-emerald-500/20">
            <FiShield size={24} />
          </div>
          <div>
            <h1 className="text-white font-bold leading-none">SmartShield</h1>
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mt-1">Admin Command</p>
          </div>
        </div>

        <nav className="flex-1 px-4 py-6 space-y-1">
          {menuItems.map(item => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-semibold text-sm ${activeTab === item.id
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800/50'
                }`}
            >
              <item.icon size={18} />
              {item.label}
            </button>
          ))}
        </nav>

        <div className="p-6 mt-auto">
          <div className="p-4 bg-slate-800/50 rounded-2xl border border-slate-700/50">
            <div className="flex items-center justify-between mb-3">
              <span className="text-[10px] font-bold text-slate-500 uppercase">System Status</span>
              <div className="flex gap-1">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
              </div>
            </div>
            <p className="text-xs font-bold text-white">All Nodes Stable</p>
            <p className="text-[10px] text-slate-500 mt-1">v2.4.0 • Enterprise</p>
          </div>

          <button
            onClick={() => {
              localStorage.removeItem('auth_token');
              setAuth(false);
            }}
            className="w-full flex items-center gap-3 px-4 py-3 mt-4 text-slate-500 hover:text-rose-400 transition-colors text-sm font-semibold"
          >
            <FiLogOut /> Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 relative">
        {/* Header */}
        <header className="h-20 bg-[#1E293B]/50 backdrop-blur-md border-b border-slate-800 flex items-center justify-between px-8 z-20">
          <div className="flex items-center gap-4 flex-1 max-w-xl">
            <div className="relative w-full">
              <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="text"
                placeholder="Search system logs, drivers, or alerts..."
                className="w-full bg-[#0F172A] border border-slate-700 rounded-xl py-2.5 pl-11 pr-4 text-sm focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/10 transition-all text-slate-200"
              />
            </div>
          </div>

          <div className="flex items-center gap-6">
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-[10px] font-bold text-emerald-400 uppercase tracking-widest">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              Live Network
            </div>
            <button className="text-slate-400 hover:text-white transition-colors relative">
              <FiBell size={20} />
              <span className="absolute -top-1 -right-1 w-2 h-2 bg-rose-500 rounded-full border-2 border-[#1E293B]"></span>
            </button>
            <div className="w-px h-8 bg-slate-800"></div>
            <div className="flex items-center gap-3">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-bold text-white leading-none">Admin Control</p>
                <p className="text-[10px] text-slate-500 mt-1 uppercase">Root Authority</p>
              </div>
              <div className="w-10 h-10 bg-slate-800 rounded-xl flex items-center justify-center text-slate-400 border border-slate-700">
                <FiSettings />
              </div>
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-8">
          {activeTab === 'Overview' && (
            <div className="space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-700">
              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-[#1E293B] p-6 rounded-3xl border border-slate-800 hover:border-emerald-500/30 transition-all group">
                  <div className="flex items-center justify-between mb-4">
                    <div className="p-3 bg-emerald-500/10 text-emerald-500 rounded-2xl group-hover:scale-110 transition-transform">
                      <FiUsers size={24} />
                    </div>
                    <span className="text-xs font-bold text-emerald-500">+4 ready</span>
                  </div>
                  <p className="text-slate-500 text-xs font-bold uppercase tracking-widest">Active Fleet</p>
                  <p className="text-3xl font-black text-white mt-1">{stats.activeDrivers}</p>
                </div>
                <div className="bg-[#1E293B] p-6 rounded-3xl border border-slate-800 hover:border-blue-500/30 transition-all group">
                  <div className="flex items-center justify-between mb-4">
                    <div className="p-3 bg-blue-500/10 text-blue-500 rounded-2xl group-hover:scale-110 transition-transform">
                      <FiActivity size={24} />
                    </div>
                    <span className="text-xs font-bold text-blue-500">Live</span>
                  </div>
                  <p className="text-slate-500 text-xs font-bold uppercase tracking-widest">Utilization</p>
                  <p className="text-3xl font-black text-white mt-1">{stats.fleetUtilization}</p>
                </div>
                <div className="bg-[#1E293B] p-6 rounded-3xl border border-slate-800 hover:border-amber-500/30 transition-all group">
                  <div className="flex items-center justify-between mb-4">
                    <div className="p-3 bg-amber-500/10 text-amber-500 rounded-2xl group-hover:scale-110 transition-transform">
                      <FiShield size={24} />
                    </div>
                    <span className="text-xs font-bold text-emerald-500">Safe</span>
                  </div>
                  <p className="text-slate-500 text-xs font-bold uppercase tracking-widest">Avg Safety</p>
                  <p className="text-3xl font-black text-white mt-1">{stats.safetyScore}%</p>
                </div>
                <div className="bg-[#1E293B] p-6 rounded-3xl border border-slate-800 hover:border-rose-500/30 transition-all group">
                  <div className="flex items-center justify-between mb-4">
                    <div className="p-3 bg-rose-500/10 text-rose-500 rounded-2xl group-hover:scale-110 transition-transform">
                      <FiAlertTriangle size={24} />
                    </div>
                    <span className="text-xs font-bold text-rose-500">Urgent</span>
                  </div>
                  <p className="text-slate-500 text-xs font-bold uppercase tracking-widest">Active Alerts</p>
                  <p className="text-3xl font-black text-white mt-1">{stats.activeAlerts}</p>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 space-y-8">
                  {/* Charts Section */}
                  <div className="bg-[#1E293B] p-8 rounded-[2.5rem] border border-slate-800 shadow-2xl">
                    <div className="flex items-center justify-between mb-8">
                      <div>
                        <h3 className="text-xl font-bold text-white">Operational Trends</h3>
                        <p className="text-slate-500 text-sm">Fleet performance over the last 24 hours</p>
                      </div>
                      <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-xs font-bold rounded-xl transition-all border border-slate-700">Export Report</button>
                    </div>
                    <div className="h-[400px]">
                      <Analytics />
                    </div>
                  </div>

                  {/* Fleet Activity */}
                  <div className="bg-[#1E293B] p-8 rounded-[2.5rem] border border-slate-800">
                    <h3 className="text-lg font-bold text-white mb-6">Recent Fleet Events</h3>
                    <div className="space-y-4">
                      {[1, 2, 3].map(i => (
                        <div key={i} className="flex items-center justify-between p-4 bg-[#0F172A] rounded-2xl border border-slate-800 group hover:border-emerald-500/30 transition-all">
                          <div className="flex items-center gap-4">
                            <div className="w-10 h-10 bg-slate-800 rounded-xl flex items-center justify-center text-emerald-500">
                              <FiCheckCircle size={20} />
                            </div>
                            <div>
                              <p className="font-bold text-white">Route Optimized - R#442</p>
                              <p className="text-xs text-slate-500">Safety factor increased by 14%</p>
                            </div>
                          </div>
                          <span className="text-[10px] font-bold text-slate-600 uppercase">2m ago</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="space-y-8">
                  {/* Incident Monitor */}
                  <div className="bg-[#1E293B] p-8 rounded-[2.5rem] border border-slate-800 shadow-2xl">
                    <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
                      <FiActivity className="text-rose-500" />
                      Incident Monitor
                    </h3>
                    <div className="space-y-4">
                      <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-2xl">
                        <div className="flex items-center gap-3 text-rose-500 mb-2">
                          <FiAlertTriangle size={18} />
                          <span className="text-xs font-black uppercase tracking-widest">High Risk Alert</span>
                        </div>
                        <p className="text-sm font-bold text-white">Abnormal vibration - Bike #22</p>
                        <p className="text-xs text-rose-300/70 mt-1">Anna Salai • Immediate check required</p>
                      </div>
                      <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-2xl">
                        <div className="flex items-center gap-3 text-amber-500 mb-2">
                          <FiAlertTriangle size={18} />
                          <span className="text-xs font-black uppercase tracking-widest">Weather Warning</span>
                        </div>
                        <p className="text-sm font-bold text-white">Heavy rain forecast - Zone 4</p>
                        <p className="text-xs text-amber-300/70 mt-1">Expected in 15 mins</p>
                      </div>
                    </div>
                    <button className="w-full mt-6 py-4 bg-slate-800 hover:bg-slate-700 text-white rounded-2xl text-sm font-bold transition-all border border-slate-700">View All Alerts</button>
                  </div>

                  {/* Quick Actions */}
                  <div className="bg-[#1E293B] p-8 rounded-[2.5rem] border border-slate-800">
                    <h3 className="text-lg font-bold text-white mb-6">Tools</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <button className="flex flex-col items-center justify-center gap-2 p-4 bg-slate-800 rounded-3xl hover:bg-slate-700 transition-all border border-slate-700">
                        <FiMonitor className="text-blue-500" />
                        <span className="text-[10px] font-bold uppercase">Broadcase</span>
                      </button>
                      <button className="flex flex-col items-center justify-center gap-2 p-4 bg-slate-800 rounded-3xl hover:bg-slate-700 transition-all border border-slate-700">
                        <FiSettings className="text-slate-400" />
                        <span className="text-[10px] font-bold uppercase">Sys Config</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'Fleet' && (
            <div className="h-full rounded-[2.5rem] overflow-hidden border border-slate-800 bg-[#1E293B]">
              <LiveTracking />
            </div>
          )}

          {activeTab === 'Analytics' && (
            <div className="bg-[#1E293B] p-8 rounded-[2.5rem] border border-slate-800 h-full">
              <Analytics />
            </div>
          )}

          {activeTab === 'Training' && (
            <div className="bg-[#1E293B] p-8 rounded-[2.5rem] border border-slate-800 h-full overflow-y-auto">
              <TrainingCenter />
            </div>
          )}

          {(activeTab === 'Users' || activeTab === 'Reports') && (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <div className="p-8 bg-[#1E293B] rounded-[3rem] border border-slate-800 shadow-2xl">
                <FiMonitor size={48} className="text-slate-700 mx-auto mb-6" />
                <h3 className="text-2xl font-black text-white">{activeTab} Interface</h3>
                <p className="text-slate-500 mt-2 max-w-xs">Connecting to secure data stream... Full panel deployment in progress.</p>
                <button className="mt-8 px-8 py-3 bg-emerald-500 text-white rounded-2xl font-bold shadow-lg shadow-emerald-500/20 active:scale-95 transition-all">Retry Link</button>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default AdminDashboard;
