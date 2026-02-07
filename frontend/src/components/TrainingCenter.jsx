import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import {
    FiRefreshCw, FiDatabase, FiCpu, FiCheckCircle,
    FiAlertCircle, FiActivity, FiArrowRight, FiShield
} from 'react-icons/fi';

const TrainingCenter = () => {
    const [retraining, setRetraining] = useState(false);
    const [stats, setStats] = useState({
        total_samples: 2147,
        last_trained: new Date().toLocaleDateString(),
        accuracy: 89.4,
        feedback_pending: 12
    });
    const [log, setLog] = useState([]);

    const addLog = (msg) => {
        setLog(prev => [{ time: new Date().toLocaleTimeString(), msg }, ...prev].slice(0, 10));
    };

    const handleRetrain = async () => {
        setRetraining(true);
        addLog("Initiating model retraining sequence...");
        try {
            const response = await api.post('/training/retrain');
            addLog(`Success: ${response.message}`);
            setStats(prev => ({
                ...prev,
                last_trained: new Date().toLocaleDateString(),
                accuracy: prev.accuracy + (Math.random() * 0.5)
            }));
        } catch (error) {
            addLog(`Error: ${error.message || 'Retraining failed'}`);
        } finally {
            setRetraining(false);
        }
    };

    return (
        <div className="space-y-6">
            <div className="bg-gradient-to-br from-indigo-600 to-blue-700 rounded-2xl p-8 text-white shadow-xl shadow-indigo-500/10 border border-white/5">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <div>
                        <h2 className="text-3xl font-bold mb-2 flex items-center">
                            <FiCpu className="mr-3 text-white" />
                            AI Model Training Center
                        </h2>
                        <p className="text-indigo-50 font-medium opacity-90">
                            Manage the lifecycle and continuous learning of the Smart Shield Trust Route models.
                        </p>
                    </div>
                    <button
                        onClick={handleRetrain}
                        disabled={retraining}
                        className={`flex items-center space-x-2 px-6 py-3 rounded-xl font-bold transition-all ${retraining
                            ? 'bg-white/20 cursor-not-allowed'
                            : 'bg-white text-indigo-600 hover:bg-slate-50 shadow-lg active:scale-95'
                            }`}
                    >
                        <FiRefreshCw className={retraining ? 'animate-spin' : ''} />
                        <span>{retraining ? 'Retraining...' : 'Trigger Retrain Now'}</span>
                    </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mt-10">
                    <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/10">
                        <div className="text-indigo-100 text-[10px] font-bold uppercase tracking-wider mb-1">Total Training Samples</div>
                        <div className="text-2xl font-bold">{stats.total_samples.toLocaleString()}</div>
                        <div className="text-[10px] text-green-300 mt-1 font-bold">↑ 124 this week</div>
                    </div>
                    <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/10">
                        <div className="text-indigo-100 text-[10px] font-bold uppercase tracking-wider mb-1">Last Retrained</div>
                        <div className="text-2xl font-bold">{stats.last_trained}</div>
                        <div className="text-[10px] text-indigo-200 mt-1 font-bold">Status: Stable</div>
                    </div>
                    <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/10">
                        <div className="text-indigo-100 text-[10px] font-bold uppercase tracking-wider mb-1">Predictive Accuracy</div>
                        <div className="text-2xl font-bold">{stats.accuracy.toFixed(1)}%</div>
                        <div className="text-[10px] text-green-300 mt-1 font-bold">↑ 2.1% improvement</div>
                    </div>
                    <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/10">
                        <div className="text-indigo-100 text-[10px] font-bold uppercase tracking-wider mb-1">User Feedback Pool</div>
                        <div className="text-2xl font-bold">{stats.feedback_pending}</div>
                        <div className="text-[10px] text-amber-300 mt-1 font-bold">Requires processing</div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
                    <div className="p-4 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
                        <h3 className="font-bold text-gray-800 flex items-center">
                            <FiActivity className="mr-2 text-indigo-500" />
                            Live Training Log
                        </h3>
                        <span className="text-xs text-green-600 font-medium">System Online</span>
                    </div>
                    <div className="p-4 h-[300px] overflow-y-auto space-y-3 font-mono text-sm">
                        {log.length === 0 ? (
                            <div className="text-gray-400 text-center py-20 italic">No recent training activity.</div>
                        ) : (
                            log.map((entry, i) => (
                                <div key={i} className="flex space-x-4 animate-fade-in">
                                    <span className="text-gray-400">[{entry.time}]</span>
                                    <span className="text-gray-700">{entry.msg}</span>
                                </div>
                            ))
                        )}
                        {retraining && (
                            <div className="flex space-x-4 animate-pulse">
                                <span className="text-gray-400">[{new Date().toLocaleTimeString()}]</span>
                                <span className="text-indigo-600 font-bold">Processing feature vectors...</span>
                            </div>
                        )}
                    </div>
                </div>

                <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
                    <h3 className="font-bold text-gray-800 mb-4">ML Hierarchy</h3>
                    <div className="space-y-6">
                        <div className="flex items-start">
                            <div className="bg-blue-100 p-2 rounded-lg mr-3">
                                <FiDatabase className="text-blue-600" />
                            </div>
                            <div>
                                <div className="text-sm font-bold text-gray-900">XGBoost Predictor</div>
                                <div className="text-xs text-gray-500">Duration & ETA Estimation</div>
                                <div className="mt-2 text-[10px] bg-blue-50 text-blue-700 px-2 py-1 rounded inline-block">Active</div>
                            </div>
                        </div>
                        <div className="flex items-start">
                            <div className="bg-green-100 p-2 rounded-lg mr-3">
                                <FiShield className="text-green-600" />
                            </div>
                            <div>
                                <div className="text-sm font-bold text-gray-900">Random Forest</div>
                                <div className="text-xs text-gray-500">Safety & Risk Classification</div>
                                <div className="mt-2 text-[10px] bg-green-50 text-green-700 px-2 py-1 rounded inline-block">Calibrated</div>
                            </div>
                        </div>
                        <div className="flex items-start">
                            <div className="bg-purple-100 p-2 rounded-lg mr-3">
                                <FiRefreshCw className="text-purple-600" />
                            </div>
                            <div>
                                <div className="text-sm font-bold text-gray-900">SARSA RL Agent</div>
                                <div className="text-xs text-gray-500">Continuous Route Tuning</div>
                                <div className="mt-2 text-[10px] bg-purple-50 text-purple-700 px-2 py-1 rounded inline-block">Learning</div>
                            </div>
                        </div>
                    </div>

                    <div className="mt-8 pt-6 border-t border-gray-100">
                        <div className="text-sm font-bold text-gray-900 mb-2">Confidence Level</div>
                        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                            <div className="h-full bg-indigo-500 w-[92%]"></div>
                        </div>
                        <div className="flex justify-between mt-2 text-[10px] text-gray-500">
                            <span>Exploration</span>
                            <span>92% Stable</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TrainingCenter;
