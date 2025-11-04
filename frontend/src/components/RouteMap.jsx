import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';

const RouteMap = () => {
  const [selectedRoute, setSelectedRoute] = useState(null);

  // Mock route data
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
        [40.7128, -74.0060],
        [40.7210, -74.0120],
        [40.7285, -74.0050],
        [40.7320, -73.9950],
        [40.7250, -73.9850],
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
        [40.7500, -73.9900],
        [40.7550, -73.9850],
        [40.7600, -73.9800],
        [40.7650, -73.9750],
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
        [40.7100, -73.9950],
        [40.7150, -73.9900],
        [40.7200, -73.9850],
        [40.7250, -73.9800],
        [40.7300, -73.9750],
        [40.7350, -73.9700],
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
                  {/* Display selected route */}
                  {selectedRoute.coordinates.map((coord, index) => (
                    <Marker key={index} position={coord}>
                      <Popup>Stop {index + 1}</Popup>
                    </Marker>
                  ))}
                  <Polyline
                    positions={selectedRoute.coordinates}
                    pathOptions={{ color: 'blue', weight: 4 }}
                  />
                </>
              ) : (
                <>
                  {/* Display all routes */}
                  {routes.map((route) => (
                    <React.Fragment key={route.id}>
                      <Polyline
                        positions={route.coordinates}
                        pathOptions={{
                          color: getSafetyColor(route.safety),
                          weight: 2,
                        }}
                      />
                      <Marker position={route.coordinates[0]}>
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

