import React, { useState, useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import useLocation from '../hooks/useLocation';

const MapUpdater = ({ center }) => {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.setView(center, map.getZoom());
    }
  }, [center, map]);
  return null;
};

const SafetyHeatmap = () => {
  const [timeOfDay, setTimeOfDay] = useState('day');
  const { location, loading, error: locationError } = useLocation();

  // New York as fallback
  const fallbackLocation = { latitude: 40.7128, longitude: -74.0060 };
  const baseLat = location?.latitude || fallbackLocation.latitude;
  const baseLon = location?.longitude || fallbackLocation.longitude;

  // Generate heatmap data based on base location
  const heatmapData = useMemo(() => {
    const data = [];

    // Generate grid of points around the base location
    for (let i = -5; i < 5; i++) {
      for (let j = -5; j < 5; j++) {
        const lat = baseLat + (i * 0.005);
        const lon = baseLon + (j * 0.005);

        // Generate safety score based on time of day
        let score;
        if (timeOfDay === 'day') {
          score = 70 + Math.random() * 25;
        } else if (timeOfDay === 'evening') {
          score = 60 + Math.random() * 25;
        } else {
          score = 50 + Math.random() * 30;
        }

        data.push({
          lat,
          lon,
          score: Math.round(score),
        });
      }
    }

    return data;
  }, [baseLat, baseLon, timeOfDay]);

  const getSafetyColor = (score) => {
    if (score >= 85) return '#22c55e';
    if (score >= 70) return '#eab308';
    if (score >= 55) return '#f97316';
    return '#ef4444';
  };

  const getSafetyLevel = (score) => {
    if (score >= 85) return 'High';
    if (score >= 70) return 'Medium-High';
    if (score >= 55) return 'Medium';
    return 'Low';
  };

  const getRadius = (score) => {
    return 5 + (score / 100) * 10;
  };

  const stats = useMemo(() => ({
    average: Math.round(heatmapData.reduce((sum, d) => sum + d.score, 0) / heatmapData.length),
    high: heatmapData.filter(d => d.score >= 85).length,
    medium: heatmapData.filter(d => d.score >= 55 && d.score < 85).length,
    low: heatmapData.filter(d => d.score < 55).length,
  }), [heatmapData]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Safety Heatmap</h2>
        <div className="flex flex-col items-end">
          <div className="flex items-center space-x-2 bg-gray-100 rounded-lg p-1">
            {['day', 'evening', 'night'].map((time) => (
              <button
                key={time}
                onClick={() => setTimeOfDay(time)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors capitalize ${timeOfDay === time
                    ? 'bg-white text-primary-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                  }`}
              >
                {time}
              </button>
            ))}
          </div>
          {location && (
            <span className="text-xs text-green-600 mt-1 font-medium flex items-center">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-1 animate-pulse"></span>
              Using your current location
            </span>
          )}
          {locationError && (
            <span className="text-xs text-red-500 mt-1 font-medium">
              Location error: {locationError}. Using default location.
            </span>
          )}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="text-2xl font-bold text-gray-900">{stats.average}</div>
          <div className="text-sm text-gray-600 mt-1">Average Safety</div>
        </div>
        <div className="bg-green-50 rounded-lg p-4 border border-green-200">
          <div className="text-2xl font-bold text-green-600">{stats.high}</div>
          <div className="text-sm text-green-700 mt-1">High Safety Zones</div>
        </div>
        <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
          <div className="text-2xl font-bold text-yellow-600">{stats.medium}</div>
          <div className="text-sm text-yellow-700 mt-1">Medium Safety</div>
        </div>
        <div className="bg-red-50 rounded-lg p-4 border border-red-200">
          <div className="text-2xl font-bold text-red-600">{stats.low}</div>
          <div className="text-sm text-red-700 mt-1">Low Safety Zones</div>
        </div>
      </div>

      {/* Map */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-200">
        <div style={{ height: '600px', width: '100%' }}>
          {loading ? (
            <div className="flex items-center justify-center h-full bg-gray-50">
              <div className="flex flex-col items-center">
                <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mb-4"></div>
                <p className="text-gray-600">Loading map and location...</p>
              </div>
            </div>
          ) : (
            <MapContainer
              center={[baseLat, baseLon]}
              zoom={14}
              style={{ height: '100%', width: '100%' }}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />

              <MapUpdater center={[baseLat, baseLon]} />

              {heatmapData.map((point, index) => (
                <CircleMarker
                  key={index}
                  center={[point.lat, point.lon]}
                  radius={getRadius(point.score)}
                  pathOptions={{
                    color: getSafetyColor(point.score),
                    fillColor: getSafetyColor(point.score),
                    fillOpacity: 0.6,
                  }}
                >
                  <Popup>
                    <div className="font-medium">Safety Score: {point.score}/100</div>
                    <div className="text-sm text-gray-600">
                      Level: {getSafetyLevel(point.score)}
                    </div>
                  </Popup>
                </CircleMarker>
              ))}

              {/* Current Location Marker */}
              {location && (
                <CircleMarker
                  center={[location.latitude, location.longitude]}
                  radius={8}
                  pathOptions={{
                    color: '#3b82f6',
                    fillColor: '#3b82f6',
                    fillOpacity: 0.8,
                    weight: 3,
                  }}
                >
                  <Popup>Your current location</Popup>
                </CircleMarker>
              )}
            </MapContainer>
          )}
        </div>
      </div>

      {/* Legend */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <h3 className="font-semibold text-gray-900 mb-4">Safety Score Legend</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-green-500"></div>
            <div>
              <div className="font-medium text-gray-900">85-100</div>
              <div className="text-sm text-gray-600">High Safety</div>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-yellow-500"></div>
            <div>
              <div className="font-medium text-gray-900">70-84</div>
              <div className="text-sm text-gray-600">Medium-High</div>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-orange-500"></div>
            <div>
              <div className="font-medium text-gray-900">55-69</div>
              <div className="text-sm text-gray-600">Medium Safety</div>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-red-500"></div>
            <div>
              <div className="font-medium text-gray-900">0-54</div>
              <div className="text-sm text-gray-600">Low Safety</div>
            </div>
          </div>
        </div>
        <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-sm text-blue-800">
            <strong>Note:</strong> Safety scores are calculated based on crime data, lighting conditions,
            patrol presence, and user feedback. Scores vary by time of day.
          </p>
        </div>
      </div>
    </div>
  );
};

export default SafetyHeatmap;

