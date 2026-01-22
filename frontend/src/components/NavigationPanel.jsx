import React, { useState, useEffect, useCallback } from 'react';
import { FiNavigation, FiPlay, FiPause, FiSquare, FiChevronRight, FiClock, FiMapPin, FiVolume2, FiVolumeX } from 'react-icons/fi';

const NavigationPanel = ({
    route,
    currentLocation,
    onNavigationEnd,
    onStepChange
}) => {
    const [isNavigating, setIsNavigating] = useState(false);
    const [isPaused, setIsPaused] = useState(false);
    const [currentStepIndex, setCurrentStepIndex] = useState(0);
    const [distanceRemaining, setDistanceRemaining] = useState(0);
    const [timeRemaining, setTimeRemaining] = useState(0);
    const [voiceEnabled, setVoiceEnabled] = useState(false);
    const [lastSpokenStep, setLastSpokenStep] = useState(-1);

    // Extract navigation steps from route
    const steps = route?.segments?.[0]?.instructions || [];
    const currentStep = steps[currentStepIndex];

    // Calculate remaining distance and time
    useEffect(() => {
        if (!route || !isNavigating) return;

        let totalDist = 0;
        let totalTime = 0;

        for (let i = currentStepIndex; i < steps.length; i++) {
            totalDist += steps[i]?.distance_value || 0;
            totalTime += steps[i]?.duration_value || 0;
        }

        setDistanceRemaining(totalDist);
        setTimeRemaining(totalTime);
    }, [currentStepIndex, route, steps, isNavigating]);

    // Voice guidance
    const speakInstruction = useCallback((instruction) => {
        if (!voiceEnabled || !window.speechSynthesis) return;

        const utterance = new SpeechSynthesisUtterance(instruction);
        utterance.rate = 0.9;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        window.speechSynthesis.speak(utterance);
    }, [voiceEnabled]);

    // Auto-advance to next step based on location
    useEffect(() => {
        if (!isNavigating || isPaused || !currentLocation || !currentStep) return;

        const stepEndLocation = currentStep.end_location;
        if (!stepEndLocation) return;

        // Calculate distance to step end point
        const distance = calculateDistance(
            currentLocation.latitude,
            currentLocation.longitude,
            stepEndLocation.lat,
            stepEndLocation.lng
        );

        // If within 50 meters of step end, advance to next step
        if (distance < 50 && currentStepIndex < steps.length - 1) {
            const nextIndex = currentStepIndex + 1;
            setCurrentStepIndex(nextIndex);

            if (onStepChange) {
                onStepChange(nextIndex);
            }

            // Speak next instruction
            if (voiceEnabled && nextIndex !== lastSpokenStep) {
                const nextStep = steps[nextIndex];
                if (nextStep?.instruction) {
                    speakInstruction(stripHtml(nextStep.instruction));
                    setLastSpokenStep(nextIndex);
                }
            }
        }
    }, [currentLocation, currentStep, currentStepIndex, isNavigating, isPaused, steps, voiceEnabled, lastSpokenStep, speakInstruction, onStepChange]);

    const handleStartNavigation = () => {
        setIsNavigating(true);
        setIsPaused(false);
        setCurrentStepIndex(0);

        // Speak first instruction
        if (voiceEnabled && steps[0]?.instruction) {
            speakInstruction(stripHtml(steps[0].instruction));
            setLastSpokenStep(0);
        }
    };

    const handlePauseNavigation = () => {
        setIsPaused(!isPaused);
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }
    };

    const handleStopNavigation = () => {
        setIsNavigating(false);
        setIsPaused(false);
        setCurrentStepIndex(0);
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }
        if (onNavigationEnd) {
            onNavigationEnd();
        }
    };

    const handleNextStep = () => {
        if (currentStepIndex < steps.length - 1) {
            const nextIndex = currentStepIndex + 1;
            setCurrentStepIndex(nextIndex);
            if (onStepChange) {
                onStepChange(nextIndex);
            }
        }
    };

    const handlePreviousStep = () => {
        if (currentStepIndex > 0) {
            const prevIndex = currentStepIndex - 1;
            setCurrentStepIndex(prevIndex);
            if (onStepChange) {
                onStepChange(prevIndex);
            }
        }
    };

    const toggleVoice = () => {
        setVoiceEnabled(!voiceEnabled);
        if (voiceEnabled && window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }
    };

    const formatDistance = (meters) => {
        if (meters < 1000) {
            return `${Math.round(meters)} m`;
        }
        return `${(meters / 1000).toFixed(1)} km`;
    };

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        if (mins < 60) {
            return `${mins} min`;
        }
        const hours = Math.floor(mins / 60);
        const remainingMins = mins % 60;
        return `${hours}h ${remainingMins}m`;
    };

    const getManeuverIcon = (maneuver) => {
        switch (maneuver) {
            case 'turn-left':
            case 'turn-slight-left':
            case 'turn-sharp-left':
                return '↰';
            case 'turn-right':
            case 'turn-slight-right':
            case 'turn-sharp-right':
                return '↱';
            case 'uturn-left':
            case 'uturn-right':
                return '⮌';
            case 'merge':
                return '⮕';
            case 'roundabout-left':
            case 'roundabout-right':
                return '⭮';
            default:
                return '↑';
        }
    };

    if (!route) {
        return null;
    }

    return (
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-4 text-white">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <FiNavigation className="w-5 h-5" />
                        <h3 className="font-semibold">Navigation</h3>
                    </div>
                    <button
                        onClick={toggleVoice}
                        className="p-2 hover:bg-white/20 rounded-lg transition-colors"
                        title={voiceEnabled ? "Disable voice" : "Enable voice"}
                    >
                        {voiceEnabled ? <FiVolume2 className="w-5 h-5" /> : <FiVolumeX className="w-5 h-5" />}
                    </button>
                </div>
            </div>

            {/* Navigation Status */}
            {!isNavigating ? (
                <div className="p-6 text-center">
                    <div className="mb-4">
                        <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-3">
                            <FiNavigation className="w-8 h-8 text-blue-600" />
                        </div>
                        <h4 className="font-semibold text-gray-900 mb-2">Ready to Navigate</h4>
                        <p className="text-sm text-gray-600">
                            {steps.length} steps • {formatDistance(route.total_distance_meters)} • {formatTime(route.total_duration_seconds)}
                        </p>
                    </div>
                    <button
                        onClick={handleStartNavigation}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
                    >
                        <FiPlay className="w-5 h-5" />
                        Start Navigation
                    </button>
                </div>
            ) : (
                <>
                    {/* Current Step Display */}
                    <div className="p-4 bg-blue-50 border-b border-blue-100">
                        <div className="flex items-start gap-3">
                            <div className="flex-shrink-0 w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white text-2xl">
                                {getManeuverIcon(currentStep?.maneuver)}
                            </div>
                            <div className="flex-1 min-w-0">
                                <div className="text-sm text-blue-600 font-medium mb-1">
                                    Step {currentStepIndex + 1} of {steps.length}
                                </div>
                                <div
                                    className="text-gray-900 font-semibold text-lg leading-tight"
                                    dangerouslySetInnerHTML={{ __html: currentStep?.instruction || 'Continue straight' }}
                                />
                                <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                                    <span className="flex items-center gap-1">
                                        <FiMapPin className="w-4 h-4" />
                                        {currentStep?.distance || '0 m'}
                                    </span>
                                    <span className="flex items-center gap-1">
                                        <FiClock className="w-4 h-4" />
                                        {currentStep?.duration || '0 min'}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* ETA and Distance Remaining */}
                    <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 border-b border-gray-200">
                        <div>
                            <div className="text-xs text-gray-600 mb-1">Distance Remaining</div>
                            <div className="text-2xl font-bold text-gray-900">{formatDistance(distanceRemaining)}</div>
                        </div>
                        <div>
                            <div className="text-xs text-gray-600 mb-1">Time Remaining</div>
                            <div className="text-2xl font-bold text-gray-900">{formatTime(timeRemaining)}</div>
                        </div>
                    </div>

                    {/* Navigation Controls */}
                    <div className="p-4 space-y-3">
                        <div className="flex gap-2">
                            <button
                                onClick={handlePreviousStep}
                                disabled={currentStepIndex === 0}
                                className="flex-1 bg-gray-100 hover:bg-gray-200 disabled:bg-gray-50 disabled:text-gray-400 text-gray-700 font-medium py-2 px-4 rounded-lg transition-colors"
                            >
                                ← Previous
                            </button>
                            <button
                                onClick={handlePauseNavigation}
                                className={`flex-1 ${isPaused ? 'bg-green-600 hover:bg-green-700' : 'bg-yellow-600 hover:bg-yellow-700'} text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2`}
                            >
                                {isPaused ? <FiPlay className="w-4 h-4" /> : <FiPause className="w-4 h-4" />}
                                {isPaused ? 'Resume' : 'Pause'}
                            </button>
                            <button
                                onClick={handleNextStep}
                                disabled={currentStepIndex === steps.length - 1}
                                className="flex-1 bg-gray-100 hover:bg-gray-200 disabled:bg-gray-50 disabled:text-gray-400 text-gray-700 font-medium py-2 px-4 rounded-lg transition-colors"
                            >
                                Next →
                            </button>
                        </div>
                        <button
                            onClick={handleStopNavigation}
                            className="w-full bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
                        >
                            <FiSquare className="w-4 h-4" />
                            Stop Navigation
                        </button>
                    </div>

                    {/* Upcoming Steps */}
                    {currentStepIndex < steps.length - 1 && (
                        <div className="p-4 bg-gray-50 border-t border-gray-200">
                            <div className="text-xs font-semibold text-gray-600 mb-2">UPCOMING</div>
                            <div className="space-y-2">
                                {steps.slice(currentStepIndex + 1, currentStepIndex + 4).map((step, idx) => (
                                    <div key={idx} className="flex items-center gap-2 text-sm">
                                        <div className="flex-shrink-0 w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center text-gray-600 text-xs">
                                            {getManeuverIcon(step.maneuver)}
                                        </div>
                                        <div
                                            className="flex-1 text-gray-700 truncate"
                                            dangerouslySetInnerHTML={{ __html: step.instruction }}
                                        />
                                        <div className="text-gray-500 text-xs">{step.distance}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

// Helper functions
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371e3; // Earth's radius in meters
    const φ1 = lat1 * Math.PI / 180;
    const φ2 = lat2 * Math.PI / 180;
    const Δφ = (lat2 - lat1) * Math.PI / 180;
    const Δλ = (lon2 - lon1) * Math.PI / 180;

    const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
        Math.cos(φ1) * Math.cos(φ2) *
        Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c;
}

function stripHtml(html) {
    const tmp = document.createElement('DIV');
    tmp.innerHTML = html;
    return tmp.textContent || tmp.innerText || '';
}

export default NavigationPanel;
