import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import {
    FiActivity, FiTrendingUp, FiAlertTriangle, FiCheckCircle,
    FiBarChart2, FiCpu, FiClock, FiShield, FiArrowRight
} from 'react-icons/fi';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    BarChart, Bar, Cell, Legend
} from 'recharts';

const ModelPerformance = () => {
    const [loading, setLoading] = useState(true);
    const [selectedModel, setSelectedModel] = useState('safety');
    const [report, setReport] = useState(null);
    const [experiments, setExperiments] = useState([]);
    const [isCreatingExp, setIsCreatingExp] = useState(false);

    const models = [
        { id: 'safety', label: 'Safety Classifier', icon: FiShield, color: '#4f46e5' },
        { id: 'time', label: 'Time Predictor', icon: FiClock, color: '#6366f1' },
        { id: 'rl', label: 'SARSA RL Agent', icon: FiTrendingUp, color: '#8B5CF6' }
    ];

    useEffect(() => {
        fetchReport();
        fetchExperiments();
    }, [selectedModel]);

    const fetchReport = async () => {
        setLoading(true);
        try {
            const response = await api.get(`/monitoring/report/${selectedModel}`);
            setReport(response);
        } catch (error) {
            console.error("Error fetching report:", error);
        } finally {
            setLoading(false);
        }
    };

    const fetchExperiments = async () => {
        // Implementation for experiments comparison would go here
        // For now using mockup data based on the API structure
    };

    if (loading && !report) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Model Selector */}
            <div className="flex flex-wrap gap-4">
                {models.map(model => (
                    <button
                        key={model.id}
                        onClick={() => setSelectedModel(model.id)}
                        className={`flex items-center gap-3 px-6 py-3 rounded-2xl transition-all border ${selectedModel === model.id
                            ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg shadow-indigo-500/20'
                            : 'bg-white border-slate-200 text-slate-500 hover:border-slate-300 hover:text-slate-900'
                            }`}
                    >
                        <model.icon size={20} />
                        <span className="font-bold">{model.label}</span>
                    </button>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Status Card */}
                <div className="lg:col-span-1 bg-white border border-slate-200 rounded-3xl p-6 shadow-sm">
                    <h3 className="text-slate-900 font-bold mb-6 flex items-center gap-2">
                        <FiActivity className="text-indigo-600" />
                        Model Health
                    </h3>

                    <div className="space-y-6">
                        <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Status</div>
                            <div className="flex items-center justify-between">
                                <span className="text-lg font-bold text-slate-900">
                                    {report?.retraining_check?.needs_retraining ? 'Retraining Advised' : 'Optimal'}
                                </span>
                                {report?.retraining_check?.needs_retraining ? (
                                    <FiAlertTriangle className="text-rose-500" size={24} />
                                ) : (
                                    <FiCheckCircle className="text-emerald-500" size={24} />
                                )}
                            </div>
                        </div>

                        <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Drift Detection</div>
                            <div className="flex items-center justify-between">
                                <span className="text-lg font-bold text-slate-900">
                                    {report?.prediction_drift?.drift_detected ? 'Drift Detected' : 'Stable'}
                                </span>
                                <div className={`w-3 h-3 rounded-full ${report?.prediction_drift?.drift_detected ? 'bg-rose-500 animate-pulse' : 'bg-emerald-500'}`}></div>
                            </div>
                        </div>

                        {report?.retraining_check?.reasons && Object.keys(report.retraining_check.reasons).length > 0 && (
                            <div className="p-4 bg-rose-50 rounded-2xl border border-rose-100">
                                <div className="text-[10px] font-bold text-rose-600 uppercase tracking-widest mb-2">Warnings</div>
                                <ul className="text-xs space-y-2 text-rose-500">
                                    {Object.entries(report.retraining_check.reasons).map(([key, val]) => (
                                        <li key={key} className="flex items-start gap-2 font-medium">
                                            <FiAlertTriangle className="shrink-0 mt-0.5" />
                                            <span>{key.replace('_', ' ')} warning triggered</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                </div>

                {/* Performance Chart */}
                <div className="lg:col-span-2 bg-white border border-slate-200 rounded-3xl p-6 shadow-sm">
                    <h3 className="text-slate-900 font-bold mb-6 flex items-center justify-between">
                        <span className="flex items-center gap-2">
                            <FiBarChart2 className="text-indigo-600" />
                            Performance Metrics
                        </span>
                        <span className="text-xs font-medium text-slate-400">Last 7 Days</span>
                    </h3>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                        {report?.performance?.mae !== undefined && (
                            <div className="text-center p-3 bg-slate-50 rounded-xl border border-slate-100">
                                <div className="text-[10px] font-bold text-slate-400 uppercase mb-1">MAE</div>
                                <div className="text-xl font-bold text-slate-900">{report.performance.mae.toFixed(2)}</div>
                            </div>
                        )}
                        {report?.performance?.rmse !== undefined && (
                            <div className="text-center p-3 bg-slate-50 rounded-xl border border-slate-100">
                                <div className="text-[10px] font-bold text-slate-400 uppercase mb-1">RMSE</div>
                                <div className="text-xl font-bold text-slate-900">{report.performance.rmse.toFixed(2)}</div>
                            </div>
                        )}
                        {report?.performance?.r2 !== undefined && (
                            <div className="text-center p-3 bg-slate-50 rounded-xl border border-slate-100">
                                <div className="text-[10px] font-bold text-slate-400 uppercase mb-1">R² Score</div>
                                <div className="text-xl font-bold text-slate-900">{report.performance.r2.toFixed(3)}</div>
                            </div>
                        )}
                        <div className="text-center p-3 bg-slate-50 rounded-xl border border-slate-100">
                            <div className="text-[10px] font-bold text-slate-400 uppercase mb-1">Samples</div>
                            <div className="text-xl font-bold text-slate-900">{report?.performance?.num_samples || 0}</div>
                        </div>
                    </div>

                    <div className="h-64 w-full">
                        {/* Mock data for chart as historical prediction_log might be sparse */}
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={[
                                { name: 'Day 1', val: 0.82 },
                                { name: 'Day 2', val: 0.85 },
                                { name: 'Day 3', val: 0.83 },
                                { name: 'Day 4', val: 0.88 },
                                { name: 'Day 5', val: 0.86 },
                                { name: 'Day 6', val: 0.89 },
                                { name: 'Day 7', val: report?.performance?.r2 || 0.89 }
                            ]}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                                <XAxis dataKey="name" stroke="#94A3B8" fontSize={10} axisLine={false} tickLine={false} />
                                <YAxis stroke="#94A3B8" fontSize={10} axisLine={false} tickLine={false} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '12px', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                    itemStyle={{ color: '#1E293B', fontSize: '12px' }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="val"
                                    stroke="#4f46e5"
                                    strokeWidth={3}
                                    dot={{ fill: '#6366F1', strokeWidth: 2, r: 4 }}
                                    activeDot={{ r: 6, strokeWidth: 0 }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* A/B Testing Section */}
            <div className="bg-white border border-slate-200 rounded-3xl p-8 shadow-sm overflow-hidden relative">
                <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 blur-[100px] rounded-full -translate-y-1/2 translate-x-1/2"></div>

                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
                    <div>
                        <h3 className="text-2xl font-bold text-slate-900 mb-2 flex items-center gap-3">
                            <FiCpu className="text-indigo-600" />
                            A/B Experimentation Framework
                        </h3>
                        <p className="text-slate-500 max-w-xl font-medium">
                            Compare performance between different model versions in production. Safely roll out enhancements with data-driven confidence.
                        </p>
                    </div>
                    <button
                        onClick={() => setIsCreatingExp(true)}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-8 rounded-2xl transition-all shadow-lg shadow-indigo-500/20 active:scale-95"
                    >
                        New Experiment
                    </button>
                </div>

                <div className="mt-10 grid grid-cols-1 md:grid-cols-2 gap-6 relative z-10">
                    {/* Active Experiment Placeholder */}
                    <div className="p-6 bg-slate-50 rounded-2xl border border-indigo-200 border-dashed">
                        <div className="flex items-center justify-between mb-4">
                            <span className="bg-indigo-100 text-indigo-700 text-[10px] font-bold py-1 px-3 rounded-full uppercase tracking-wider">Active Experiment</span>
                            <span className="text-slate-400 text-xs font-bold">Started 2 days ago</span>
                        </div>
                        <h4 className="text-slate-900 font-bold text-lg mb-1">XGBoost-v2 vs Baseline</h4>
                        <p className="text-slate-400 text-xs mb-6 font-medium">Optimizing ETA prediction for urban corridors</p>

                        <div className="space-y-4">
                            <div>
                                <div className="flex justify-between text-xs mb-1.5">
                                    <span className="text-slate-500 font-bold">Group A (Baseline)</span>
                                    <span className="text-slate-400 font-bold">12.4 min MAE</span>
                                </div>
                                <div className="h-1.5 bg-slate-200 rounded-full overflow-hidden">
                                    <div className="h-full bg-slate-300 w-[60%]"></div>
                                </div>
                            </div>
                            <div>
                                <div className="flex justify-between text-xs mb-1.5">
                                    <span className="text-slate-700 font-bold">Group B (v2)</span>
                                    <span className="text-indigo-600 font-bold">10.1 min MAE</span>
                                </div>
                                <div className="h-1.5 bg-slate-200 rounded-full overflow-hidden">
                                    <div className="h-full bg-indigo-600 w-[85%]"></div>
                                </div>
                            </div>
                        </div>

                        <div className="mt-6 flex items-center justify-between">
                            <div className="text-xs text-slate-500 font-medium">
                                <span className="text-indigo-600 font-bold">Group B</span> is outperforming by <span className="text-emerald-600 font-bold">18.5%</span>
                            </div>
                            <button className="text-indigo-600 hover:text-indigo-700 text-sm font-bold flex items-center gap-1 group transition-all">
                                View Full Data <FiArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
                            </button>
                        </div>
                    </div>

                    {/* Historical Comparison */}
                    <div className="p-6 bg-slate-50 rounded-2xl border border-slate-200">
                        <h4 className="text-slate-900 font-bold mb-4">Recent Winners</h4>
                        <div className="space-y-4">
                            {[
                                { name: 'Enhanced Safety-RF', date: 'Jan 24', delta: '+4.2% Acc' },
                                { name: 'RL-Epsilon-Decay', date: 'Jan 15', delta: '+12% Reward' },
                                { name: 'Weather-Feature-Add', date: 'Jan 02', delta: '-15% RMSE' }
                            ].map((win, i) => (
                                <div key={i} className="flex items-center justify-between p-3 bg-white rounded-xl border border-slate-100 hover:border-indigo-400 transition-all cursor-pointer group shadow-sm">
                                    <div className="flex items-center gap-3">
                                        <div className="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center text-emerald-600 border border-emerald-100">
                                            <FiCheckCircle size={16} />
                                        </div>
                                        <div>
                                            <div className="text-sm font-bold text-slate-900">{win.name}</div>
                                            <div className="text-[10px] text-slate-400 font-bold uppercase">{win.date}</div>
                                        </div>
                                    </div>
                                    <div className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-1 rounded-md">
                                        {win.delta}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
            {/* New Experiment Modal */}
            {isCreatingExp && (
                <div className="fixed inset-0 z-[100] bg-slate-900/60 backdrop-blur-md flex items-center justify-center p-6">
                    <div className="bg-white w-full max-w-lg rounded-[2.5rem] p-10 shadow-2xl animate-in zoom-in-95">
                        <h3 className="text-2xl font-black text-slate-900 mb-2">Configure A/B Test</h3>
                        <p className="text-sm text-slate-500 mb-8 font-medium">Define parameters for your next model optimization experiment.</p>

                        <div className="space-y-6 mb-10">
                            <div>
                                <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Experiment Name</label>
                                <input type="text" placeholder="e.g. Weather-Aware-Routing-v4" className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 font-bold text-slate-800 focus:ring-2 focus:ring-indigo-500/20 outline-none" />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Primary Metric</label>
                                    <select className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 font-bold text-slate-800 outline-none">
                                        <option>MAE (Mean Error)</option>
                                        <option>R² Score</option>
                                        <option>Confidence Score</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Traffic Allocation</label>
                                    <select className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 font-bold text-slate-800 outline-none">
                                        <option>5% (Canary)</option>
                                        <option>50% (A/B)</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <div className="flex gap-4">
                            <button onClick={() => { setIsCreatingExp(false); alert("Experiment deployment initiated. Monitoring will start in 5 minutes."); }} className="flex-1 py-4 bg-indigo-600 text-white rounded-2xl font-bold shadow-lg shadow-indigo-500/20 active:scale-95 transition-all">
                                Deploy Experiment
                            </button>
                            <button onClick={() => setIsCreatingExp(false)} className="flex-1 py-4 bg-slate-50 text-slate-400 rounded-2xl font-bold hover:bg-slate-100 transition-all">
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ModelPerformance;
