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

    const models = [
        { id: 'safety', label: 'Safety Classifier', icon: FiShield, color: '#10B981' },
        { id: 'time', label: 'Time Predictor', icon: FiClock, color: '#3B82F6' },
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
            setReport(response.data);
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
                            ? 'bg-indigo-500 border-indigo-400 text-white shadow-lg shadow-indigo-500/20'
                            : 'bg-slate-800/50 border-slate-700 text-slate-400 hover:border-slate-600'
                            }`}
                    >
                        <model.icon size={20} />
                        <span className="font-bold">{model.label}</span>
                    </button>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Status Card */}
                <div className="lg:col-span-1 bg-slate-800/50 border border-slate-700 rounded-3xl p-6 backdrop-blur-xl">
                    <h3 className="text-white font-bold mb-6 flex items-center gap-2">
                        <FiActivity className="text-indigo-400" />
                        Model Health
                    </h3>

                    <div className="space-y-6">
                        <div className="p-4 bg-slate-900/50 rounded-2xl border border-slate-700">
                            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Status</div>
                            <div className="flex items-center justify-between">
                                <span className="text-lg font-bold text-white">
                                    {report?.retraining_check?.needs_retraining ? 'Retraining Advised' : 'Optimal'}
                                </span>
                                {report?.retraining_check?.needs_retraining ? (
                                    <FiAlertTriangle className="text-rose-500" size={24} />
                                ) : (
                                    <FiCheckCircle className="text-emerald-500" size={24} />
                                )}
                            </div>
                        </div>

                        <div className="p-4 bg-slate-900/50 rounded-2xl border border-slate-700">
                            <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Drift Detection</div>
                            <div className="flex items-center justify-between">
                                <span className="text-lg font-bold text-white">
                                    {report?.prediction_drift?.drift_detected ? 'Drift Detected' : 'Stable'}
                                </span>
                                <div className={`w-3 h-3 rounded-full ${report?.prediction_drift?.drift_detected ? 'bg-rose-500 animate-pulse' : 'bg-emerald-500'}`}></div>
                            </div>
                        </div>

                        {report?.retraining_check?.reasons && Object.keys(report.retraining_check.reasons).length > 0 && (
                            <div className="p-4 bg-rose-500/10 rounded-2xl border border-rose-500/20">
                                <div className="text-[10px] font-bold text-rose-400 uppercase tracking-widest mb-2">Warnings</div>
                                <ul className="text-xs space-y-2 text-rose-300">
                                    {Object.entries(report.retraining_check.reasons).map(([key, val]) => (
                                        <li key={key} className="flex items-start gap-2">
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
                <div className="lg:col-span-2 bg-slate-800/50 border border-slate-700 rounded-3xl p-6 backdrop-blur-xl">
                    <h3 className="text-white font-bold mb-6 flex items-center justify-between">
                        <span className="flex items-center gap-2">
                            <FiBarChart2 className="text-indigo-400" />
                            Performance Metrics
                        </span>
                        <span className="text-xs font-medium text-slate-500">Last 7 Days</span>
                    </h3>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                        {report?.performance?.mae !== undefined && (
                            <div className="text-center p-3 bg-slate-900/50 rounded-xl border border-slate-700">
                                <div className="text-[10px] font-bold text-slate-500 uppercase mb-1">MAE</div>
                                <div className="text-xl font-bold text-white">{report.performance.mae.toFixed(2)}</div>
                            </div>
                        )}
                        {report?.performance?.rmse !== undefined && (
                            <div className="text-center p-3 bg-slate-900/50 rounded-xl border border-slate-700">
                                <div className="text-[10px] font-bold text-slate-500 uppercase mb-1">RMSE</div>
                                <div className="text-xl font-bold text-white">{report.performance.rmse.toFixed(2)}</div>
                            </div>
                        )}
                        {report?.performance?.r2 !== undefined && (
                            <div className="text-center p-3 bg-slate-900/50 rounded-xl border border-slate-700">
                                <div className="text-[10px] font-bold text-slate-500 uppercase mb-1">R² Score</div>
                                <div className="text-xl font-bold text-white">{report.performance.r2.toFixed(3)}</div>
                            </div>
                        )}
                        <div className="text-center p-3 bg-slate-900/50 rounded-xl border border-slate-700">
                            <div className="text-[10px] font-bold text-slate-500 uppercase mb-1">Samples</div>
                            <div className="text-xl font-bold text-white">{report?.performance?.num_samples || 0}</div>
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
                                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
                                <XAxis dataKey="name" stroke="#64748B" fontSize={10} axisLine={false} tickLine={false} />
                                <YAxis stroke="#64748B" fontSize={10} axisLine={false} tickLine={false} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1E293B', border: '1px solid #334155', borderRadius: '12px' }}
                                    itemStyle={{ color: '#F1F5F9', fontSize: '12px' }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="val"
                                    stroke="#6366F1"
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
            <div className="bg-slate-800/50 border border-slate-700 rounded-3xl p-8 backdrop-blur-xl overflow-hidden relative">
                <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 blur-[100px] rounded-full -translate-y-1/2 translate-x-1/2"></div>

                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
                    <div>
                        <h3 className="text-2xl font-bold text-white mb-2 flex items-center gap-3">
                            <FiCpu className="text-indigo-400" />
                            A/B Experimentation Framework
                        </h3>
                        <p className="text-slate-400 max-w-xl">
                            Compare performance between different model versions in production. Safely roll out enhancements with data-driven confidence.
                        </p>
                    </div>
                    <button className="bg-indigo-500 hover:bg-indigo-600 text-white font-bold py-3 px-8 rounded-2xl transition-all shadow-lg shadow-indigo-500/20 active:scale-95">
                        New Experiment
                    </button>
                </div>

                <div className="mt-10 grid grid-cols-1 md:grid-cols-2 gap-6 relative z-10">
                    {/* Active Experiment Placeholder */}
                    <div className="p-6 bg-slate-900/50 rounded-2xl border border-indigo-500/20 border-dashed">
                        <div className="flex items-center justify-between mb-4">
                            <span className="bg-indigo-500/10 text-indigo-400 text-[10px] font-bold py-1 px-3 rounded-full uppercase tracking-wider">Active Experiment</span>
                            <span className="text-slate-500 text-xs">Started 2 days ago</span>
                        </div>
                        <h4 className="text-white font-bold text-lg mb-1">XGBoost-v2 vs Baseline</h4>
                        <p className="text-slate-500 text-xs mb-6">Optimizing ETA prediction for urban corridors</p>

                        <div className="space-y-4">
                            <div>
                                <div className="flex justify-between text-xs mb-1.5">
                                    <span className="text-slate-300 font-medium">Group A (Baseline)</span>
                                    <span className="text-emerald-400 font-bold">12.4 min MAE</span>
                                </div>
                                <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                                    <div className="h-full bg-slate-600 w-[60%]"></div>
                                </div>
                            </div>
                            <div>
                                <div className="flex justify-between text-xs mb-1.5">
                                    <span className="text-slate-300 font-medium">Group B (v2)</span>
                                    <span className="text-indigo-400 font-bold">10.1 min MAE</span>
                                </div>
                                <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                                    <div className="h-full bg-indigo-500 w-[85%]"></div>
                                </div>
                            </div>
                        </div>

                        <div className="mt-6 flex items-center justify-between">
                            <div className="text-xs text-slate-400">
                                <span className="text-indigo-400 font-bold">Group B</span> is outperforming by <span className="text-emerald-400 font-bold">18.5%</span>
                            </div>
                            <button className="text-indigo-400 hover:text-indigo-300 text-sm font-bold flex items-center gap-1 group transition-all">
                                View Full Data <FiArrowRight size={14} className="group-translate-x-1" />
                            </button>
                        </div>
                    </div>

                    {/* Historical Comparison */}
                    <div className="p-6 bg-slate-900/50 rounded-2xl border border-slate-700">
                        <h4 className="text-white font-bold mb-4">Recent Winners</h4>
                        <div className="space-y-4">
                            {[
                                { name: 'Enhanced Safety-RF', date: 'Jan 24', delta: '+4.2% Acc' },
                                { name: 'RL-Epsilon-Decay', date: 'Jan 15', delta: '+12% Reward' },
                                { name: 'Weather-Feature-Add', date: 'Jan 02', delta: '-15% RMSE' }
                            ].map((win, i) => (
                                <div key={i} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-xl border border-slate-700/50 hover:border-indigo-500/30 transition-all cursor-pointer">
                                    <div className="flex items-center gap-3">
                                        <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400">
                                            <FiCheckCircle size={16} />
                                        </div>
                                        <div>
                                            <div className="text-sm font-bold text-white">{win.name}</div>
                                            <div className="text-[10px] text-slate-500 font-bold uppercase">{win.date}</div>
                                        </div>
                                    </div>
                                    <div className="text-xs font-bold text-emerald-400 bg-emerald-500/5 px-2 py-1 rounded-md">
                                        {win.delta}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ModelPerformance;
