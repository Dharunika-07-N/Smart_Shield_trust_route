/**
 * Traffic Data API Service
 * Fetches real-time traffic information from OpenTraffic and OSM
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Traffic levels enum matching backend
 */
export const TrafficLevel = {
    UNKNOWN: { value: 0, name: 'UNKNOWN', color: '#9ca3af', description: 'No data' },
    FREE_FLOW: { value: 1, name: 'FREE_FLOW', color: '#10b981', description: 'Free flow' },
    LIGHT: { value: 2, name: 'LIGHT', color: '#84cc16', description: 'Light traffic' },
    MODERATE: { value: 3, name: 'MODERATE', color: '#f59e0b', description: 'Moderate' },
    HEAVY: { value: 4, name: 'HEAVY', color: '#f97316', description: 'Heavy traffic' },
    SEVERE: { value: 5, name: 'SEVERE', color: '#ef4444', description: 'Severe congestion' }
};

/**
 * Get traffic level object by name
 */
export const getTrafficLevelByName = (name) => {
    return Object.values(TrafficLevel).find(level => level.name === name) || TrafficLevel.UNKNOWN;
};

/**
 * Get traffic level object by value
 */
export const getTrafficLevelByValue = (value) => {
    return Object.values(TrafficLevel).find(level => level.value === value) || TrafficLevel.UNKNOWN;
};

/**
 * Fetch traffic segments for a bounding box
 * @param {Object} bounds - Map bounds {minLat, minLng, maxLat, maxLng}
 * @returns {Promise<Array>} Array of traffic segments
 */
export const getTrafficSegments = async (bounds) => {
    try {
        const { minLat, minLng, maxLat, maxLng } = bounds;

        const response = await axios.get(`${API_BASE_URL}/api/traffic/segments`, {
            params: {
                min_lat: minLat,
                min_lng: minLng,
                max_lat: maxLat,
                max_lng: maxLng
            }
        });

        return response.data;
    } catch (error) {
        console.error('Error fetching traffic segments:', error);
        return [];
    }
};

/**
 * Get traffic information for a specific route
 * @param {Array<Array<number>>} coordinates - Route coordinates [[lat, lng], ...]
 * @returns {Promise<Object>} Traffic information for the route
 */
export const getRouteTraffic = async (coordinates) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/api/traffic/route/analysis`, {
            coordinates
        });

        return response.data;
    } catch (error) {
        console.error('Error fetching route traffic:', error);
        return {
            overall_level: 'UNKNOWN',
            overall_level_value: 0,
            total_segments: 0,
            segments: []
        };
    }
};

/**
 * Get traffic service status
 * @returns {Promise<Object>} Service status and available providers
 */
export const getTrafficServiceStatus = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/api/traffic/status`);
        return response.data;
    } catch (error) {
        console.error('Error fetching traffic service status:', error);
        return {
            status: 'unavailable',
            providers: []
        };
    }
};

/**
 * Get traffic level definitions
 * @returns {Promise<Object>} Traffic level definitions
 */
export const getTrafficLevels = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/api/traffic/levels`);
        return response.data;
    } catch (error) {
        console.error('Error fetching traffic levels:', error);
        return { levels: Object.values(TrafficLevel) };
    }
};

/**
 * Convert traffic segments to Leaflet polylines
 * @param {Array} segments - Traffic segments from API
 * @returns {Array} Polyline data for Leaflet
 */
export const segmentsToPolylines = (segments) => {
    return segments.map(segment => ({
        positions: [
            [segment.start.lat, segment.start.lng],
            [segment.end.lat, segment.end.lng]
        ],
        color: getTrafficLevelByName(segment.traffic_level).color,
        weight: 5,
        opacity: 0.7,
        data: {
            segmentId: segment.segment_id,
            speed: segment.speed_kmh,
            freeFlowSpeed: segment.free_flow_speed,
            trafficLevel: segment.traffic_level,
            source: segment.source,
            timestamp: segment.timestamp
        }
    }));
};

/**
 * Format traffic level for display
 * @param {string} levelName - Traffic level name
 * @returns {Object} Formatted traffic level info
 */
export const formatTrafficLevel = (levelName) => {
    const level = getTrafficLevelByName(levelName);

    return {
        name: level.name,
        description: level.description,
        color: level.color,
        icon: getTrafficIcon(level.value),
        badge: getTrafficBadge(level.value)
    };
};

/**
 * Get icon for traffic level
 */
const getTrafficIcon = (value) => {
    const icons = {
        0: '❓',
        1: '🟢',
        2: '🟡',
        3: '🟠',
        4: '🔴',
        5: '🚨'
    };
    return icons[value] || '❓';
};

/**
 * Get badge style for traffic level
 */
const getTrafficBadge = (value) => {
    const badges = {
        0: { bg: 'bg-gray-100', text: 'text-gray-600', border: 'border-gray-300' },
        1: { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-300' },
        2: { bg: 'bg-lime-100', text: 'text-lime-700', border: 'border-lime-300' },
        3: { bg: 'bg-amber-100', text: 'text-amber-700', border: 'border-amber-300' },
        4: { bg: 'bg-orange-100', text: 'text-orange-700', border: 'border-orange-300' },
        5: { bg: 'bg-red-100', text: 'text-red-700', border: 'border-red-300' }
    };
    return badges[value] || badges[0];
};

/**
 * Calculate estimated time with traffic
 * @param {number} distanceKm - Distance in kilometers
 * @param {number} freeFlowSpeed - Free flow speed in km/h
 * @param {string} trafficLevel - Traffic level name
 * @returns {Object} Time estimates
 */
export const calculateTimeWithTraffic = (distanceKm, freeFlowSpeed, trafficLevel) => {
    const level = getTrafficLevelByName(trafficLevel);

    // Speed reduction factors
    const speedFactors = {
        0: 0.8,  // Unknown - assume some delay
        1: 1.0,  // Free flow
        2: 0.85, // Light
        3: 0.65, // Moderate
        4: 0.45, // Heavy
        5: 0.25  // Severe
    };

    const factor = speedFactors[level.value] || 0.8;
    const effectiveSpeed = freeFlowSpeed * factor;

    const freeFlowTime = (distanceKm / freeFlowSpeed) * 60; // minutes
    const trafficTime = (distanceKm / effectiveSpeed) * 60; // minutes
    const delay = trafficTime - freeFlowTime;

    return {
        freeFlowMinutes: Math.round(freeFlowTime),
        trafficMinutes: Math.round(trafficTime),
        delayMinutes: Math.round(delay),
        effectiveSpeed: Math.round(effectiveSpeed)
    };
};

export default {
    getTrafficSegments,
    getRouteTraffic,
    getTrafficServiceStatus,
    getTrafficLevels,
    segmentsToPolylines,
    formatTrafficLevel,
    calculateTimeWithTraffic,
    TrafficLevel,
    getTrafficLevelByName,
    getTrafficLevelByValue
};
