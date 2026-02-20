"""
backend/api/services/graphhopper.py - GraphHopper API Integration
"""
import requests
import polyline
from typing import List, Dict, Optional, Tuple
from loguru import logger
from config.config import settings

class GraphHopperService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.GRAPHHOPPER_API_KEY
        self.base_url = "https://graphhopper.com/api/1"

    def get_directions(
        self, 
        origin: Tuple[float, float], 
        destination: Tuple[float, float], 
        waypoints: Optional[List[Tuple[float, float]]] = None,
        vehicle: str = "car",
        locale: str = "en",
        **kwargs
    ) -> Optional[Dict]:
        """
        Get directions from GraphHopper Routing API
        """
        if not self.api_key:
            logger.warning("GraphHopper API key not provided")
            return None

        url = f"{self.base_url}/route"
        
        # Prepare points: [lat, lng] -> "lat,lng"
        points = [f"{origin[0]},{origin[1]}"]
        if waypoints:
            for wp in waypoints:
                points.append(f"{wp[0]},{wp[1]}")
        points.append(f"{destination[0]},{destination[1]}")

        params = {
            "point": points,
            "vehicle": vehicle,
            "locale": locale,
            "key": self.api_key,
            "points_encoded": "true", # GraphHopper uses its own encoding by default
            "instructions": "true",
            "type": "json"
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if response.status_code != 200:
                logger.error(f"GraphHopper API error: {data.get('message', 'Unknown error')}")
                return None

            # Normalize to match Google Maps-like structure used in maps.py
            return self._normalize_response(data)
        except Exception as e:
            logger.error(f"GraphHopper request failed: {e}")
            return None

    def _normalize_response(self, gh_data: Dict) -> Dict:
        """
        Convert GraphHopper response format to the one expected by our MapsService
        """
        if not gh_data.get('paths'):
            return {}

        path = gh_data['paths'][0]
        
        # GraphHopper uses [lng, lat] for points in its encoded format if decoded?
        # Actually points_encoded=true returns a string.
        
        # Create a Google-like structure
        route = {
            'summary': path.get('description', 'GraphHopper Route'),
            'legs': [{
                'distance': {
                    'text': f"{path['distance'] / 1000:.1f} km",
                    'value': int(path['distance'])
                },
                'duration': {
                    'text': f"{int(path['time'] / 60000)} mins",
                    'value': int(path['time'] / 1000) # milliseconds to seconds
                },
                'steps': self._normalize_instructions(path.get('instructions', [])),
                'start_address': "Coordinates Search", # GH geocoding would be extra
                'end_address': "Coordinates Search"
            }],
            'overview_polyline': {
                'points': path['points'] # This is a polyline string
            },
            # Custom field for our app
            'waypoint_order': list(range(len(gh_data.get('points', [])))),
            'average_safety_score': 0 # To be calculated by SafetyScorer
        }

        return route

    def _normalize_instructions(self, gh_instructions: List[Dict]) -> List[Dict]:
        steps = []
        for instr in gh_instructions:
            steps.append({
                'html_instructions': instr.get('text', ''),
                'distance': {
                    'text': f"{instr['distance']:.0f} m",
                    'value': int(instr['distance'])
                },
                'duration': {
                    'text': f"{int(instr['time'] / 1000)} s",
                    'value': int(instr['time'] / 1000)
                },
                'maneuver': self._map_maneuver(instr.get('sign', 0)),
                'start_location': {'lat': 0, 'lng': 0}, # GH doesn't provide these per instruction directly easily
                'end_location': {'lat': 0, 'lng': 0}
            })
        return steps

    def _map_maneuver(self, sign: int) -> str:
        # GraphHopper sign codes
        mapping = {
            -3: "sharp_left",
            -2: "left",
            -1: "slight_left",
            0: "straight",
            1: "slight_right",
            2: "right",
            3: "sharp_right",
            4: "destination",
            5: "arrival_at_waypoint",
            6: "roundabout"
        }
        return mapping.get(sign, "straight")

    def get_matrix(self, points: List[Tuple[float, float]], out_arrays: List[str] = ["times", "distances"]) -> Optional[Dict]:
        """
        Get distance/time matrix using GraphHopper Matrix API
        """
        if not self.api_key: return None
        
        url = f"{self.base_url}/matrix"
        point_strings = [f"{p[0]},{p[1]}" for p in points]
        
        params = {
            "point": point_strings,
            "out_array": out_arrays,
            "key": self.api_key,
            "vehicle": "car"
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            return response.json()
        except Exception as e:
            logger.error(f"GraphHopper Matrix API failed: {e}")
            return None

    def solve_vrp(self, vehicles: List[Dict], services: List[Dict]) -> Optional[Dict]:
        """
        Solve Vehicle Routing Problem using GraphHopper Route Optimization API
        """
        if not self.api_key: return None
        
        url = f"{self.base_url}/vrp/optimize"
        
        body = {
            "vehicles": vehicles,
            "services": services
        }
        
        try:
            # VRP is a POST request
            response = requests.post(f"{url}?key={self.api_key}", json=body, timeout=20)
            data = response.json()
            
            if response.status_code == 200:
                return data
            else:
                logger.error(f"GraphHopper VRP error: {data.get('message', 'Unknown error')}")
                return None
        except Exception as e:
            logger.error(f"GraphHopper VRP request failed: {e}")
            return None

    def geocode(self, query: str) -> Optional[Dict[str, float]]:
        """
        Geocoding using GraphHopper Geocoding API
        """
        if not self.api_key:
            return None

        url = f"{self.base_url}/geocode"
        params = {
            "q": query,
            "key": self.api_key,
            "limit": 1
        }

        try:
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if data.get('hits'):
                hit = data['hits'][0]
                return {
                    'lat': hit['point']['lat'],
                    'lng': hit['point']['lng'],
                    'display_name': hit.get('name', query)
                }
        except Exception:
            pass
        return None

    def reverse_geocode(self, lat: float, lng: float) -> Optional[str]:
        """
        Reverse geocoding using GraphHopper Geocoding API
        """
        if not self.api_key:
            return None

        url = f"{self.base_url}/geocode"
        params = {
            "reverse": "true",
            "point": f"{lat},{lng}",
            "key": self.api_key
        }

        try:
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if data.get('hits'):
                return data['hits'][0].get('name', "Unknown Address")
        except Exception:
            pass
        return "Unknown Address"
