/**
 * API Client for Smart Shield Backend
 */
import axios from 'axios';

import { API_BASE_URL } from '../utils/constants';

// Log the API base URL in development
if (process.env.NODE_ENV === 'development') {
  console.log('API Base URL:', API_BASE_URL);
  console.log('REACT_APP_API_URL:', process.env.REACT_APP_API_URL);
  console.log('REACT_APP_API_BASE:', process.env.REACT_APP_API_BASE);
}

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
    // Handle errors with more detail
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const data = error.response.data;
      const url = error.config?.url || 'unknown endpoint';

      console.error('API Error:', {
        status,
        url,
        data,
        message: data?.detail || data?.message || data?.error || 'API request failed'
      });

      // Provide more specific error messages based on status code
      let errorMessage = data?.detail || data?.message || data?.error;

      if (!errorMessage) {
        switch (status) {
          case 400:
            errorMessage = 'Invalid request. Please check your input.';
            break;
          case 401:
            errorMessage = 'Unauthorized. Please check your authentication.';
            break;
          case 403:
            errorMessage = 'Access forbidden.';
            break;
          case 404:
            errorMessage = `Endpoint not found: ${url}`;
            break;
          case 422:
            errorMessage = 'Validation error. Please check your input data.';
            break;
          case 500:
            errorMessage = 'Server error. Please try again later.';
            break;
          case 503:
            errorMessage = 'Service unavailable. The server may be overloaded.';
            break;
          default:
            errorMessage = `API request failed (Status ${status})`;
        }
      }

      // Create error with more context
      const enhancedError = new Error(errorMessage);
      enhancedError.status = status;
      enhancedError.data = data;
      enhancedError.url = url;
      throw enhancedError;

    } else if (error.request) {
      // Request made but no response received
      console.error('Network Error:', {
        message: 'No response received from server',
        url: error.config?.url,
        request: error.request
      });

      const errorMessage = error.code === 'ECONNABORTED'
        ? 'Request timed out. The server may be slow or unavailable.'
        : 'Network error: Unable to connect to server. Make sure the backend is running on ' + (process.env.REACT_APP_API_URL || 'http://localhost:8000');

      const enhancedError = new Error(errorMessage);
      enhancedError.isNetworkError = true;
      throw enhancedError;

    } else {
      // Something else happened (setup error, etc.)
      console.error('Request Setup Error:', error.message);
      throw error;
    }
  }
);

// API Methods
export const api = {
  // Health Check
  healthCheck: () => apiClient.get('/health', { baseURL: API_BASE_URL.split('/api/v1')[0] }),

  // Delivery Routes
  optimizeRoute: (data) => apiClient.post('/delivery/optimize', data),
  getRoute: (routeId) => apiClient.get(`/delivery/routes/${routeId}`),
  updateRoute: (routeId, data) => apiClient.put(`/delivery/routes/${routeId}`, data),
  getDeliveryStats: () => apiClient.get('/delivery/stats'),

  // Safety
  calculateSafetyScore: (data) => apiClient.post('/safety/score', data),
  getSafetyConditions: (location, data) => apiClient.post(`/safety/conditions/${location}`, data),

  // Feedback
  submitFeedback: (data) => apiClient.post('/feedback/submit', data),
  submitRouteFeedback: (data) => apiClient.post('/feedback/route', data),
  getFeedbackStats: () => apiClient.get('/feedback/stats'),
  getRouteFeedback: (routeId) => apiClient.get(`/feedback/route/${routeId}`),
  submitAlert: (data) => apiClient.post('/feedback/alert', data),
  getAlerts: (serviceType) => apiClient.get('/feedback/alerts', { params: { service_type: serviceType } }),

  // Traffic
  getTrafficSegment: (data) => apiClient.post('/traffic/segment', data),
  getTrafficRoute: (data) => apiClient.post('/traffic/route', data),

  // Delivery Tracking
  updateLocation: (data) => apiClient.post('/delivery/location-update', data),
  trackDelivery: (deliveryId) => apiClient.get(`/delivery/${deliveryId}/track`),
  reoptimizeRoute: (routeId, data) => apiClient.post(`/delivery/routes/${routeId}/reoptimize`, data),

  // Safety Features
  triggerPanicButton: (data) => apiClient.post('/safety/panic-button', data),
  resolvePanicButton: (data) => apiClient.post('/safety/panic-button/resolve', data),
  checkIn: (data) => apiClient.post('/safety/check-in', data),
  getSafeZones: (data) => apiClient.post('/safety/safe-zones', data),
  createRideAlong: (data) => apiClient.post('/safety/ride-along', data),
  getRideAlongStatus: (shareToken) => apiClient.get(`/safety/ride-along/${shareToken}`),

  // Training
  retrainModel: () => apiClient.post('/training/retrain'),

  // Generic methods
  get: (url, config) => apiClient.get(url, config),
  post: (url, data, config) => apiClient.post(url, data, config),
  put: (url, data, config) => apiClient.put(url, data, config),
  patch: (url, data, config) => apiClient.patch(url, data, config),
  delete: (url, config) => apiClient.delete(url, config),
};

export default apiClient;

