import React from 'react';
import { Link } from 'react-router-dom';
import { FiShield, FiNavigation, FiZap, FiCheckCircle, FiArrowRight, FiActivity, FiMap } from 'react-icons/fi';

const LandingPage = () => {
    return (
        <div className="min-h-screen bg-[#0F172A] text-slate-300 font-['Inter'] overflow-x-hidden">
            {/* Nav */}
            <nav className="h-20 flex items-center justify-between px-8 md:px-20 border-b border-slate-800">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-emerald-500 rounded-xl flex items-center justify-center text-[#0F172A] shadow-lg shadow-emerald-500/20">
                        <FiShield size={24} />
                    </div>
                    <span className="text-white font-black text-xl tracking-tight">SmartShield</span>
                </div>
                <div className="flex items-center gap-8">
                    <Link to="/login" className="text-sm font-bold hover:text-white transition-colors">Sign In</Link>
                    <Link
                        to="/login"
                        state={{ mode: 'register' }}
                        className="px-6 py-2.5 bg-emerald-500 text-[#0F172A] rounded-xl font-bold text-sm shadow-lg shadow-emerald-500/20 hover:bg-emerald-400 transition-all active:scale-95"
                    >
                        Join Network
                    </Link>
                </div>
            </nav>

            {/* Hero */}
            <header className="relative py-20 md:py-32 px-8 overflow-hidden">
                <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16 items-center relative z-10">
                    <div>
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-[10px] font-bold text-emerald-400 uppercase tracking-[0.2em] mb-6">
                            <FiActivity /> Next-Gen Route Safety
                        </div>
                        <h1 className="text-5xl md:text-7xl font-black text-white leading-[1.1] mb-8">
                            Trust Every <span className="text-emerald-500">Coordinate.</span>
                        </h1>
                        <p className="text-lg text-slate-400 leading-relaxed mb-10 max-w-lg">
                            SmartShield AI monitors 100+ variables in real-time to ensure your fleet, drivers, and deliveries move through the safest, most efficient sectors.
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4">
                            <Link to="/login" className="px-10 py-5 bg-emerald-500 text-[#0F172A] rounded-2xl font-black text-lg flex items-center justify-center gap-3 shadow-2xl shadow-emerald-500/20 hover:scale-[1.02] transition-all">
                                Get Started <FiArrowRight />
                            </Link>
                            <Link to="/login" className="px-10 py-5 bg-slate-800 text-white rounded-2xl font-black text-lg flex items-center justify-center gap-3 border border-slate-700 hover:bg-slate-700 transition-all">
                                Live Demo
                            </Link>
                        </div>
                    </div>

                    <div className="relative">
                        <div className="absolute -inset-10 bg-emerald-500/20 blur-[120px] rounded-full"></div>
                        <div className="relative bg-[#1E293B] border border-slate-700 rounded-[3rem] p-8 shadow-2xl transform lg:rotate-3">
                            {/* Mock Map UI */}
                            <div className="h-64 bg-slate-900 rounded-3xl overflow-hidden relative mb-6">
                                <div className="absolute inset-0 opacity-20 bg-[url('https://api.mapbox.com/styles/v1/mapbox/dark-v10/static/13,101,12.97,13/500x300?access_token=pk.mock')] bg-center bg-cover"></div>
                                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-4 h-4 bg-emerald-500 rounded-full border-4 border-white animate-ping"></div>
                                <div className="absolute bottom-4 left-4 right-4 h-2 bg-slate-800 rounded-full overflow-hidden">
                                    <div className="w-3/4 h-full bg-emerald-500"></div>
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-4 bg-slate-900/50 rounded-2xl border border-slate-700">
                                    <p className="text-[10px] text-slate-500 font-bold uppercase mb-1">Safety Index</p>
                                    <p className="text-2xl font-black text-white">98.4</p>
                                </div>
                                <div className="p-4 bg-slate-900/50 rounded-2xl border border-slate-700">
                                    <p className="text-[10px] text-slate-500 font-bold uppercase mb-1">Time Saved</p>
                                    <p className="text-2xl font-black text-emerald-500">+18%</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* Features */}
            <section className="py-24 bg-[#0F172A] border-t border-slate-800">
                <div className="max-w-6xl mx-auto px-8">
                    <div className="text-center mb-20">
                        <h2 className="text-3xl md:text-5xl font-black text-white mb-6">Built for Total Sovereignty.</h2>
                        <p className="text-slate-400 max-w-2xl mx-auto">Our multi-layered AI architecture provides unparalleled protection and optimization for modern logistics operations.</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        {[
                            { title: 'Trust-Route AI', icon: FiNavigation, desc: 'Dynamic route optimization based on live safety scores and traffic density.' },
                            { title: 'Fleet Command', icon: FiMap, desc: 'Real-time monitoring of all active nodes with instant SOS protocols.' },
                            { title: 'Safe-Sense ML', icon: FiZap, desc: 'Predictive analytics that identify sector risks before they impact your fleet.' }
                        ].map((f, i) => (
                            <div key={i} className="p-8 bg-[#1E293B] rounded-[2.5rem] border border-slate-800 hover:border-emerald-500/30 transition-all group">
                                <div className="w-16 h-16 bg-emerald-500/10 rounded-2xl flex items-center justify-center text-emerald-500 mb-6 group-hover:scale-110 transition-transform">
                                    <f.icon size={32} />
                                </div>
                                <h3 className="text-xl font-bold text-white mb-4">{f.title}</h3>
                                <p className="text-slate-400 leading-relaxed text-sm">{f.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA */}
            <section className="py-20 px-8">
                <div className="max-w-4xl mx-auto bg-gradient-to-br from-emerald-500 to-teal-600 rounded-[3rem] p-12 md:p-20 text-center shadow-2xl shadow-emerald-900/40 relative overflow-hidden">
                    <FiShield className="absolute -right-10 -bottom-10 text-white/10 w-64 h-64 rotate-12" />
                    <h2 className="text-3xl md:text-5xl font-black text-[#0F172A] mb-8 relative z-10">Start Protecting Your Journey Today.</h2>
                    <Link to="/login" className="inline-flex items-center gap-3 px-10 py-5 bg-[#0F172A] text-white rounded-2xl font-black text-lg hover:scale-[1.05] transition-all relative z-10">
                        Deploy SmartShield <FiArrowRight />
                    </Link>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-12 border-t border-slate-800 px-8 md:px-20 flex flex-col md:flex-row items-center justify-between gap-8">
                <div className="flex items-center gap-3 opacity-50">
                    <FiShield size={20} />
                    <span className="font-bold tracking-tight">SmartShield</span>
                </div>
                <div className="text-slate-500 text-xs font-medium">
                    © 2026 SmartShield Global. All rights reserved. Secure Logistics Framework.
                </div>
                <div className="flex gap-8">
                    <span className="text-xs font-bold hover:text-white cursor-pointer transition-colors">Safety Protocols</span>
                    <span className="text-xs font-bold hover:text-white cursor-pointer transition-colors">API Docs</span>
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;
