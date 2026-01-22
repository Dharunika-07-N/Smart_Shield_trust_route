import React, { useState, useEffect } from 'react';
import { TileLayer, Circle, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { FiCloud, FiCloudRain, FiCloudSnow, FiSun, FiWind, FiAlertTriangle } from 'react-icons/fi';

const TrafficWeatherOverlay = ({
    map,
    showTraffic,
    showWeather,
    center,
    onWeatherData
}) => {
    const [weatherData, setWeatherData] = useState(null);
    const [trafficIncidents, setTrafficIncidents] = useState([]);
    const [loading, setLoading] = useState(false);

    // Fetch weather data
    useEffect(() => {
        if (!showWeather || !center) return;

        const fetchWeather = async () => {
            setLoading(true);
            try {
                const API_KEY = process.env.REACT_APP_OPENWEATHER_API_KEY || 'demo';
                const response = await fetch(
                    `https://api.openweathermap.org/data/2.5/weather?lat=${center[0]}&lon=${center[1]}&appid=${API_KEY}&units=metric`
                );

                if (response.ok) {
                    const data = await response.json();
                    setWeatherData(data);
                    if (onWeatherData) {
                        onWeatherData(data);
                    }
                }
            } catch (error) {
                console.warn('Weather fetch failed:', error);
                // Use mock data for demo
                setWeatherData({
                    weather: [{ main: 'Clear', description: 'clear sky', icon: '01d' }],
                    main: { temp: 28, feels_like: 30, humidity: 65 },
                    wind: { speed: 3.5 },
                    visibility: 10000,
                    name: 'Current Location'
                });
            } finally {
                setLoading(false);
            }
        };

        fetchWeather();
        const interval = setInterval(fetchWeather, 600000); // Update every 10 minutes
        return () => clearInterval(interval);
    }, [center, showWeather, onWeatherData]);

    // Fetch traffic incidents (mock data for demo)
    useEffect(() => {
        if (!showTraffic || !center) return;

        // In production, integrate with Google Maps Traffic API or Waze API
        const mockIncidents = [
            {
                id: 1,
                type: 'accident',
                severity: 'high',
                location: [center[0] + 0.01, center[1] + 0.01],
                description: 'Vehicle accident reported',
                delay: '15 min delay'
            },
            {
                id: 2,
                type: 'construction',
                severity: 'medium',
                location: [center[0] - 0.015, center[1] + 0.02],
                description: 'Road construction ahead',
                delay: '5 min delay'
            },
            {
                id: 3,
                type: 'congestion',
                severity: 'low',
                location: [center[0] + 0.02, center[1] - 0.01],
                description: 'Heavy traffic',
                delay: '8 min delay'
            }
        ];

        setTrafficIncidents(mockIncidents);
    }, [center, showTraffic]);

    const getWeatherIcon = (iconCode) => {
        const iconMap = {
            '01d': <FiSun className="w-6 h-6 text-yellow-500" />,
            '01n': <FiSun className="w-6 h-6 text-gray-400" />,
            '02d': <FiCloud className="w-6 h-6 text-gray-500" />,
            '02n': <FiCloud className="w-6 h-6 text-gray-600" />,
            '03d': <FiCloud className="w-6 h-6 text-gray-500" />,
            '03n': <FiCloud className="w-6 h-6 text-gray-600" />,
            '04d': <FiCloud className="w-6 h-6 text-gray-600" />,
            '04n': <FiCloud className="w-6 h-6 text-gray-700" />,
            '09d': <FiCloudRain className="w-6 h-6 text-blue-500" />,
            '09n': <FiCloudRain className="w-6 h-6 text-blue-600" />,
            '10d': <FiCloudRain className="w-6 h-6 text-blue-500" />,
            '10n': <FiCloudRain className="w-6 h-6 text-blue-600" />,
            '11d': <FiAlertTriangle className="w-6 h-6 text-yellow-600" />,
            '11n': <FiAlertTriangle className="w-6 h-6 text-yellow-700" />,
            '13d': <FiCloudSnow className="w-6 h-6 text-blue-300" />,
            '13n': <FiCloudSnow className="w-6 h-6 text-blue-400" />,
        };
        return iconMap[iconCode] || <FiCloud className="w-6 h-6 text-gray-500" />;
    };

    const getTrafficIcon = (type, severity) => {
        const colors = {
            high: '#ef4444',
            medium: '#f59e0b',
            low: '#eab308'
        };

        const icons = {
            accident: '🚗💥',
            construction: '🚧',
            congestion: '🚦',
            closure: '🚫'
        };

        return L.divIcon({
            className: 'traffic-incident-marker',
            html: `
        <div style="
          background: ${colors[severity]};
          color: white;
          padding: 8px;
          border-radius: 50%;
          border: 3px solid white;
          box-shadow: 0 2px 8px rgba(0,0,0,0.3);
          font-size: 20px;
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-center;
        ">
          ${icons[type] || '⚠️'}
        </div>
      `,
            iconSize: [40, 40],
            iconAnchor: [20, 20]
        });
    };

    return (
        <>
            {/* Google Maps Traffic Layer */}
            {showTraffic && (
                <TileLayer
                    url="https://mt1.google.com/vt/lyrs=h@159000000,traffic&x={x}&y={y}&z={z}"
                    attribution='&copy; Google Maps Traffic'
                    opacity={0.7}
                    zIndex={1000}
                />
            )}

            {/* Traffic Incidents */}
            {showTraffic && trafficIncidents.map((incident) => (
                <Marker
                    key={incident.id}
                    position={incident.location}
                    icon={getTrafficIcon(incident.type, incident.severity)}
                >
                    <Popup>
                        <div className="p-2">
                            <div className="font-semibold text-gray-900 mb-1">
                                {incident.description}
                            </div>
                            <div className="text-sm text-gray-600">
                                {incident.delay}
                            </div>
                            <div className={`text-xs mt-1 font-medium ${incident.severity === 'high' ? 'text-red-600' :
                                    incident.severity === 'medium' ? 'text-orange-600' :
                                        'text-yellow-600'
                                }`}>
                                {incident.severity.toUpperCase()} SEVERITY
                            </div>
                        </div>
                    </Popup>
                </Marker>
            ))}

            {/* Weather Overlay */}
            {showWeather && weatherData && (
                <>
                    {/* Weather condition visualization */}
                    {weatherData.weather[0].main === 'Rain' && (
                        <Circle
                            center={center}
                            radius={5000}
                            pathOptions={{
                                color: '#3b82f6',
                                fillColor: '#3b82f6',
                                fillOpacity: 0.2,
                                weight: 2
                            }}
                        />
                    )}
                    {weatherData.weather[0].main === 'Clouds' && (
                        <Circle
                            center={center}
                            radius={3000}
                            pathOptions={{
                                color: '#6b7280',
                                fillColor: '#6b7280',
                                fillOpacity: 0.1,
                                weight: 1
                            }}
                        />
                    )}
                </>
            )}

            {/* Weather Info Panel (Fixed Position) */}
            {showWeather && weatherData && (
                <div
                    className="leaflet-top leaflet-right"
                    style={{
                        position: 'absolute',
                        top: '10px',
                        right: '10px',
                        zIndex: 1000,
                        pointerEvents: 'none'
                    }}
                >
                    <div
                        className="bg-white rounded-lg shadow-lg p-4 border border-gray-200"
                        style={{ pointerEvents: 'auto' }}
                    >
                        <div className="flex items-center gap-3">
                            {getWeatherIcon(weatherData.weather[0].icon)}
                            <div>
                                <div className="font-semibold text-gray-900">
                                    {Math.round(weatherData.main.temp)}°C
                                </div>
                                <div className="text-xs text-gray-600">
                                    {weatherData.weather[0].description}
                                </div>
                            </div>
                        </div>
                        <div className="mt-3 pt-3 border-t border-gray-200 space-y-1">
                            <div className="flex items-center gap-2 text-xs text-gray-600">
                                <FiWind className="w-3 h-3" />
                                <span>Wind: {weatherData.wind.speed} m/s</span>
                            </div>
                            <div className="text-xs text-gray-600">
                                Humidity: {weatherData.main.humidity}%
                            </div>
                            <div className="text-xs text-gray-600">
                                Visibility: {(weatherData.visibility / 1000).toFixed(1)} km
                            </div>
                        </div>
                        {(weatherData.weather[0].main === 'Rain' ||
                            weatherData.weather[0].main === 'Thunderstorm') && (
                                <div className="mt-2 pt-2 border-t border-yellow-200 bg-yellow-50 -mx-4 -mb-4 px-4 py-2 rounded-b-lg">
                                    <div className="flex items-center gap-2 text-xs text-yellow-800">
                                        <FiAlertTriangle className="w-3 h-3" />
                                        <span className="font-medium">Drive carefully in wet conditions</span>
                                    </div>
                                </div>
                            )}
                    </div>
                </div>
            )}

            {/* Traffic Legend */}
            {showTraffic && (
                <div
                    className="leaflet-bottom leaflet-left"
                    style={{
                        position: 'absolute',
                        bottom: '10px',
                        left: '10px',
                        zIndex: 1000,
                        pointerEvents: 'none'
                    }}
                >
                    <div
                        className="bg-white rounded-lg shadow-lg p-3 border border-gray-200"
                        style={{ pointerEvents: 'auto' }}
                    >
                        <div className="text-xs font-semibold text-gray-700 mb-2">Traffic Legend</div>
                        <div className="space-y-1">
                            <div className="flex items-center gap-2 text-xs">
                                <div className="w-3 h-3 bg-green-500 rounded"></div>
                                <span className="text-gray-600">Light Traffic</span>
                            </div>
                            <div className="flex items-center gap-2 text-xs">
                                <div className="w-3 h-3 bg-yellow-500 rounded"></div>
                                <span className="text-gray-600">Moderate Traffic</span>
                            </div>
                            <div className="flex items-center gap-2 text-xs">
                                <div className="w-3 h-3 bg-orange-500 rounded"></div>
                                <span className="text-gray-600">Heavy Traffic</span>
                            </div>
                            <div className="flex items-center gap-2 text-xs">
                                <div className="w-3 h-3 bg-red-500 rounded"></div>
                                <span className="text-gray-600">Severe Congestion</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default TrafficWeatherOverlay;
