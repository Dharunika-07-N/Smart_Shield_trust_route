import { useState, useEffect } from 'react';

const useLocation = () => {
    const [location, setLocation] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!navigator.geolocation) {
            setError('Geolocation is not supported by your browser');
            setLoading(false);
            return;
        }

        const handleSuccess = (position) => {
            setLocation({
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
            });
            setLoading(false);
        };

        const handleError = (error) => {
            setError(error.message);
            setLoading(false);
        };

        navigator.geolocation.getCurrentPosition(handleSuccess, handleError, {
            enableHighAccuracy: true,
            timeout: 5000,
            maximumAge: 0,
        });

        // Also watch for changes
        const watchId = navigator.geolocation.watchPosition(handleSuccess, handleError, {
            enableHighAccuracy: true,
            timeout: 5000,
            maximumAge: 0,
        });

        return () => navigator.geolocation.clearWatch(watchId);
    }, []);

    return { location, error, loading };
};

export default useLocation;
