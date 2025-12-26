import React, { useState } from 'react';
import {
  FiShield, FiPackage, FiTrendingUp, FiMap,
  FiActivity, FiAlertCircle, FiCheckCircle, FiAlertTriangle
} from 'react-icons/fi';
import Analytics from './Analytics';
import RouteMap from './RouteMap';
import SafetyHeatmap from './SafetyHeatmap';
import SnapMap from './SnapMap';
import LiveTracking from './LiveTracking';
import { api } from '../services/api';
import useLocation from '../hooks/useLocation';

const Dashboard = ({ setAuth }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [panicAlerting, setPanicAlerting] = useState(false);
  const [riderId, setRiderId] = useState(localStorage.getItem('rider_id') || '');
  const { location: currentLocation, loading: locationLoading } = useLocation();
  const [backendConnected, setBackendConnected] = useState(null);

  // Check backend connection on mount
  React.useEffect(() => {
    const checkBackendConnection = async () => {
      try {
        const response = await api.healthCheck();
        if (response && (response.status === 'healthy' || response.status === 'running')) {
          setBackendConnected(true);
        } else {
          setBackendConnected(false);
        }
      } catch (error) {
        setBackendConnected(false);
      }
    };

    checkBackendConnection();
    const interval = setInterval(checkBackendConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  const handlePanicButton = async () => {
    if (!currentLocation || !riderId) {
      alert('Location or rider ID not available. Please ensure location services are enabled and rider ID is set.');
      return;
    }

    if (!window.confirm('Are you sure you want to trigger the emergency SOS alert? This will notify your company and emergency contacts immediately.')) {
      return;
    }

    setPanicAlerting(true);
    try {
      const response = await api.triggerPanicButton({
        rider_id: riderId,
        location: currentLocation,
        delivery_id: undefined,
        route_id: undefined
      });

      if (response.success) {
        alert('Emergency SOS alert sent successfully! Your company and emergency contacts have been notified.');
      } else {
        throw new Error(response.message || 'Failed to send alert');
      }
    } catch (error) {
      console.error('Panic button error:', error);

      // Provide more helpful error messages
      let errorMessage = error.message || 'Unknown error';

      if (error.isNetworkError || errorMessage.includes('Unable to connect to server') || errorMessage.includes('Network error')) {
        errorMessage = `Cannot connect to backend server.\n\n` +
          `The backend server is not running. To start it:\n\n` +
          `1. Open a terminal/command prompt\n` +
          `2. Navigate to the backend directory:\n` +
          `   cd backend\n` +
          `3. Activate the virtual environment (if using one):\n` +
          `   venv\\Scripts\\activate  (Windows)\n` +
          `   source venv/bin/activate  (Mac/Linux)\n` +
          `4. Start the server:\n` +
          `   python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000\n\n` +
          `Or if you have a startup script, use that instead.\n\n` +
          `Once the server is running, try again.`;
      }

      alert(`Failed to send emergency alert: ${errorMessage}`);
    } finally {
      setPanicAlerting(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setAuth(false);
  };

  const stats = [
    {
      title: 'Total Routes',
      value: '1,247',
      change: '+12.5%',
      icon: FiMap,
      color: 'bg-primary-500',
    },
    {
      title: 'Avg Safety Score',
      value: '87/100',
      change: '+3.2%',
      icon: FiShield,
      color: 'bg-success-500',
    },
    {
      title: 'Fuel Saved',
      value: '2.4k L',
      change: '+18.1%',
      icon: FiActivity,
      color: 'bg-warning-500',
    },
    {
      title: 'Delivery Time',
      value: '32 min',
      change: '-24.3%',
      icon: FiTrendingUp,
      color: 'bg-danger-500',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Backend Connection Status Banner */}
      {backendConnected === false && (
        <div className="bg-red-50 border-b border-red-200 px-4 py-3">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <FiAlertCircle className="text-red-600 text-xl" />
              <div>
                <p className="text-sm font-medium text-red-800">
                  Backend server is not connected
                </p>
                <p className="text-xs text-red-600 mt-1">
                  Please start the backend server. Check the console for instructions or run: <code className="bg-red-100 px-1 rounded">cd backend && python -m uvicorn api.main:app --reload</code>
                </p>
              </div>
            </div>
            <button
              onClick={() => window.location.reload()}
              className="text-sm text-red-700 hover:text-red-900 underline"
            >
              Retry Connection
            </button>
          </div>
        </div>
      )}

      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-primary-500 p-2 rounded-lg">
                <FiShield className="text-white text-2xl" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  AI Smart Shield Trust Route
                </h1>
                <p className="text-sm text-gray-600">
                  Intelligent Delivery Route Optimization
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                {backendConnected === true ? (
                  <>
                    <FiCheckCircle className="text-green-500 text-xl" />
                    <span className="text-sm font-medium text-gray-700">Backend Connected</span>
                  </>
                ) : backendConnected === false ? (
                  <>
                    <FiAlertTriangle className="text-red-500 text-xl" />
                    <span className="text-sm font-medium text-red-700">Backend Disconnected</span>
                  </>
                ) : (
                  <>
                    <div className="w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
                    <span className="text-sm font-medium text-gray-700">Checking Connection...</span>
                  </>
                )}
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-4 py-2 rounded-lg font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 transition-all border border-gray-300"
              >
                <span>Logout</span>
              </button>

              {/* Emergency SOS Button */}
              <button
                onClick={handlePanicButton}
                disabled={panicAlerting || !currentLocation || !riderId}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-semibold text-white transition-all ${panicAlerting
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-red-600 hover:bg-red-700 active:bg-red-800 shadow-lg hover:shadow-xl'
                  }`}
                title={!riderId ? 'Please set Rider ID to use SOS' : !currentLocation ? 'Location not available' : 'Emergency SOS Alert'}
              >
                <FiAlertTriangle className="text-xl" />
                <span>{panicAlerting ? 'Sending...' : 'SOS'}</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', label: 'Overview' },
              { id: 'snap-map', label: 'Live Map' },
              { id: 'tracking', label: 'Live Tracking' },
              { id: 'analytics', label: 'Analytics' },
              { id: 'route-map', label: 'Route Map' },
              { id: 'safety-heatmap', label: 'Safety Heatmap' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {stats.map((stat, index) => (
                <div
                  key={index}
                  className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 card-hover"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className={`${stat.color} p-3 rounded-lg`}>
                      <stat.icon className="text-white text-xl" />
                    </div>
                    <span className="text-sm font-medium text-success-600 bg-success-50 px-2 py-1 rounded">
                      {stat.change}
                    </span>
                  </div>
                  <h3 className="text-gray-600 text-sm font-medium mb-1">
                    {stat.title}
                  </h3>
                  <p className="text-3xl font-bold text-gray-900">
                    {stat.value}
                  </p>
                </div>
              ))}
            </div>

            {/* Emergency SOS Section */}
            <div className="bg-gradient-to-r from-red-50 to-red-100 border-2 border-red-300 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="bg-red-600 p-3 rounded-lg">
                    <FiAlertTriangle className="text-white text-2xl" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-red-900">Emergency SOS</h2>
                    <p className="text-sm text-red-700">Quick access emergency alert system</p>
                  </div>
                </div>
                <button
                  onClick={handlePanicButton}
                  disabled={panicAlerting || !currentLocation || !riderId}
                  className={`px-6 py-3 rounded-lg font-bold text-white transition-all ${panicAlerting
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-red-600 hover:bg-red-700 active:bg-red-800 shadow-lg hover:shadow-xl transform hover:scale-105'
                    }`}
                >
                  {panicAlerting ? 'Sending Alert...' : 'TRIGGER SOS'}
                </button>
              </div>
              <div className="space-y-2">
                <div className="flex items-center space-x-2 text-sm">
                  <input
                    type="text"
                    value={riderId}
                    onChange={(e) => {
                      const id = e.target.value;
                      setRiderId(id);
                      localStorage.setItem('rider_id', id);
                    }}
                    placeholder="Enter Rider ID (required for SOS)"
                    className="flex-1 border border-red-300 rounded-md px-3 py-2 text-sm"
                  />
                </div>
                <div className="text-xs text-red-700">
                  {!currentLocation && '⚠️ Location not available. '}
                  {!riderId && '⚠️ Please enter your Rider ID to use the SOS feature. '}
                  {currentLocation && riderId && '✓ Ready to send emergency alerts'}
                </div>
                <p className="text-xs text-red-600 mt-2">
                  <strong>Note:</strong> This will immediately notify your delivery company and emergency contacts with your current location.
                </p>
              </div>
            </div>

            {/* Recent Activity & Quick Actions */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Recent Activity */}
              <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Recent Deliveries
                </h2>
                <div className="space-y-4">
                  {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <FiPackage className="text-primary-500" />
                        <div>
                          <p className="font-medium text-gray-900">Route #{1000 + i}</p>
                          <p className="text-sm text-gray-600">5 stops • 12.5 km</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <FiShield className="text-success-500" />
                        <span className="text-sm font-medium text-gray-700">85%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Safety Alerts */}
              <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <FiAlertCircle className="mr-2 text-warning-500" />
                  Safety Alerts
                </h2>
                <div className="space-y-4">
                  <div className="flex items-start space-x-3 p-3 bg-warning-50 rounded-lg border border-warning-200">
                    <FiAlertCircle className="text-warning-500 mt-0.5" />
                    <div className="flex-1">
                      <p className="font-medium text-warning-800">
                        Night Route Adjustment
                      </p>
                      <p className="text-sm text-warning-700 mt-1">
                        3 routes modified for better lighting conditions
                      </p>
                      <span className="text-xs text-warning-600 mt-1 block">
                        Updated 2 hours ago
                      </span>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                    <FiCheckCircle className="text-success-500 mt-0.5" />
                    <div className="flex-1">
                      <p className="font-medium text-gray-800">
                        All Systems Normal
                      </p>
                      <p className="text-sm text-gray-600 mt-1">
                        No safety issues detected in the last 24 hours
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Performance Metrics */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900 mb-6">
                Performance Metrics
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center p-4 bg-gradient-to-br from-primary-50 to-primary-100 rounded-lg">
                  <div className="text-4xl font-bold text-primary-600">27%</div>
                  <div className="text-sm text-gray-600 mt-2">Time Reduction</div>
                  <div className="text-xs text-success-600 mt-1">✓ Target Achieved</div>
                </div>
                <div className="text-center p-4 bg-gradient-to-br from-success-50 to-success-100 rounded-lg">
                  <div className="text-4xl font-bold text-success-600">21%</div>
                  <div className="text-sm text-gray-600 mt-2">Fuel Savings</div>
                  <div className="text-xs text-success-600 mt-1">✓ Target Achieved</div>
                </div>
                <div className="text-center p-4 bg-gradient-to-br from-warning-50 to-warning-100 rounded-lg">
                  <div className="text-4xl font-bold text-warning-600">13%</div>
                  <div className="text-sm text-gray-600 mt-2">Success Rate Increase</div>
                  <div className="text-xs text-success-600 mt-1">✓ Target Achieved</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'snap-map' && <SnapMap />}
        {activeTab === 'tracking' && <LiveTracking />}
        {activeTab === 'analytics' && <Analytics />}
        {activeTab === 'route-map' && <RouteMap />}
        {activeTab === 'safety-heatmap' && <SafetyHeatmap />}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-600">
            © 2024 AI Smart Shield Trust Route. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Dashboard;

