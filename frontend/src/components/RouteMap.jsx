import React, { useEffect, useMemo, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMapEvents, useMap, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import { api } from '../services/api';
import useLocation from '../hooks/useLocation';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';

const MapUpdater = ({ center }) => {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.setView(center, map.getZoom());
    }
  }, [center, map]);
  return null;
};

const RouteMap = () => {
  const { location, loading: locationLoading, error: locationError } = useLocation();
  const [currentPos, setCurrentPos] = useState(null);
  const [destPos, setDestPos] = useState(null);
  const [fastest, setFastest] = useState(null);
  const [safest, setSafest] = useState(null);
  const [shortest, setShortest] = useState(null);
  const [recommended, setRecommended] = useState(null);
  const [alternatives, setAlternatives] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState([]);
  const [safetyOverlay, setSafetyOverlay] = useState(null);
  const [showSafetyOverlay, setShowSafetyOverlay] = useState(true);

  // Navigation State
  const [navigationMode, setNavigationMode] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [eta, setEta] = useState(null);
  const [distanceRemaining, setDistanceRemaining] = useState(null);


  // Fallback to New York
  const baseLat = location?.latitude || 40.7128;
  const baseLon = location?.longitude || -74.0060;

  // Animated pulsing dot icon for current location (Snapchat-like)
  const pulsingIcon = useMemo(() => {
    const size = 20;
    return L.divIcon({
      className: 'pulsing-marker',
      html: `<div style="width:${size}px;height:${size}px;border-radius:50%;background:#3b82f6;box-shadow:0 0 0 0 rgba(59,130,246,0.7);animation:pulse 2s infinite"></div>`
    });
  }, []);

  // Update current position when location changes
  useEffect(() => {
    if (location) {
      setCurrentPos([location.latitude, location.longitude]);
    }
  }, [location]);

  // Mock route data with traffic relative to base location
  const routes = useMemo(() => [
    {
      id: 1,
      name: 'Route #1247',
      status: 'active',
      safety: 92,
      stops: 5,
      distance: '12.5 km',
      time: '28 min',
      coordinates: [
        { lat: baseLat, lng: baseLon, traffic: 'low', safety: 95 },
        { lat: baseLat + 0.008, lng: baseLon + 0.006, traffic: 'medium', safety: 90 },
        { lat: baseLat + 0.015, lng: baseLon + 0.01, traffic: 'high', safety: 85 },
        { lat: baseLat + 0.02, lng: baseLon + 0.005, traffic: 'low', safety: 95 },
        { lat: baseLat + 0.025, lng: baseLon - 0.005, traffic: 'medium', safety: 88 },
      ],
    },
    {
      id: 2,
      name: 'Route #1246',
      status: 'completed',
      safety: 85,
      stops: 4,
      distance: '8.3 km',
      time: '22 min',
      coordinates: [
        { lat: baseLat + 0.01, lng: baseLon - 0.01, traffic: 'low', safety: 88 },
        { lat: baseLat + 0.015, lng: baseLon - 0.015, traffic: 'medium', safety: 85 },
        { lat: baseLat + 0.02, lng: baseLon - 0.02, traffic: 'high', safety: 80 },
        { lat: baseLat + 0.025, lng: baseLon - 0.025, traffic: 'low', safety: 87 },
      ],
    },
    {
      id: 3,
      name: 'Route #1245',
      status: 'active',
      safety: 88,
      stops: 6,
      distance: '15.2 km',
      time: '35 min',
      coordinates: [
        { lat: baseLat - 0.005, lng: baseLon + 0.01, traffic: 'low', safety: 90 },
        { lat: baseLat - 0.01, lng: baseLon + 0.015, traffic: 'medium', safety: 88 },
        { lat: baseLat - 0.015, lng: baseLon + 0.02, traffic: 'low', safety: 92 },
        { lat: baseLat - 0.02, lng: baseLon + 0.025, traffic: 'high', safety: 82 },
        { lat: baseLat - 0.025, lng: baseLon + 0.03, traffic: 'medium', safety: 86 },
        { lat: baseLat - 0.03, lng: baseLon + 0.035, traffic: 'low', safety: 89 },
      ],
    },
  ], [baseLat, baseLon]);

  // Get traffic color
  const getTrafficColor = (traffic) => {
    switch (traffic) {
      case 'low': return '#22c55e';
      case 'medium': return '#eab308';
      case 'high': return '#ef4444';
      default: return '#6b7280';
    }
  };

  // Destination search via Nominatim
  const searchPlaces = async (text) => {
    if (!text || text.length < 3) { setResults([]); return; }
    setSearching(true);
    try {
      const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(text)}`;
      const res = await fetch(url, { headers: { 'Accept': 'application/json' } });
      const data = await res.json();
      setResults(data.slice(0, 5));
    } catch (e) {
      // ignore
    } finally {
      setSearching(false);
    }
  };

  const buildRequest = (start, dest, optimizeFor) => ({
    starting_point: { latitude: start[0], longitude: start[1] },
    stops: [
      {
        stop_id: 'DEST_1',
        address: 'Destination',
        coordinates: { latitude: dest[0], longitude: dest[1] },
        priority: 'high'
      }
    ],
    optimize_for: optimizeFor,
    rider_info: { gender: 'neutral', prefers_safe_routes: true },
    vehicle_type: 'motorcycle',
    avoid_highways: false,
    avoid_tolls: false
  });

  const optimize = async () => {
    if (!currentPos || !destPos) {
      setError('Please select a destination by searching or clicking on the map');
      return;
    }

    setLoading(true);
    setError('');
    setFastest(null);
    setSafest(null);
    setShortest(null);
    setRecommended(null);
    setAlternatives([]);

    try {
      // Build requests
      const fastestRequest = buildRequest(currentPos, destPos, ['time', 'distance']);
      const safestRequest = buildRequest(currentPos, destPos, ['safety', 'time']);
      const shortestRequest = buildRequest(currentPos, destPos, ['distance']);

      console.log('Optimizing route...', {
        currentPos,
        destPos,
        fastestRequest,
        safestRequest,
        shortestRequest
      });

      // Log the full request for debugging
      console.log('Fastest request:', JSON.stringify(fastestRequest, null, 2));
      console.log('Safest request:', JSON.stringify(safestRequest, null, 2));
      console.log('Shortest request:', JSON.stringify(shortestRequest, null, 2));

      // Use API service instead of fetch
      const [fastJson, safeJson, shortJson] = await Promise.all([
        api.optimizeRoute(fastestRequest).catch(err => {
          console.error('Fastest route error:', err);
          return null;
        }),
        api.optimizeRoute(safestRequest).catch(err => {
          console.error('Safest route error:', err);
          return null;
        }),
        api.optimizeRoute(shortestRequest).catch(err => {
          console.error('Shortest route error:', err);
          return null;
        })
      ]);

      // Check if ANY response is successful
      if ((!fastJson || !fastJson.success) && (!safeJson || !safeJson.success) && (!shortJson || !shortJson.success)) {
        throw new Error('All route optimizations failed');
      }

      if (fastJson?.success && fastJson.data) setFastest(fastJson.data);
      if (safeJson?.success && safeJson.data) setSafest(safeJson.data);
      if (shortJson?.success && shortJson.data) setShortest(shortJson.data);

      // Collect unique alternatives
      const alts = [];
      const seenCoords = new Set();

      // Helper to generate a rough signature for a route to dedup
      const getRouteSig = (r) => {
        if (!r.segments?.[0]?.route_coordinates?.length) return Math.random();
        const first = r.segments[0].route_coordinates[0];
        const last = r.segments[0].route_coordinates[r.segments[0].route_coordinates.length - 1];
        const mid = r.segments[0].route_coordinates[Math.floor(r.segments[0].route_coordinates.length / 2)];
        return `${first.lat},${first.lng}-${mid.lat},${mid.lng}-${last.lat},${last.lng}`;
      };

      // Add main routes to seen
      if (fastJson?.data) seenCoords.add(getRouteSig(fastJson.data));
      if (safeJson?.data) seenCoords.add(getRouteSig(safeJson.data));
      if (shortJson?.data) seenCoords.add(getRouteSig(shortJson.data));

      const processAlts = (routeData) => {
        if (routeData?.alternatives) {
          routeData.alternatives.forEach(alt => {
            const sig = getRouteSig(alt);
            if (!seenCoords.has(sig)) {
              seenCoords.add(sig);
              alts.push(alt);
            }
          });
        }
      };

      processAlts(fastJson?.data);
      processAlts(safeJson?.data);
      processAlts(shortJson?.data);

      setAlternatives(alts);

      // Simple recommendation logic
      let best = 'fastest';
      // If we have data, logic: prefer safe if safety < 65 on fastest or time diff < 20%
      const fastData = fastJson?.data;
      const safeData = safeJson?.data;
      const shortData = shortJson?.data;

      if (fastData && safeData) {
        const fastestSecs = fastData.total_duration_seconds || 0;
        const safestSecs = safeData.total_duration_seconds || 0;
        const fastestSafety = fastData.average_safety_score || 0;
        const chooseSafe = fastestSafety < 65 || (safestSecs && fastestSecs && (safestSecs - fastestSecs) / fastestSecs < 0.2);
        if (chooseSafe) best = 'safest';
      } else if (safeData) {
        best = 'safest';
      }
      // Could accept Shortest if specifically much shorter, but for now stick to 2 main defaults unless user clicks
      setRecommended(best);

      // Fetch safety overlay for recommended route
      const recData = best === 'safest' ? safeData : (best === 'shortest' ? shortData : fastData);
      if (recData) await fetchSafetyOverlay(recData);
    } catch (e) {
      console.error('Route optimization error:', {
        message: e.message,
        status: e.status,
        isNetworkError: e.isNetworkError,
        error: e
      });

      let errorMessage = e.message || 'Optimization failed';

      // Provide more helpful error messages based on error type
      if (e.isNetworkError || errorMessage.includes('Network error') || errorMessage.includes('Unable to connect')) {
        errorMessage = `Cannot connect to server. Make sure the backend is running on ${API_BASE}`;
      } else if (errorMessage.includes('timeout') || errorMessage.includes('timed out')) {
        errorMessage = 'Request timed out. The server may be slow or unavailable.';
      } else if (e.status === 400) {
        errorMessage = 'Invalid request. Please check that both start and destination are valid locations.';
      } else if (e.status === 404) {
        errorMessage = 'API endpoint not found. Please check the backend server configuration.';
      } else if (e.status === 500) {
        errorMessage = 'Server error occurred. Please try again or contact support.';
      } else if (e.status === 422) {
        errorMessage = 'Validation error. Please check your input data.';
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const fetchSafetyOverlay = async (routeData) => {
    if (!routeData || !routeData.segments || routeData.segments.length === 0) return;

    try {
      // Collect coordinates from route segments
      const coords = [];
      if (currentPos) {
        coords.push({ latitude: currentPos[0], longitude: currentPos[1] });
      }

      // Extract coordinates from segments
      routeData.segments.forEach(segment => {
        if (segment.route_coordinates && segment.route_coordinates.length > 0) {
          segment.route_coordinates.forEach(coord => {
            coords.push({ latitude: coord.lat, longitude: coord.lng });
          });
        }
      });

      if (destPos) {
        coords.push({ latitude: destPos[0], longitude: destPos[1] });
      }

      if (coords.length < 2) return;

      // Call safety score API
      const response = await fetch(`${API_BASE}/api/v1/safety/score`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          coordinates: coords,
          time_of_day: 'day',
          rider_gender: 'neutral',
          include_factors: true
        })
      });

      const safetyData = await response.json();
      if (safetyData.segment_scores) {
        setSafetyOverlay(safetyData);
      }
    } catch (e) {
      console.warn('Failed to fetch safety overlay:', e);
    }
  };

  const getSafetyColor = (score) => {
    if (score >= 85) return '#16a34a'; // green
    if (score >= 70) return '#ea580c'; // orange
    if (score >= 50) return '#dc2626'; // red
    return '#991b1b'; // dark red
  };

  const getSafetyColorOpacity = (score) => {
    // Higher opacity for lower safety scores (more visible danger zones)
    if (score >= 85) return 0.3;
    if (score >= 70) return 0.5;
    if (score >= 50) return 0.7;
    return 0.9;
  };

  // Convert route segments to polyline coordinates with safety coloring
  const getRoutePolylines = (routeData, segments) => {
    if (!routeData || !segments || segments.length === 0) return [];

    const polylines = [];
    let currentPos_ = currentPos;

    segments.forEach((segment, idx) => {
      const coords = [];
      if (currentPos_) {
        coords.push(currentPos_);
      }

      // Use route coordinates if available, otherwise use straight line
      if (segment.route_coordinates && segment.route_coordinates.length > 0) {
        segment.route_coordinates.forEach(coord => {
          coords.push([coord.lat, coord.lng]);
        });
      } else if (destPos) {
        coords.push(destPos);
      }

      if (coords.length >= 2) {
        const safetyScore = segment.safety_score || 70;
        const isRecommended = (recommended === 'fastest' && routeData === fastest) ||
          (recommended === 'safest' && routeData === safest);
        polylines.push({
          positions: coords,
          color: getSafetyColor(safetyScore),
          weight: isRecommended ? 5 : 3,
          opacity: getSafetyColorOpacity(safetyScore),
          safetyScore: safetyScore
        });
      }

      // Update current position for next segment
      if (coords.length > 0) {
        currentPos_ = coords[coords.length - 1];
      }
    });

    return polylines;
  };

  const centerPosition = currentPos || [11.0168, 76.9558]; // Default to Coimbatore

  const [selectionMode, setSelectionMode] = useState('destination'); // 'start' or 'destination'

  const ClickToSetLocation = () => {
    useMapEvents({
      click(e) {
        const coords = [e.latlng.lat, e.latlng.lng];
        if (selectionMode === 'start') {
          console.log('Start point selected from map click:', coords);
          setCurrentPos(coords);
          // Auto-switch to destination mode after setting start
          setSelectionMode('destination');
        } else {
          console.log('Destination selected from map click:', coords);
          setDestPos(coords);
          // Clear search query when clicking on map
          setQuery('');
          setResults([]);
        }
      }
    });
    return null;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Live Route Map</h2>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">Last updated:</span>
          <span className="text-sm font-medium text-gray-900">2 min ago</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls */}
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-4">Route Planner</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm text-gray-600 mb-1">Destination</label>
                <input
                  type="text"
                  value={query}
                  onChange={(e) => { setQuery(e.target.value); searchPlaces(e.target.value); }}
                  placeholder="Search place or click on map"
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                />
                {searching && <div className="text-xs text-gray-500 mt-1">Searching...</div>}
                {!!results.length && (
                  <div className="mt-2 border border-gray-200 rounded-md max-h-40 overflow-auto">
                    {results.map((r) => (
                      <button
                        key={`${r.place_id}`}
                        className="block w-full text-left px-3 py-2 text-sm hover:bg-gray-50 transition-colors"
                        onClick={() => {
                          const newDest = [parseFloat(r.lat), parseFloat(r.lon)];
                          console.log('Destination selected from search:', newDest, r.display_name);
                          setDestPos(newDest);
                          setQuery(r.display_name);
                          setResults([]);
                        }}
                      >
                        {r.display_name}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              <div className="text-xs text-gray-600">
                Tip: You can also click anywhere on the map to set destination.
              </div>

              {/* Status indicators */}
              <div className="space-y-2 text-xs">
                {!currentPos && (
                  <div className="flex flex-col space-y-2">
                    <div className="flex items-center space-x-2 text-yellow-600">
                      <span>⏳</span>
                      <span>Waiting for your location...</span>
                    </div>
                    <button
                      onClick={() => setCurrentPos([11.0168, 76.9558])}
                      className="text-primary-600 hover:text-primary-700 underline text-left"
                    >
                      Use Demo Location (Coimbatore)
                    </button>
                    <div className="text-gray-500">
                      Or click "Set Start Point" below to choose manually
                    </div>
                  </div>
                )}
                {currentPos && (
                  <div className="flex items-center space-x-2 text-green-600">
                    <span>✓</span>
                    <span>Current location set</span>
                  </div>
                )}
                {destPos && (
                  <div className="flex items-center space-x-2 text-green-600">
                    <span>✓</span>
                    <span>Destination selected</span>
                  </div>
                )}
                {!destPos && currentPos && (
                  <div className="flex items-center space-x-2 text-gray-500">
                    <span>→</span>
                    <span>Select destination above or click on map</span>
                  </div>
                )}
              </div>

              <button
                onClick={optimize}
                disabled={!currentPos || !destPos || loading}
                className={`w-full px-4 py-2 rounded-md text-white font-medium transition-colors ${(!currentPos || !destPos || loading)
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-primary-600 hover:bg-primary-700'
                  }`}
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <span className="animate-spin mr-2">⏳</span>
                    Optimizing Route...
                  </span>
                ) : (
                  'Optimize Route'
                )}
              </button>

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-700">
                  <div className="font-medium mb-1">Error</div>
                  <div className="mb-2">{error}</div>

                  {/* Debug info in development */}
                  {process.env.NODE_ENV === 'development' && (
                    <div className="mt-2 pt-2 border-t border-red-200 text-xs text-red-600">
                      <p><strong>Debug Info:</strong></p>
                      <p>API Base: {process.env.REACT_APP_API_URL || process.env.REACT_APP_API_BASE || 'http://localhost:8000/api/v1'}</p>
                      <p>Current Pos: {currentPos ? `[${currentPos[0].toFixed(4)}, ${currentPos[1].toFixed(4)}]` : 'Not set'}</p>
                      <p>Dest Pos: {destPos ? `[${destPos[0].toFixed(4)}, ${destPos[1].toFixed(4)}]` : 'Not set'}</p>
                      <p className="mt-1">Check browser console (F12) for detailed error logs and actual API URL being used.</p>
                    </div>
                  )}

                  {(error.includes('Cannot connect') || error.includes('Network error') || error.includes('Unable to connect')) && (
                    <div className="mt-2 pt-2 border-t border-red-200">
                      <p className="text-xs text-red-600">
                        <strong>Tip:</strong> Make sure the backend server is running.
                        Start it with: <code className="bg-red-100 px-1 rounded">cd backend && python -m uvicorn api.main:app --reload</code>
                      </p>
                      <p className="text-xs text-red-600 mt-1">
                        Expected backend URL: <code className="bg-red-100 px-1 rounded">{API_BASE}</code>
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Safety overlay toggle */}
              {(fastest || safest || shortest) && (
                <div className="mt-3 flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="safety-overlay"
                    checked={showSafetyOverlay}
                    onChange={(e) => setShowSafetyOverlay(e.target.checked)}
                    className="rounded"
                  />
                  <label htmlFor="safety-overlay" className="text-sm text-gray-700">
                    Show safety overlay
                  </label>
                </div>
              )}
            </div>
          </div>

          {(fastest || safest || shortest) && (
            <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-4">Results</h3>
              <div className="space-y-3 text-sm">
                {(() => {
                  // Consolidate unique routes
                  const allRoutes = [];
                  const seenIds = new Set();

                  const addRoute = (route, type) => {
                    if (!route) return;
                    // Use a rough signature if IDs are not stable across calls (though they should be unique per optimization)
                    // For now, assuming route objects are distinct references but might have same content
                    const sig = route.route_id || `${route.total_duration_seconds}-${route.total_distance_meters}`;

                    let existing = allRoutes.find(r => r.sig === sig);
                    if (!existing) {
                      existing = { ...route, sig, types: [] };
                      allRoutes.push(existing);
                    }
                    if (!existing.types.includes(type)) {
                      existing.types.push(type);
                    }
                  };

                  addRoute(fastest, 'Fastest');
                  addRoute(safest, 'Safest');
                  addRoute(shortest, 'Shortest');

                  // Calculate ranges for normalization
                  const maxDuration = Math.max(...allRoutes.map(r => r.total_duration_seconds));
                  const minDuration = Math.min(...allRoutes.map(r => r.total_duration_seconds));
                  const maxDistance = Math.max(...allRoutes.map(r => r.total_distance_meters));
                  const minDistance = Math.min(...allRoutes.map(r => r.total_distance_meters));

                  return allRoutes.map((route, idx) => {
                    // Normalize scores (0-100), higher is better
                    // Speed Score: Lower duration is better
                    const speedScore = maxDuration === minDuration ? 100 :
                      Math.round(100 * (1 - (route.total_duration_seconds - minDuration) / (maxDuration - minDuration + 1))); // +1 to avoid div by zero if equal

                    // Distance Score: Lower distance is better
                    const distScore = maxDistance === minDistance ? 100 :
                      Math.round(100 * (1 - (route.total_distance_meters - minDistance) / (maxDistance - minDistance + 1)));

                    // Safety Score: Already 0-100
                    const safeScore = Math.round(route.average_safety_score);

                    // Check if this route is currently 'recommended' (active)
                    // matched by simple reference or type
                    const isActive =
                      (recommended === 'fastest' && route.types.includes('Fastest')) ||
                      (recommended === 'safest' && route.types.includes('Safest')) ||
                      (recommended === 'shortest' && route.types.includes('Shortest'));

                    // If multiple match (e.g. fastest is also safest), isActive might default to one.
                    // Better logic: if we clicked this specific CARD, it sets the mode.
                    // But we just want to highlight the *Active Navigation Route*.

                    return (
                      <div
                        key={route.sig}
                        className={`p-3 rounded-lg cursor-pointer border-2 transition-all ${isActive ? 'border-primary-500 bg-primary-50 ring-1 ring-primary-500' : 'border-gray-200 hover:border-gray-300'
                          }`}
                        onClick={() => {
                          // Set recommended based on the primary type or 'fastest' if multiple
                          if (route.types.includes('Fastest')) setRecommended('fastest');
                          else if (route.types.includes('Safest')) setRecommended('safest');
                          else if (route.types.includes('Shortest')) setRecommended('shortest');
                        }}
                      >
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex flex-wrap gap-1">
                            {route.types.map(t => (
                              <span key={t} className={`text-xs px-2 py-0.5 rounded-full font-bold ${t === 'Fastest' ? 'bg-blue-100 text-blue-700' :
                                t === 'Safest' ? 'bg-green-100 text-green-700' :
                                  'bg-purple-100 text-purple-700'
                                }`}>
                                {t}
                              </span>
                            ))}
                          </div>
                          <div className="text-right">
                            <div className="font-bold text-gray-900">{Math.round(route.total_duration_seconds / 60)} min</div>
                            <div className="text-xs text-gray-500">{(route.total_distance_meters / 1000).toFixed(1)} km</div>
                          </div>
                        </div>

                        {/* Level Scores */}
                        <div className="space-y-2">
                          {/* Safety */}
                          <div>
                            <div className="flex justify-between text-xs mb-1">
                              <span className="text-gray-600">Safety Score</span>
                              <span className="font-medium text-gray-900">{safeScore}/100</span>
                            </div>
                            <div className="h-1.5 w-full bg-gray-200 rounded-full overflow-hidden">
                              <div className="h-full bg-green-500 rounded-full" style={{ width: `${safeScore}%` }}></div>
                            </div>
                          </div>

                          {/* Speed/Time Efficiency */}
                          <div>
                            <div className="flex justify-between text-xs mb-1">
                              <span className="text-gray-600">Speed Score</span>
                              <span className="font-medium text-gray-900">{speedScore}/100</span>
                            </div>
                            <div className="h-1.5 w-full bg-gray-200 rounded-full overflow-hidden">
                              <div className="h-full bg-blue-500 rounded-full" style={{ width: `${speedScore}%` }}></div>
                            </div>
                          </div>

                          {/* Distance Efficiency */}
                          <div>
                            <div className="flex justify-between text-xs mb-1">
                              <span className="text-gray-600">Distance Score</span>
                              <span className="font-medium text-gray-900">{distScore}/100</span>
                            </div>
                            <div className="h-1.5 w-full bg-gray-200 rounded-full overflow-hidden">
                              <div className="h-full bg-purple-500 rounded-full" style={{ width: `${distScore}%` }}></div>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  });
                })()}

                <button
                  onClick={() => setNavigationMode(true)}
                  className="w-full mt-3 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg font-semibold flex items-center justify-center space-x-2 transition-colors"
                >
                  <span>🚀</span>
                  <span>Start Navigation</span>
                </button>
              </div>
            </div>
          )}

          {/* Safety Legend */}
          {showSafetyOverlay && (fastest || safest || shortest) && (
            <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-3 text-sm">Safety Legend</h3>
              <div className="space-y-2 text-xs">
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded-full" style={{ backgroundColor: '#16a34a' }}></div>
                  <span className="text-gray-700">High Safety (85-100)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded-full" style={{ backgroundColor: '#ea580c' }}></div>
                  <span className="text-gray-700">Medium Safety (70-84)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded-full" style={{ backgroundColor: '#dc2626' }}></div>
                  <span className="text-gray-700">Low Safety (50-69)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded-full" style={{ backgroundColor: '#991b1b' }}></div>
                  <span className="text-gray-700">Very Low Safety (&lt;50)</span>
                </div>
              </div>
              <div className="mt-3 text-xs text-gray-600">
                <p>Data sources:</p>
                <ul className="list-disc list-inside mt-1 space-y-1">
                  <li>Tamil Nadu Crime Data 2022</li>
                  <li>Real-time weather conditions</li>
                  <li>Traffic-aware routing</li>
                </ul>
              </div>
            </div>
          )}
        </div>

        {/* Navigation Overlay (Mobile-like) */}
        {navigationMode && (recommended === 'fastest' ? fastest : (recommended === 'shortest' ? shortest : safest)) && (
          <div className="lg:col-span-2 relative h-[600px] bg-gray-900 rounded-xl overflow-hidden text-white flex flex-col">
            <div className="absolute top-0 left-0 right-0 z-[1001] bg-gray-900/90 backdrop-blur p-4 shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-2xl font-bold flex items-center">
                    <span className="mr-2">⬆️</span>
                    {(distanceRemaining || ((recommended === 'fastest' ? fastest : (recommended === 'shortest' ? shortest : safest)).total_distance_meters / 1000).toFixed(1))} km
                  </h2>
                  <p className="text-gray-300 text-sm">
                    {/* Display first instruction if available */}
                    {(recommended === 'fastest' ? fastest : (recommended === 'shortest' ? shortest : safest)).segments?.[0]?.instructions?.[0]
                      ? <span dangerouslySetInnerHTML={{ __html: (recommended === 'fastest' ? fastest : (recommended === 'shortest' ? shortest : safest)).segments[0].instructions[0] }} />
                      : "Head towards destination"}
                  </p>
                </div>
                <button
                  onClick={() => setNavigationMode(false)}
                  className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg font-bold text-sm"
                >
                  Exit
                </button>
              </div>
              <div className="flex justify-between items-center bg-gray-800 rounded-lg p-3">
                <div className="text-center">
                  <div className="text-xl font-bold text-green-400">
                    {eta || Math.round(((recommended === 'fastest' ? fastest : (recommended === 'shortest' ? shortest : safest)).total_duration_seconds) / 60)} min
                  </div>
                  <div className="text-xs text-gray-400">ETA</div>
                </div>
                <div className="text-center">
                  <div className="text-xl font-bold">
                    {(distanceRemaining || ((recommended === 'fastest' ? fastest : (recommended === 'shortest' ? shortest : safest)).total_distance_meters / 1000).toFixed(1))} km
                  </div>
                  <div className="text-xs text-gray-400">Remaining</div>
                </div>
                <div className="text-center">
                  <div className="text-xl font-bold text-blue-400">
                    {Math.round((recommended === 'fastest' ? fastest : (recommended === 'shortest' ? shortest : safest)).average_safety_score)}
                  </div>
                  <div className="text-xs text-gray-400">Safety Score</div>
                </div>
              </div>
            </div>

            <div className="flex-1 relative">
              {/* Re-using MapContainer but in dark/nav mode would be ideal. For now, we render the map similarly but customized for nav */}
              <MapContainer
                center={currentPos || centerPosition} // Center on user
                zoom={18} // Zoomed in for navigation
                style={{ height: '100%', width: '100%' }}
                zoomControl={false}
                attributionControl={false}
              >
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  // Dark mode tiles for navigation feel
                  url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                />

                {/* User Location Arrow */}
                {currentPos && (
                  <Marker position={currentPos} icon={pulsingIcon}>
                  </Marker>
                )}

                {/* Route Line */}
                {/* Route Line */}
                {getRoutePolylines(
                  recommended === 'fastest' ? fastest : (recommended === 'shortest' ? shortest : safest),
                  (recommended === 'fastest' ? fastest : (recommended === 'shortest' ? shortest : safest)).segments
                ).map((poly, idx) => (
                  <Polyline
                    key={`nav-poly-${idx}`}
                    positions={poly.positions}
                    pathOptions={{
                      color: poly.color, // Keep safety colors
                      weight: 8, // Thicker line for navigation
                      opacity: 0.8,
                    }}
                  />
                ))}

                {/* Destination */}
                {destPos && (
                  <Marker position={destPos}>
                    <Popup>Destination</Popup>
                  </Marker>
                )}

                <MapUpdater center={currentPos} />
              </MapContainer>
            </div>

            <div className="absolute bottom-6 left-4 right-4 z-[1001] pointer-events-none">
              <div className="bg-white/10 backdrop-blur-md rounded-xl p-3 border border-white/20 text-center">
                <p className="text-sm font-medium text-white shadow-black drop-shadow-md">
                  ⚠️ You are on a {recommended === 'safest' ? 'Safe Route' : (recommended === 'shortest' ? 'Shortest Route' : 'Fast Route')}. High patrol area nearby.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Standard Map (Hidden in Nav Mode) */}
        {!navigationMode && (
          <div className="lg:col-span-2 bg-white rounded-xl shadow-sm overflow-hidden border border-gray-200">

            <div style={{ height: '600px', width: '100%' }}>
              <MapContainer
                center={centerPosition}
                zoom={12}
                style={{ height: '100%', width: '100%' }}
              >
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                <ClickToSetLocation />

                <div className="leaflet-top leaflet-right" style={{ top: '80px', right: '10px', zIndex: 1000 }}>
                  <div className="bg-white rounded-md shadow-md p-1 flex flex-col space-y-1">
                    <button
                      onClick={(e) => { e.stopPropagation(); setSelectionMode('start'); }}
                      className={`p-2 rounded ${selectionMode === 'start' ? 'bg-blue-100 text-blue-700 font-bold' : 'hover:bg-gray-100 text-gray-700'}`}
                      title="Set Start Point"
                    >
                      <span className="text-xl">🚩</span>
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); setSelectionMode('destination'); }}
                      className={`p-2 rounded ${selectionMode === 'destination' ? 'bg-red-100 text-red-700 font-bold' : 'hover:bg-gray-100 text-gray-700'}`}
                      title="Set Destination"
                    >
                      <span className="text-xl">📍</span>
                    </button>
                  </div>
                </div>

                {/* Current location */}
                {currentPos && (
                  <Marker position={currentPos} icon={pulsingIcon}>
                    <Popup>Your location</Popup>
                  </Marker>
                )}

                {/* Display all routes */}
                {routes.map((route) => (
                  <React.Fragment key={route.id}>
                    {route.coordinates.map((coord, index) => {
                      if (index === route.coordinates.length - 1) return null;
                      const start = route.coordinates[index];
                      const end = route.coordinates[index + 1];
                      const traffic = end.traffic || 'low';
                      return (
                        <Polyline
                          key={`${route.id}-${index}`}
                          positions={[
                            [start.lat || start[0], start.lng || start[1]],
                            [end.lat || end[0], end.lng || end[1]]
                          ]}
                          pathOptions={{
                            color: getTrafficColor(traffic),
                            weight: 3,
                            opacity: 0.6,
                          }}
                        />
                      );
                    })}
                    <Marker position={[route.coordinates[0].lat || route.coordinates[0][0], route.coordinates[0].lng || route.coordinates[0][1]]}>
                      <Popup>{route.name}</Popup>
                    </Marker>
                  </React.Fragment>
                ))}

                {/* Destination marker */}
                {destPos && (
                  <Marker
                    position={destPos}
                    icon={L.divIcon({
                      className: 'destination-marker',
                      html: `<div style="width:30px;height:30px;border-radius:50%;background:#ef4444;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;font-size:18px">📍</div>`,
                      iconSize: [30, 30],
                      iconAnchor: [15, 15]
                    })}
                  >
                    <Popup>
                      <div>
                        <strong>Destination</strong><br />
                        Lat: {destPos[0].toFixed(6)}<br />
                        Lng: {destPos[1].toFixed(6)}
                      </div>
                    </Popup>
                  </Marker>
                )}

                {/* Draw route polylines with safety coloring */}
                {/* Alternative Routes */}
                {alternatives.map((alt, altIdx) => (
                  <React.Fragment key={`alt-${altIdx}`}>
                    {showSafetyOverlay && getRoutePolylines(alt, alt.segments).map((poly, idx) => (
                      <Polyline
                        key={`alt-${altIdx}-${idx}`}
                        positions={poly.positions}
                        pathOptions={{
                          color: poly.color,
                          weight: 4,
                          opacity: 0.4,
                        }}
                      >
                        <Popup>
                          <div>
                            <strong>Alternative Route {altIdx + 1}</strong><br />
                            Time: {Math.round((alt.total_duration_seconds || 0) / 60)} min<br />
                            Distance: {(alt.total_distance_meters / 1000).toFixed(1)} km<br />
                            Safety Score: {Math.round(alt.average_safety_score)}
                          </div>
                        </Popup>
                      </Polyline>
                    ))}
                  </React.Fragment>
                ))}

                {fastest && showSafetyOverlay && getRoutePolylines(fastest, fastest.segments).map((poly, idx) => (
                  <Polyline
                    key={`fastest-${idx}`}
                    positions={poly.positions}
                    pathOptions={{
                      color: poly.color,
                      weight: recommended === 'fastest' ? 5 : 3,
                      opacity: poly.opacity
                    }}
                  >
                    <Popup>
                      Fastest Route Segment<br />
                      Safety Score: {Math.round(poly.safetyScore)}
                    </Popup>
                  </Polyline>
                ))}

                {shortest && showSafetyOverlay && getRoutePolylines(shortest, shortest.segments).map((poly, idx) => (
                  <Polyline
                    key={`shortest-${idx}`}
                    positions={poly.positions}
                    pathOptions={{
                      color: poly.color,
                      weight: recommended === 'shortest' ? 5 : 3,
                      opacity: poly.opacity
                    }}
                  >
                    <Popup>
                      Shortest Route Segment<br />
                      Safety Score: {Math.round(poly.safetyScore)}
                    </Popup>
                  </Polyline>
                ))}

                {safest && showSafetyOverlay && getRoutePolylines(safest, safest.segments).map((poly, idx) => (
                  <Polyline
                    key={`safest-${idx}`}
                    positions={poly.positions}
                    pathOptions={{
                      color: poly.color,
                      weight: recommended === 'safest' ? 6 : 4,
                      opacity: poly.opacity
                    }}
                  >
                    <Popup>
                      Safest Route Segment<br />
                      Safety Score: {Math.round(poly.safetyScore)}
                    </Popup>
                    {/* Add time label label to the path like Google Maps */}
                    {idx === Math.floor(getRoutePolylines(safest, safest.segments).length / 2) && (
                      <Tooltip permanent direction="center" className="route-label-tooltip">
                        <div className="flex items-center gap-1">
                          <span className="font-bold">{Math.round((safest.total_duration_seconds || 0) / 60)} min</span>
                          {recommended === 'safest' && <span className="text-xs">🛡️</span>}
                        </div>
                      </Tooltip>
                    )}
                  </Polyline>
                ))}

                {/* Fastest Labels */}
                {fastest && recommended === 'fastest' && getRoutePolylines(fastest, fastest.segments).length > 0 && (
                  <Tooltip
                    position={getRoutePolylines(fastest, fastest.segments)[Math.floor(getRoutePolylines(fastest, fastest.segments).length / 2)].positions[0]}
                    permanent
                    direction="top"
                    className="route-label-tooltip fastest-active"
                  >
                    <div className="flex flex-col items-center">
                      <span className="font-bold text-white">{Math.round((fastest.total_duration_seconds || 0) / 60)} min</span>
                      <span className="text-[10px] text-blue-100">Fastest</span>
                    </div>
                  </Tooltip>
                )}

                {/* Fallback: Simple lines if no route geometry */}
                {fastest && (!fastest.segments || fastest.segments.length === 0) && currentPos && destPos && (
                  <Polyline
                    positions={[currentPos, destPos]}
                    pathOptions={{
                      color: recommended === 'fastest' ? '#2563eb' : '#9ca3af',
                      weight: recommended === 'fastest' ? 5 : 3,
                      opacity: 0.8
                    }}
                  />
                )}

                {safest && (!safest.segments || safest.segments.length === 0) && currentPos && destPos && (
                  <Polyline
                    positions={[currentPos, destPos]}
                    pathOptions={{
                      color: recommended === 'safest' ? '#16a34a' : '#9ca3af',
                      weight: recommended === 'safest' ? 5 : 3,
                      opacity: 0.8
                    }}
                  />
                )}


              </MapContainer>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RouteMap;

