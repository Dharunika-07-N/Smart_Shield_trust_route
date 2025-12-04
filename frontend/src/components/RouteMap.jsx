import React, { useEffect, useMemo, useRef, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMapEvents } from 'react-leaflet';
import L from 'leaflet';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';

const RouteMap = () => {
  const [currentPos, setCurrentPos] = useState(null);
  const [destPos, setDestPos] = useState(null);
  const [fastest, setFastest] = useState(null);
  const [safest, setSafest] = useState(null);
  const [recommended, setRecommended] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState([]);
  const [safetyOverlay, setSafetyOverlay] = useState(null);
  const [showSafetyOverlay, setShowSafetyOverlay] = useState(true);

  // Get traffic color
  const getTrafficColor = (traffic) => {
    switch (traffic) {
      case 'low': return '#22c55e';
      case 'medium': return '#eab308';
      case 'high': return '#ef4444';
      default: return '#6b7280';
    }
  };

  // Mock route data with traffic (used as example when no optimized routes)
  const routes = [
    {
      id: 1,
      name: 'Route #1247',
      status: 'active',
      safety: 92,
      stops: 5,
      distance: '12.5 km',
      time: '28 min',
      coordinates: [
        { lat: 40.7128, lng: -74.0060, traffic: 'low', safety: 95 },
        { lat: 40.7210, lng: -74.0120, traffic: 'medium', safety: 90 },
        { lat: 40.7285, lng: -74.0050, traffic: 'high', safety: 85 },
        { lat: 40.7320, lng: -73.9950, traffic: 'low', safety: 95 },
        { lat: 40.7250, lng: -73.9850, traffic: 'medium', safety: 88 },
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
        { lat: 40.7500, lng: -73.9900, traffic: 'low', safety: 88 },
        { lat: 40.7550, lng: -73.9850, traffic: 'medium', safety: 85 },
        { lat: 40.7600, lng: -73.9800, traffic: 'high', safety: 80 },
        { lat: 40.7650, lng: -73.9750, traffic: 'low', safety: 87 },
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
        { lat: 40.7100, lng: -73.9950, traffic: 'low', safety: 90 },
        { lat: 40.7150, lng: -73.9900, traffic: 'medium', safety: 88 },
        { lat: 40.7200, lng: -73.9850, traffic: 'low', safety: 92 },
        { lat: 40.7250, lng: -73.9800, traffic: 'high', safety: 82 },
        { lat: 40.7300, lng: -73.9750, traffic: 'medium', safety: 86 },
        { lat: 40.7350, lng: -73.9700, traffic: 'low', safety: 89 },
      ],
    },
  ];

  // Animated pulsing dot icon for current location
  const pulsingIcon = useMemo(() => {
    const size = 20;
    return L.divIcon({
      className: 'pulsing-marker',
      html: `<div style="width:${size}px;height:${size}px;border-radius:50%;background:#3b82f6;box-shadow:0 0 0 0 rgba(59,130,246,0.7);animation:pulse 2s infinite"></div>`
    });
  }, []);

  useEffect(() => {
    const style = document.createElement('style');
    style.innerHTML = `
      @keyframes pulse { 0%{box-shadow:0 0 0 0 rgba(59,130,246,0.7)} 70%{box-shadow:0 0 0 15px rgba(59,130,246,0)} 100%{box-shadow:0 0 0 0 rgba(59,130,246,0)} }
      .leaflet-container .pulsing-marker { transform: translate(-50%, -50%); }
    `;
    document.head.appendChild(style);
    return () => { document.head.removeChild(style); };
  }, []);

  // Geolocate user and keep updating
  useEffect(() => {
    if (!navigator.geolocation) return;
    const watchId = navigator.geolocation.watchPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords;
        setCurrentPos([latitude, longitude]);
      },
      () => setError('Unable to get current location'),
      { enableHighAccuracy: true, maximumAge: 5000, timeout: 10000 }
    );
    return () => navigator.geolocation.clearWatch(watchId);
  }, []);

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
    if (!currentPos || !destPos) { setError('Select destination'); return; }
    setLoading(true);
    setError('');
    setFastest(null); setSafest(null); setRecommended(null);
    try {
      const [fastRes, safeRes] = await Promise.all([
        fetch(`${API_BASE}/api/v1/delivery/optimize`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(buildRequest(currentPos, destPos, [ 'time', 'distance' ]))
        }),
        fetch(`${API_BASE}/api/v1/delivery/optimize`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(buildRequest(currentPos, destPos, [ 'safety', 'time' ]))
        })
      ]);
      const fastJson = await fastRes.json();
      const safeJson = await safeRes.json();
      if (!fastJson.success) throw new Error(fastJson.detail || 'Fastest route failed');
      if (!safeJson.success) throw new Error(safeJson.detail || 'Safest route failed');
      setFastest(fastJson.data);
      setSafest(safeJson.data);
      // Simple recommendation logic
      const fastestSecs = fastJson.data?.total_duration_seconds || 0;
      const safestSecs = safeJson.data?.total_duration_seconds || 0;
      const fastestSafety = fastJson.data?.average_safety_score || 0;
      const chooseSafe = fastestSafety < 65 || (safestSecs && fastestSecs && (safestSecs - fastestSecs) / fastestSecs < 0.2);
      setRecommended(chooseSafe ? 'safest' : 'fastest');

      // Fetch safety overlay for recommended route
      await fetchSafetyOverlay(chooseSafe ? safeJson.data : fastJson.data);
    } catch (e) {
      setError(e.message || 'Optimization failed');
    } finally {
      setLoading(false);
    }
  };

  const fetchSafetyOverlay = async (routeData) => {
    if (!routeData || !routeData.segments || routeData.segments.length === 0) return;

    try {
      const coords = [];
      if (currentPos) {
        coords.push({ latitude: currentPos[0], longitude: currentPos[1] });
      }

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

      if (coords.length > 0) {
        currentPos_ = coords[coords.length - 1];
      }
    });

    return polylines;
  };

  const centerPosition = currentPos || [11.0168, 76.9558]; // Default to Coimbatore

  const ClickToSetDestination = () => {
    useMapEvents({
      click(e) {
        setDestPos([e.latlng.lat, e.latlng.lng]);
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
                        className="block w-full text-left px-3 py-2 text-sm hover:bg-gray-50"
                        onClick={() => { setDestPos([parseFloat(r.lat), parseFloat(r.lon)]); setQuery(r.display_name); setResults([]); }}
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
              <button
                onClick={optimize}
                disabled={!currentPos || !destPos || loading}
                className={`w-full px-4 py-2 rounded-md text-white ${(!currentPos || !destPos || loading) ? 'bg-gray-400' : 'bg-primary-600 hover:bg-primary-700'}`}
              >
                {loading ? 'Optimizing…' : 'Optimize Route'}
              </button>
              {error && <div className="text-sm text-red-600">{error}</div>}

              {/* Safety overlay toggle */}
              {(fastest || safest) && (
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

          {(fastest || safest) && (
            <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-4">Results</h3>
              <div className="space-y-3 text-sm">
                {fastest && (
                  <div className="flex items-center justify-between">
                    <span className="text-gray-700">Fastest</span>
                    <span className="text-gray-900 font-medium">{Math.round((fastest.total_duration_seconds||0)/60)} min • {(fastest.total_distance_meters/1000).toFixed(1)} km</span>
                  </div>
                )}
                {safest && (
                  <div className="flex items-center justify-between">
                    <span className="text-gray-700">Safest</span>
                    <span className="text-gray-900 font-medium">{Math.round((safest.total_duration_seconds||0)/60)} min • {(safest.total_distance_meters/1000).toFixed(1)} km • {Math.round(safest.average_safety_score)} safety</span>
                  </div>
                )}
                {recommended && (
                  <div className="text-xs text-success-700 bg-success-50 border border-success-200 rounded px-2 py-1 inline-block">
                    Recommended: {recommended === 'safest' ? 'Safest Route' : 'Fastest Route'}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Safety Legend */}
          {showSafetyOverlay && (fastest || safest) && (
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

        {/* Map */}
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

              <ClickToSetDestination />

              {/* Current location */}
              {currentPos && (
                <Marker position={currentPos} icon={pulsingIcon}>
                  <Popup>Your location</Popup>
                </Marker>
              )}

              {/* Destination marker */}
              {destPos && (
                <Marker position={destPos}>
                  <Popup>Destination</Popup>
                </Marker>
              )}

              {/* If optimized routes exist, draw them with safety coloring */}
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

              {safest && showSafetyOverlay && getRoutePolylines(safest, safest.segments).map((poly, idx) => (
                <Polyline
                  key={`safest-${idx}`}
                  positions={poly.positions}
                  pathOptions={{
                    color: poly.color,
                    weight: recommended === 'safest' ? 5 : 3,
                    opacity: poly.opacity
                  }}
                >
                  <Popup>
                    Safest Route Segment<br />
                    Safety Score: {Math.round(poly.safetyScore)}
                  </Popup>
                </Polyline>
              ))}

              {/* Fallback: show example sample routes when no optimized data */}
              {!fastest && !safest && routes.map((route) => (
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

              {/* Fallback simple connection lines if segments missing */}
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

              {/* Safety overlay markers for segment scores */}
              {showSafetyOverlay && safetyOverlay && safetyOverlay.segment_scores && safetyOverlay.segment_scores.map((segment, idx) => {
                const coord = segment.coordinates;
                const score = segment.overall_score;
                return (
                  <Marker
                    key={`safety-${idx}`}
                    position={[coord.latitude, coord.longitude]}
                    icon={L.divIcon({
                      className: 'safety-marker',
                      html: `<div style="width:12px;height:12px;border-radius:50%;background:${getSafetyColor(score)};border:2px solid white;box-shadow:0 2px 4px rgba(0,0,0,0.3)"></div>`
                    })}
                  >
                    <Popup>
                      Safety Score: {Math.round(score)}<br />
                      Risk Level: {segment.risk_level}
                    </Popup>
                  </Marker>
                );
              })}
            </MapContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RouteMap;
