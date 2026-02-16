"""
backend/api/services/maps.py - Complete Maps Service with Real Routing
"""
import googlemaps
import requests
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import polyline
import math
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import settings
from api.schemas.delivery import Coordinate
from loguru import logger
import functools
try:
    from geopy.distance import distance as geopy_distance
except ImportError:
    geopy_distance = None
import os

class MapsService:
    def __init__(self, api_key: str = None, weather_api_key: Optional[str] = None):
        # Use provided key or fall back to settings
        self.api_key = api_key or settings.GOOGLE_MAPS_API_KEY
        self.weather_api_key = weather_api_key or os.getenv("OPENWEATHER_API_KEY") # Attempt to get from env if not passed
        
        if self.api_key:
            self.gmaps = googlemaps.Client(key=self.api_key)
        else:
            self.gmaps = None
            print("Warning: Google Maps API key not provided")
            
        # Crime data by district (Tamil Nadu 2022)
        self.crime_data = {
            'Coimbatore': {'murders': 45, 'theft': 890, 'accidents': 1245, 'total': 2180},
            'Chennai': {'murders': 89, 'theft': 2340, 'accidents': 2890, 'total': 5319},
            'Madurai': {'murders': 67, 'theft': 1120, 'accidents': 1567, 'total': 2754},
            'Tiruchirappalli': {'murders': 34, 'theft': 670, 'accidents': 890, 'total': 1594},
            'Salem': {'murders': 56, 'theft': 780, 'accidents': 1123, 'total': 1959},
            'Tiruppur': {'murders': 23, 'theft': 450, 'accidents': 678, 'total': 1151},
        }

    def _get_lat_lng(self, point: any) -> Tuple[float, float]:
        """Utility to convert various point formats to (lat, lng) tuple"""
        if hasattr(point, 'latitude'):
            return (point.latitude, point.longitude)
        if isinstance(point, dict):
            if 'lat' in point: return (point['lat'], point['lng'])
            if 'latitude' in point: return (point['latitude'], point['longitude'])
        return point

    def get_directions(
        self, 
        origin: any, 
        destination: any, 
        waypoints: Optional[List[any]] = None,
        alternatives: bool = True,
        **kwargs
    ) -> Optional[List[Dict]]:
        """
        Get driving directions with multiple alternatives and traffic data
        """
        if not self.gmaps:
            return self._get_mock_directions(origin, destination, waypoints)
            
        try:
            orig = self._get_lat_lng(origin)
            dest = self._get_lat_lng(destination)
            
            # Prepare waypoints if multi-stop delivery
            waypoint_list = None
            if waypoints:
                waypoint_list = [f"{self._get_lat_lng(wp)[0]},{self._get_lat_lng(wp)[1]}" for wp in waypoints]
            
            directions = self.gmaps.directions(
                origin=orig,
                destination=dest,
                waypoints=waypoint_list,
                mode="driving",
                alternatives=alternatives,
                departure_time=datetime.now(),
                traffic_model="best_guess",
                optimize_waypoints=True if waypoints else False
            )
            
            if not directions:
                return self._get_mock_directions(origin, destination, waypoints)

            # Post-process for backward compatibility (adding route_coordinates)
            for route in directions:
                route_coords = []
                for leg in route.get('legs', []):
                    for step in leg.get('steps', []):
                        start = step.get('start_location', {})
                        route_coords.append({'lat': start.get('lat'), 'lng': start.get('lng')})
                        end = step.get('end_location', {})
                        route_coords.append({'lat': end.get('lat'), 'lng': end.get('lng')})
                route['route_coordinates'] = route_coords
            
            return directions
        except Exception as e:
            logger.warning(f"Google Maps API error: {e}. Falling back to mock data.")
            return self._get_mock_directions(origin, destination, waypoints)

    def _get_mock_directions(self, origin, destination, waypoints=None) -> List[Dict]:
        """Generate mock directions when API is unavailable - Returns FAST and SAFE options."""
        orig = self._get_lat_lng(origin)
        dest = self._get_lat_lng(destination)
        
        # Calculate midpoint
        mid_lat = (orig[0] + dest[0]) / 2
        mid_lng = (orig[1] + dest[1]) / 2
        
        # Route 1: Fastest (Direct Line)
        # Represents taking the main highway
        fast_route = {
            'summary': 'Main Highway (Verified Fast)',
            'legs': [{
                'distance': {'text': '12.5 km', 'value': 12500},
                'duration': {'text': '18 mins', 'value': 1080}, # 18 mins
                'duration_in_traffic': {'text': '20 mins', 'value': 1200},
                'start_address': f'{orig[0]}, {orig[1]}',
                'end_address': f'{dest[0]}, {dest[1]}',
                'steps': [{
                    'distance': {'text': '12.5 km', 'value': 12500},
                    'duration': {'text': '18 mins', 'value': 1080},
                    'html_instructions': 'Take the main highway directly to destination',
                    'start_location': {'lat': orig[0], 'lng': orig[1]},
                    'end_location': {'lat': dest[0], 'lng': dest[1]},
                    'maneuver': 'straight'
                }]
            }],
            'overview_polyline': {'points': polyline.encode([orig, dest])},
            'route_coordinates': [
                {'lat': orig[0], 'lng': orig[1]}, 
                {'lat': mid_lat, 'lng': mid_lng}, # Midpoint
                {'lat': dest[0], 'lng': dest[1]}
            ],
            'warnings': []
        }
        
        # Route 2: Safest (Slight detour through residential/safe areas)
        # We create a "curved" path by adding an offset waypoint
        offset_lat = mid_lat + 0.01  # ~1km offset
        offset_lng = mid_lng + 0.01
        
        safe_route = {
            'summary': 'Safety Corridor (Patrolled)',
            'legs': [{
                'distance': {'text': '14.2 km', 'value': 14200}, # Longer
                'duration': {'text': '24 mins', 'value': 1440},  # Slower
                'duration_in_traffic': {'text': '25 mins', 'value': 1500},
                'start_address': f'{orig[0]}, {orig[1]}',
                'end_address': f'{dest[0]}, {dest[1]}',
                'steps': [
                    {
                        'distance': {'text': '7.1 km', 'value': 7100},
                        'duration': {'text': '12 mins', 'value': 720},
                        'html_instructions': 'Head towards Safety Zone',
                        'start_location': {'lat': orig[0], 'lng': orig[1]},
                        'end_location': {'lat': offset_lat, 'lng': offset_lng},
                        'maneuver': 'turn-right'
                    },
                    {
                        'distance': {'text': '7.1 km', 'value': 7100},
                        'duration': {'text': '12 mins', 'value': 720},
                        'html_instructions': 'Continue to destination through well-lit area',
                        'start_location': {'lat': offset_lat, 'lng': offset_lng},
                        'end_location': {'lat': dest[0], 'lng': dest[1]},
                        'maneuver': 'turn-left'
                    }
                ]
            }],
            'overview_polyline': {'points': polyline.encode([orig, (offset_lat, offset_lng), dest])},
            'route_coordinates': [
                {'lat': orig[0], 'lng': orig[1]},
                {'lat': offset_lat, 'lng': offset_lng}, # Safe detour
                {'lat': dest[0], 'lng': dest[1]}
            ],
            'warnings': [] 
        }
        
        return [fast_route, safe_route]
    
    def process_routes(
        self, 
        directions: List[Dict], 
        origin: any
    ) -> List[Dict]:
        """Process and score multiple route alternatives"""
        routes = []
        
        for idx, route in enumerate(directions):
            leg = route['legs'][0]
            
            # Extract route geometry
            polyline_points = self.decode_polyline(
                route['overview_polyline']['points']
            )
            
            # Calculate comprehensive scores
            safety_score = self.calculate_safety_score(route, polyline_points)
            weather_score = self.get_weather_impact(polyline_points[0])
            
            # Extract turn-by-turn instructions
            turn_by_turn = self.extract_turn_by_turn(leg['steps'])
            
            route_info = {
                'index': idx,
                'duration': leg['duration']['value'],  # seconds
                'duration_in_traffic': leg.get('duration_in_traffic', {}).get('value', leg['duration']['value']),
                'distance': leg['distance']['value'],  # meters
                'summary': route['summary'],
                'polyline': route['overview_polyline']['points'],
                'polyline_decoded': [{'lat': p[0], 'lng': p[1]} for p in polyline_points],
                'safety_score': safety_score,
                'weather_score': weather_score,
                'speed_score': self.calculate_speed_score(leg),
                'distance_score': self.calculate_distance_score(leg),
                'turn_by_turn': turn_by_turn,
                'warnings': self.generate_warnings(safety_score, weather_score),
                'waypoint_order': route.get('waypoint_order', []),
                'route_coordinates': route.get('route_coordinates', [])
            }
            
            # Calculate composite score
            route_info['composite_score'] = self.calculate_composite_score(route_info)
            
            routes.append(route_info)
        
        # Sort by composite score
        routes.sort(key=lambda x: x['composite_score'], reverse=True)
        
        return routes
    
    def decode_polyline(self, polyline_str: str) -> List[Tuple[float, float]]:
        """Decode Google Maps polyline to list of coordinates"""
        return polyline.decode(polyline_str)
    
    def calculate_safety_score(
        self, 
        route_data: Dict, 
        polyline_points: Optional[List[Tuple[float, float]]] = None
    ) -> int:
        """Calculate comprehensive safety score"""
        score = 70  # Base score
        
        # 1. Highway bonus (safer, faster)
        summary = route_data.get('summary', '').lower()
        if any(term in summary for term in ['highway', 'expressway', 'nh', 'sh']):
            score += 15
        
        # 2. Route complexity penalty
        leg = route_data['legs'][0]
        turn_count = len(leg['steps'])
        score -= min(10, turn_count / 5)
        
        # 3. Time-based adjustment
        hour = datetime.now().hour
        if hour >= 22 or hour <= 6:  # Night hours
            score -= 15
        elif 6 <= hour <= 9 or 17 <= hour <= 20:  # Peak hours
            score -= 5
        
        # 4. District crime data
        if polyline_points is None:
            # Fallback for compatibility if polyline is not decoded yet
            if 'overview_polyline' in route_data:
                polyline_points = self.decode_polyline(route_data['overview_polyline']['points'])
        
        if polyline_points:
            district = self.get_district_from_route(polyline_points)
            if district and district in self.crime_data:
                crime_rate = self.crime_data[district]['total']
                # Normalize crime rate (lower is better)
                crime_penalty = min(15, crime_rate / 200)
                score -= crime_penalty
        
        # 5. Route length consideration (longer routes = more exposure)
        distance_km = leg['distance']['value'] / 1000
        if distance_km > 50:
            score -= 10
        elif distance_km > 30:
            score -= 5
        
        return max(0, min(100, int(score)))
    
    def get_district_from_route(self, polyline_points: List[Tuple[float, float]]) -> Optional[str]:
        """Determine district from route midpoint"""
        if not polyline_points:
            return None
        
        mid_point = polyline_points[len(polyline_points) // 2]
        
        # Approximate district boundaries (simplified)
        lat, lng = mid_point
        
        # Coimbatore region
        if 10.8 <= lat <= 11.2 and 76.8 <= lng <= 77.1:
            return 'Coimbatore'
        # Tiruppur region
        elif 11.0 <= lat <= 11.2 and 77.2 <= lng <= 77.5:
            return 'Tiruppur'
        # Chennai region (Approximate)
        elif 12.8 <= lat <= 13.2 and 80.1 <= lng <= 80.4:
            return 'Chennai'
        # Madurai region (Approximate)
        elif 9.8 <= lat <= 10.0 and 78.0 <= lng <= 78.3:
            return 'Madurai'
        
        return None
    
    def get_weather_impact(self, location: Tuple[float, float]) -> int:
        """Get weather conditions and calculate impact score"""
        if not self.weather_api_key or self.weather_api_key == "YOUR_OPENWEATHER_KEY":
            return 85  # Default good weather score
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': location[0],
                'lon': location[1],
                'appid': self.weather_api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if response.status_code != 200:
                return 85

            score = 100
            
            # Rain penalty
            if 'rain' in data:
                rain_mm = data['rain'].get('1h', 0)
                score -= min(30, rain_mm * 3)
            
            # Visibility penalty
            visibility = data.get('visibility', 10000)
            if visibility < 1000:
                score -= 20
            elif visibility < 5000:
                score -= 10
            
            # Wind penalty
            wind_speed = data.get('wind', {}).get('speed', 0)
            if wind_speed > 15:  # Strong wind
                score -= 15
            elif wind_speed > 10:
                score -= 5
            
            return max(0, min(100, int(score)))
            
        except Exception as e:
            print(f"Weather API error: {e}")
            return 85
    
    def calculate_speed_score(self, leg: Dict) -> int:
        """Calculate speed efficiency score"""
        distance_m = leg['distance']['value']
        duration_s = leg.get('duration_in_traffic', leg['duration'])['value']
        
        if duration_s == 0: return 100
        
        # Calculate average speed (km/h)
        avg_speed = (distance_m / 1000) / (duration_s / 3600)
        
        # Score based on speed (optimal is 40-60 km/h in city)
        if 40 <= avg_speed <= 60:
            return 100
        elif 30 <= avg_speed < 40 or 60 < avg_speed <= 70:
            return 85
        elif 20 <= avg_speed < 30 or 70 < avg_speed <= 80:
            return 70
        else:
            return 50
    
    def calculate_distance_score(self, leg: Dict) -> int:
        """Calculate distance efficiency score"""
        distance_km = leg['distance']['value'] / 1000
        
        # Shorter is generally better, but normalize to 0-100
        if distance_km <= 5:
            return 100
        elif distance_km <= 15:
            return 90
        elif distance_km <= 30:
            return 75
        elif distance_km <= 50:
            return 60
        else:
            return max(40, 100 - int(distance_km))
    
    def extract_turn_by_turn(self, steps: List[Dict]) -> List[Dict]:
        """Extract detailed turn-by-turn navigation instructions with enhanced formatting"""
        instructions = []
        
        for idx, step in enumerate(steps):
            # Extract polyline for this step if available
            step_polyline = None
            if 'polyline' in step and 'points' in step['polyline']:
                step_polyline = step['polyline']['points']
            
            instruction = {
                'step_number': idx + 1,
                'distance': step['distance']['text'],
                'distance_value': step['distance']['value'],
                'duration': step['duration']['text'],
                'duration_value': step['duration']['value'],
                'instruction': step['html_instructions'],
                'maneuver': step.get('maneuver', 'straight'),
                'start_location': step['start_location'],
                'end_location': step['end_location'],
                'polyline': step_polyline,
                # Add traffic data if available
                'has_traffic_data': 'duration_in_traffic' in step,
                'traffic_duration': step.get('duration_in_traffic', {}).get('value'),
                'traffic_delay': self._calculate_traffic_delay(step)
            }
            instructions.append(instruction)
        
        return instructions
    
    def _calculate_traffic_delay(self, step: Dict) -> Optional[int]:
        """Calculate traffic delay for a step in seconds"""
        if 'duration_in_traffic' not in step:
            return None
        
        normal_duration = step['duration']['value']
        traffic_duration = step['duration_in_traffic']['value']
        delay = traffic_duration - normal_duration
        
        return max(0, delay)
    
    def calculate_composite_score(self, route_info: Dict) -> float:
        """Calculate weighted composite score for route ranking"""
        weights = {
            'safety': 0.40,
            'speed': 0.25,
            'distance': 0.20,
            'weather': 0.15
        }
        
        composite = (
            route_info['safety_score'] * weights['safety'] +
            route_info['speed_score'] * weights['speed'] +
            route_info['distance_score'] * weights['distance'] +
            route_info['weather_score'] * weights['weather']
        )
        
        return round(composite, 2)
    
    def generate_warnings(self, safety_score: int, weather_score: int) -> List[str]:
        """Generate route warnings based on conditions"""
        warnings = []
        
        if safety_score < 50:
            warnings.append("⚠️ Low safety score - Consider alternative route")
        elif safety_score < 70:
            warnings.append("⚡ Moderate safety - Stay alert")
        
        if weather_score < 60:
            warnings.append("🌧️ Poor weather conditions - Drive carefully")
        elif weather_score < 80:
            warnings.append("☁️ Weather may affect travel time")
        
        hour = datetime.now().hour
        if hour >= 22 or hour <= 6:
            warnings.append("🌙 Night travel - Extra caution advised")
        
        return warnings
    
    def create_safety_heatmap_data(
        self, 
        bounds: Dict[str, Dict[str, float]]
    ) -> List[Dict]:
        """
        Generate safety heatmap data for map overlay
        """
        heatmap_points = []
        
        # Create grid of points within bounds
        lat_step = (bounds['northeast']['lat'] - bounds['southwest']['lat']) / 20
        lng_step = (bounds['northeast']['lng'] - bounds['southwest']['lng']) / 20
        
        for i in range(21):
            for j in range(21):
                lat = bounds['southwest']['lat'] + (i * lat_step)
                lng = bounds['southwest']['lng'] + (j * lng_step)
                
                # Calculate safety intensity for this point
                district = self.get_district_from_route([(lat, lng)])
                intensity = self.calculate_point_safety(lat, lng, district)
                
                heatmap_points.append({
                    'lat': lat,
                    'lng': lng,
                    'intensity': intensity
                })
        
        return heatmap_points
    
    def calculate_point_safety(
        self, 
        lat: float, 
        lng: float, 
        district: Optional[str]
    ) -> float:
        """Calculate safety intensity for a point (0-1, higher is safer)"""
        base_safety = 0.7
        
        # District crime factor
        if district and district in self.crime_data:
            crime_rate = self.crime_data[district]['total']
            crime_factor = max(0, 1 - (crime_rate / 5000))
            base_safety = (base_safety + crime_factor) / 2
        
        # Time factor
        hour = datetime.now().hour
        if hour >= 22 or hour <= 6:
            base_safety *= 0.7
        elif 6 <= hour <= 9 or 17 <= hour <= 20:
            base_safety *= 0.85
        
        return round(base_safety, 2)
    
    def optimize_multi_stop_route(
        self, 
        origin: any,
        destination: any,
        stops: List[any]
    ) -> Dict:
        """
        Optimize route for multiple delivery stops
        """
        orig = self._get_lat_lng(origin)
        dest = self._get_lat_lng(destination)
        stop_list = [self._get_lat_lng(s) for s in stops]
        
        directions = self.get_directions(
            origin=orig,
            destination=dest,
            waypoints=stop_list,
            alternatives=False
        )
        
        if not directions:
            return None
        
        route = directions[0]
        optimized_order = route.get('waypoint_order', [])
        
        # Calculate total metrics
        total_distance = sum(leg['distance']['value'] for leg in route['legs'])
        total_duration = sum(leg['duration']['value'] for leg in route['legs'])
        
        # Extract polyline for entire route
        polyline_points = self.decode_polyline(route['overview_polyline']['points'])
        
        return {
            'optimized_order': optimized_order,
            'total_distance': total_distance,
            'total_duration': total_duration,
            'total_distance_text': f"{total_distance / 1000:.1f} km",
            'total_duration_text': f"{total_duration // 60} min",
            'polyline': route['overview_polyline']['points'],
            'polyline_decoded': [{'lat': p[0], 'lng': p[1]} for p in polyline_points],
            'legs': [
                {
                    'distance': leg['distance']['text'],
                    'duration': leg['duration']['text'],
                    'start_address': leg['start_address'],
                    'end_address': leg['end_address']
                }
                for leg in route['legs']
            ],
            'safety_score': self.calculate_safety_score(route, polyline_points)
        }
    
    # --- Compatibility Methods ---
    
    def calculate_straight_distance(self, coord1: Coordinate, coord2: Coordinate) -> float:
        """Calculate straight-line distance in meters (Required by RouteOptimizer)"""
        if geopy_distance:
            return geopy_distance(
                (coord1.latitude, coord1.longitude),
                (coord2.latitude, coord2.longitude)
            ).meters
        # Simple Euclidean fallback if geopy is missing
        return ((coord1.latitude - coord2.latitude)**2 + (coord1.longitude - coord2.longitude)**2)**0.5 * 111000

    def geocode(self, address: str) -> Optional[Coordinate]:
        """Geocode an address (Required by Auth/Registration)"""
        res = self.geocode_address(address)
        if res:
            return Coordinate(latitude=res['lat'], longitude=res['lng'])
        return None

    @functools.lru_cache(maxsize=512)
    def geocode_address(self, address: str) -> Optional[Dict[str, float]]:
        """Convert address to coordinates with caching."""
        if not self.gmaps: return None
        try:
            result = self.gmaps.geocode(address)
            if result:
                location = result[0]['geometry']['location']
                return {'lat': location['lat'], 'lng': location['lng']}
        except Exception as e:
            logger.error(f"Geocoding error for '{address}': {e}")
        return None
    
    @functools.lru_cache(maxsize=512)
    def _reverse_geocode_cached(self, lat: float, lng: float) -> str:
        """Internal cached reverse geocoding."""
        if not self.gmaps: return "Unknown Address"
        try:
            result = self.gmaps.reverse_geocode((lat, lng))
            if result:
                return result[0]['formatted_address']
        except Exception as e:
            logger.error(f"Reverse geocoding error at ({lat}, {lng}): {e}")
        return "Unknown Address"

    def reverse_geocode(self, lat_or_coord: any, lng: Optional[float] = None) -> Optional[str]:
        """Convert coordinates to address (Supports both signatures) with caching."""
        try:
            if hasattr(lat_or_coord, 'latitude'):
                lat, lng = lat_or_coord.latitude, lat_or_coord.longitude
            elif isinstance(lat_or_coord, (int, float)) and lng is not None:
                lat, lng = lat_or_coord, lng
            else:
                return "Unknown Address"
            
            # Round coordinates to ~10m precision for cache hits on nearby points
            return self._reverse_geocode_cached(round(lat, 4), round(lng, 4))
        except Exception as e:
            logger.error(f"Error in reverse_geocode wrapper: {e}")
            return "Unknown Address"

    def get_all_directions(self, origin: any, destination: any, **kwargs) -> List[Dict]:
        """Get all route variations (Required by RouteOptimizer)"""
        return self.get_directions(origin, destination, alternatives=True, **kwargs)

    def find_nearby_places(self, location: Coordinate, radius_meters: int = 2000, place_type: str = "police") -> List[Dict]:
        """Find nearby places (Required by SafetyService)"""
        if not self.gmaps: return []
        try:
            places_result = self.gmaps.places_nearby(
                location=(location.latitude, location.longitude),
                radius=radius_meters,
                type=place_type
            )
            places = []
            if 'results' in places_result:
                for result in places_result['results']:
                    places.append({
                        "name": result.get('name'),
                        "location": {
                            "latitude": result['geometry']['location']['lat'],
                            "longitude": result['geometry']['location']['lng']
                        },
                        "address": result.get('vicinity'),
                        "place_id": result.get('place_id'),
                        "is_open": result.get('opening_hours', {}).get('open_now'),
                        "distance_meters": self.calculate_straight_distance(
                            location, 
                            Coordinate(latitude=result['geometry']['location']['lat'], longitude=result['geometry']['location']['lng'])
                        )
                    })
            return places
        except Exception:
            return []
import os
