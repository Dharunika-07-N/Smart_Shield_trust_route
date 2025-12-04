/**
 * Custom React Hook for API calls with error handling and loading states
 */
import { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';

export const useApi = (apiCall, immediate = false) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(immediate);
  const [error, setError] = useState(null);

  const execute = useCallback(
    async (...args) => {
      try {
        setLoading(true);
        setError(null);
        const result = await apiCall(...args);
        setData(result);
        return result;
      } catch (err) {
        setError(err.message || 'An error occurred');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [apiCall]
  );

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [immediate, execute]);

  return { data, loading, error, execute };
};

export const useRouteOptimization = () => {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const optimize = async (routeData) => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.optimizeRoute(routeData);
      setResult(response);
      return response;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { result, loading, error, optimize };
};

export const useTrafficData = () => {
  const [trafficData, setTrafficData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getTrafficForRoute = async (coordinates) => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.getTrafficRoute({ coordinates });
      setTrafficData(response);
      return response;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { trafficData, loading, error, getTrafficForRoute };
};

export default useApi;

