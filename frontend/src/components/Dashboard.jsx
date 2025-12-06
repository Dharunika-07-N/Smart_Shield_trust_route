import React, { useState } from 'react';
import { 
  FiShield, FiPackage, FiTrendingUp, FiMap, 
  FiActivity, FiAlertCircle, FiCheckCircle 
} from 'react-icons/fi';
import Analytics from './Analytics';
import RouteMap from './RouteMap';
import SafetyHeatmap from './SafetyHeatmap';
import SnapMap from './SnapMap';
import LiveTracking from './LiveTracking';

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');

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
            <div className="flex items-center space-x-2">
              <FiCheckCircle className="text-success-500 text-xl" />
              <span className="text-sm font-medium text-gray-700">System Operational</span>
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
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
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

