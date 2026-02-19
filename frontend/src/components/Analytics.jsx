import React, { useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { FiCalendar, FiClock } from 'react-icons/fi';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const Analytics = ({ hideTitle = false, externalData = null }) => {
  const [timeRange, setTimeRange] = useState('7d');

  // Generator for dynamic mock data based on range
  const generateData = (range) => {
    const factor = range === '7d' ? 1 : range === '30d' ? 4 : 12;
    const labels = range === '7d'
      ? ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
      : range === '30d' ? ['Week 1', 'Week 2', 'Week 3', 'Week 4']
        : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];

    return {
      labels,
      deliveryTime: labels.map(() => 25 + Math.random() * 20),
      fuelSavings: labels.map(() => 500 + Math.random() * 1000),
      safetyDistribution: [60 + Math.random() * 10, 25 + Math.random() * 5, 5 + Math.random() * 5],
      activeNodes: labels.map(() => 50 + Math.random() * 100)
    };
  };

  const activeData = externalData || generateData(timeRange);

  const deliveryTimeData = {
    labels: activeData.labels,
    datasets: [
      {
        label: 'Avg Delivery Time (min)',
        data: activeData.deliveryTime,
        borderColor: 'rgb(79, 70, 229)', // indigo-600
        backgroundColor: 'rgba(79, 70, 229, 0.1)', // indigo-600 with transparency
        tension: 0.4,
      },
    ],
  };

  const fuelConsumptionData = {
    labels: activeData.labels,
    datasets: [
      {
        label: 'Fuel Consumed (L)',
        data: activeData.fuelSavings,
        backgroundColor: 'rgba(34, 197, 94, 0.6)', // emerald-500
        borderColor: 'rgb(34, 197, 94)', // emerald-500
        borderWidth: 2,
      },
    ],
  };

  const safetyDistributionData = {
    labels: ['High', 'Med', 'Low'],
    datasets: [
      {
        data: activeData.safetyDistribution,
        backgroundColor: [
          'rgba(79, 70, 229, 0.8)', // indigo-600
          'rgba(245, 158, 11, 0.8)', // warning-600
          'rgba(239, 68, 68, 0.8)', // danger-600
        ],
        borderWidth: 0,
      },
    ],
  };

  const routesByTimeData = {
    labels: activeData.labels,
    datasets: [
      {
        label: 'Delivery Routes',
        data: activeData.activeNodes || [45, 120, 95, 140, 80, 25],
        backgroundColor: 'rgba(79, 70, 229, 0.8)', // indigo-600
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
    },
  };

  return (
    <div className="space-y-6">
      {/* Time Range Selector */}
      {!hideTitle && (
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h2>
          <div className="flex items-center space-x-2 bg-gray-100 rounded-lg p-1">
            {['7d', '30d', '90d'].map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${timeRange === range
                  ? 'bg-white text-indigo-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
                  }`}
              >
                {range === '7d' ? '7 Days' : range === '30d' ? '30 Days' : '90 Days'}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Delivery Time Trend */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <FiClock className="mr-2 text-indigo-500" />
              Delivery Time Trend
            </h3>
          </div>
          <div className="h-64">
            <Line data={deliveryTimeData} options={chartOptions} />
          </div>
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Average This Week</span>
              <span className="text-2xl font-bold text-gray-900">32 min</span>
            </div>
            <div className="flex items-center mt-2">
              <span className="text-success-600 font-medium">↓ 24% reduction</span>
              <span className="text-gray-500 ml-2">vs previous week</span>
            </div>
          </div>
        </div>

        {/* Fuel Consumption */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              Fuel Consumption
            </h3>
          </div>
          <div className="h-64">
            <Bar data={fuelConsumptionData} options={chartOptions} />
          </div>
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Total Savings</span>
              <span className="text-2xl font-bold text-success-600">400 L</span>
            </div>
            <div className="flex items-center mt-2">
              <span className="text-success-600 font-medium">↓ 21% reduction</span>
              <span className="text-gray-500 ml-2">vs previous month</span>
            </div>
          </div>
        </div>

        {/* Safety Distribution */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Safety Score Distribution
          </h3>
          <div className="h-64 flex items-center justify-center">
            <Doughnut data={safetyDistributionData} options={chartOptions} />
          </div>
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-indigo-600">65%</div>
                <div className="text-sm text-gray-600">High Safety</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-warning-600">30%</div>
                <div className="text-sm text-gray-600">Medium Safety</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-danger-600">5%</div>
                <div className="text-sm text-gray-600">Low Safety</div>
              </div>
            </div>
          </div>
        </div>

        {/* Routes by Time Period */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <FiCalendar className="mr-2 text-indigo-500" />
            Peak Delivery Hours
          </h3>
          <div className="h-64">
            <Bar data={routesByTimeData} options={chartOptions} />
          </div>
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Peak Time</span>
              <span className="text-lg font-bold text-gray-900">15:00 - 18:00</span>
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics Summary */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-xl shadow-lg p-8 text-white">
        <div className="flex justify-between items-start mb-6">
          <h3 className="text-xl font-bold">Smart Shield ML Performance Summary</h3>
          <span className="bg-white/20 text-xs px-2 py-1 rounded uppercase tracking-wider font-semibold">
            Data Source: TN Crime 2022
          </span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div>
            <div className="text-3xl font-bold">1,247</div>
            <div className="text-blue-100 mt-2">Total Deliveries</div>
            <div className="text-xs text-blue-200">2,000 Trained Samples</div>
          </div>
          <div>
            <div className="text-3xl font-bold">87%</div>
            <div className="text-blue-100 mt-2">Safety Accuracy</div>
            <div className="text-xs text-green-300">↑ 4.2% Optimization</div>
          </div>
          <div>
            <div className="text-3xl font-bold">32 min</div>
            <div className="text-blue-100 mt-2">Avg Prediction Error</div>
            <div className="text-xs text-blue-200">XGBoost Optimized</div>
          </div>
          <div>
            <div className="text-3xl font-bold">12.4%</div>
            <div className="text-blue-100 mt-2">Fuel Efficiency Gain</div>
            <div className="text-xs text-blue-200">Adaptive RL Routing</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;

