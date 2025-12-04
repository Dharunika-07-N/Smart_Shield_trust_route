import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';

const RouteMap = () => {
  const [selectedRoute, setSelectedRoute] = useState(null);

  // Get traffic color
  const getTrafficColor = (traffic) => {
    switch (traffic) {
      case 'low': return '#22c55e';
      case 'medium': return '#eab308';
      case 'high': return '#ef4444';
      default: return '#6b7280';
    }
  };

  // Mock route data with traffic
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

  const getSafetyColor = (score) => {
    if (score >= 85) return 'green';
    if (score >= 70) return 'orange';
    return 'red';
  };

  const centerPosition = [40.7128, -74.0060];

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
        {/* Routes List */}
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-4">Active Routes</h3>
            <div className="space-y-3">
              {routes.map((route) => (
                <div
                  key={route.id}
                  onClick={() => setSelectedRoute(route)}
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    selectedRoute?.id === route.id
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900">{route.name}</h4>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        route.status === 'active'
                          ? 'bg-success-100 text-success-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {route.status}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm text-gray-600">
                    <span>{route.stops} stops • {route.distance}</span>
                    <span className={`font-medium text-${getSafetyColor(route.safety)}-600`}>
                      Safety: {route.safety}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Route Details */}
          {selectedRoute && (
            <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-4">Route Details</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Safety Score</span>
                  <span className="font-medium text-gray-900">{selectedRoute.safety}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Distance</span>
                  <span className="font-medium text-gray-900">{selectedRoute.distance}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Estimated Time</span>
                  <span className="font-medium text-gray-900">{selectedRoute.time}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Stops</span>
                  <span className="font-medium text-gray-900">{selectedRoute.stops}</span>
                </div>
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
              
              {selectedRoute ? (
                <>
                  {/* Display selected route with traffic-colored segments */}
                  {selectedRoute.coordinates.map((coord, index) => (
                    <Marker key={index} position={[coord.lat || coord[0], coord.lng || coord[1]]}>
                      <Popup>
                        Stop {index + 1}
                        {coord.traffic && (
                          <div className="mt-2">
                            <div className="text-xs">Traffic: <span style={{ color: getTrafficColor(coord.traffic) }}>{coord.traffic}</span></div>
                            {coord.safety && <div className="text-xs">Safety: {coord.safety}%</div>}
                          </div>
                        )}
                      </Popup>
                    </Marker>
                  ))}
                  {/* Create segments with traffic colors */}
                  {selectedRoute.coordinates.map((coord, index) => {
                    if (index === selectedRoute.coordinates.length - 1) return null;
                    const start = selectedRoute.coordinates[index];
                    const end = selectedRoute.coordinates[index + 1];
                    const traffic = end.traffic || 'low';
                    return (
                      <Polyline
                        key={index}
                        positions={[
                          [start.lat || start[0], start.lng || start[1]],
                          [end.lat || end[0], end.lng || end[1]]
                        ]}
                        pathOptions={{
                          color: getTrafficColor(traffic),
                          weight: traffic === 'high' ? 8 : traffic === 'medium' ? 6 : 4,
                          opacity: 0.8,
                          dashArray: traffic === 'high' ? '10, 10' : null,
                        }}
                      />
                    );
                  })}
                </>
              ) : (
                <>
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
                </>
              )}
            </MapContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RouteMap;

