import React, { useState, useEffect } from 'react';
import {
    FiPackage, FiMapPin, FiSearch, FiLogOut, FiShield,
    FiAlertCircle, FiClock, FiUser, FiPhone, FiCheckCircle,
    FiMessageSquare, FiStar, FiFlag
} from 'react-icons/fi';
import RouteMap from './RouteMap';
import { api } from '../services/api';
import dashboardApi from '../services/dashboardApi';

const CustomerDashboard = ({ setAuth }) => {
    const [trackingId, setTrackingId] = useState('');
    const [isTracking, setIsTracking] = useState(false);
    const [orderData, setOrderData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    // Mock order data for demonstration
    const mockOrder = {
        id: 'ORD-7742-XJ',
        status: 'in_transit', // confirmed, assigned, picked_up, in_transit, delivered
        eta: '14 mins',
        driver: {
            name: 'Karan Singh',
            rating: 4.8,
            phone: '+91 98765 43210',
            vehicle: 'TVS Apache (TN 01 AB 1234)'
        },
        items: [
            { name: 'Organic Grocery Bundle', qty: 1, price: '₹1,249' },
            { name: 'Fresh Fruits Pack', qty: 1, price: '₹450' }
        ],
        total: '₹1,699',
        address: 'Apartment 4B, Emerald Heights, T. Nagar, Chennai',
        route: [
            [13.0418, 80.2341], // Chennai start
            [13.0450, 80.2380],
            [13.0500, 80.2400],
            [13.0520, 80.2450]  // End
        ],
        markers: [
            { position: [13.0418, 80.2341], color: '#3b82f6', popup: 'Warehouse' },
            { position: [13.0520, 80.2450], color: '#ef4444', popup: 'Your Location' },
            { position: [13.0470, 80.2390], color: '#10b981', popup: 'Driver Current Location', icon: null }
        ]
    };

    const handleTrack = async (e) => {
        e.preventDefault();
        if (!trackingId) return;

        setLoading(true);
        setError('');

        try {
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 800));
            setOrderData(mockOrder);
            setIsTracking(true);
        } catch (err) {
            setError('Booking ID not found. Please check and try again.');
        } finally {
            setLoading(false);
        }
    };

    const getStatusStep = () => {
        const statuses = ['confirmed', 'assigned', 'picked_up', 'in_transit', 'delivered'];
        return statuses.indexOf(orderData?.status || 'confirmed');
    };

    return (
        <div className="flex flex-col h-screen bg-slate-50 font-['Inter']">
            {/* Header */}
            <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-30">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
                        <FiShield size={24} />
                    </div>
                    <div>
                        <h1 className="text-lg font-bold text-slate-800 leading-none">SmartShield</h1>
                        <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider mt-1">Customer Portal</p>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <button
                        onClick={() => {
                            localStorage.removeItem('auth_token');
                            setAuth(false);
                        }}
                        className="flex items-center gap-2 text-sm font-semibold text-slate-500 hover:text-red-500 transition-colors"
                    >
                        <FiLogOut /> Sign Out
                    </button>
                </div>
            </header>

            <main className="flex-1 flex flex-col md:flex-row overflow-hidden">
                {/* Left Panel: Search & Details */}
                <div className="w-full md:w-[400px] bg-white border-r border-slate-200 flex flex-col p-6 overflow-y-auto">
                    <div className="mb-8">
                        <h2 className="text-2xl font-bold text-slate-800 mb-2">Track Your Route</h2>
                        <p className="text-sm text-slate-500">Enter your order ID for real-time safety monitoring.</p>
                    </div>

                    <form onSubmit={handleTrack} className="mb-8">
                        <div className="flex gap-2">
                            <div className="relative flex-1">
                                <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                                <input
                                    type="text"
                                    value={trackingId}
                                    onChange={(e) => setTrackingId(e.target.value)}
                                    placeholder="Enter Order ID"
                                    className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all font-medium text-slate-800"
                                />
                            </div>
                            <button
                                type="submit"
                                disabled={loading || !trackingId}
                                className="px-6 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl transition-all shadow-lg shadow-indigo-500/20 disabled:opacity-50"
                            >
                                {loading ? '...' : 'Track'}
                            </button>
                        </div>
                        {error && <p className="mt-2 text-xs text-red-500 font-medium">{error}</p>}
                    </form>

                    {isTracking && orderData && (
                        <div className="flex-1 space-y-6">
                            {/* Order Progress */}
                            <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100">
                                <div className="flex items-center justify-between mb-4">
                                    <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">Live Status</span>
                                    <span className="text-xs font-bold text-indigo-600 bg-indigo-50 px-2 py-1 rounded-full uppercase tracking-wider">
                                        {orderData.status.replace('_', ' ')}
                                    </span>
                                </div>

                                <div className="relative pt-2 pb-6 px-1">
                                    <div className="flex justify-between relative z-10">
                                        {[0, 1, 2, 3, 4].map((step) => (
                                            <div
                                                key={step}
                                                className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold transition-colors ${getStatusStep() >= step ? 'bg-indigo-600 text-white' : 'bg-slate-200 text-slate-400'
                                                    }`}
                                            >
                                                {getStatusStep() > step ? <FiCheckCircle /> : step + 1}
                                            </div>
                                        ))}
                                    </div>
                                    <div className="absolute top-5 left-0 w-full h-0.5 bg-slate-200 -z-0">
                                        <div
                                            className="h-full bg-indigo-600 transition-all duration-500"
                                            style={{ width: `${(getStatusStep() / 4) * 100}%` }}
                                        ></div>
                                    </div>
                                    <div className="flex justify-between mt-2 text-[8px] font-bold text-slate-400 uppercase tracking-tighter">
                                        <span>Confirmed</span>
                                        <span>Assigned</span>
                                        <span>Picked Up</span>
                                        <span>In Transit</span>
                                        <span>Delivered</span>
                                    </div>
                                </div>

                                <div className="mt-4 flex items-center justify-between pt-4 border-t border-slate-200">
                                    <div className="flex items-center gap-2">
                                        <FiClock className="text-indigo-600" />
                                        <span className="text-sm font-bold text-slate-700">ETA: {orderData.eta}</span>
                                    </div>
                                    <span className="text-xs text-slate-400">Arriving Soon</span>
                                </div>
                            </div>

                            {/* Driver Info */}
                            <div className="bg-white rounded-2xl p-4 border border-slate-200">
                                <h3 className="text-xs font-bold text-slate-400 uppercase mb-4 tracking-widest">Delivery Partner</h3>
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center text-slate-400 border border-slate-200">
                                        <FiUser size={24} />
                                    </div>
                                    <div className="flex-1">
                                        <div className="flex items-center justify-between">
                                            <h4 className="font-bold text-slate-800">{orderData.driver.name}</h4>
                                            <div className="flex items-center gap-1 text-xs font-bold text-amber-500 bg-amber-50 px-2 py-0.5 rounded-full">
                                                <FiStar size={10} fill="currentColor" />
                                                {orderData.driver.rating}
                                            </div>
                                        </div>
                                        <p className="text-xs text-slate-500 mt-0.5">{orderData.driver.vehicle}</p>
                                    </div>
                                </div>
                                <div className="grid grid-cols-2 gap-2 mt-4">
                                    <button className="flex items-center justify-center gap-2 py-2.5 bg-slate-50 hover:bg-slate-100 rounded-xl text-slate-700 text-sm font-bold transition-all border border-slate-200">
                                        <FiPhone size={14} /> Call
                                    </button>
                                    <button className="flex items-center justify-center gap-2 py-2.5 bg-indigo-50 hover:bg-indigo-100 rounded-xl text-indigo-700 text-sm font-bold transition-all border border-indigo-100">
                                        <FiMessageSquare size={14} /> Chat
                                    </button>
                                </div>
                            </div>

                            {/* Order Details */}
                            <div className="bg-white rounded-2xl p-4 border border-slate-200">
                                <h3 className="text-xs font-bold text-slate-400 uppercase mb-4 tracking-widest">Order Details</h3>
                                <div className="space-y-3">
                                    {orderData.items.map((item, idx) => (
                                        <div key={idx} className="flex justify-between text-sm">
                                            <span className="text-slate-600">{item.qty}x {item.name}</span>
                                            <span className="font-bold text-slate-800">{item.price}</span>
                                        </div>
                                    ))}
                                    <div className="pt-3 border-t border-slate-100 flex justify-between items-center">
                                        <span className="font-bold text-slate-800">Total</span>
                                        <span className="text-lg font-extrabold text-indigo-600">{orderData.total}</span>
                                    </div>
                                </div>
                            </div>

                            {/* Safety Promise */}
                            <div className="p-4 bg-indigo-50 rounded-2xl border border-indigo-100 flex items-start gap-4">
                                <FiShield className="text-indigo-600 shrink-0 mt-1" />
                                <div>
                                    <h4 className="text-sm font-bold text-indigo-900">Your route is safe</h4>
                                    <p className="text-xs text-indigo-700/70 mt-1 leading-relaxed">
                                        SmartShield AI is monitoring your delivery path in real-time. Emergency responders are on standby.
                                    </p>
                                </div>
                            </div>

                            {/* Actions */}
                            <div className="flex gap-2">
                                <button className="flex-1 flex items-center justify-center gap-2 py-3 bg-red-50 hover:bg-red-100 rounded-xl text-red-600 text-sm font-bold transition-all border border-red-100">
                                    <FiFlag /> Report Issue
                                </button>
                            </div>
                        </div>
                    )}

                    {!isTracking && (
                        <div className="flex-1 flex flex-col items-center justify-center text-center px-4">
                            <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center text-slate-200 mb-6 border border-slate-100">
                                <FiPackage size={40} />
                            </div>
                            <h3 className="text-lg font-bold text-slate-400">Ready to track?</h3>
                            <p className="text-sm text-slate-400 mt-2">Enter your Order ID from your confirmation email.</p>
                        </div>
                    )}
                </div>

                {/* Right Area: Map */}
                <div className="flex-1 relative bg-slate-100">
                    <RouteMap
                        variant="light-minimal"
                        route={orderData?.route}
                        markers={orderData?.markers}
                        center={orderData?.markers[0]?.position}
                        zoom={15}
                    />

                    {!isTracking && (
                        <div className="absolute inset-0 bg-white/60 backdrop-blur-sm z-10 flex items-center justify-center">
                            <div className="text-center p-8 bg-white/40 border border-white/20 rounded-3xl backdrop-blur-xl">
                                <FiMapPin size={48} className="text-slate-300 mx-auto mb-4" />
                                <h3 className="text-xl font-bold text-slate-400">Live Map View</h3>
                                <p className="text-sm text-slate-400 mt-1">Waiting for booking ID...</p>
                            </div>
                        </div>
                    )}

                    {isTracking && (
                        <div className="absolute top-6 right-6 z-20">
                            <div className="bg-white/80 backdrop-blur-md p-3 rounded-2xl shadow-xl border border-white/20 flex flex-col items-center gap-2">
                                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Signal State</div>
                                <div className="flex gap-1">
                                    <div className="w-1 h-3 bg-indigo-600 rounded-full animate-pulse"></div>
                                    <div className="w-1 h-4 bg-indigo-600 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                                    <div className="w-1 h-3 bg-indigo-600 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                                    <div className="w-1 h-5 bg-indigo-600 rounded-full animate-pulse" style={{ animationDelay: '0.6s' }}></div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
};

export default CustomerDashboard;
