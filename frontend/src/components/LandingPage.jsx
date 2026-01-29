import React from 'react';
import { Link } from 'react-router-dom';
import { FiShield, FiNavigation, FiZap, FiCheckCircle, FiArrowRight, FiActivity, FiMap } from 'react-icons/fi';

const LandingPage = () => {
    return (
        <div className="min-h-screen bg-white text-slate-600 font-['Inter'] overflow-x-hidden">
            {/* Nav */}
            <nav className="h-20 flex items-center justify-between px-8 md:px-20 border-b border-slate-100 bg-white/80 backdrop-blur-md sticky top-0 z-[100]">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
                        <FiShield size={24} />
                    </div>
                    <span className="text-slate-900 font-black text-xl tracking-tight">SmartShield</span>
                </div>
                <div className="flex items-center gap-8">
                    <Link to="/login" className="text-sm font-bold text-slate-500 hover:text-indigo-600 transition-colors">Sign In</Link>
                    <Link
                        to="/login"
                        state={{ mode: 'register' }}
                        className="px-6 py-2.5 bg-indigo-600 text-white rounded-xl font-bold text-sm shadow-lg shadow-indigo-600/20 hover:bg-indigo-700 transition-all active:scale-95"
                    >
                        Join Network
                    </Link>
                </div>
            </nav>

            {/* Hero */}
            <header className="relative py-20 md:py-32 px-8 overflow-hidden bg-slate-50">
                <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16 items-center relative z-10">
                    <div>
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-100 text-[10px] font-bold text-indigo-600 uppercase tracking-[0.2em] mb-6">
                            <FiActivity /> Next-Gen Route Safety
                        </div>
                        <h1 className="text-5xl md:text-7xl font-black text-slate-900 leading-[1.1] mb-8">
                            Trust Every <span className="text-indigo-600">Coordinate.</span>
                        </h1>
                        <p className="text-lg text-slate-500 leading-relaxed mb-10 max-w-lg font-medium">
                            SmartShield AI monitors 100+ variables in real-time to ensure your fleet, drivers, and deliveries move through the safest, most efficient sectors.
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4">
                            <Link to="/login" className="px-10 py-5 bg-indigo-600 text-white rounded-2xl font-black text-lg flex items-center justify-center gap-3 shadow-2xl shadow-indigo-600/20 hover:scale-[1.02] transition-all">
                                Get Started <FiArrowRight />
                            </Link>
                            <Link to="/login" className="px-10 py-5 bg-white text-slate-900 rounded-2xl font-black text-lg flex items-center justify-center gap-3 border border-slate-200 hover:bg-slate-50 transition-all shadow-sm">
                                Live Demo
                            </Link>
                        </div>
                    </div>

                    <div className="relative">
                        <div className="absolute -inset-10 bg-indigo-500/10 blur-[120px] rounded-full"></div>
                        <div className="relative bg-white border border-slate-200 rounded-[3rem] p-8 shadow-[0_32px_64px_-16px_rgba(0,0,0,0.1)] transform lg:rotate-3 backdrop-blur-xl">
                            {/* Mock Map UI */}
                            <div className="h-64 bg-slate-100 rounded-3xl overflow-hidden relative mb-6 border border-slate-200">
                                <div className="absolute inset-0 opacity-40 bg-[url('https://api.mapbox.com/styles/v1/mapbox/light-v10/static/13,101,12.97,13/500x300?access_token=pk.mock')] bg-center bg-cover"></div>
                                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-4 h-4 bg-indigo-600 rounded-full border-4 border-white animate-ping"></div>
                                <div className="absolute bottom-4 left-4 right-4 h-2 bg-slate-200 rounded-full overflow-hidden">
                                    <div className="w-3/4 h-full bg-indigo-600"></div>
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                                    <p className="text-[10px] text-slate-400 font-bold uppercase mb-1">Safety Index</p>
                                    <p className="text-2xl font-black text-slate-900">98.4</p>
                                </div>
                                <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                                    <p className="text-[10px] text-slate-400 font-bold uppercase mb-1">Time Saved</p>
                                    <p className="text-2xl font-black text-indigo-600">+18%</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* Features */}
            <section className="py-24 bg-white border-t border-slate-100">
                <div className="max-w-6xl mx-auto px-8">
                    <div className="text-center mb-20">
                        <h2 className="text-3xl md:text-5xl font-black text-slate-900 mb-6 tracking-tight">Built for Total Sovereignty.</h2>
                        <p className="text-slate-500 max-w-2xl mx-auto font-medium">Our multi-layered AI architecture provides unparalleled protection and optimization for modern logistics operations.</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        {[
                            { title: 'Trust-Route AI', icon: FiNavigation, desc: 'Dynamic route optimization based on live safety scores and traffic density.', color: 'indigo' },
                            { title: 'Fleet Command', icon: FiMap, desc: 'Real-time monitoring of all active nodes with instant SOS protocols.', color: 'blue' },
                            { title: 'Safe-Sense ML', icon: FiZap, desc: 'Predictive analytics that identify sector risks before they impact your fleet.', color: 'emerald' }
                        ].map((f, i) => (
                            <div key={i} className="p-8 bg-slate-50 rounded-[2.5rem] border border-slate-100 hover:border-indigo-400/30 transition-all group hover:bg-white hover:shadow-xl hover:shadow-indigo-500/5">
                                <div className={`w-16 h-16 bg-white rounded-2xl flex items-center justify-center text-indigo-600 mb-6 group-hover:scale-110 transition-transform shadow-sm border border-slate-100`}>
                                    <f.icon size={32} />
                                </div>
                                <h3 className="text-xl font-bold text-slate-900 mb-4">{f.title}</h3>
                                <p className="text-slate-500 leading-relaxed text-sm font-medium">{f.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA */}
            <section className="py-20 px-8 bg-slate-50">
                <div className="max-w-4xl mx-auto bg-gradient-to-br from-indigo-600 to-blue-700 rounded-[3rem] p-12 md:p-20 text-center shadow-2xl shadow-indigo-900/20 relative overflow-hidden">
                    <FiShield className="absolute -right-10 -bottom-10 text-white/10 w-64 h-64 rotate-12" />
                    <h2 className="text-3xl md:text-5xl font-black text-white mb-8 relative z-10 tracking-tight">Start Protecting Your Journey Today.</h2>
                    <Link to="/login" className="inline-flex items-center gap-3 px-10 py-5 bg-white text-indigo-600 rounded-2xl font-black text-lg hover:scale-[1.05] transition-all relative z-10 shadow-xl">
                        Deploy SmartShield <FiArrowRight />
                    </Link>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-12 border-t border-slate-100 px-8 md:px-20 flex flex-col md:flex-row items-center justify-between gap-8 bg-white">
                <div className="flex items-center gap-3 opacity-80">
                    <FiShield size={20} className="text-indigo-600" />
                    <span className="font-bold tracking-tight text-slate-900">SmartShield</span>
                </div>
                <div className="text-slate-400 text-xs font-bold">
                    © 2026 SmartShield Global. All rights reserved. Secure Logistics Framework.
                </div>
                <div className="flex gap-8">
                    <span className="text-xs font-black text-slate-500 hover:text-indigo-600 cursor-pointer transition-colors">Safety Protocols</span>
                    <span className="text-xs font-black text-slate-500 hover:text-indigo-600 cursor-pointer transition-colors">API Docs</span>
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;
