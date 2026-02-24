/**
 * useRealTimeTracking — Custom React Hook
 * ==========================================
 * Real-time GPS tracking via WebSocket (primary) with SSE fallback.
 *
 * Architecture:
 *  1. Connects to WS /api/v1/tracking/live/{deliveryId}
 *  2. Server immediately pushes latest cached location (no waiting for next ping)
 *  3. All subsequent rider GPS updates are pushed via the WebSocket
 *  4. Marker position is updated → React re-renders ONLY the marker (not the map)
 *  5. If WS fails, falls back to SSE (/api/v1/tracking/stream/{deliveryId})
 *
 * Interview keywords:
 *   WebSockets, SSE, push-based, real-time event streaming,
 *   geo-location updates, Redis caching, scalable architecture
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { API_ROOT_URL } from '../utils/constants';

const WS_BASE = API_ROOT_URL
    ? API_ROOT_URL.replace(/^http/, 'ws')
    : `ws://${window.location.hostname}:8000`;

const API_BASE = API_ROOT_URL || `http://${window.location.hostname}:8000`;

export function useRealTimeTracking(deliveryId, { enabled = true } = {}) {
    const [currentLocation, setCurrentLocation] = useState(null);
    const [locationHistory, setLocationHistory] = useState([]);
    const [status, setStatus] = useState('pending');
    const [speed, setSpeed] = useState(null);
    const [heading, setHeading] = useState(null);
    const [batteryLevel, setBatteryLevel] = useState(null);
    const [lastUpdate, setLastUpdate] = useState(null);
    const [connected, setConnected] = useState(false);
    const [connectionMode, setConnectionMode] = useState(null); // 'ws' | 'sse' | null
    const [error, setError] = useState(null);
    const [reoptimizationNeeded, setReoptimizationNeeded] = useState(false);

    const wsRef = useRef(null);
    const esRef = useRef(null);         // EventSource for SSE
    const reconnectTimer = useRef(null);
    const reconnectAttempts = useRef(0);
    const MAX_RECONNECT = 5;

    /** Process a location update event (shared between WS and SSE) */
    const handleLocationEvent = useCallback((data) => {
        if (!data) return;

        const eventType = data.type || '';

        if (eventType === 'location_update' || eventType === 'initial_location') {
            const { latitude, longitude } = data.location || {};
            if (latitude == null || longitude == null) return;

            const coords = [latitude, longitude];
            setCurrentLocation(coords);
            setStatus(data.status || 'in_transit');
            setSpeed(data.speed_kmh ?? null);
            setHeading(data.heading ?? null);
            setBatteryLevel(data.battery_level ?? null);
            setLastUpdate(new Date(data.timestamp || Date.now()));
            setReoptimizationNeeded(data.reoptimization_needed || false);

            // Append to history (max 150 points for smooth polyline)
            setLocationHistory(prev => {
                const next = [...prev, { location: coords, timestamp: data.timestamp, speed: data.speed_kmh }];
                return next.slice(-150);
            });
        } else if (eventType === 'pong' || eventType === 'keepalive') {
            // Ignore keepalive messages
        } else if (eventType === 'status_change') {
            setStatus(data.status || status);
        }
    }, [status]);

    /** Connect via WebSocket */
    const connectWebSocket = useCallback(() => {
        if (!deliveryId || !enabled) return;

        // Close any existing connection
        if (wsRef.current) {
            wsRef.current.close(1000, 'reconnecting');
            wsRef.current = null;
        }

        const url = `${WS_BASE}/api/v1/tracking/live/${deliveryId}`;
        console.log('[WS] Connecting to', url);

        try {
            const ws = new WebSocket(url);
            wsRef.current = ws;

            ws.onopen = () => {
                console.log('[WS] ✅ Connected');
                setConnected(true);
                setConnectionMode('ws');
                setError(null);
                reconnectAttempts.current = 0;

                // Send ping every 25s to keep connection alive
                const pingInterval = setInterval(() => {
                    if (ws.readyState === WebSocket.OPEN) {
                        ws.send('ping');
                    } else {
                        clearInterval(pingInterval);
                    }
                }, 25000);

                ws._pingInterval = pingInterval;
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    handleLocationEvent(data);
                } catch (e) {
                    console.error('[WS] Parse error:', e);
                }
            };

            ws.onerror = () => {
                console.warn('[WS] Connection error — will try SSE fallback');
                setConnected(false);
            };

            ws.onclose = (event) => {
                console.log('[WS] Closed:', event.code, event.reason);
                setConnected(false);
                clearInterval(ws._pingInterval);

                if (event.code === 1000) return; // Clean close, don't reconnect

                // Progressive backoff reconnection
                if (reconnectAttempts.current < MAX_RECONNECT) {
                    const delay = Math.min(1000 * 2 ** reconnectAttempts.current, 15000);
                    reconnectAttempts.current++;
                    console.log(`[WS] Reconnecting in ${delay}ms (attempt ${reconnectAttempts.current})`);
                    reconnectTimer.current = setTimeout(connectWebSocket, delay);
                } else {
                    console.warn('[WS] Max reconnect attempts. Falling back to SSE.');
                    connectSSE();
                }
            };
        } catch (e) {
            console.error('[WS] Failed to create WebSocket:', e);
            connectSSE(); // Fall back to SSE
        }
    }, [deliveryId, enabled, handleLocationEvent]);

    /** Connect via SSE (fallback when WebSocket fails) */
    const connectSSE = useCallback(() => {
        if (!deliveryId || !enabled) return;

        if (esRef.current) {
            esRef.current.close();
            esRef.current = null;
        }

        const url = `${API_BASE}/api/v1/tracking/stream/${deliveryId}`;
        console.log('[SSE] Connecting to', url);

        try {
            const es = new EventSource(url);
            esRef.current = es;

            es.onopen = () => {
                console.log('[SSE] ✅ Connected');
                setConnected(true);
                setConnectionMode('sse');
                setError(null);
            };

            es.addEventListener('location_update', (event) => {
                try {
                    const data = JSON.parse(event.data);
                    handleLocationEvent({ ...data, type: 'location_update' });
                } catch (e) {
                    console.error('[SSE] Parse error:', e);
                }
            });

            es.addEventListener('initial_location', (event) => {
                try {
                    const data = JSON.parse(event.data);
                    handleLocationEvent({ ...data, type: 'initial_location' });
                } catch (e) {
                    console.error('[SSE] Parse error:', e);
                }
            });

            es.onerror = () => {
                console.warn('[SSE] Connection error');
                setConnected(false);
                setError('Real-time stream interrupted. Attempting to reconnect...');
                // SSE auto-reconnects natively in browsers
            };
        } catch (e) {
            console.error('[SSE] Failed to create EventSource:', e);
            setError('Cannot connect to tracking server. Check that the backend is running.');
        }
    }, [deliveryId, enabled, handleLocationEvent]);

    /** Main effect: connect when deliveryId changes */
    useEffect(() => {
        if (!deliveryId || deliveryId.trim().length < 3 || !enabled) {
            return;
        }

        // Debounce: wait 400ms after user stops typing
        const debounce = setTimeout(() => {
            reconnectAttempts.current = 0;
            connectWebSocket();
        }, 400);

        return () => {
            clearTimeout(debounce);
            clearTimeout(reconnectTimer.current);

            // Cleanup WebSocket
            if (wsRef.current) {
                clearInterval(wsRef.current._pingInterval);
                wsRef.current.close(1000, 'component unmount');
                wsRef.current = null;
            }

            // Cleanup SSE
            if (esRef.current) {
                esRef.current.close();
                esRef.current = null;
            }

            setConnected(false);
            setConnectionMode(null);
        };
    }, [deliveryId, enabled, connectWebSocket]);

    return {
        currentLocation,
        locationHistory,
        status,
        speed,
        heading,
        batteryLevel,
        lastUpdate,
        connected,
        connectionMode,
        error,
        reoptimizationNeeded,
        /** Force-reconnect manually */
        reconnect: connectWebSocket
    };
}

/**
 * useRiderGPS — Hook for the delivery partner (rider/driver) side.
 *
 * Continuously reads the device's GPS and POSTs updates to the backend.
 * The backend then broadcasts these to all watchers of the order.
 *
 * Update frequency: every 5 seconds (configurable)
 * Battery optimization: uses watchPosition with maximumAge to avoid duplicate reads
 */
export function useRiderGPS(deliveryId, routeId, { enabled = true, intervalMs = 5000 } = {}) {
    const [currentLocation, setCurrentLocation] = useState(null);
    const [gpsError, setGpsError] = useState(null);
    const [isSending, setIsSending] = useState(false);
    const [lastSent, setLastSent] = useState(null);
    const [sendCount, setSendCount] = useState(0);

    const watchIdRef = useRef(null);
    const sendTimerRef = useRef(null);
    const latestCoordsRef = useRef(null); // Always hold latest GPS without re-triggering effect

    const sendUpdate = useCallback(async (coords) => {
        if (!deliveryId || !coords) return;

        setIsSending(true);
        try {
            const token = localStorage.getItem('auth_token');
            const response = await fetch(`${API_BASE}/api/v1/tracking/location`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { Authorization: `Bearer ${token}` } : {})
                },
                body: JSON.stringify({
                    delivery_id: deliveryId,
                    route_id: routeId || null,
                    latitude: coords.latitude,
                    longitude: coords.longitude,
                    status: 'in_transit',
                    speed_kmh: coords.speed ? coords.speed * 3.6 : null, // m/s → km/h
                    heading: coords.heading || null,
                    battery_level: null // Battery API not widely available
                })
            });

            if (response.ok) {
                setLastSent(new Date());
                setSendCount(c => c + 1);
                setGpsError(null);
            }
        } catch (e) {
            console.error('[GPS] Failed to send location update:', e);
            setGpsError('Failed to send location — retrying...');
        } finally {
            setIsSending(false);
        }
    }, [deliveryId, routeId]);

    useEffect(() => {
        if (!enabled || !deliveryId) return;

        if (!navigator.geolocation) {
            setGpsError('Geolocation not supported by this browser.');
            return;
        }

        // Watch GPS position continuously
        watchIdRef.current = navigator.geolocation.watchPosition(
            (position) => {
                const coords = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    speed: position.coords.speed,
                    heading: position.coords.heading,
                    accuracy: position.coords.accuracy
                };
                latestCoordsRef.current = coords;
                setCurrentLocation(coords);
                setGpsError(null);
            },
            (error) => {
                const messages = {
                    1: 'Location permission denied. Please enable GPS.',
                    2: 'GPS position unavailable.',
                    3: 'GPS timeout. Retrying...'
                };
                setGpsError(messages[error.code] || 'GPS error');
                console.error('[GPS] Error:', error);
            },
            { enableHighAccuracy: true, maximumAge: 2000, timeout: 10000 }
        );

        // Send update on interval (not on every GPS tick to save battery/bandwidth)
        sendTimerRef.current = setInterval(() => {
            if (latestCoordsRef.current) {
                sendUpdate(latestCoordsRef.current);
            }
        }, intervalMs);

        // Also send immediately on first GPS fix
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const coords = {
                    latitude: pos.coords.latitude,
                    longitude: pos.coords.longitude,
                    speed: pos.coords.speed,
                    heading: pos.coords.heading
                };
                latestCoordsRef.current = coords;
                setCurrentLocation(coords);
                sendUpdate(coords);
            },
            () => { },
            { enableHighAccuracy: true, timeout: 10000 }
        );

        return () => {
            if (watchIdRef.current !== null) {
                navigator.geolocation.clearWatch(watchIdRef.current);
            }
            clearInterval(sendTimerRef.current);
        };
    }, [enabled, deliveryId, sendUpdate, intervalMs]);

    return {
        currentLocation,
        gpsError,
        isSending,
        lastSent,
        sendCount
    };
}
