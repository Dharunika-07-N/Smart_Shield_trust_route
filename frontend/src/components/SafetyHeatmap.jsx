import React, { useEffect, useState } from 'react';
import { useMap, Circle, Marker, Popup } from 'react-leaflet';
import { api } from '../services/api';
import L from 'leaflet';

const SafetyHeatmap = ({ show = true }) => {
    const map = useMap();
    const [heatmapData, setHeatmapData] = useState([]);
    const [loading, setLoading] = useState(false);

    const fetchHeatmapData = async () => {
        if (!show) return;

        setLoading(true);
        try {
            const bounds = map.getBounds();
            const params = {
                min_lat: bounds.getSouth(),
                min_lng: bounds.getWest(),
                max_lat: bounds.getNorth(),
                max_lng: bounds.getEast(),
                grid_size: 15
            };

            const response = await api.get('/safety/heatmap', { params });
            if (response && response.points) {
                setHeatmapData(response.points || []);
            }
        } catch (error) {
            console.error("Error fetching heatmap:", error);
        } finally {
            setLoading(false);
        }
    };

    // Re-fetch when map moves or show toggles
    useEffect(() => {
        fetchHeatmapData();

        const onMoveEnd = () => {
            fetchHeatmapData();
        };

        map.on('moveend', onMoveEnd);
        return () => {
            map.off('moveend', onMoveEnd);
        };
    }, [show]);

    if (!show || heatmapData.length === 0) return null;

    const getColor = (intensity) => {
        // intensity is 0 to 1 (safety score / 100)
        // Low safety (intensity near 0) -> Red
        // High safety (intensity near 1) -> Green
        if (intensity < 0.4) return '#ef4444'; // Red-500
        if (intensity < 0.7) return '#f59e0b'; // Amber-500
        return '#22c55e'; // Green-500
    };

    return (
        <>
            {heatmapData
                .filter(point => point && typeof point.lat === 'number' && typeof point.lng === 'number' && !isNaN(point.lat) && !isNaN(point.lng))
                .map((point, idx) => (
                    <Circle
                        key={idx}
                        center={[point.lat, point.lng]}
                        radius={500} // meters
                        pathOptions={{
                            fillColor: getColor(point.intensity || 0.5),
                            fillOpacity: 0.15,
                            stroke: false
                        }}
                    />
                ))}
        </>
    );
};

export default SafetyHeatmap;
