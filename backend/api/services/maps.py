"""Maps API service."""
import googlemaps
from typing import List, Dict, Tuple, Optional
from geopy.distance import distance as geopy_distance
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import settings
from api.schemas.delivery import Coordinate
from loguru import logger

class MapsService:
    """Service for maps and geocoding operations."""
    
    def __init__(self):
        self.gmaps = None
        if settings.GOOGLE_MAPS_API_KEY:
            self.gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
            logger.info("Google Maps client initialized")
        else:
            logger.warning("Google Maps API key not provided")
    
    def geocode(self, address: str) -> Optional[Coordinate]:
        """Geocode an address to coordinates."""
        if not self.gmaps:
            logger.warning("Geocoding without API key - returning mock data")
            return Coordinate(latitude=40.7128, longitude=-74.0060)
        
        try:
            geocode_result = self.gmaps.geocode(address)
            if geocode_result:
                location = geocode_result[0]['geometry']['location']
                return Coordinate(
                    latitude=location['lat'],
                    longitude=location['lng']
                )
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
        
        return None
    
    def reverse_geocode(self, coord: Coordinate) -> Optional[str]:
        """Reverse geocode coordinates to address."""
        if not self.gmaps:
            return "Unknown Address"
        
        try:
            result = self.gmaps.reverse_geocode((coord.latitude, coord.longitude))
            if result:
                return result[0].get('formatted_address', 'Unknown Address')
        except Exception as e:
            logger.error(f"Reverse geocoding error: {e}")
        
        return None
    
    def calculate_distance_matrix(
        self,
        origins: List[Coordinate],
        destinations: List[Coordinate],
        mode: str = "driving"
    ) -> Optional[List[List[Dict]]]:
        """Calculate distance matrix between multiple points."""
        if not self.gmaps:
            # Return mock distance matrix
            logger.warning("Distance matrix without API key - returning mock data")
            return self._mock_distance_matrix(origins, destinations)
        
        try:
            origins_list = [(c.latitude, c.longitude) for c in origins]
            destinations_list = [(c.latitude, c.longitude) for c in destinations]
            
            result = self.gmaps.distance_matrix(
                origins_list,
                destinations_list,
                mode=mode,
                units="metric"
            )
            
            if result['status'] == 'OK':
                return result['rows']
        except Exception as e:
            logger.error(f"Distance matrix error: {e}")
        
        return None
    
    def get_directions(
        self,
        origin: Coordinate,
        destination: Coordinate,
        waypoints: Optional[List[Coordinate]] = None,
        mode: str = "driving",
        avoid: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """Get directions between points."""
        if not self.gmaps:
            logger.warning("Directions without API key - returning mock data")
            return self._mock_directions(origin, destination)
        
        try:
            origin_str = f"{origin.latitude},{origin.longitude}"
            dest_str = f"{destination.latitude},{destination.longitude}"
            
            waypoints_list = None
            if waypoints:
                waypoints_list = [
                    f"{w.latitude},{w.longitude}" for w in waypoints
                ]
            
            directions = self.gmaps.directions(
                origin=origin_str,
                destination=dest_str,
                waypoints=waypoints_list,
                mode=mode,
                avoid=avoid or [],
                units="metric"
            )
            
            if directions:
                return directions[0]
        except Exception as e:
            logger.error(f"Directions error: {e}")
        
        return None
    
    def _mock_distance_matrix(
        self,
        origins: List[Coordinate],
        destinations: List[Coordinate]
    ) -> List[List[Dict]]:
        """Generate mock distance matrix using haversine distance."""
        matrix = []
        for origin in origins:
            row = []
            for dest in destinations:
                dist = geopy_distance(
                    (origin.latitude, origin.longitude),
                    (dest.latitude, dest.longitude)
                ).meters
                
                # Rough time estimate: 30 km/h average
                duration = dist / 8.33  # 8.33 m/s
                
                row.append({
                    'distance': {'value': int(dist), 'text': f"{dist/1000:.1f} km"},
                    'duration': {'value': int(duration), 'text': f"{duration/60:.1f} mins"}
                })
            matrix.append(row)
        
        return matrix
    
    def _mock_directions(
        self,
        origin: Coordinate,
        destination: Coordinate
    ) -> Dict:
        """Generate mock directions data."""
        dist = geopy_distance(
            (origin.latitude, origin.longitude),
            (destination.latitude, destination.longitude)
        ).meters
        
        duration = dist / 8.33
        
        return {
            'legs': [{
                'distance': {'value': int(dist), 'text': f"{dist/1000:.1f} km"},
                'duration': {'value': int(duration), 'text': f"{duration/60:.1f} mins"},
                'steps': []
            }],
            'overview_polyline': {'points': ''}
        }
    
    def calculate_straight_distance(
        self,
        coord1: Coordinate,
        coord2: Coordinate
    ) -> float:
        """Calculate straight-line distance between two points in meters."""
        return geopy_distance(
            (coord1.latitude, coord1.longitude),
            (coord2.latitude, coord2.longitude)
        ).meters

