import React, { useState } from 'react';
import { FiPackage, FiMapPin, FiSearch, FiLogOut, FiShield, FiAlertCircle } from 'react-icons/fi';
import RouteMap from './RouteMap';
import { api } from '../services/api';

const CustomerDashboard = ({ setAuth }) => {
    const [trackingId, setTrackingId] = useState('');
    const [isTracking, setIsTracking] = useState(false);
    const [deliveryData, setDeliveryData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleTrack = async (e) => {
        e.preventDefault();
        if (!trackingId) return;

        setLoading(true);
        setError('');

        try {
            // In a real app, we'd fetch this. ideally the track endpoint returns live data
            // const response = await api.trackDelivery(trackingId); 
            // Since delivery ID might not match DB exactly in demo, we mock success for UI

            // Mock Success
            setIsTracking(true);
            setDeliveryData({
                status: 'in_transit',
                current_location: { latitude: 12.9716, longitude: 77.5946 }, // Bangalore coords
                eta_minutes: 14
            });

        } catch (err) {
            console.error(err);
            setError('Unable to track package. Please check the ID.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex h-screen bg-gray-50 flex-col">
            <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between shadow-sm z-10">
                <div className="flex items-center gap-3">
                    <div className="bg-purple-600 p-2 rounded-xl text-white">
                        <FiPackage size={24} />
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-gray-900">Delivery Track</h1>
                        <p className="text-xs text-gray-500">Customer Portal</p>
                    </div>
                </div>
                <button
                    onClick={() => setAuth(false)}
                    className="text-sm font-medium text-gray-500 hover:text-red-500 flex items-center gap-2"
                >
                    <FiLogOut /> Sign Out
                </button>
            </header>

            <main className="flex-1 flex flex-col md:flex-row relative overflow-hidden">
                {/* Sidebar / Search Panel */}
                <div className="w-full md:w-96 bg-white border-r border-gray-200 p-6 z-10 flex flex-col shadow-xl">
                    <div className="mb-8">
                        <h2 className="text-2xl font-bold text-gray-900 mb-2">Track your order</h2>
                        <p className="text-gray-500 text-sm">Enter your delivery ID to see real-time updates and safety status.</p>
                    </div>

                    <form onSubmit={handleTrack} className="mb-6">
                        <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Tracking ID</label>
                        <div className="flex gap-2">
                            <div className="relative flex-1">
                                <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                                <input
                                    type="text"
                                    className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all"
                                    placeholder="e.g. DEL-8842-XJ"
                                    value={trackingId}
                                    onChange={(e) => setTrackingId(e.target.value)}
                                />
                            </div>
                            <button
                                type="submit"
                                disabled={loading}
                                className="bg-purple-600 hover:bg-purple-700 text-white px-6 rounded-xl font-bold transition-all shadow-lg shadow-purple-500/20 disabled:opacity-50"
                            >
                                {loading ? '...' : 'Go'}
                            </button>
                        </div>
                        {error && (
                            <div className="mt-3 flex items-center gap-2 text-red-500 text-sm">
                                <FiAlertCircle />
                                <span>{error}</span>
                            </div>
                        )}
                    </form>

                    {isTracking && deliveryData && (
                        <div className="mb-8 p-4 bg-purple-50 rounded-2xl border border-purple-100">
                            <div className="flex justify-between items-start mb-2">
                                <div>
                                    <p className="text-xs text-purple-600 font-bold uppercase">Status</p>
                                    <p className="text-lg font-bold text-gray-900 capitalize">{deliveryData.status?.replace('_', ' ') || 'In Transit'}</p>
                                </div>
                                <div className="bg-purple-200 text-purple-700 px-2 py-1 rounded text-xs font-bold">
                                    ETA: {deliveryData.eta_minutes || 14} min
                                </div>
                            </div>
                            <div className="w-full bg-purple-200 h-1.5 rounded-full mt-2 overflow-hidden">
                                <div className="bg-purple-600 h-full w-[60%] rounded-full animate-pulse"></div>
                            </div>
                        </div>
                    )}

                    <div className="mt-auto">
                        <div className="bg-blue-50 border border-blue-100 rounded-2xl p-4">
                            <div className="flex items-start gap-3">
                                <FiShield className="text-blue-600 mt-1" />
                                <div>
                                    <h3 className="font-bold text-blue-900 text-sm">Secure Delivery Promise</h3>
                                    <p className="text-xs text-blue-700 mt-1">
                                        Your delivery partner is monitored by our SmartShield AI for maximum safety and efficiency.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Map Area */}
                <div className="flex-1 bg-gray-100 relative">
                    <RouteMap />
                    {!isTracking && (
                        <div className="absolute inset-0 bg-white/60 backdrop-blur-sm flex items-center justify-center z-10">
                            <div className="text-center p-8">
                                <div className="bg-white p-4 rounded-full shadow-xl inline-block mb-4">
                                    <FiMapPin size={48} className="text-purple-300" />
                                </div>
                                <h3 className="text-xl font-bold text-gray-400">Map Standby</h3>
                                <p className="text-gray-400">Enter a tracking ID to locate your package</p>
                            </div>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
};

export default CustomerDashboard;
