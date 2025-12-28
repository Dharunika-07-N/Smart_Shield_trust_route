import React, { useState } from 'react';
import { api } from '../services/api';

const FeedbackForm = ({ routeId, riderId, onComplete }) => {
    const [formData, setFormData] = useState({
        safety_rating: 5,
        route_quality_rating: 5,
        comfort_rating: 5,
        feedback_text: '',
    });
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await api.post('/feedback/submit', {
                ...formData,
                route_id: routeId,
                rider_id: riderId || 'guest_rider'
            });
            setSuccess(true);
            if (onComplete) setTimeout(onComplete, 2000);
        } catch (error) {
            console.error("Feedback error:", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-white rounded-xl shadow-lg p-6 max-w-md mx-auto">
            <h3 className="text-xl font-bold mb-4">How was your journey?</h3>
            {success ? (
                <div className="bg-green-100 text-green-700 p-4 rounded-lg text-center">
                    ✅ Thank you! Your feedback helps us improve route safety.
                </div>
            ) : (
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Safety Rating (1-10)</label>
                        <input
                            type="range" min="1" max="10"
                            value={formData.safety_rating}
                            onChange={(e) => setFormData({ ...formData, safety_rating: parseInt(e.target.value) })}
                            className="w-full"
                        />
                        <div className="flex justify-between text-xs text-gray-500">
                            <span>Unsafe</span><span>Safe</span>
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Route Smoothness</label>
                        <input
                            type="range" min="1" max="10"
                            value={formData.route_quality_rating}
                            onChange={(e) => setFormData({ ...formData, route_quality_rating: parseInt(e.target.value) })}
                            className="w-full"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Comments</label>
                        <textarea
                            className="w-full border border-gray-300 rounded-lg p-2 h-24"
                            placeholder="Any incidents or unsafe areas encountered?"
                            value={formData.feedback_text}
                            onChange={(e) => setFormData({ ...formData, feedback_text: e.target.value })}
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg transition-colors"
                    >
                        {loading ? 'Submitting...' : 'Submit Feedback'}
                    </button>
                </form>
            )}
        </div>
    );
};

export default FeedbackForm;
