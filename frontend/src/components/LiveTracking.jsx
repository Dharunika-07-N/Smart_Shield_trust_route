import React, { useEffect, useState, useRef, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import { api } from '../services/api';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';

// Component to update map view when location changes
const MapUpdater = ({ center, zoom }) => {
  const map = useMap();
  
  useEffect(() => {
    if (center) {
      map.setView(center, zoom || map.getZoom());
    }
  }, [center, zoom, map]);
  
  return null;
};

const LiveTracking = ({ deliveryId, isRider = false }) => {
  const [currentLocation, setCurrentLocation] = useState(null);
  const [locationHistory, setLocationHistory] = useState([]);
  const [status, setStatus] = useState('pending');
  const [speed, setSpeed] = useState(null);
  const [heading, setHeading] = useState(null);
  const [batteryLevel, setBatteryLevel] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState('');
  const [deliveryIdInput, setDeliveryIdInput] = useState(deliveryId || '');
  
  const wsRef = useRef(null);
  const watchIdRef = useRef(null);

  // Rider icon with direction indicator
  const riderIcon = useMemo(() => {
    if (!heading) {
      return L.divIcon({
        className: 'rider-marker',
        html: `<div style="width:30px;height:30px;border-radius:50%;background:#3b82f6;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.3);position:relative">
                 <div style="position:absolute;top:-8px;left:50%;transform:translateX(-50%);width:0;height:0;border-left:6px solid transparent;border-right:6px solid transparent;border-bottom:8px solid #3b82f6"></div>
               </div>`,
        iconSize: [30, 30],
        iconAnchor: [15, 15]
      });
    }
    
    return L.divIcon({
      className: 'rider-marker',
      html: `<div style="width:30px;height:30px;border-radius:50%;background:#3b82f6;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.3);position:relative;transform:rotate(${heading}deg)">
               <div style="position:absolute;top:-8px;left:50%;transform:translateX(-50%) rotate(0deg);width:0;height:0;border-left:6px solid transparent;border-right:6px solid transparent;border-bottom:8px solid #3b82f6"></div>
             </div>`,
      iconSize: [30, 30],
      iconAnchor: [15, 15]
    });
  }, [heading]);

  // Connect to WebSocket for real-time updates (with debouncing)
  useEffect(() => {
    // Don't connect if rider mode, no delivery ID, or delivery ID is too short
    if (isRider || !deliveryIdInput || deliveryIdInput.trim().length < 3) {
      // Close existing connection if delivery ID is too short
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
        setConnected(false);
      }
      return;
    }

    // Debounce: wait 500ms after user stops typing before connecting
    const debounceTimer = setTimeout(() => {
      const connectWebSocket = () => {
        // Double-check delivery ID is still valid
        if (!deliveryIdInput || deliveryIdInput.trim().length < 3) {
          return;
        }

        try {
          // Close existing connection if any
          if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
          }

          // Construct WebSocket URL from API_BASE
          let wsUrl;
          if (API_BASE.startsWith('http://')) {
            wsUrl = API_BASE.replace('http://', 'ws://') + `/api/v1/delivery/${deliveryIdInput.trim()}/ws`;
          } else if (API_BASE.startsWith('https://')) {
            wsUrl = API_BASE.replace('https://', 'wss://') + `/api/v1/delivery/${deliveryIdInput.trim()}/ws`;
          } else {
            // If API_BASE is relative or doesn't have protocol, use current origin
            const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            wsUrl = `${wsProtocol}//${window.location.host}${API_BASE}/api/v1/delivery/${deliveryIdInput.trim()}/ws`;
          }
          
          const ws = new WebSocket(wsUrl);
          wsRef.current = ws;

          ws.onopen = () => {
            console.log('WebSocket connected');
            setConnected(true);
            setError('');
          };

          ws.onmessage = (event) => {
            try {
              const data = JSON.parse(event.data);
              
              if (data.type === 'location_update' || data.type === 'initial_location') {
                const location = [data.location.latitude, data.location.longitude];
                setCurrentLocation(location);
                setStatus(data.status || 'in_transit');
                setSpeed(data.speed_kmh);
                setHeading(data.heading);
                setBatteryLevel(data.battery_level);
                setLastUpdate(new Date(data.timestamp));
                
                // Add to history
                setLocationHistory(prev => {
                  const newHistory = [...prev, {
                    location,
                    timestamp: data.timestamp,
                    speed: data.speed_kmh,
                    heading: data.heading
                  }];
                  // Keep only last 100 points
                  return newHistory.slice(-100);
                });
              } else if (data.type === 'pong') {
                // Keep-alive response
                console.log('WebSocket pong received');
              }
            } catch (e) {
              console.error('Error parsing WebSocket message:', e);
            }
          };

          ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            // Only show error if it's not a connection refused (backend might not be running)
            if (ws.readyState === WebSocket.CONNECTING || ws.readyState === WebSocket.CLOSED) {
              setError('Cannot connect to server. Make sure the backend is running on ' + API_BASE);
            } else {
              setError('WebSocket connection error');
            }
            setConnected(false);
          };

          ws.onclose = (event) => {
            console.log('WebSocket disconnected', event.code, event.reason);
            setConnected(false);
            
            // Only attempt to reconnect if it wasn't a manual close and delivery ID is still valid
            if (event.code !== 1000 && deliveryIdInput && deliveryIdInput.trim().length >= 3) {
              // Attempt to reconnect after 3 seconds
              setTimeout(connectWebSocket, 3000);
            }
          };
        } catch (e) {
          console.error('Error connecting WebSocket:', e);
          setError('Failed to connect to tracking server: ' + e.message);
        }
      };

      connectWebSocket();
    }, 500); // Wait 500ms after user stops typing

    return () => {
      clearTimeout(debounceTimer);
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [deliveryIdInput, isRider]);

  // For rider mode: Get GPS location and send updates every 30 seconds
  useEffect(() => {
    if (!isRider || !deliveryIdInput) return;

    const sendLocationUpdate = async (position) => {
      try {
        const location = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        };

        const updateData = {
          delivery_id: deliveryIdInput,
          current_location: location,
          status: 'in_transit',
          speed_kmh: position.coords.speed ? (position.coords.speed * 3.6) : null, // Convert m/s to km/h
          heading: position.coords.heading || null,
          battery_level: null // Could be added if available
        };

        await api.updateLocation(updateData);
        
        // Update local state
        setCurrentLocation([location.latitude, location.longitude]);
        setSpeed(updateData.speed_kmh);
        setHeading(updateData.heading);
        setLastUpdate(new Date());
        setError('');
      } catch (e) {
        console.error('Error sending location update:', e);
        setError('Failed to send location update');
      }
    };

    if (navigator.geolocation) {
      // Get initial location
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          sendLocationUpdate(pos);
          setCurrentLocation([pos.coords.latitude, pos.coords.longitude]);
        },
        (err) => {
          console.error('Geolocation error:', err);
          setError('Unable to get your location. Please enable location services.');
        },
        { enableHighAccuracy: true, timeout: 10000 }
      );

      // Watch position and send updates every 30 seconds
      watchIdRef.current = navigator.geolocation.watchPosition(
        (pos) => {
          sendLocationUpdate(pos);
        },
        (err) => {
          console.error('Geolocation watch error:', err);
        },
        {
          enableHighAccuracy: true,
          maximumAge: 5000,
          timeout: 10000
        }
      );
    } else {
      setError('Geolocation is not supported by your browser');
    }

    return () => {
      if (watchIdRef.current !== null) {
        navigator.geolocation.clearWatch(watchIdRef.current);
      }
    };
  }, [isRider, deliveryIdInput]);

  // Load initial tracking data (with debouncing)
  useEffect(() => {
    // Don't load if rider mode, no delivery ID, or delivery ID is too short
    if (isRider || !deliveryIdInput || deliveryIdInput.trim().length < 3) {
      return;
    }

    // Debounce: wait 500ms after user stops typing before loading
    const debounceTimer = setTimeout(async () => {
      // Double-check delivery ID is still valid
      if (!deliveryIdInput || deliveryIdInput.trim().length < 3) {
        return;
      }

      try {
        const response = await api.trackDelivery(deliveryIdInput.trim());
        if (response.success && response.data) {
          const data = response.data;
          if (data.current_location) {
            setCurrentLocation([data.current_location.latitude, data.current_location.longitude]);
          }
          setStatus(data.status);
          setSpeed(data.speed_kmh);
          setHeading(data.heading);
          setBatteryLevel(data.battery_level);
          if (data.timestamp) {
            setLastUpdate(new Date(data.timestamp));
          }
          
          // Load location history
          if (data.location_history && data.location_history.length > 0) {
            setLocationHistory(
              data.location_history.map(h => ({
                location: [h.location.latitude, h.location.longitude],
                timestamp: h.timestamp,
                speed: h.speed_kmh,
                heading: h.heading
              }))
            );
          }
        }
      } catch (e) {
        console.error('Error loading tracking data:', e);
        // Don't set error if backend is not running - WebSocket error will handle that
        if (e.message && !e.message.includes('Network error')) {
          setError('Failed to load tracking data: ' + e.message);
        }
      }
    }, 500); // Wait 500ms after user stops typing

    return () => {
      clearTimeout(debounceTimer);
    };
  }, [deliveryIdInput, isRider]);

  const centerPosition = currentLocation || [11.0168, 76.9558]; // Default to Coimbatore

  const getStatusColor = (status) => {
    switch (status) {
      case 'delivered': return 'bg-green-500';
      case 'in_transit': return 'bg-blue-500';
      case 'pending': return 'bg-yellow-500';
      case 'failed': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const formatTimeAgo = (date) => {
    if (!date) return 'Never';
    const seconds = Math.floor((new Date() - date) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ago`;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">
          {isRider ? 'Share Your Location' : 'Live Delivery Tracking'}
        </h2>
        <div className="flex items-center space-x-4">
          {!isRider && (
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></div>
              <span className="text-sm text-gray-600">
                {connected ? 'Live' : 'Disconnected'}
              </span>
            </div>
          )}
          {lastUpdate && (
            <div className="text-sm text-gray-600">
              Last update: {formatTimeAgo(lastUpdate)}
            </div>
          )}
        </div>
      </div>

      {/* Delivery ID Input */}
      <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-200">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Delivery ID
        </label>
        <input
          type="text"
          value={deliveryIdInput}
          onChange={(e) => setDeliveryIdInput(e.target.value)}
          placeholder="Enter delivery ID (min 3 characters)"
          className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
          disabled={isRider && !!deliveryIdInput}
        />
        {deliveryIdInput && deliveryIdInput.trim().length > 0 && deliveryIdInput.trim().length < 3 && (
          <p className="mt-2 text-xs text-gray-500">
            Please enter at least 3 characters
          </p>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-700">
          <div className="font-medium mb-1">Connection Error</div>
          <div>{error}</div>
          {error.includes('Cannot connect to server') && (
            <div className="mt-2 pt-2 border-t border-red-200">
              <p className="text-xs text-red-600">
                <strong>Tip:</strong> Make sure the backend server is running. 
                Start it with: <code className="bg-red-100 px-1 rounded">cd backend && python -m uvicorn api.main:app --reload</code>
              </p>
            </div>
          )}
        </div>
      )}

      {!error && !connected && deliveryIdInput && deliveryIdInput.trim().length >= 3 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3 text-sm text-yellow-700">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 rounded-full bg-yellow-500 animate-pulse"></div>
            <span>Connecting to tracking server...</span>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Status Panel */}
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-4">Delivery Status</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-xs text-gray-600 mb-1">Status</label>
                <div className="flex items-center space-x-2">
                  <div className={`w-3 h-3 rounded-full ${getStatusColor(status)}`}></div>
                  <span className="text-sm font-medium text-gray-900 capitalize">
                    {status.replace('_', ' ')}
                  </span>
                </div>
              </div>
              
              {speed !== null && (
                <div>
                  <label className="block text-xs text-gray-600 mb-1">Speed</label>
                  <span className="text-sm font-medium text-gray-900">
                    {speed.toFixed(1)} km/h
                  </span>
                </div>
              )}
              
              {heading !== null && (
                <div>
                  <label className="block text-xs text-gray-600 mb-1">Heading</label>
                  <span className="text-sm font-medium text-gray-900">
                    {Math.round(heading)}°
                  </span>
                </div>
              )}
              
              {batteryLevel !== null && (
                <div>
                  <label className="block text-xs text-gray-600 mb-1">Battery</label>
                  <div className="flex items-center space-x-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          batteryLevel > 50 ? 'bg-green-500' :
                          batteryLevel > 20 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${batteryLevel}%` }}
                      ></div>
                    </div>
                    <span className="text-xs text-gray-600">{batteryLevel}%</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {isRider && (
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <p className="text-sm text-blue-800">
                <strong>Rider Mode:</strong> Your location is being shared every 30 seconds.
                Make sure location services are enabled.
              </p>
            </div>
          )}
        </div>

        {/* Map */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm overflow-hidden border border-gray-200">
          <div style={{ height: '600px', width: '100%' }}>
            <MapContainer
              center={centerPosition}
              zoom={15}
              style={{ height: '100%', width: '100%' }}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />

              <MapUpdater center={currentLocation} zoom={15} />

              {/* Current location marker */}
              {currentLocation && (
                <Marker position={currentLocation} icon={riderIcon}>
                  <Popup>
                    <div>
                      <strong>Current Location</strong><br />
                      Status: {status.replace('_', ' ')}<br />
                      {speed !== null && `Speed: ${speed.toFixed(1)} km/h`}
                      {heading !== null && <><br />Heading: {Math.round(heading)}°</>}
                    </div>
                  </Popup>
                </Marker>
              )}

              {/* Location history path */}
              {locationHistory.length > 1 && (
                <Polyline
                  positions={locationHistory.map(h => h.location)}
                  pathOptions={{
                    color: '#3b82f6',
                    weight: 3,
                    opacity: 0.6
                  }}
                />
              )}
            </MapContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveTracking;