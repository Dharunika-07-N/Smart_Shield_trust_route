import React, { useEffect, useState, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { api } from '../services/api';
import { FiUsers, FiActivity, FiMapPin, FiTruck } from 'react-icons/fi';

// Component to handle map view updates
const MapAutoCenter = ({ center }) => {
    const map = useMap();
    useEffect(() => {
        if (center) map.setView(center, map.getZoom());
    }, [center, map]);
    return null;
};

const FleetMap = () => {
    const [fleet, setFleet] = useState([]);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({ online: 0, active: 0, areas: 0 });

    const fetchFleetData = async () => {
        try {
            const data = await api.get('/users/fleet-locations');
            setFleet(Array.isArray(data) ? data : []);
            setLoading(false);
        } catch (error) {
            console.error("Failed to fetch fleet data", error);
            setLoading(false);
        }
    };

    // Use positions directly from backend
    const simulatedFleet = useMemo(() => {
        return fleet.map(f => ({
            ...f,
            position: f.location || [13.0827, 80.2707]
        }));
    }, [fleet]);

    useEffect(() => {
        fetchFleetData();
        const interval = setInterval(fetchFleetData, 5000);
        return () => clearInterval(interval);
    }, []);

    const driverIcon = (status) => L.divIcon({
        className: 'custom-driver-icon',
        html: `<div class="relative flex items-center justify-center">
            <div class="absolute w-8 h-8 ${status === 'online' ? 'bg-indigo-500' : 'bg-rose-500'} rounded-full opacity-20 animate-ping"></div>
            <div class="relative w-10 h-10 ${status === 'online' ? 'bg-indigo-600' : 'bg-rose-600'} rounded-2xl flex items-center justify-center text-white shadow-xl border-2 border-white transform hover:scale-110 transition-transform">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 18H3c-1.1 0-2-.9-2-2V7c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2v2"/><path d="M10 18h10c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2H10"/><circle cx="8" cy="18" r="3"/><circle cx="18" cy="18" r="3"/></svg>
            </div>
        </div>`,
        iconSize: [40, 40],
        iconAnchor: [20, 20]
    });

    return (
        <div className="flex flex-col h-full bg-slate-50 font-['Inter']">
            {/* Header / Stats Overlay */}
            <div className="absolute top-6 left-6 z-[1000] flex flex-col gap-4 max-w-sm">
                <div className="bg-white/80 backdrop-blur-xl p-6 rounded-[2rem] border border-white/40 shadow-2xl">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white">
                            <FiActivity size={24} />
                        </div>
                        <div>
                            <h3 className="font-black text-slate-900 text-lg">Fleet Intelligence</h3>
                            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Live Network Simulation</p>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                        <div className="bg-indigo-50/50 p-3 rounded-2xl border border-indigo-100">
                            <p className="text-[10px] font-black text-indigo-400 uppercase">Online Nodes</p>
                            <p className="text-xl font-black text-indigo-600">{fleet.length}</p>
                        </div>
                        <div className="bg-emerald-50/50 p-3 rounded-2xl border border-emerald-100">
                            <p className="text-[10px] font-black text-emerald-400 uppercase">Available</p>
                            <p className="text-xl font-black text-emerald-600">{fleet.filter(f => f.status === 'online').length}</p>
                        </div>
                    </div>
                </div>

                <div className="bg-white/80 backdrop-blur-xl p-4 rounded-2xl border border-white/40 shadow-xl">
                    <h4 className="text-[10px] font-black text-slate-400 uppercase mb-3 px-1">Active Personnel</h4>
                    <div className="space-y-2 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
                        {simulatedFleet.map(f => (
                            <div key={f.id} className="flex items-center gap-3 p-2 rounded-xl hover:bg-white transition-colors cursor-pointer group">
                                <div className="w-8 h-8 bg-slate-100 rounded-lg flex items-center justify-center text-slate-400 font-bold text-xs uppercase group-hover:bg-indigo-100 group-hover:text-indigo-600 transition-colors">
                                    {f.full_name?.substring(0, 2)}
                                </div>
                                <div className="flex-1">
                                    <p className="text-xs font-bold text-slate-800">{f.full_name}</p>
                                    <p className="text-[9px] font-black text-slate-400 uppercase">{f.role}</p>
                                </div>
                                <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse"></div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Map Container */}
            <div className="flex-1 relative">
                <MapContainer
                    center={[13.0827, 80.2707]}
                    zoom={13}
                    style={{ height: "100%", width: "100%" }}
                    zoomControl={false}
                >
                    <TileLayer
                        url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    />

                    {simulatedFleet.map((driver) => (
                        <Marker
                            key={driver.id}
                            position={driver.position}
                            icon={driverIcon(driver.status)}
                        >
                            <Popup className="custom-popup">
                                <div className="p-2 min-w-[150px]">
                                    <div className="flex items-center gap-2 mb-2">
                                        <div className="w-6 h-6 bg-indigo-100 text-indigo-600 rounded flex items-center justify-center text-[10px] font-bold">
                                            {driver.full_name?.substring(0, 2)}
                                        </div>
                                        <span className="font-bold text-sm text-slate-800">{driver.full_name}</span>
                                    </div>
                                    <div className="space-y-1">
                                        <div className="flex justify-between text-[10px]">
                                            <span className="text-slate-400">Status</span>
                                            <span className="font-bold text-emerald-600 uppercase">Available</span>
                                        </div>
                                        <div className="flex justify-between text-[10px]">
                                            <span className="text-slate-400">Signal</span>
                                            <span className="font-bold text-slate-700">98% Strong</span>
                                        </div>
                                    </div>
                                    <button className="w-full mt-3 py-1.5 bg-indigo-600 text-white rounded text-[10px] font-bold hover:bg-indigo-700 transition-colors">
                                        Assign Duty
                                    </button>
                                </div>
                            </Popup>
                        </Marker>
                    ))}
                </MapContainer>
            </div>

            <style jsx global>{`
                .custom-popup .leaflet-popup-content-wrapper {
                    border-radius: 1rem;
                    padding: 0;
                    overflow: hidden;
                    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
                }
                .custom-popup .leaflet-popup-content {
                    margin: 0;
                }
                .custom-scrollbar::-webkit-scrollbar {
                    width: 4px;
                }
                .custom-scrollbar::-webkit-scrollbar-track {
                    background: transparent;
                }
                .custom-scrollbar::-webkit-scrollbar-thumb {
                    background: #e2e8f0;
                    border-radius: 10px;
                }
            `}</style>
        </div>
    );
};

export default FleetMap;
