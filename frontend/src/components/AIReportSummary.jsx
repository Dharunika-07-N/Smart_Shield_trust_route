import React, { useState, useEffect } from 'react';
import {
    Sparkles,
    TrendingUp,
    Users,
    Bike,
    MessageSquare,
    Brain,
    Download,
    RefreshCw,
    Calendar,
    ChevronDown,
    AlertCircle,
    CheckCircle,
    Clock,
    Zap
} from 'lucide-react';
import './AIReportSummary.css';
import { api } from '../services/api';

const AIReportSummary = () => {
    const [activeTab, setActiveTab] = useState('executive');
    const [timePeriod, setTimePeriod] = useState('weekly');
    const [summaries, setSummaries] = useState({});
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [aiProvider, setAiProvider] = useState('openai');
    const [expandedSections, setExpandedSections] = useState({});

    const reportTypes = [
        { id: 'executive', label: 'Executive Dashboard', icon: Sparkles, color: '#8b5cf6' },
        { id: 'user', label: 'User Activity', icon: Users, color: '#3b82f6' },
        { id: 'rider', label: 'Rider Performance', icon: Bike, color: '#10b981' },
        { id: 'feedback', label: 'Feedback Analysis', icon: MessageSquare, color: '#f59e0b' },
        { id: 'ml', label: 'ML Performance', icon: Brain, color: '#ec4899' }
    ];

    const timePeriods = [
        { value: 'daily', label: 'Last 24 Hours' },
        { value: 'weekly', label: 'Last 7 Days' },
        { value: 'monthly', label: 'Last 30 Days' }
    ];

    const aiProviders = [
        { value: 'openai', label: 'GPT-4', icon: '🤖' },
        { value: 'anthropic', label: 'Claude', icon: '🧠' },
        { value: 'gemini', label: 'Gemini', icon: '✨' }
    ];

    useEffect(() => {
        fetchSummary(activeTab);
    }, [activeTab, timePeriod, aiProvider]);

    const fetchSummary = async (reportType) => {
        setLoading(true);
        setError(null);

        try {
            let endpoint = '';

            switch (reportType) {
                case 'executive':
                    endpoint = '/ai/reports/executive-dashboard';
                    break;
                case 'user':
                    endpoint = '/ai/reports/user-summary';
                    break;
                case 'rider':
                    endpoint = '/ai/reports/rider-summary';
                    break;
                case 'feedback':
                    endpoint = '/ai/reports/feedback-summary';
                    break;
                case 'ml':
                    endpoint = '/ai/reports/ml-performance';
                    break;
                default:
                    endpoint = '/ai/reports/executive-dashboard';
            }

            const data = await api.post(endpoint, {
                time_period: timePeriod,
                provider: aiProvider,
                format: 'json'
            });

            setSummaries(prev => ({ ...prev, [reportType]: data }));
        } catch (err) {
            setError(err.message || 'Failed to fetch summary');
            console.error('Error fetching summary:', err);
        } finally {
            setLoading(false);
        }
    };

    const downloadReport = (format) => {
        const summary = summaries[activeTab];
        if (!summary) return;

        const blob = new Blob([summary.summary], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `smart-shield-${activeTab}-report-${Date.now()}.${format}`;
        a.click();
        URL.revokeObjectURL(url);
    };

    const toggleSection = (section) => {
        setExpandedSections(prev => ({
            ...prev,
            [section]: !prev[section]
        }));
    };

    const parseSummary = (summaryText) => {
        if (!summaryText) return [];

        const sections = summaryText.split(/\n(?=\d+\.\s+\*\*|\*\*)/);
        return sections.map((section, index) => {
            const titleMatch = section.match(/\*\*(.+?)\*\*/);
            const title = titleMatch ? titleMatch[1] : `Section ${index + 1}`;
            const content = section.replace(/\*\*(.+?)\*\*/, '').trim();

            return { title, content, id: `section-${index}` };
        });
    };

    const renderSummaryContent = () => {
        const summary = summaries[activeTab];
        if (!summary) return null;

        const sections = parseSummary(summary.summary);

        return (
            <div className="summary-content">
                <div className="summary-header">
                    <div className="summary-meta">
                        <div className="meta-item">
                            <Clock size={16} />
                            <span>Generated: {new Date(summary.generated_at).toLocaleString()}</span>
                        </div>
                        <div className="meta-item">
                            <Calendar size={16} />
                            <span>Period: {summary.time_period || timePeriod}</span>
                        </div>
                        <div className="meta-item">
                            <Zap size={16} />
                            <span>AI: {aiProvider.toUpperCase()}</span>
                        </div>
                    </div>
                    <div className="summary-actions">
                        <button
                            className="action-btn refresh"
                            onClick={() => fetchSummary(activeTab)}
                            disabled={loading}
                        >
                            <RefreshCw size={16} className={loading ? 'spinning' : ''} />
                            Refresh
                        </button>
                        <button
                            className="action-btn download"
                            onClick={() => downloadReport('txt')}
                        >
                            <Download size={16} />
                            Download
                        </button>
                    </div>
                </div>

                <div className="summary-sections">
                    {sections.map((section, index) => (
                        <div
                            key={section.id}
                            className={`summary-section ${expandedSections[section.id] ? 'expanded' : ''}`}
                        >
                            <div
                                className="section-header"
                                onClick={() => toggleSection(section.id)}
                            >
                                <div className="section-title">
                                    <span className="section-number">{index + 1}</span>
                                    <h3>{section.title}</h3>
                                </div>
                                <ChevronDown
                                    size={20}
                                    className={`chevron ${expandedSections[section.id] ? 'rotated' : ''}`}
                                />
                            </div>
                            <div className="section-content">
                                <p>{section.content}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    return (
        <div className="ai-report-summary">
            <div className="report-header">
                <div className="header-content">
                    <div className="header-title">
                        <Sparkles className="sparkle-icon" size={32} />
                        <div>
                            <h1>AI-Powered Insights</h1>
                            <p>Intelligent summaries generated from your data</p>
                        </div>
                    </div>

                    <div className="header-controls">
                        <div className="control-group">
                            <label>Time Period</label>
                            <select
                                value={timePeriod}
                                onChange={(e) => setTimePeriod(e.target.value)}
                                className="period-select"
                            >
                                {timePeriods.map(period => (
                                    <option key={period.value} value={period.value}>
                                        {period.label}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div className="control-group">
                            <label>AI Model</label>
                            <select
                                value={aiProvider}
                                onChange={(e) => setAiProvider(e.target.value)}
                                className="provider-select"
                            >
                                {aiProviders.map(provider => (
                                    <option key={provider.value} value={provider.value}>
                                        {provider.icon} {provider.label}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>
                </div>

                <div className="report-tabs">
                    {reportTypes.map(report => {
                        const Icon = report.icon;
                        return (
                            <button
                                key={report.id}
                                className={`tab-btn ${activeTab === report.id ? 'active' : ''}`}
                                onClick={() => setActiveTab(report.id)}
                                style={{
                                    '--tab-color': report.color
                                }}
                            >
                                <Icon size={20} />
                                <span>{report.label}</span>
                            </button>
                        );
                    })}
                </div>
            </div>

            <div className="report-body">
                {loading && (
                    <div className="loading-state">
                        <div className="loading-spinner">
                            <Brain className="brain-icon" size={48} />
                            <div className="loading-dots">
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>
                        </div>
                        <p>AI is analyzing your data...</p>
                    </div>
                )}

                {error && (
                    <div className="error-state">
                        <AlertCircle size={48} />
                        <h3>Failed to Generate Summary</h3>
                        <p>{error}</p>
                        <button
                            className="retry-btn"
                            onClick={() => fetchSummary(activeTab)}
                        >
                            <RefreshCw size={16} />
                            Try Again
                        </button>
                    </div>
                )}

                {!loading && !error && summaries[activeTab] && renderSummaryContent()}

                {!loading && !error && !summaries[activeTab] && (
                    <div className="empty-state">
                        <CheckCircle size={48} />
                        <h3>No Summary Available</h3>
                        <p>Generate a summary to see AI-powered insights</p>
                        <button
                            className="generate-btn"
                            onClick={() => fetchSummary(activeTab)}
                        >
                            <Sparkles size={16} />
                            Generate Summary
                        </button>
                    </div>
                )}
            </div>

            <div className="report-footer">
                <div className="footer-info">
                    <Sparkles size={16} />
                    <span>Powered by Advanced AI • Real-time Analysis • Actionable Insights</span>
                </div>
            </div>
        </div>
    );
};

export default AIReportSummary;
