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
        avoid: Optional[List[str]] = None,
        departure_time: Optional[int] = None,
        traffic_model: str = "best_guess"
    ) -> Optional[Dict]:
        """
        Get directions between points with traffic-aware routing.
        
        Args:
            origin: Starting point
            destination: End point
            waypoints: Intermediate waypoints
            mode: Transportation mode (driving, walking, bicycling)
            avoid: Things to avoid (tolls, highways, ferries, indoor)
            departure_time: Unix timestamp for traffic prediction (None = current time)
            traffic_model: Traffic model (best_guess, optimistic, pessimistic)
        """
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
            
            # Build directions request
            directions_params = {
                "origin": origin_str,
                "destination": dest_str,
                "mode": mode,
                "avoid": avoid or [],
                "units": "metric",
                "alternatives": True  # Get multiple route options
            }
            
            # Add traffic-aware parameters for driving mode
            if mode == "driving" and departure_time:
                directions_params["departure_time"] = departure_time
                directions_params["traffic_model"] = traffic_model
            
            if waypoints_list:
                directions_params["waypoints"] = waypoints_list
            
            directions = self.gmaps.directions(**directions_params)
            
            if directions:
                # Return the best route (first one) with traffic info
                route = directions[0]
                
                # Extract route geometry (polyline)
                if 'overview_polyline' in route:
                    polyline_points = route['overview_polyline'].get('points', '')
                    
                    # Decode polyline to get coordinates (simplified - in production use polyline library)
                    # For now, extract from legs
                    route_coords = []
                    instructions = []
                    for leg in route.get('legs', []):
                        for step in leg.get('steps', []):
                            start = step.get('start_location', {})
                            route_coords.append({
                                'lat': start.get('lat'),
                                'lng': start.get('lng')
                            })
                            end = step.get('end_location', {})
                            route_coords.append({
                                'lat': end.get('lat'),
                                'lng': end.get('lng')
                            })
                            
                            # Extract instruction
                            if 'html_instructions' in step:
                                # Clean HTML tags if needed, or keep for frontend to render
                                instructions.append(step['html_instructions'])
                    
                    route['route_coordinates'] = route_coords
                    route['instructions'] = instructions
                    route['polyline'] = polyline_points
                
                # Add traffic duration if available
                for leg in route.get('legs', []):
                    if 'duration_in_traffic' in leg:
                        route['has_traffic_data'] = True
                        break
                
                return route
        except Exception as e:
            logger.error(f"Directions error: {e}")
        
        return None
    
    def get_all_directions(
        self,
        origin: Coordinate,
        destination: Coordinate,
        mode: str = "driving",
        avoid: Optional[List[str]] = None,
        departure_time: Optional[int] = None,
        traffic_model: str = "best_guess"
    ) -> List[Dict]:
        """
        Get all available route options between points.
        
        Args:
            origin: Starting point
            destination: End point
            mode: Transportation mode
            avoid: Things to avoid
            departure_time: Unix timestamp for traffic
            traffic_model: Traffic model
            
        Returns:
            List of route dictionaries
        """
        if not self.gmaps:
            logger.warning("Directions without API key - returning mock data")
            return self._generate_mock_alternatives(origin, destination)
        
        try:
            origin_str = f"{origin.latitude},{origin.longitude}"
            dest_str = f"{destination.latitude},{destination.longitude}"
            
            # Build directions request
            directions_params = {
                "origin": origin_str,
                "destination": dest_str,
                "mode": mode,
                "avoid": avoid or [],
                "units": "metric",
                "alternatives": True  # Get multiple route options
            }
            
            # Add traffic-aware parameters for driving mode
            if mode == "driving" and departure_time:
                directions_params["departure_time"] = departure_time
                directions_params["traffic_model"] = traffic_model
            
            directions = self.gmaps.directions(**directions_params)
            
            routes = []
            if directions:
                for route in directions:
                    # Extract route geometry (polyline)
                    if 'overview_polyline' in route:
                        polyline_points = route['overview_polyline'].get('points', '')
                        
                        # Extract coords from legs
                        route_coords = []
                        instructions = []
                        for leg in route.get('legs', []):
                            for step in leg.get('steps', []):
                                start = step.get('start_location', {})
                                route_coords.append({
                                    'lat': start.get('lat'),
                                    'lng': start.get('lng')
                                })
                                end = step.get('end_location', {})
                                route_coords.append({
                                    'lat': end.get('lat'),
                                    'lng': end.get('lng')
                                })
                                
                                if 'html_instructions' in step:
                                    instructions.append(step['html_instructions'])
                        
                        route['route_coordinates'] = route_coords
                        route['instructions'] = instructions
                        route['polyline'] = polyline_points
                    
                    # Add traffic duration if available
                    for leg in route.get('legs', []):
                        if 'duration_in_traffic' in leg:
                            route['has_traffic_data'] = True
                            break
                    
                    routes.append(route)
                
                if routes:
                    return routes
                
        except Exception as e:
            logger.error(f"Directions error: {e}")
        
        # Fallback to mock if API fails or returns no routes
        logger.warning(f"Falling back to mock directions for {origin} -> {destination}")
        return self._generate_mock_alternatives(origin, destination)

    def _generate_mock_alternatives(self, origin: Coordinate, destination: Coordinate) -> List[Dict]:
        """Generate multiple mock route alternatives with different characteristics."""
        routes = []
        
        # 1. Standard/Fastest Route (Straight-ish)
        routes.append(self._mock_directions(origin, destination, "fastest", 0))
        
        # 2. Safer Route (Slightly longer diversion)
        routes.append(self._mock_directions(origin, destination, "safest", 0.012))
        
        # 3. Alternative Route (Larger diversion)
        routes.append(self._mock_directions(origin, destination, "alternative", -0.018))
        
        return routes

    def decode_polyline(self, encoded: str) -> List[Dict]:
        """Decode Google polyline string to list of coordinates."""
        try:
            import polyline
            coords = polyline.decode(encoded)
            return [{'lat': lat, 'lng': lon} for lat, lon in coords]
        except ImportError:
            logger.warning("polyline library not installed, using fallback")
            return []
    
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
        destination: Coordinate,
        name: str = "standard",
        offset: float = 0
    ) -> Dict:
        """Generate mock directions data with variability."""
        # Calculate base metrics
        base_dist = geopy_distance(
            (origin.latitude, origin.longitude),
            (destination.latitude, destination.longitude)
        ).meters
        
        # Add variability based on offset
        # Offset shifts the midpoint to create a 'curve'
        dist_factor = 1.0 + abs(offset) * 10 
        dist = base_dist * dist_factor
        
        # Slower speed for safer/alternative routes in mock
        speed = 8.33 # ~30km/h
        if offset != 0:
            speed = 7.5 # ~27km/h
            
        duration = dist / speed
        
        # Mock route coordinates (curved path using offset)
        num_points = 8
        route_coords = []
        for i in range(num_points + 1):
            ratio = i / num_points
            # Linear interpolation
            lat = origin.latitude + (destination.latitude - origin.latitude) * ratio
            lng = origin.longitude + (destination.longitude - origin.longitude) * ratio
            
            # Add 'bulge' in the middle based on offset
            # bulge follows a simple parabola: offset * (1 - (2*ratio - 1)^2)
            bulge = offset * (1.0 - (2.0 * ratio - 1.0)**2)
            
            # Apply bulge perpendicular to the general direction (simplified as adding to lat/lng)
            route_coords.append({
                'lat': lat + bulge,
                'lng': lng + bulge * 0.5
            })
            
        instructions = [
            f'Head towards {name} route direction',
            f'Continue on path with {abs(offset)*1000:.1f}m diversion',
            'Arrive at destination'
        ]
        
        return {
            'legs': [{
                'distance': {'value': int(dist), 'text': f"{dist/1000:.1f} km"},
                'duration': {'value': int(duration), 'text': f"{duration/60:.1f} mins"},
                'steps': [
                    {
                        'html_instructions': instructions[0],
                        'start_location': {'lat': origin.latitude, 'lng': origin.longitude},
                        'end_location': {'lat': route_coords[2]['lat'], 'lng': route_coords[2]['lng']}
                    },
                    {
                        'html_instructions': instructions[1],
                        'start_location': {'lat': route_coords[2]['lat'], 'lng': route_coords[2]['lng']},
                        'end_location': {'lat': route_coords[6]['lat'], 'lng': route_coords[6]['lng']}
                    },
                    {
                         'html_instructions': instructions[2],
                         'start_location': {'lat': route_coords[6]['lat'], 'lng': route_coords[6]['lng']},
                         'end_location': {'lat': destination.latitude, 'lng': destination.longitude}
                    }
                ]
            }],
            'route_coordinates': route_coords,
            'instructions': instructions,
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

    def find_nearby_places(
            self,
            location: Coordinate,
            radius_meters: int = 2000,
            place_type: str = "police"
        ) -> List[Dict]:
            """
            Find nearby places using Google Places API.
            
            Args:
                location: Search center
                radius_meters: Search radius in meters
                place_type: Type of place to search (police, hospital, store, etc.)
            
            Returns:
                List of places with details
            """
            if not self.gmaps:
                logger.warning("Places search without API key - returning empty list")
                # Return mock data for development
                return self._mock_nearby_places(location, place_type)
            
            try:
                # Search nearby places
                places_result = self.gmaps.places_nearby(
                    location=(location.latitude, location.longitude),
                    radius=radius_meters,
                    type=place_type
                )
                
                places = []
                if 'results' in places_result:
                    for result in places_result['results']:
                        place = {
                            "name": result.get('name'),
                            "location": {
                                "latitude": result['geometry']['location']['lat'],
                                "longitude": result['geometry']['location']['lng']
                            },
                            "address": result.get('vicinity'),
                            "place_id": result.get('place_id'),
                            "rating": result.get('rating'),
                            "types": result.get('types', []),
                            "is_open": result.get('opening_hours', {}).get('open_now')
                        }
                        
                        # Calculate distance from search center
                        dist = self.calculate_straight_distance(
                            location,
                            Coordinate(
                                latitude=place['location']['latitude'],
                                longitude=place['location']['longitude']
                            )
                        )
                        place['distance_meters'] = dist
                        
                        places.append(place)
                
                return places
                
            except Exception as e:
                logger.error(f"Places search error: {e}")
                return []

    def _mock_nearby_places(self, location: Coordinate, place_type: str) -> List[Dict]:
        """Generate mock nearby places."""
        import random
        
        places = []
        count = random.randint(1, 5)
        
        for i in range(count):
            # Random offset from current location
            lat_offset = (random.random() - 0.5) * 0.02
            lng_offset = (random.random() - 0.5) * 0.02
            
            place_lat = location.latitude + lat_offset
            place_lng = location.longitude + lng_offset
            
            dist = self.calculate_straight_distance(
                location,
                Coordinate(latitude=place_lat, longitude=place_lng)
            )
            
            if place_type == "police":
                name = f"Police Station {i+1}"
            elif place_type == "hospital":
                name = f"City Hospital {i+1}"
            else:
                name = f"Safe Store {i+1}"
            
            places.append({
                "name": name,
                "location": {
                    "latitude": place_lat,
                    "longitude": place_lng
                },
                "address": f"Mock Address {i+1}",
                "place_id": f"mock_place_{i}",
                "rating": 4.5,
                "types": [place_type, "establishment"],
                "distance_meters": dist,
                "is_open": True
            })
            
        return places

