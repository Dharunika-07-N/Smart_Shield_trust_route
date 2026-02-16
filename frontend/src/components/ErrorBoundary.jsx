import React from 'react';
import { FiAlertTriangle, FiRefreshCw } from 'react-icons/fi';

/**
 * Error Boundary Component
 * Catches React errors and displays user-friendly error messages
 * Prevents entire app crashes
 */
class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            hasError: false,
            error: null,
            errorInfo: null,
            errorCount: 0
        };
    }

    static getDerivedStateFromError(error) {
        // Update state so the next render will show the fallback UI
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        // Log error details
        console.error('Error Boundary caught an error:', error, errorInfo);

        // Update state with error details
        this.setState(prevState => ({
            error,
            errorInfo,
            errorCount: prevState.errorCount + 1
        }));

        // You can also log the error to an error reporting service here
        // Example: logErrorToService(error, errorInfo);
    }

    handleReset = () => {
        this.setState({
            hasError: false,
            error: null,
            errorInfo: null
        });
    };

    handleReload = () => {
        window.location.reload();
    };

    render() {
        if (this.state.hasError) {
            // Fallback UI
            return (
                <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900 flex items-center justify-center p-4">
                    <div className="max-w-2xl w-full bg-white rounded-2xl shadow-2xl overflow-hidden">
                        {/* Header */}
                        <div className="bg-gradient-to-r from-red-500 to-rose-600 p-8 text-white">
                            <div className="flex items-center gap-4 mb-4">
                                <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                                    <FiAlertTriangle className="text-4xl" />
                                </div>
                                <div>
                                    <h1 className="text-3xl font-black">Oops! Something went wrong</h1>
                                    <p className="text-red-100 text-sm mt-1">
                                        We encountered an unexpected error
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Content */}
                        <div className="p-8">
                            <div className="mb-6">
                                <h2 className="text-lg font-bold text-slate-800 mb-2">What happened?</h2>
                                <p className="text-slate-600 text-sm leading-relaxed">
                                    The application encountered an error and couldn't continue. This has been logged
                                    and our team will look into it. You can try refreshing the page or going back to
                                    the dashboard.
                                </p>
                            </div>

                            {/* Error Details (Development Mode) */}
                            {process.env.NODE_ENV === 'development' && this.state.error && (
                                <div className="mb-6">
                                    <h3 className="text-sm font-bold text-slate-700 mb-2">Error Details (Dev Mode)</h3>
                                    <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 overflow-auto max-h-48">
                                        <p className="text-xs font-mono text-red-600 mb-2">
                                            {this.state.error.toString()}
                                        </p>
                                        {this.state.errorInfo && (
                                            <pre className="text-xs text-slate-600 whitespace-pre-wrap">
                                                {this.state.errorInfo.componentStack}
                                            </pre>
                                        )}
                                    </div>
                                </div>
                            )}

                            {/* Action Buttons */}
                            <div className="flex flex-col sm:flex-row gap-3">
                                <button
                                    onClick={this.handleReset}
                                    className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-xl font-bold hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-600/20"
                                >
                                    <FiRefreshCw className="text-lg" />
                                    Try Again
                                </button>
                                <button
                                    onClick={this.handleReload}
                                    className="flex-1 px-6 py-3 bg-slate-100 text-slate-700 rounded-xl font-bold hover:bg-slate-200 transition-all"
                                >
                                    Reload Page
                                </button>
                                <button
                                    onClick={() => window.location.href = '/dashboard'}
                                    className="flex-1 px-6 py-3 bg-slate-100 text-slate-700 rounded-xl font-bold hover:bg-slate-200 transition-all"
                                >
                                    Go to Dashboard
                                </button>
                            </div>

                            {/* Error Count Warning */}
                            {this.state.errorCount > 2 && (
                                <div className="mt-4 p-4 bg-amber-50 border border-amber-200 rounded-lg">
                                    <p className="text-xs text-amber-800">
                                        <strong>Multiple errors detected.</strong> If this persists, please try:
                                        <ul className="list-disc list-inside mt-2 space-y-1">
                                            <li>Clearing your browser cache</li>
                                            <li>Using a different browser</li>
                                            <li>Contacting support if the issue continues</li>
                                        </ul>
                                    </p>
                                </div>
                            )}
                        </div>

                        {/* Footer */}
                        <div className="bg-slate-50 border-t border-slate-200 px-8 py-4">
                            <p className="text-xs text-slate-500 text-center">
                                Need help? Contact support at{' '}
                                <a href="mailto:support@smartshield.com" className="text-indigo-600 hover:underline">
                                    support@smartshield.com
                                </a>
                            </p>
                        </div>
                    </div>
                </div>
            );
        }

        // Normally, just render children
        return this.props.children;
    }
}

export default ErrorBoundary;
