/**
 * Dashboard API Service
 * Handles all dashboard-related API calls
 */

import axios from 'axios';
import { API_BASE_URL } from '../utils/constants';

const dashboardApi = {
    /**
     * Get dashboard statistics
     */
    getStats: async (userId = null) => {
        try {
            const params = userId ? { user_id: userId } : {};
            const response = await axios.get(`${API_BASE_URL}/dashboard/stats`, { params });
            return response.data;
        } catch (error) {
            console.error('Error fetching dashboard stats:', error);
            throw error;
        }
    },

    /**
     * Get delivery queue
     */
    getDeliveryQueue: async (limit = 10) => {
        try {
            const response = await axios.get(`${API_BASE_URL}/dashboard/deliveries/queue`, {
                params: { limit }
            });
            return response.data;
        } catch (error) {
            console.error('Error fetching delivery queue:', error);
            throw error;
        }
    },

    /**
     * Get zone safety information
     */
    getZoneSafety: async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/dashboard/zones/safety`);
            return response.data;
        } catch (error) {
            console.error('Error fetching zone safety:', error);
            throw error;
        }
    },

    /**
     * Get weather conditions
     */
    getWeather: async (lat = 13.0827, lon = 80.2707) => {
        try {
            const response = await axios.get(`${API_BASE_URL}/dashboard/weather`, {
                params: { lat, lon }
            });
            return response.data;
        } catch (error) {
            console.error('Error fetching weather:', error);
            throw error;
        }
    },

    /**
     * Optimize current route
     */
    optimizeRoute: async (deliveryIds) => {
        try {
            const response = await axios.post(`${API_BASE_URL}/dashboard/route/optimize`, {
                delivery_ids: deliveryIds
            });
            return response.data;
        } catch (error) {
            console.error('Error optimizing route:', error);
            throw error;
        }
    },

    /**
     * Get recent alerts
     */
    getRecentAlerts: async (limit = 5) => {
        try {
            const response = await axios.get(`${API_BASE_URL}/dashboard/alerts/recent`, {
                params: { limit }
            });
            return response.data;
        } catch (error) {
            console.error('Error fetching alerts:', error);
            throw error;
        }
    }
};

export default dashboardApi;
