import React, { useState, useEffect } from 'react';
import {
  FiShield, FiActivity, FiUsers, FiCpu, FiBarChart2,
  FiAlertTriangle, FiNavigation, FiSettings, FiLogOut,
  FiBell, FiSearch, FiMonitor, FiMap, FiCheckCircle,
  FiTrash2, FiToggleLeft, FiToggleRight, FiRefreshCw,
  FiUserCheck, FiUserX, FiFilter
} from 'react-icons/fi';
import Analytics from './Analytics';
import RouteMap from './RouteMap';
import LiveTracking from './LiveTracking';
import TrainingCenter from './TrainingCenter';
import ModelPerformance from './ModelPerformance';
import AIReportSummary from './AIReportSummary';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';

const AdminDashboard = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('Overview');
  const [systemHealth, setSystemHealth] = useState('stable');
  const [stats, setStats] = useState({
    activeDrivers: 42,
    fleetUtilization: '89%',
    safetyScore: 94,
    activeAlerts: 3
  });

  // User Management state
  const [allUsers, setAllUsers] = useState([]);
  const [usersLoading, setUsersLoading] = useState(false);
  const [usersError, setUsersError] = useState('');
  const [userSearch, setUserSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');

  const [allAlerts, setAllAlerts] = useState([]);
  const [allFeedback, setAllFeedback] = useState([]);

  const fetchReports = async () => {
    try {
      const alerts = await api.get('/safety/alerts');
      setAllAlerts(Array.isArray(alerts) ? alerts : []);
      const feedbacks = await api.get('/feedback/all');
      setAllFeedback(feedbacks.data || []);
    } catch (e) {
      console.error("Failed to load reports", e);
    }
  };

  const fetchAllUsers = async () => {
    setUsersLoading(true);
    setUsersError('');
    try {
      // api interceptor already unwraps response.data
      const data = await api.get('/users/all');
      setAllUsers(Array.isArray(data) ? data : []);
    } catch (e) {
      setUsersError(e.response?.data?.detail || 'Failed to load users. Make sure you are logged in as Admin.');
    } finally {
      setUsersLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'Users') fetchAllUsers();
    if (activeTab === 'Reports') fetchReports();
  }, [activeTab]);

  const handleToggleStatus = async (u) => {
    const newStatus = u.status === 'active' ? 'inactive' : 'active';
    try {
      await api.patch(`/users/${u.id}/status`, { status: newStatus });
      setAllUsers(prev => prev.map(x => x.id === u.id ? { ...x, status: newStatus } : x));
    } catch (e) {
      alert(e.response?.data?.detail || 'Failed to update status');
    }
  };

  const handleDeleteUser = async (u) => {
    if (!window.confirm(`Delete user "${u.full_name || u.username}"? This cannot be undone.`)) return;
    try {
      await api.delete(`/users/${u.id}`);
      setAllUsers(prev => prev.filter(x => x.id !== u.id));
    } catch (e) {
      alert(e.response?.data?.detail || 'Failed to delete user');
    }
  };

  const ROLE_COLORS = {
    admin: 'bg-purple-100 text-purple-700 border-purple-200',
    super_admin: 'bg-rose-100   text-rose-700   border-rose-200',
    dispatcher: 'bg-blue-100   text-blue-700   border-blue-200',
    driver: 'bg-amber-100  text-amber-700  border-amber-200',
    rider: 'bg-indigo-100 text-indigo-700 border-indigo-200',
    customer: 'bg-emerald-100 text-emerald-700 border-emerald-200',
  };

  const filteredUsers = allUsers.filter(u => {
    const matchRole = roleFilter === 'all' || u.role === roleFilter;
    const q = userSearch.toLowerCase();
    const matchSearch = !q ||
      (u.full_name || '').toLowerCase().includes(q) ||
      (u.email || '').toLowerCase().includes(q) ||
      (u.role || '').toLowerCase().includes(q);
    return matchRole && matchSearch;
  });

  const menuItems = [
    { id: 'Overview', icon: FiMonitor, label: 'System Overview' },
    { id: 'Optimizer', icon: FiNavigation, label: 'Route Optimizer' },
    { id: 'Fleet', icon: FiMap, label: 'Fleet Map' },
    { id: 'Users', icon: FiUsers, label: 'User Management' },
    { id: 'Analytics', icon: FiBarChart2, label: 'Advanced Analytics' },
    { id: 'Training', icon: FiCpu, label: 'ML Training Center' },
    { id: 'Performance', icon: FiActivity, label: 'AI Monitoring' },
    { id: 'AIReports', icon: FiCpu, label: 'AI Reports' },
    { id: 'Reports', icon: FiAlertTriangle, label: 'Incident Reports' }
  ];

  return (
    <div className="flex h-screen bg-slate-50 text-slate-600 font-['Inter'] overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-slate-200 flex flex-col z-30 shadow-sm">
        <div className="p-6 flex items-center gap-3">
          <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
            <FiShield size={24} />
          </div>
          <div>
            <h1 className="text-slate-900 font-bold leading-none">SmartShield</h1>
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mt-1">Admin Command</p>
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
            <p className="text-[10px] text-indigo-600 font-bold uppercase tracking-wider mt-0.5">{user?.role?.replace('_', ' ')}</p>
          </div>
          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200">
            <div className="flex items-center justify-between mb-3">
              <span className="text-[10px] font-bold text-slate-400 uppercase">System Status</span>
              <div className="flex gap-1">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
              </div>
            </div>
            <p className="text-xs font-bold text-slate-900">All Nodes Stable</p>
            <p className="text-[10px] text-slate-400 mt-1">v2.4.0 • Enterprise</p>
          </div>

          <button
            onClick={logout}
            className="w-full flex items-center gap-3 px-4 py-3 mt-4 text-slate-400 hover:text-rose-500 transition-colors text-sm font-semibold"
          >
            <FiLogOut /> Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 relative">
        {/* Header */}
        <header className="h-20 bg-white/80 backdrop-blur-md border-b border-slate-200 flex items-center justify-between px-8 z-20 sticky top-0">
          <div className="flex items-center gap-4 flex-1 max-w-xl">
            <div className="relative w-full">
              <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Search system logs, drivers, or alerts..."
                className="w-full bg-slate-50 border border-slate-200 rounded-xl py-2.5 pl-11 pr-4 text-sm focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/10 transition-all text-slate-900 placeholder:text-slate-400"
              />
            </div>
          </div>

          <div className="flex items-center gap-6">
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-50 border border-indigo-100 text-[10px] font-bold text-indigo-600 uppercase tracking-widest">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />
              Live Network
            </div>
            <button className="text-slate-400 hover:text-slate-900 transition-colors relative">
              <FiBell size={20} />
              <span className="absolute -top-1 -right-1 w-2 h-2 bg-rose-500 rounded-full border-2 border-white"></span>
            </button>
            <div className="w-px h-8 bg-slate-200"></div>
            <div className="flex items-center gap-3">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-bold text-slate-900 leading-none">{user?.full_name || user?.username || 'Admin'}</p>
                <p className="text-[10px] text-indigo-600 mt-1 uppercase font-bold tracking-tight">{user?.role?.replace('_', ' ') || 'Admin'}</p>
              </div>
              <div className="w-10 h-10 bg-indigo-100 rounded-xl flex items-center justify-center text-indigo-600 border border-indigo-200 shadow-sm font-bold">
                {(user?.full_name || user?.username || 'A')[0].toUpperCase()}
              </div>
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-8">
          {activeTab === 'Overview' && (
            <div className="space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-700">
              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white p-6 rounded-3xl border border-slate-200 hover:border-indigo-500/30 transition-all group shadow-sm">
                  <div className="flex items-center justify-between mb-4">
                    <div className="p-3 bg-indigo-50 text-indigo-600 rounded-2xl group-hover:scale-110 transition-transform">
                      <FiUsers size={24} />
                    </div>
                    <button
                      onClick={() => setActiveTab('Optimizer')}
                      className="text-[10px] font-bold text-indigo-600 bg-indigo-50 px-2 py-1 rounded-lg border border-indigo-100 hover:bg-indigo-600 hover:text-white transition-all"
                    >
                      Open Optimizer
                    </button>
                  </div>
                  <p className="text-slate-500 text-[10px] font-bold uppercase tracking-widest">Active Fleet</p>
                  <p className="text-3xl font-black text-slate-900 mt-1">{stats.activeDrivers}</p>
                </div>
                <div className="bg-white p-6 rounded-3xl border border-slate-200 hover:border-blue-500/30 transition-all group shadow-sm">
                  <div className="flex items-center justify-between mb-4">
                    <div className="p-3 bg-blue-50 text-blue-600 rounded-2xl group-hover:scale-110 transition-transform">
                      <FiActivity size={24} />
                    </div>
                    <span className="text-xs font-bold text-blue-600">Live</span>
                  </div>
                  <p className="text-slate-500 text-[10px] font-bold uppercase tracking-widest">Utilization</p>
                  <p className="text-3xl font-black text-slate-900 mt-1">{stats.fleetUtilization}</p>
                </div>
                <div className="bg-white p-6 rounded-3xl border border-slate-200 hover:border-amber-500/30 transition-all group shadow-sm">
                  <div className="flex items-center justify-between mb-4">
                    <div className="p-3 bg-amber-50 text-amber-600 rounded-2xl group-hover:scale-110 transition-transform">
                      <FiShield size={24} />
                    </div>
                    <span className="text-xs font-bold text-indigo-600">Safe</span>
                  </div>
                  <p className="text-slate-500 text-[10px] font-bold uppercase tracking-widest">Avg Safety</p>
                  <p className="text-3xl font-black text-slate-900 mt-1">{stats.safetyScore}%</p>
                </div>
                <div className="bg-white p-6 rounded-3xl border border-slate-200 hover:border-rose-500/30 transition-all group shadow-sm">
                  <div className="flex items-center justify-between mb-4">
                    <div className="p-3 bg-rose-50 text-rose-600 rounded-2xl group-hover:scale-110 transition-transform">
                      <FiAlertTriangle size={24} />
                    </div>
                    <span className="text-xs font-bold text-rose-600">Urgent</span>
                  </div>
                  <p className="text-slate-500 text-[10px] font-bold uppercase tracking-widest">Active Alerts</p>
                  <p className="text-3xl font-black text-slate-900 mt-1">{stats.activeAlerts}</p>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 space-y-8">
                  {/* Charts Section */}
                  <div className="bg-white p-8 rounded-[2.5rem] border border-slate-200 shadow-sm">
                    <div className="flex items-center justify-between mb-8">
                      <div>
                        <h3 className="text-xl font-bold text-slate-900">Operational Trends</h3>
                        <p className="text-slate-500 text-sm">Fleet performance over the last 24 hours</p>
                      </div>
                      <button className="px-4 py-2 bg-white hover:bg-slate-50 text-xs font-bold text-slate-600 rounded-xl transition-all border border-slate-200">Export Report</button>
                    </div>
                    <div className="mt-4 h-auto overflow-visible">
                      <Analytics hideTitle={true} />
                    </div>
                  </div>

                  {/* Fleet Activity */}
                  <div className="bg-white p-8 rounded-[2.5rem] border border-slate-200 shadow-sm">
                    <h3 className="text-lg font-bold text-slate-900 mb-6">Recent Fleet Events</h3>
                    <div className="space-y-4">
                      {[1, 2, 3].map(i => (
                        <div key={i} className="flex items-center justify-between p-4 bg-slate-50 rounded-2xl border border-transparent group hover:border-emerald-500/30 transition-all">
                          <div className="flex items-center gap-4">
                            <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center text-emerald-600 border border-slate-100 shadow-sm">
                              <FiCheckCircle size={20} />
                            </div>
                            <div>
                              <p className="font-bold text-slate-900">Route Optimized - R#442</p>
                              <p className="text-xs text-slate-500">Safety factor increased by 14%</p>
                            </div>
                          </div>
                          <span className="text-[10px] font-bold text-slate-400 uppercase">2m ago</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="space-y-8">
                  {/* Incident Monitor */}
                  <div className="bg-white p-8 rounded-[2.5rem] border border-slate-200 shadow-sm">
                    <h3 className="text-lg font-bold text-slate-900 mb-6 flex items-center gap-2">
                      <FiActivity className="text-rose-600" />
                      Incident Monitor
                    </h3>
                    <div className="space-y-4">
                      <div className="p-4 bg-rose-50 border border-rose-100 rounded-2xl">
                        <div className="flex items-center gap-3 text-rose-600 mb-2">
                          <FiAlertTriangle size={18} />
                          <span className="text-xs font-black uppercase tracking-widest">High Risk Alert</span>
                        </div>
                        <p className="text-sm font-bold text-slate-900">Abnormal vibration - Bike #22</p>
                        <p className="text-xs text-rose-500/70 mt-1">Anna Salai • Immediate check required</p>
                      </div>
                      <div className="p-4 bg-amber-50 border border-amber-100 rounded-2xl">
                        <div className="flex items-center gap-3 text-amber-600 mb-2">
                          <FiAlertTriangle size={18} />
                          <span className="text-xs font-black uppercase tracking-widest">Weather Warning</span>
                        </div>
                        <p className="text-sm font-bold text-slate-900">Heavy rain forecast - Zone 4</p>
                        <p className="text-xs text-amber-600/70 mt-1">Expected in 15 mins</p>
                      </div>
                    </div>
                    <button className="w-full mt-6 py-4 bg-slate-50 hover:bg-slate-100 text-slate-600 rounded-2xl text-sm font-bold transition-all border border-slate-200">View All Alerts</button>
                  </div>

                  {/* Quick Actions */}
                  <div className="bg-white p-8 rounded-[2.5rem] border border-slate-200 shadow-sm">
                    <h3 className="text-lg font-bold text-slate-900 mb-6">Tools</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <button className="flex flex-col items-center justify-center gap-2 p-4 bg-slate-50 rounded-3xl hover:bg-slate-100 transition-all border border-slate-200 group">
                        <FiMonitor className="text-blue-500 group-hover:scale-110 transition-transform" />
                        <span className="text-[10px] font-bold uppercase text-slate-500">Broadcast</span>
                      </button>
                      <button className="flex flex-col items-center justify-center gap-2 p-4 bg-slate-50 rounded-3xl hover:bg-slate-100 transition-all border border-slate-200 group">
                        <FiSettings className="text-slate-400 group-hover:scale-110 transition-transform" />
                        <span className="text-[10px] font-bold uppercase text-slate-500">Sys Config</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'Optimizer' && (
            <div className="flex-1 flex flex-col bg-white rounded-[2.5rem] p-8 border border-slate-200 shadow-sm min-h-[800px]">
              <div className="mb-6 flex justify-between items-end">
                <div>
                  <h2 className="text-3xl font-black text-slate-900 tracking-tight">AI Route Optimizer</h2>
                  <p className="text-slate-500 font-medium">Plan, compare and monitor safety-first paths for your fleet.</p>
                </div>
                <div className="flex gap-2">
                  <span className="px-3 py-1 bg-emerald-50 text-emerald-600 text-[10px] font-bold rounded-full border border-emerald-100">XGBoost Active</span>
                  <span className="px-3 py-1 bg-blue-50 text-blue-600 text-[10px] font-bold rounded-full border border-blue-100">RF Scoring Live</span>
                </div>
              </div>
              <div className="flex-1">
                <RouteMap />
              </div>
            </div>
          )}

          {activeTab === 'Fleet' && (
            <div className="h-full rounded-[2.5rem] overflow-hidden border border-slate-200 bg-white ring-8 ring-slate-100/50">
              <LiveTracking />
            </div>
          )}

          {activeTab === 'Analytics' && (
            <div className="bg-white p-8 rounded-[2.5rem] border border-slate-200 h-full shadow-sm">
              <Analytics />
            </div>
          )}

          {activeTab === 'Training' && (
            <div className="bg-white p-8 rounded-[2.5rem] border border-slate-200 h-full overflow-y-auto shadow-sm">
              <TrainingCenter />
            </div>
          )}

          {activeTab === 'Users' && (
            <div className="space-y-6">
              {/* Header row */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div>
                  <h2 className="text-2xl font-black text-slate-900">User Management</h2>
                  <p className="text-slate-500 text-sm mt-1">{allUsers.length} total accounts across all roles</p>
                </div>
                <button
                  onClick={fetchAllUsers}
                  className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm font-bold text-slate-600 hover:bg-slate-50 transition-all shadow-sm"
                >
                  <FiRefreshCw size={14} className={usersLoading ? 'animate-spin' : ''} /> Refresh
                </button>
              </div>

              {/* Filters */}
              <div className="flex flex-wrap gap-3">
                <div className="relative flex-1 min-w-[200px]">
                  <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={14} />
                  <input
                    type="text"
                    placeholder="Search by name or email..."
                    value={userSearch}
                    onChange={e => setUserSearch(e.target.value)}
                    className="w-full pl-9 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-indigo-500 shadow-sm"
                  />
                </div>
                <select
                  value={roleFilter}
                  onChange={e => setRoleFilter(e.target.value)}
                  className="px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 focus:outline-none focus:border-indigo-500 shadow-sm"
                >
                  <option value="all">All Roles</option>
                  <option value="admin">Admin</option>
                  <option value="dispatcher">Dispatcher</option>
                  <option value="driver">Driver</option>
                  <option value="rider">Rider</option>
                  <option value="customer">Customer</option>
                </select>
              </div>

              {/* Error */}
              {usersError && (
                <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl text-rose-700 text-sm font-medium">
                  ⚠️ {usersError}
                </div>
              )}

              {/* Table */}
              <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
                {usersLoading ? (
                  <div className="flex items-center justify-center py-20">
                    <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
                  </div>
                ) : filteredUsers.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-20 text-slate-400">
                    <FiUsers size={40} className="mb-4 opacity-30" />
                    <p className="font-bold">No users found</p>
                  </div>
                ) : (
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-slate-100 bg-slate-50">
                        <th className="text-left px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">User</th>
                        <th className="text-left px-4 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Role</th>
                        <th className="text-left px-4 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Status</th>
                        <th className="text-left px-4 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest hidden md:table-cell">Joined</th>
                        <th className="text-right px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50">
                      {filteredUsers.map(u => (
                        <tr key={u.id} className="hover:bg-slate-50/50 transition-colors group">
                          <td className="px-6 py-4">
                            <div className="flex items-center gap-3">
                              <div className={`w-9 h-9 rounded-xl flex items-center justify-center font-black text-sm border ${ROLE_COLORS[u.role] || 'bg-slate-100 text-slate-600 border-slate-200'}`}>
                                {(u.full_name || u.username || '?')[0].toUpperCase()}
                              </div>
                              <div>
                                <p className="font-bold text-slate-900 leading-none">{u.full_name || '—'}</p>
                                <p className="text-xs text-slate-400 mt-0.5">{u.email}</p>
                              </div>
                            </div>
                          </td>
                          <td className="px-4 py-4">
                            <span className={`px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-wider border ${ROLE_COLORS[u.role] || 'bg-slate-100 text-slate-600 border-slate-200'}`}>
                              {u.role?.replace('_', ' ')}
                            </span>
                          </td>
                          <td className="px-4 py-4">
                            <span className={`px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-wider border ${u.status === 'active'
                              ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                              : 'bg-slate-100 text-slate-500 border-slate-200'
                              }`}>
                              {u.status}
                            </span>
                          </td>
                          <td className="px-4 py-4 hidden md:table-cell">
                            <span className="text-xs text-slate-400">
                              {u.created_at ? new Date(u.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) : '—'}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex items-center justify-end gap-2">
                              <button
                                onClick={() => handleToggleStatus(u)}
                                title={u.status === 'active' ? 'Deactivate' : 'Activate'}
                                className={`p-2 rounded-xl border transition-all ${u.status === 'active'
                                  ? 'bg-amber-50 border-amber-200 text-amber-600 hover:bg-amber-100'
                                  : 'bg-emerald-50 border-emerald-200 text-emerald-600 hover:bg-emerald-100'
                                  }`}
                              >
                                {u.status === 'active' ? <FiUserX size={14} /> : <FiUserCheck size={14} />}
                              </button>
                              <button
                                onClick={() => handleDeleteUser(u)}
                                title="Delete user"
                                className="p-2 rounded-xl border bg-rose-50 border-rose-200 text-rose-500 hover:bg-rose-100 transition-all"
                              >
                                <FiTrash2 size={14} />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>

              {/* Summary cards */}
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                {['admin', 'dispatcher', 'driver', 'rider', 'customer'].map(role => {
                  const count = allUsers.filter(u => u.role === role).length;
                  return (
                    <div
                      key={role}
                      onClick={() => setRoleFilter(role)}
                      className={`p-4 bg-white rounded-2xl border cursor-pointer hover:shadow-md transition-all ${roleFilter === role ? 'border-indigo-400 shadow-md shadow-indigo-100' : 'border-slate-200'
                        }`}
                    >
                      <p className="text-2xl font-black text-slate-900">{count}</p>
                      <p className={`text-[10px] font-black uppercase tracking-widest mt-1 ${ROLE_COLORS[role]?.split(' ')[1] || 'text-slate-500'
                        }`}>{role}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {activeTab === 'Reports' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between mb-2">
                <div>
                  <h2 className="text-2xl font-black text-slate-900">Safety Incident Reports</h2>
                  <p className="text-slate-500 text-sm mt-1">Real-time SOS alerts and driver safety feedback</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={async () => {
                      try {
                        const alerts = await api.get('/safety/alerts');
                        setAllAlerts(alerts);
                        const feedbacks = await api.get('/feedback/all');
                        setAllFeedback(feedbacks.data || []);
                      } catch (e) {
                        console.error("Failed to refresh reports", e);
                      }
                    }}
                    className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm font-bold text-slate-600 hover:bg-slate-50 transition-all shadow-sm"
                  >
                    <FiRefreshCw size={14} /> Sync Feed
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Panic Alerts */}
                <div className="space-y-4">
                  <h3 className="text-sm font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></div>
                    Active Panic Alerts
                  </h3>
                  {allAlerts.length === 0 ? (
                    <div className="p-12 bg-white rounded-[2.5rem] border border-slate-200 text-center border-dashed">
                      <FiAlertTriangle className="mx-auto text-slate-100 mb-4" size={40} />
                      <p className="text-slate-400 font-bold">No active SOS signals</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {allAlerts.map(alert => (
                        <div key={alert.id} className={`p-5 bg-white rounded-3xl border ${alert.status === 'active' ? 'border-rose-200 shadow-lg shadow-rose-100' : 'border-slate-200'} transition-all`}>
                          <div className="flex justify-between items-start mb-3">
                            <div className="flex items-center gap-3">
                              <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${alert.status === 'active' ? 'bg-rose-100 text-rose-600' : 'bg-slate-100 text-slate-400'}`}>
                                <FiAlertTriangle />
                              </div>
                              <div>
                                <p className="font-bold text-slate-900">SOS Triggered</p>
                                <p className="text-[10px] text-slate-400 uppercase font-black tracking-widest">{new Date(alert.created_at).toLocaleString()}</p>
                              </div>
                            </div>
                            <span className={`px-2 py-1 rounded-full text-[10px] font-black uppercase tracking-wider ${alert.status === 'active' ? 'bg-rose-500 text-white' : 'bg-slate-100 text-slate-500'}`}>
                              {alert.status}
                            </span>
                          </div>
                          <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-50">
                            <div className="text-[10px] font-bold text-slate-500 uppercase">Rider: {alert.rider_id}</div>
                            <button
                              onClick={async () => {
                                if (alert.status === 'resolved') return;
                                const notes = window.prompt("Enter resolution notes:");
                                if (notes) {
                                  await api.post('/safety/panic-button/resolve', {
                                    alert_id: alert.id,
                                    rider_id: alert.rider_id,
                                    resolution_notes: notes
                                  });
                                  // Refresh
                                  const updated = await api.get('/safety/alerts');
                                  setAllAlerts(updated);
                                }
                              }}
                              className={`px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${alert.status === 'resolved' ? 'bg-slate-50 text-slate-300 cursor-not-allowed' : 'bg-emerald-600 text-white hover:bg-emerald-700 shadow-lg shadow-emerald-500/20'}`}
                            >
                              Resolve Issue
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Safety Feedback */}
                <div className="space-y-4">
                  <h3 className="text-sm font-black text-slate-400 uppercase tracking-widest">Driver Feedback</h3>
                  {allFeedback.length === 0 ? (
                    <div className="p-12 bg-white rounded-[2.5rem] border border-slate-200 text-center border-dashed">
                      <FiActivity className="mx-auto text-slate-100 mb-4" size={40} />
                      <p className="text-slate-400 font-bold">No feedback submitted yet</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {allFeedback.map(fb => (
                        <div key={fb.id} className="p-5 bg-white rounded-3xl border border-slate-200 hover:border-indigo-200 transition-all group">
                          <div className="flex justify-between items-start mb-2">
                            <div className="flex items-center gap-3">
                              <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-xs uppercase">
                                {fb.rider_id?.substring(0, 2)}
                              </div>
                              <p className="font-bold text-slate-800 text-sm">Zone Safety Rating</p>
                            </div>
                            <div className="flex gap-0.5">
                              {[1, 2, 3, 4, 5].map(star => (
                                <div key={star} className={`w-1.5 h-1.5 rounded-full ${star <= fb.safety_rating ? 'bg-indigo-600' : 'bg-slate-200'}`}></div>
                              ))}
                            </div>
                          </div>
                          <p className="text-xs text-slate-500 italic mb-3 line-clamp-2">"{fb.feedback_text || 'No comments provided'}"</p>
                          <div className="flex items-center justify-between text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                            <span>{fb.rider_id}</span>
                            <span>{new Date(fb.submitted_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'Performance' && <ModelPerformance />}
          {activeTab === 'AIReports' && <AIReportSummary />}
        </main>
      </div>
    </div>
  );
};

export default AdminDashboard;
