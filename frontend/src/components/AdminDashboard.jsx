import React, { useState, useEffect } from 'react';
import {
  FiShield, FiPackage, FiTrendingUp, FiMap,
  FiActivity, FiAlertCircle, FiCheckCircle, FiAlertTriangle, FiCpu, FiNavigation,
  FiUser, FiLogOut, FiSettings, FiBarChart2, FiLayers, FiMessageSquare
} from 'react-icons/fi';
import Analytics from './Analytics';
import RouteMap from './RouteMap';
import SnapMap from './SnapMap';
import LiveTracking from './LiveTracking';
import TrainingCenter from './TrainingCenter';
import { api } from '../services/api';
import useLocation from '../hooks/useLocation';

const AdminDashboard = ({ setAuth }) => {
  const [activeTab, setActiveTab] = useState('route-map');
  const [panicAlerting, setPanicAlerting] = useState(false);
  const [riderId, setRiderId] = useState(localStorage.getItem('rider_id') || 'RIDER_402');
  const { location: currentLocation } = useLocation();
  const [backendConnected, setBackendConnected] = useState(null);
  const [liveAlerts, setLiveAlerts] = useState([]);

  useEffect(() => {
    const checkBackendConnection = async () => {
      try {
        const response = await api.healthCheck();
        setBackendConnected(response && (response.status === 'healthy' || response.status === 'running'));
      } catch (error) {
        setBackendConnected(false);
      }
    };
    checkBackendConnection();
    const interval = setInterval(checkBackendConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await api.getAlerts();
        if (res.status === 'success') {
          setLiveAlerts(res.data.slice(0, 5));
        }
      } catch (err) {
        console.warn('Failed to fetch alerts for dashboard');
      }
    };
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 15000);
    return () => clearInterval(interval);
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

  const navItems = [
    { id: 'route-map', label: 'Route Optimizer', icon: FiNavigation },
    { id: 'overview', label: 'Fleet Overview', icon: FiLayers },
    { id: 'tracking', label: 'Live Tracking', icon: FiMap },
    { id: 'analytics', label: 'Insights', icon: FiBarChart2 },
    { id: 'training', label: 'AI Training', icon: FiCpu },
  ];

  const stats = [
    { title: 'Total Trips', value: '1,247', icon: FiPackage, color: 'text-blue-500' },
    { title: 'Safety Score', value: '92/100', icon: FiShield, color: 'text-green-500' },
    { title: 'Fuel Saved', value: '18%', icon: FiActivity, color: 'text-orange-500' },
    { title: 'Avg Time', value: '24 min', icon: FiTrendingUp, color: 'text-red-500' },
  ];

  return (
    <div className="flex h-screen bg-[#f8fafc] overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 flex-shrink-0 hidden lg:flex flex-col">
        <div className="p-6">
          <div className="flex items-center gap-3 text-white">
            <div className="bg-blue-600 p-2 rounded-xl">
              <FiShield className="text-2xl" />
            </div>
            <div className="font-bold text-xl tracking-tight">SmartShield</div>
          </div>
        </div>

        <nav className="flex-1 px-4 space-y-2 mt-4">
          {navItems.map(item => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all ${activeTab === item.id
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/20'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
                }`}
            >
              <item.icon className="text-lg" />
              {item.label}
            </button>
          ))}
        </nav>

        <div className="p-4 mt-auto border-t border-white/10">
          <div className="bg-white/5 rounded-xl p-4">
            <p className="text-xs text-gray-500 font-medium uppercase mb-2">Crowdsourced Alerts</p>
            <div className="space-y-3">
              {liveAlerts.length > 0 ? liveAlerts.map(alert => (
                <div key={alert.id} className="flex gap-2">
                  <span className="text-sm">
                    {alert.has_traffic_issues ? '⚠️' : '🚀'}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-[10px] text-gray-300 font-bold uppercase truncate">{alert.service_type}</p>
                    <p className="text-[10px] text-gray-500 truncate">
                      {alert.has_traffic_issues ? 'Traffic issues' : 'Smooth route'}
                    </p>
                  </div>
                </div>
              )) : (
                <p className="text-[10px] text-gray-500 italic">No recent reports</p>
              )}
            </div>
          </div>
        </div>

        <div className="p-4">
          <button
            onClick={() => setAuth(false)}
            className="w-full flex items-center gap-3 px-4 py-3 text-gray-400 hover:text-red-400 hover:bg-red-400/5 rounded-xl transition-all"
          >
            <FiLogOut />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header */}
        <header className="h-20 bg-white border-b border-gray-200 flex items-center justify-between px-8 flex-shrink-0 z-10">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold text-gray-900 lg:hidden">SmartShield</h1>
            <div className={`hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold ${backendConnected ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
              }`}>
              <div className={`w-2 h-2 rounded-full ${backendConnected ? 'bg-green-500' : 'bg-red-500 animate-pulse'}`}></div>
              {backendConnected ? 'Network Online' : 'Service Offline'}
            </div>
          </div>

          <div className="flex items-center gap-6">
            <button
              onClick={handlePanicButton}
              disabled={panicAlerting}
              className={`hidden sm:flex items-center gap-2 px-6 py-2.5 rounded-full text-sm font-bold shadow-lg transition-all ${panicAlerting ? 'bg-gray-400 cursor-not-allowed' : 'bg-red-600 text-white hover:bg-red-700 active:scale-95'
                }`}
            >
              <FiAlertTriangle className="animate-pulse" />
              SOS EMERGENY
            </button>

            <div className="flex items-center gap-3 pl-6 border-l border-gray-200">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-bold text-gray-900">{riderId}</p>
                <p className="text-xs text-gray-500">Fleet Operations</p>
              </div>
              <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center text-gray-600 border border-gray-200">
                <FiUser />
              </div>
            </div>
          </div>
        </header>

        {/* Dynamic Toolbar for Mobile Menu */}
        <div className="lg:hidden bg-gray-900 p-2 overflow-x-auto">
          <div className="flex gap-2 min-w-max">
            {navItems.map(item => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold ${activeTab === item.id ? 'bg-blue-600 text-white' : 'text-gray-400 hover:bg-white/5'
                  }`}
              >
                <item.icon />
                {item.label}
              </button>
            ))}
          </div>
        </div>

        <main className="flex-1 overflow-y-auto p-4 md:p-8">
          {activeTab === 'overview' && (
            <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                {stats.map((s, i) => (
                  <div key={i} className="premium-card p-6 border-l-4 border-l-transparent hover:border-l-blue-600">
                    <div className="flex items-center justify-between mb-4">
                      <div className={`p-3 rounded-2xl bg-gray-50 ${s.color}`}>
                        <s.icon className="text-xl" />
                      </div>
                      <span className="text-xs font-bold text-green-600 bg-green-50 px-2 py-1 rounded-full">+12%</span>
                    </div>
                    <p className="text-gray-500 text-xs font-bold uppercase tracking-wider">{s.title}</p>
                    <p className="text-2xl font-black text-gray-900 mt-1">{s.value}</p>
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 premium-card p-6 h-[400px]">
                  <h3 className="text-lg font-bold text-gray-900 mb-4">Real-time Performance</h3>
                  <Analytics compact />
                </div>
                <div className="premium-card p-6">
                  <h3 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
                    <FiMessageSquare className="text-blue-600" />
                    Rider Pulse Feed
                  </h3>
                  <div className="space-y-6">
                    {liveAlerts.length > 0 ? liveAlerts.map(alert => (
                      <div key={alert.id} className="flex gap-4 p-3 rounded-xl bg-gray-50 border border-gray-100 hover:shadow-md transition-all">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center text-xl shadow-sm ${alert.has_traffic_issues ? 'bg-red-100 text-red-600' : 'bg-green-100 text-green-600'
                          }`}>
                          {alert.has_traffic_issues ? '⚠️' : '🚀'}
                        </div>
                        <div>
                          <p className="text-xs font-black text-gray-400 uppercase">{alert.service_type}</p>
                          <p className="text-sm font-bold text-gray-800">
                            {alert.has_traffic_issues ? 'Heavy Traffic Detected' : 'Smooth Route Verified'}
                          </p>
                          <p className="text-xs text-gray-500 mt-0.5">
                            {new Date(alert.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </p>
                        </div>
                      </div>
                    )) : (
                      <div className="text-center py-12">
                        <FiMessageSquare className="text-4xl text-gray-200 mx-auto mb-4" />
                        <p className="text-sm text-gray-500">Wait for rider reports...</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'route-map' && <RouteMap />}
          {activeTab === 'tracking' && <LiveTracking />}
          {activeTab === 'analytics' && <Analytics />}
          {activeTab === 'training' && <TrainingCenter />}
        </main>
      </div>
    </div>
  );
};

export default AdminDashboard;
