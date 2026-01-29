import React, { useEffect, useMemo, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMapEvents, useMap, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import { api } from '../services/api';
import { FiNavigation, FiClock, FiShield, FiMapPin, FiChevronRight } from 'react-icons/fi';
import useLocation from '../hooks/useLocation';
import SafetyHeatmap from './SafetyHeatmap';

import { API_ROOT_URL as API_BASE } from '../utils/constants';

const MapUpdater = ({ center }) => {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.setView(center, map.getZoom());
    }
  }, [center, map]);
  return null;
};

const serviceColors = {
  swiggy: '#fc8019',
  zomato: '#cb202d',
  rapido: '#f9d923',
  'red-taxi': '#800000'
};

const SafetyGauge = ({ score }) => {
  const radius = 24;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  const getColor = (s) => {
    if (s >= 80) return '#10b981';
    if (s >= 60) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="relative flex items-center justify-center w-20 h-20">
      <svg className="w-full h-full transform -rotate-90">
        <circle
          cx="40"
          cy="40"
          r={radius}
          stroke="#e5e7eb"
          strokeWidth="6"
          fill="transparent"
        />
        <circle
          cx="40"
          cy="40"
          r={radius}
          stroke={getColor(score)}
          strokeWidth="6"
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.5s ease' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-gray-900 font-bold text-lg leading-none">{score}</span>
        <span className="text-gray-500 text-[10px]">Safety</span>
      </div>
    </div>
  );
};

const RouteMap = ({ variant = 'default' }) => {
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
  const [startQuery, setStartQuery] = useState('');
  const [destQuery, setDestQuery] = useState('');
  const [searching, setSearching] = useState(null); // 'start' or 'destination' or null
  const [results, setResults] = useState([]);
  const [safetyOverlay, setSafetyOverlay] = useState(null);
  const [showSafetyOverlay, setShowSafetyOverlay] = useState(true);

  // Delivery Service & Crowdsourcing
  // const [selectedService, setSelectedService] = useState('swiggy'); // Removed branding
  const [crowdsourcedAlerts, setCrowdsourcedAlerts] = useState([]);
  const [quizOpen, setQuizOpen] = useState(false);
  const [quizAnswers, setQuizAnswers] = useState({ isFaster: null, hasTraffic: null });
  const [submittingQuiz, setSubmittingQuiz] = useState(false);

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
    const color = '#3b82f6'; // Default Blue
    return L.divIcon({
      className: 'pulsing-marker',
      html: `<div style="width:${size}px;height:${size}px;border-radius:50%;background:${color};box-shadow:0 0 0 0 ${color}77;animation:pulse 2s infinite"></div>`
    });
  }, []);

  // Update current position when location changes
  useEffect(() => {
    if (location && !startQuery) {
      setCurrentPos([location.latitude, location.longitude]);
      setStartQuery('Current Location');
    }
  }, [location, startQuery]);

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

  // Search via Nominatim
  const searchPlaces = async (text, type) => {
    if (!text || text.length < 3) { setResults([]); return; }
    setSearching(type);
    try {
      const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(text)}`;
      const res = await fetch(url, { headers: { 'Accept': 'application/json' } });
      const data = await res.json();
      setResults(data.slice(0, 5));
    } catch (e) {
      // ignore
    } finally {
      // Small delay to allow click to register before results disappear if needed,
      // but usually not needed with React state.
    }
  };

  const reverseGeocode = async (lat, lon) => {
    try {
      const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`;
      const res = await fetch(url, { headers: { 'Accept': 'application/json' } });
      const data = await res.json();
      return data.display_name;
    } catch (e) {
      return `${lat.toFixed(4)}, ${lon.toFixed(4)}`;
    }
  };

  // Fetch alerts on mount and every 30s
  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await api.getAlerts();
        if (res.status === 'success') {
          setCrowdsourcedAlerts(res.data);
        }
      } catch (err) {
        console.warn('Failed to fetch crowdsourced alerts');
      }
    };
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleQuizSubmit = async () => {
    if (quizAnswers.isFaster === null || quizAnswers.hasTraffic === null) {
      alert('Please answer both questions');
      return;
    }
    setSubmittingQuiz(true);
    try {
      await api.submitAlert({
        rider_id: 'RIDER_' + Math.floor(Math.random() * 1000),
        service_type: 'generic',
        location: { lat: currentPos[0], lng: currentPos[1] },
        is_faster: quizAnswers.isFaster,
        has_traffic_issues: quizAnswers.hasTraffic
      });
      setQuizOpen(false);
      setQuizAnswers({ isFaster: null, hasTraffic: null });
      // Refresh alerts
      const res = await api.getAlerts();
      if (res.status === 'success') setCrowdsourcedAlerts(res.data);
    } catch (err) {
      alert('Failed to submit report. Please try again.');
    } finally {
      setSubmittingQuiz(false);
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
      setError('Please select both a starting point and a destination by searching or clicking on the map');
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
    if (score >= 85) return '#39FF14'; // Neon Green
    if (score >= 70) return '#ea580c'; // Orange
    if (score >= 50) return '#ef4444'; // Red
    return '#991b1b'; // Dark Red
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
          color: '#39FF14', // Neon Green as requested
          weight: isRecommended ? 6 : 4,
          opacity: isRecommended ? 0.9 : 0.6,
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
      async click(e) {
        const coords = [e.latlng.lat, e.latlng.lng];
        if (selectionMode === 'start') {
          console.log('Start point selected from map click:', coords);
          setCurrentPos(coords);
          const address = await reverseGeocode(coords[0], coords[1]);
          setStartQuery(address);
          setSelectionMode('destination');
        } else {
          console.log('Destination selected from map click:', coords);
          setDestPos(coords);
          const address = await reverseGeocode(coords[0], coords[1]);
          setDestQuery(address);
          setResults([]);
        }
      }
    });
    return null;
  };

  if (variant === 'dark-minimal') {
    return (
      <div className="w-full h-full">
        <MapContainer
          center={centerPosition}
          zoom={13}
          zoomControl={false}
          style={{ height: '100%', width: '100%' }}
          className="dark-map"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />

          {/* Display current position */}
          {currentPos && (
            <Marker position={currentPos} icon={pulsingIcon} />
          )}

          {/* Simple Curved Route Visualization (Mocking Image 2) */}
          <Polyline
            positions={[
              [centerPosition[0], centerPosition[1] - 0.02],
              [centerPosition[0] + 0.01, centerPosition[1] - 0.01],
              [centerPosition[0] - 0.01, centerPosition[1] + 0.01],
              [centerPosition[0], centerPosition[1] + 0.02],
            ]}
            pathOptions={{
              color: '#39FF14',
              weight: 5,
              opacity: 0.8,
              dashArray: '10, 10'
            }}
          />

          {/* Map markers like Image 2 */}
          <Marker
            position={[centerPosition[0], centerPosition[1] - 0.02]}
            icon={L.divIcon({
              className: 'map-num-marker',
              html: `<div style="width:24px;height:24px;background:#10b981;border-radius:50%;display:flex;items-center;justify-content:center;color:white;font-weight:bold;font-size:12px;border:2px solid rgba(255,255,255,0.2)">1</div>`
            })}
          />

          <Marker
            position={[centerPosition[0] + 0.01, centerPosition[1] - 0.01]}
            icon={L.divIcon({
              className: 'map-num-marker',
              html: `<div style="width:24px;height:24px;background:#10b981;border-radius:50%;display:flex;items-center;justify-content:center;color:white;font-weight:bold;font-size:12px;border:2px solid rgba(255,255,255,0.2)">2</div>`
            })}
          />

          <Marker
            position={[centerPosition[0], centerPosition[1] + 0.02]}
            icon={L.divIcon({
              className: 'map-pin-marker',
              html: `<div style="color:#f97316;font-size:24px;filter:drop-shadow(0 0 10px rgba(249,115,22,0.4))">📍</div>`
            })}
          />

          <MapUpdater center={centerPosition} />
        </MapContainer>
      </div>
    );
  }

  return (
    <div className="space-y-6 lg:p-4">


      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls */}
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-4">Route Planner</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm text-gray-600 mb-1">Starting Point</label>
                <div className="relative">
                  <input
                    type="text"
                    value={startQuery}
                    onChange={(e) => {
                      setStartQuery(e.target.value);
                      searchPlaces(e.target.value, 'start');
                    }}
                    placeholder="Search start or click on map"
                    className={`w-full border rounded-md px-3 py-2 text-sm ${selectionMode === 'start' ? 'border-primary-500 ring-1 ring-primary-200' : 'border-gray-300'}`}
                    onFocus={() => setSelectionMode('start')}
                  />
                  {currentPos && (
                    <button
                      onClick={() => {
                        if (location) {
                          setCurrentPos([location.latitude, location.longitude]);
                          setStartQuery('Current Location');
                        }
                      }}
                      className="absolute right-2 top-1/2 -translate-y-1/2 text-primary-600 hover:text-primary-700 p-1"
                      title="Use current location"
                    >
                      📍
                    </button>
                  )}
                </div>
                {searching === 'start' && <div className="text-xs text-gray-500 mt-1">Searching...</div>}
                {searching === 'start' && !!results.length && (
                  <div className="mt-2 border border-gray-200 rounded-md max-h-40 overflow-auto bg-white z-[1002] relative">
                    {results.map((r) => (
                      <button
                        key={`${r.place_id}`}
                        className="block w-full text-left px-3 py-2 text-sm hover:bg-gray-50 transition-colors"
                        onClick={() => {
                          const newStart = [parseFloat(r.lat), parseFloat(r.lon)];
                          setCurrentPos(newStart);
                          setStartQuery(r.display_name);
                          setResults([]);
                          setSearching(null);
                          setSelectionMode('destination');
                        }}
                      >
                        {r.display_name}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm text-gray-600 mb-1">Destination</label>
                <input
                  type="text"
                  value={destQuery}
                  onChange={(e) => {
                    setDestQuery(e.target.value);
                    searchPlaces(e.target.value, 'destination');
                  }}
                  placeholder="Search destination or click on map"
                  className={`w-full border rounded-md px-3 py-2 text-sm ${selectionMode === 'destination' ? 'border-primary-500 ring-1 ring-primary-200' : 'border-gray-300'}`}
                  onFocus={() => setSelectionMode('destination')}
                />
                {searching === 'destination' && <div className="text-xs text-gray-500 mt-1">Searching...</div>}
                {searching === 'destination' && !!results.length && (
                  <div className="mt-2 border border-gray-200 rounded-md max-h-40 overflow-auto bg-white z-[1002] relative">
                    {results.map((r) => (
                      <button
                        key={`${r.place_id}`}
                        className="block w-full text-left px-3 py-2 text-sm hover:bg-gray-50 transition-colors"
                        onClick={() => {
                          const newDest = [parseFloat(r.lat), parseFloat(r.lon)];
                          setDestPos(newDest);
                          setDestQuery(r.display_name);
                          setResults([]);
                          setSearching(null);
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

              <div className="bg-blue-50 p-3 rounded-lg border border-blue-100 mb-4">
                <p className="text-xs text-blue-800 font-medium mb-2">Crowdsourced Intelligence</p>
                <button
                  onClick={() => setQuizOpen(true)}
                  className="w-full flex items-center justify-center gap-2 bg-white text-blue-600 py-2 rounded-md text-xs font-bold border border-blue-200 hover:bg-blue-50 transition-colors"
                >
                  📡 Report Live Conditions
                </button>
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
            <div className="space-y-4">
              <h3 className="font-bold text-gray-900 text-lg px-1">Route Options</h3>
              <div className="space-y-4">
                {(() => {
                  const allRoutes = [];
                  const addRoute = (route, type) => {
                    if (!route) return;
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

                  // Add alternative routes as well
                  if (alternatives && alternatives.length > 0) {
                    alternatives.forEach((alt, idx) => {
                      addRoute(alt, `Alt ${idx + 1}`);
                    });
                  }

                  return allRoutes.map((route) => {
                    const isActive =
                      (recommended === 'fastest' && route.types.includes('Fastest')) ||
                      (recommended === 'safest' && route.types.includes('Safest')) ||
                      (recommended === 'shortest' && route.types.includes('Shortest'));

                    const duration = Math.round(route.total_duration_seconds / 60);
                    const distanceKm = (route.total_distance_meters / 1000).toFixed(1);
                    const distanceMi = (route.total_distance_meters / 1609.34).toFixed(1);
                    const safetyScore = Math.round(route.average_safety_score);

                    return (
                      <div
                        key={route.sig}
                        className={`p-5 rounded-2xl border-2 transition-all cursor-pointer ${isActive
                          ? 'border-blue-500 bg-blue-50/50 shadow-md ring-1 ring-blue-500/20'
                          : 'border-gray-100 bg-white hover:border-gray-200 shadow-sm'
                          }`}
                        onClick={() => {
                          if (route.types.includes('Fastest')) setRecommended('fastest');
                          else if (route.types.includes('Safest')) setRecommended('safest');
                          else if (route.types.includes('Shortest')) setRecommended('shortest');
                        }}
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex gap-4">
                            {/* Vertical Timeline */}
                            <div className="flex flex-col items-center py-1">
                              <div className="w-3 h-3 rounded-full bg-green-500"></div>
                              <div className="w-0.5 flex-1 bg-blue-200 my-1 min-h-[40px]"></div>
                              <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                            </div>

                            <div className="space-y-4">
                              <div className="flex flex-wrap gap-1 mb-1">
                                {route.types.map(t => (
                                  <span key={t} className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${t === 'Fastest' ? 'bg-blue-100 text-blue-700' :
                                    t === 'Safest' ? 'bg-green-100 text-green-700' :
                                      t === 'Shortest' ? 'bg-purple-100 text-purple-700' :
                                        'bg-gray-100 text-gray-700'
                                    }`}>
                                    {t}
                                  </span>
                                ))}
                              </div>
                              <div>
                                <div className="flex items-center gap-2 text-gray-500 text-xs">
                                  <FiMapPin className="text-[10px]" />
                                  <span className="truncate max-w-[120px]">{startQuery || 'Current Location'}</span>
                                </div>
                                <div className="flex items-center gap-2 text-gray-900 font-bold text-sm mt-2">
                                  <FiMapPin className="text-[10px]" />
                                  <span className="truncate max-w-[120px]">{destQuery || 'Destination'}</span>
                                </div>
                              </div>

                              <div className="flex items-center gap-4 text-gray-600">
                                <div className="flex items-center gap-1.5 text-sm">
                                  <FiNavigation className="text-gray-400 rotate-45" />
                                  <span>{distanceMi} mi</span>
                                </div>
                                <div className="flex items-center gap-1.5 text-sm">
                                  <FiClock className="text-gray-400" />
                                  <span>{duration} min</span>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Safety Gauge */}
                          <SafetyGauge score={safetyScore} />
                        </div>

                        <button
                          className={`w-full mt-5 py-3 rounded-xl font-bold text-sm transition-all transform active:scale-[0.98] ${isActive
                            ? 'bg-blue-600 text-white shadow-lg shadow-blue-200'
                            : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-50'
                            }`}
                        >
                          {isActive ? 'Selected' : 'Select Route'}
                        </button>
                      </div>
                    );
                  });
                })()}

                <button
                  onClick={() => setNavigationMode(true)}
                  className="w-full mt-2 bg-gray-900 hover:bg-black text-white py-4 rounded-2xl font-bold text-base flex items-center justify-center space-x-3 transition-all shadow-xl hover:translate-y-[-2px] active:translate-y-[0px]"
                >
                  <span className="text-xl">🚀</span>
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
                  <div className="w-4 h-4 rounded-full" style={{ backgroundColor: '#22c55e' }}></div>
                  <span className="text-gray-700">Safe Zone (75-100)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded-full" style={{ backgroundColor: '#f59e0b' }}></div>
                  <span className="text-gray-700">Moderate Risk (50-74)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded-full" style={{ backgroundColor: '#ef4444' }}></div>
                  <span className="text-gray-700">Caution: High Risk (&lt;50)</span>
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
                      color: poly.safetyScore >= 80 ? '#39FF14' : poly.color,
                      weight: 10,
                      opacity: 0.9,
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
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                  url={variant === 'dark-minimal'
                    ? "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                    : "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  }
                />

                <SafetyHeatmap show={showSafetyOverlay} />

                <ClickToSetLocation />

                {/* Crowdsourced Alerts */}
                {crowdsourcedAlerts.map((alert) => (
                  <Marker
                    key={alert.id}
                    position={[alert.location.lat, alert.location.lng]}
                    icon={L.divIcon({
                      className: 'alert-marker',
                      html: `<div style="color: ${alert.has_traffic_issues ? '#ef4444' : '#22c55e'}; font-size: 24px;">${alert.has_traffic_issues ? '⚠️' : '🚀'}</div>`,
                      iconSize: [30, 30],
                      iconAnchor: [15, 15]
                    })}
                  >
                    <Popup>
                      <div className="p-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold text-white bg-gray-800 uppercase`}>
                            {alert.service_type}
                          </span>
                          <span className="text-[10px] text-gray-500">
                            {new Date(alert.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>
                        <p className="text-sm font-bold">
                          {alert.has_traffic_issues ? 'Traffic Reported' : 'Smooth Route'}
                        </p>
                        <p className="text-xs text-gray-600">
                          {alert.is_faster ? 'Rider says: Much faster than regular.' : 'Rider says: Slower than expected.'}
                        </p>
                      </div>
                    </Popup>
                  </Marker>
                ))}

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
                    <Popup>{startQuery === 'Current Location' ? 'Your current location' : 'Starting Point'}</Popup>
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
                      color: recommended === 'safest' ? '#39FF14' : '#9ca3af',
                      weight: recommended === 'safest' ? 6 : 4,
                      opacity: 0.9
                    }}
                  />
                )}


              </MapContainer>
            </div>
          </div>
        )}
      </div>

      {/* Interactive Quiz Modal */}
      {quizOpen && (
        <div className="fixed inset-0 z-[2000] flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden transform animate-in fade-in zoom-in duration-300">
            <div className="p-6 text-white bg-blue-600">
              <h3 className="text-xl font-bold flex items-center gap-2">
                <span>⚡</span> Rider Pulse Check
              </h3>
              <p className="text-sm opacity-90 mt-1">Help other riders find better routes!</p>
            </div>

            <div className="p-6 space-y-6">
              <div>
                <p className="font-semibold text-gray-900 mb-3 text-sm">1. Is this route faster and has less traffic?</p>
                <div className="flex gap-3">
                  <button
                    onClick={() => setQuizAnswers({ ...quizAnswers, isFaster: true })}
                    className={`flex-1 py-3 rounded-xl border-2 font-medium transition-all ${quizAnswers.isFaster === true ? 'border-green-500 bg-green-50 text-green-700' : 'border-gray-100 hover:border-gray-200'}`}
                  >
                    🚀 Yes, Smooth
                  </button>
                  <button
                    onClick={() => setQuizAnswers({ ...quizAnswers, isFaster: false })}
                    className={`flex-1 py-3 rounded-xl border-2 font-medium transition-all ${quizAnswers.isFaster === false ? 'border-red-500 bg-red-50 text-red-700' : 'border-gray-100 hover:border-gray-200'}`}
                  >
                    🚗 No, Slow
                  </button>
                </div>
              </div>

              <div>
                <p className="font-semibold text-gray-900 mb-3 text-sm">2. Does this route have traffic issues (constructions/accidents)?</p>
                <div className="flex gap-3">
                  <button
                    onClick={() => setQuizAnswers({ ...quizAnswers, hasTraffic: true })}
                    className={`flex-1 py-3 rounded-xl border-2 font-medium transition-all ${quizAnswers.hasTraffic === true ? 'border-amber-500 bg-amber-50 text-amber-700' : 'border-gray-100 hover:border-gray-200'}`}
                  >
                    ⚠️ Yes, Blocked
                  </button>
                  <button
                    onClick={() => setQuizAnswers({ ...quizAnswers, hasTraffic: false })}
                    className={`flex-1 py-3 rounded-xl border-2 font-medium transition-all ${quizAnswers.hasTraffic === false ? 'border-blue-500 bg-blue-50 text-blue-700' : 'border-gray-100 hover:border-gray-200'}`}
                  >
                    ✅ No, Clear
                  </button>
                </div>
              </div>

              <div className="flex gap-4 pt-4">
                <button
                  onClick={() => setQuizOpen(false)}
                  className="flex-1 py-3 text-gray-500 font-semibold hover:bg-gray-50 rounded-xl transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleQuizSubmit}
                  disabled={submittingQuiz || quizAnswers.isFaster === null || quizAnswers.hasTraffic === null}
                  className={`flex-[2] py-3 rounded-xl text-white font-bold shadow-lg transition-all transform active:scale-95 ${submittingQuiz ? 'bg-gray-400' : 'bg-gray-900 hover:bg-black'
                    }`}
                >
                  {submittingQuiz ? 'Sending...' : 'Report Condition'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RouteMap;

