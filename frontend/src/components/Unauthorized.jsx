import React from 'react';
import { Link } from 'react-router-dom';
import { FiShieldOff, FiLock, FiArrowLeft } from 'react-icons/fi';

const Unauthorized = () => {
    return (
        <div className="min-h-screen bg-slate-50 flex items-center justify-center p-8 font-['Inter']">
            <div className="text-center">
                <div className="relative inline-block mb-12">
                    <div className="absolute inset-0 bg-amber-500 blur-[80px] opacity-10 animate-pulse"></div>
                    <FiLock size={120} className="text-amber-500 relative z-10 mx-auto" />
                </div>
                <h1 className="text-4xl font-black text-slate-900 mb-4 tracking-tight">RESTRICTED ACCESS</h1>
                <h2 className="text-xl font-bold text-slate-400 mb-8 uppercase tracking-[0.2em]">Security Protocol 403</h2>
                <p className="text-slate-500 max-w-sm mx-auto mb-10 leading-relaxed font-medium font-medium">
                    Your current credentials do not have the required clearance level to access this sector. This incident has been logged.
                </p>
                <Link to="/login" className="inline-flex items-center gap-2 px-10 py-5 bg-indigo-600 text-white rounded-2xl font-black transition-all hover:bg-indigo-700 active:scale-95 shadow-xl shadow-indigo-600/20">
                    <FiShieldOff /> Upgrade Clearance
                </Link>
                <div className="mt-8">
                    <Link to="/" className="text-slate-400 hover:text-indigo-600 transition-colors text-sm font-bold flex items-center justify-center gap-2">
                        <FiArrowLeft /> Return to Safe Zone
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default Unauthorized;
