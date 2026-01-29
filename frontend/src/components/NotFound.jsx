import React from 'react';
import { Link } from 'react-router-dom';
import { FiAlertOctagon, FiArrowLeft, FiNavigation } from 'react-icons/fi';

const NotFound = () => {
    return (
        <div className="min-h-screen bg-slate-50 flex items-center justify-center p-8 font-['Inter']">
            <div className="text-center">
                <div className="relative inline-block mb-12">
                    <div className="absolute inset-0 bg-rose-500 blur-[80px] opacity-10 animate-pulse"></div>
                    <FiAlertOctagon size={120} className="text-rose-500 relative z-10 mx-auto" />
                </div>
                <h1 className="text-6xl font-black text-slate-900 mb-4">404</h1>
                <h2 className="text-xl font-bold text-slate-400 mb-8 uppercase tracking-[0.2em]">Sector Not Found</h2>
                <p className="text-slate-500 max-w-sm mx-auto mb-10 leading-relaxed font-medium">
                    The coordinates you are looking for do not exist in the SmartShield grid. You have reached a dead-end zone.
                </p>
                <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                    <Link to="/" className="w-full sm:w-auto flex items-center justify-center gap-2 px-8 py-4 bg-white text-slate-900 rounded-2xl font-black transition-all hover:bg-slate-50 border border-slate-200 shadow-sm">
                        <FiArrowLeft /> Back to Command
                    </Link>
                    <Link to="/dashboard" className="w-full sm:w-auto flex items-center justify-center gap-2 px-8 py-4 bg-indigo-600 text-white rounded-2xl font-black transition-all hover:bg-indigo-700 shadow-lg shadow-indigo-600/20">
                        <FiNavigation /> Recalculate Route
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default NotFound;
