/**
 * API Client for Smart Shield Backend
 */
import axios from 'axios';

// Get API URL from environment or use proxy
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    // Handle errors
    if (error.response) {
      // Server responded with error
      console.error('API Error:', error.response.data);
      throw new Error(error.response.data.detail || error.response.data.message || 'API request failed');
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.request);
      throw new Error('Network error: Unable to connect to server. Make sure the backend is running.');
    } else {
      // Something else happened
      console.error('Error:', error.message);
      throw error;
    }
  }
);

// API Methods
export const api = {
  // Health Check
  healthCheck: () => apiClient.get('/health', { baseURL: '/' }),

  // Delivery Routes
  optimizeRoute: (data) => apiClient.post('/delivery/optimize', data),
  getRoute: (routeId) => apiClient.get(`/delivery/routes/${routeId}`),
  updateRoute: (routeId, data) => apiClient.put(`/delivery/routes/${routeId}`, data),
  getDeliveryStats: () => apiClient.get('/delivery/stats'),

  // Safety
  calculateSafetyScore: (data) => apiClient.post('/safety/score', data),
  getSafetyHeatmap: (data) => apiClient.post('/safety/heatmap', data),
  getSafetyConditions: (location, data) => apiClient.post(`/safety/conditions/${location}`, data),

  // Feedback
  submitFeedback: (data) => apiClient.post('/feedback/submit', data),
  submitRouteFeedback: (data) => apiClient.post('/feedback/route', data),
  getFeedbackStats: () => apiClient.get('/feedback/stats'),
  getRouteFeedback: (routeId) => apiClient.get(`/feedback/route/${routeId}`),

  // Traffic
  getTrafficSegment: (data) => apiClient.post('/traffic/segment', data),
  getTrafficRoute: (data) => apiClient.post('/traffic/route', data),
};

export default apiClient;

