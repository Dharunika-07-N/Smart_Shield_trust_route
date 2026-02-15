import React, { useEffect, useState } from 'react';
import { useMap, Polyline, Popup } from 'react-leaflet';
import { getTrafficSegments, segmentsToPolylines, formatTrafficLevel } from '../services/trafficApi';

/**
 * TrafficLayer Component
 * Displays real-time traffic data on the map
 * Fetches data from OpenTraffic and OSM sources
 */
const TrafficLayer = ({ show = true, autoRefresh = true, refreshInterval = 60000 }) => {
    const map = useMap();
    const [trafficPolylines, setTrafficPolylines] = useState([]);
    const [loading, setLoading] = useState(false);
    const [lastUpdate, setLastUpdate] = useState(null);

    const fetchTrafficData = async () => {
        if (!show) return;

        setLoading(true);
        try {
            const bounds = map.getBounds();
            const boundsObj = {
                minLat: bounds.getSouth(),
                minLng: bounds.getWest(),
                maxLat: bounds.getNorth(),
                maxLng: bounds.getEast()
            };

            const segments = await getTrafficSegments(boundsObj);
            const polylines = segmentsToPolylines(segments);

            setTrafficPolylines(polylines);
            setLastUpdate(new Date());

            console.log(`[Traffic] Loaded ${segments.length} traffic segments`);
        } catch (error) {
            console.error('Error fetching traffic data:', error);
        } finally {
            setLoading(false);
        }
    };

    // Fetch traffic data when map moves or show toggles
    useEffect(() => {
        if (show) {
            fetchTrafficData();

            const onMoveEnd = () => {
                fetchTrafficData();
            };

            map.on('moveend', onMoveEnd);
            return () => {
                map.off('moveend', onMoveEnd);
            };
        } else {
            setTrafficPolylines([]);
        }
    }, [show, map]);

    // Auto-refresh traffic data
    useEffect(() => {
        if (show && autoRefresh && refreshInterval > 0) {
            const interval = setInterval(fetchTrafficData, refreshInterval);
            return () => clearInterval(interval);
        }
    }, [show, autoRefresh, refreshInterval]);

    if (!show || trafficPolylines.length === 0) return null;

    return (
        <>
            {trafficPolylines.map((polyline, idx) => {
                const trafficInfo = formatTrafficLevel(polyline.data.trafficLevel);

                return (
                    <Polyline
                        key={`traffic-${idx}`}
                        positions={polyline.positions}
                        pathOptions={{
                            color: polyline.color,
                            weight: polyline.weight,
                            opacity: polyline.opacity,
                            lineCap: 'round',
                            lineJoin: 'round'
                        }}
                    >
                        <Popup>
                            <div style={{ minWidth: '200px' }}>
                                <div style={{
                                    fontWeight: 'bold',
                                    fontSize: '14px',
                                    marginBottom: '8px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '8px'
                                }}>
                                    <span style={{ fontSize: '20px' }}>{trafficInfo.icon}</span>
                                    <span>{trafficInfo.description}</span>
                                </div>

                                <div style={{
                                    fontSize: '12px',
                                    color: '#64748b',
                                    marginBottom: '8px'
                                }}>
                                    {polyline.data.speed ? (
                                        <>
                                            <div>🚗 Current: <strong>{Math.round(polyline.data.speed)} km/h</strong></div>
                                            <div>🏁 Normal: {Math.round(polyline.data.freeFlowSpeed)} km/h</div>
                                            <div style={{
                                                marginTop: '4px',
                                                padding: '4px 8px',
                                                background: polyline.color + '20',
                                                borderRadius: '4px',
                                                color: polyline.color,
                                                fontWeight: 'bold'
                                            }}>
                                                {Math.round((polyline.data.speed / polyline.data.freeFlowSpeed) * 100)}% of normal speed
                                            </div>
                                        </>
                                    ) : (
                                        <div>⚠️ Speed data unavailable</div>
                                    )}
                                </div>

                                <div style={{
                                    fontSize: '10px',
                                    color: '#94a3b8',
                                    borderTop: '1px solid #e2e8f0',
                                    paddingTop: '8px',
                                    marginTop: '8px'
                                }}>
                                    <div>📡 Source: {polyline.data.source}</div>
                                    <div>🕐 Updated: {new Date(polyline.data.timestamp).toLocaleTimeString()}</div>
                                </div>
                            </div>
                        </Popup>
                    </Polyline>
                );
            })}

            {/* Loading indicator */}
            {loading && (
                <div style={{
                    position: 'absolute',
                    top: '10px',
                    right: '10px',
                    background: 'white',
                    padding: '8px 12px',
                    borderRadius: '8px',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                    fontSize: '12px',
                    fontWeight: 'bold',
                    color: '#4f46e5',
                    zIndex: 1000
                }}>
                    🔄 Loading traffic data...
                </div>
            )}
        </>
    );
};

export default TrafficLayer;
