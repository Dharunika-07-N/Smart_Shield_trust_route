/**
 * Application Constants
 */

const getApiUrls = () => {
  const envUrl = process.env.REACT_APP_API_URL || process.env.REACT_APP_API_BASE;
  if (envUrl) {
    // If it's a relative path, convert to full URL for development
    let root = envUrl;
    if (envUrl.startsWith('/') && process.env.NODE_ENV === 'development') {
      root = `http://localhost:8000${envUrl}`;
    }

    // Split to get root and base
    const rootUrl = root.split('/api/v1')[0].replace(/\/$/, '');
    const baseUrl = `${rootUrl}/api/v1`;
    return { rootUrl, baseUrl };
  }
  return {
    rootUrl: 'http://localhost:8000',
    baseUrl: 'http://localhost:8000/api/v1'
  };
};

const urls = getApiUrls();
export const API_ROOT_URL = urls.rootUrl;
export const API_BASE_URL = urls.baseUrl;

export const API_ENDPOINTS = {
  HEALTH: '/health',
  DELIVERY: {
    OPTIMIZE: '/delivery/optimize',
    GET_ROUTE: (id) => `/delivery/routes/${id}`,
    UPDATE_ROUTE: (id) => `/delivery/routes/${id}`,
    STATS: '/delivery/stats',
  },
  SAFETY: {
    SCORE: '/safety/score',
    HEATMAP: '/safety/heatmap',
    CONDITIONS: (location) => `/safety/conditions/${location}`,
  },
  FEEDBACK: {
    SUBMIT: '/feedback/submit',
    ROUTE: '/feedback/route',
    STATS: '/feedback/stats',
    GET_ROUTE: (id) => `/feedback/route/${id}`,
  },
  TRAFFIC: {
    SEGMENT: '/traffic/segment',
    ROUTE: '/traffic/route',
  },
};

export const TRAFFIC_COLORS = {
  low: '#22c55e',      // green
  medium: '#eab308',   // yellow
  high: '#ef4444',     // red
};

export const SAFETY_COLORS = {
  high: '#22c55e',     // green (90+)
  medium: '#eab308',   // yellow (75-89)
  low: '#f97316',      // orange (60-74)
  veryLow: '#ef4444',  // red (<60)
};

export default {
  API_BASE_URL,
  API_ENDPOINTS,
  TRAFFIC_COLORS,
  SAFETY_COLORS,
};

